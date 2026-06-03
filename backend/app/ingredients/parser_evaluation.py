from __future__ import annotations

import argparse
import csv
import json
import random
import time
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from app.ingredients.parser_adapter import ParsedIngredientLine, parse_ingredient_line

DATASET_FILES = {
    "ar": "recipes_raw_nosource_ar.json",
    "epi": "recipes_raw_nosource_epi.json",
    "fn": "recipes_raw_nosource_fn.json",
}

HAND_PICKED_LINES = [
    "4 skinless, boneless chicken breast halves",
    "2 tablespoons butter",
    "2 (10.75 ounce) cans condensed cream of chicken soup",
    "1 onion, finely diced",
    "2 (10 ounce) packages refrigerated biscuit dough, torn into pieces",
    "Kosher salt and fresh cracked black pepper",
    "Garnish: ground nutmeg",
    "Apple cider vinegar, best quality",
    "Crusty bread, for serving",
    "1 (15-ounce) can cannellini beans, with liquid",
]


@dataclass(frozen=True)
class IngredientLineSample:
    source: str
    source_file: str
    recipe_id: str | None
    title: str | None
    line_position: int | None
    raw_line: str


@dataclass(frozen=True)
class ParsedSample:
    sample: IngredientLineSample
    parsed: ParsedIngredientLine


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate ingredient-parser-nlp on KitchenCopilot recipe data."
    )
    parser.add_argument(
        "dataset_path",
        type=Path,
        help="Path to the recipes_raw directory containing the three JSON files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(".eval") / "ingredient-parser",
        help="Directory for local generated evaluation reports.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--stratified-per-source", type=int, default=500)
    parser.add_argument("--performance-size", type=int, default=10000)
    parser.add_argument("--confidence-threshold", type=float, default=0.8)
    args = parser.parse_args()

    run_evaluation(
        dataset_path=args.dataset_path,
        output_dir=args.output_dir,
        seed=args.seed,
        stratified_per_source=args.stratified_per_source,
        performance_size=args.performance_size,
        confidence_threshold=args.confidence_threshold,
    )


def run_evaluation(
    dataset_path: Path,
    output_dir: Path,
    seed: int = 42,
    stratified_per_source: int = 500,
    performance_size: int = 10000,
    confidence_threshold: float = 0.8,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)

    samples_by_source = load_samples_by_source(dataset_path)
    smoke_samples = build_smoke_samples(samples_by_source)
    stratified_samples = build_stratified_samples(
        samples_by_source=samples_by_source,
        sample_size_per_source=stratified_per_source,
        seed=seed,
    )
    performance_samples = build_performance_samples(
        samples_by_source=samples_by_source,
        sample_size=performance_size,
        seed=seed,
    )

    write_jsonl(output_dir / "smoke_sample.jsonl", smoke_samples)
    write_jsonl(output_dir / "stratified_sample.jsonl", stratified_samples)
    write_jsonl(output_dir / "performance_sample.jsonl", performance_samples)

    start = time.perf_counter()
    parsed_smoke = parse_samples(smoke_samples, confidence_threshold)
    parsed_stratified = parse_samples(stratified_samples, confidence_threshold)
    parsed_performance = parse_samples(performance_samples, confidence_threshold)
    runtime_seconds = time.perf_counter() - start

    all_parsed = parsed_smoke + parsed_stratified + parsed_performance
    write_parsed_outputs(output_dir, all_parsed)
    summary = build_summary(
        parsed_smoke=parsed_smoke,
        parsed_stratified=parsed_stratified,
        parsed_performance=parsed_performance,
        runtime_seconds=runtime_seconds,
        confidence_threshold=confidence_threshold,
    )
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    return summary


def load_samples_by_source(dataset_path: Path) -> dict[str, list[IngredientLineSample]]:
    samples_by_source: dict[str, list[IngredientLineSample]] = {}
    for source, filename in DATASET_FILES.items():
        file_path = dataset_path / filename
        data = json.loads(file_path.read_text(encoding="utf-8"))
        samples: list[IngredientLineSample] = []
        for recipe_id, recipe in data.items():
            if not isinstance(recipe, dict):
                continue
            title = _clean_optional_text(recipe.get("title"))
            ingredients = recipe.get("ingredients")
            if not isinstance(ingredients, list):
                continue
            for position, raw_line in enumerate(ingredients):
                cleaned_line = str(raw_line or "").strip()
                if not cleaned_line:
                    continue
                samples.append(
                    IngredientLineSample(
                        source=source,
                        source_file=filename,
                        recipe_id=recipe_id,
                        title=title,
                        line_position=position,
                        raw_line=cleaned_line,
                    )
                )
        samples_by_source[source] = samples
    return samples_by_source


def build_smoke_samples(
    samples_by_source: dict[str, list[IngredientLineSample]],
) -> list[IngredientLineSample]:
    lookup = {
        sample.raw_line.lower(): sample
        for samples in samples_by_source.values()
        for sample in samples
    }
    smoke_samples = []
    for index, raw_line in enumerate(HAND_PICKED_LINES):
        sample = lookup.get(raw_line.lower())
        smoke_samples.append(
            sample
            or IngredientLineSample(
                source="hand_picked",
                source_file="hand_picked",
                recipe_id=f"hand-picked-{index}",
                title=None,
                line_position=index,
                raw_line=raw_line,
            )
        )
    return smoke_samples


def build_stratified_samples(
    samples_by_source: dict[str, list[IngredientLineSample]],
    sample_size_per_source: int,
    seed: int,
) -> list[IngredientLineSample]:
    rng = random.Random(seed)
    selected: list[IngredientLineSample] = []
    for source in sorted(samples_by_source):
        source_samples = samples_by_source[source]
        selected.extend(rng.sample(source_samples, min(sample_size_per_source, len(source_samples))))
    return selected


def build_performance_samples(
    samples_by_source: dict[str, list[IngredientLineSample]],
    sample_size: int,
    seed: int,
) -> list[IngredientLineSample]:
    rng = random.Random(seed)
    all_samples = [
        sample
        for source_samples in samples_by_source.values()
        for sample in source_samples
    ]
    return rng.sample(all_samples, min(sample_size, len(all_samples)))


def parse_samples(
    samples: Iterable[IngredientLineSample],
    confidence_threshold: float,
) -> list[ParsedSample]:
    return [
        ParsedSample(
            sample=sample,
            parsed=parse_ingredient_line(
                sample.raw_line,
                confidence_threshold=confidence_threshold,
            ),
        )
        for sample in samples
    ]


def write_jsonl(path: Path, samples: Iterable[IngredientLineSample]) -> None:
    with path.open("w", encoding="utf-8") as file:
        for sample in samples:
            file.write(json.dumps(asdict(sample), ensure_ascii=False) + "\n")


def write_parsed_outputs(output_dir: Path, parsed_samples: list[ParsedSample]) -> None:
    rows = [parsed_sample_to_row(item) for item in parsed_samples]
    write_csv(output_dir / "parsed_sample.csv", rows)
    write_csv(
        output_dir / "low_confidence.csv",
        [row for row in rows if row["needs_review"] == "true"],
    )
    write_csv(
        output_dir / "parse_errors.csv",
        [row for row in rows if row["error"]],
    )
    write_csv(
        output_dir / "multi_name_lines.csv",
        [row for row in rows if int(row["name_count"]) > 1],
    )
    with (output_dir / "parsed_sample.jsonl").open("w", encoding="utf-8") as file:
        for parsed_sample in parsed_samples:
            payload = {
                "sample": asdict(parsed_sample.sample),
                "parsed": parsed_sample.parsed.to_dict(),
            }
            file.write(json.dumps(payload, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "source",
        "source_file",
        "recipe_id",
        "title",
        "line_position",
        "raw_line",
        "names",
        "name_count",
        "amounts",
        "preparation",
        "comment",
        "purpose",
        "min_confidence",
        "needs_review",
        "error",
    ]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parsed_sample_to_row(parsed_sample: ParsedSample) -> dict[str, str]:
    sample = parsed_sample.sample
    parsed = parsed_sample.parsed
    return {
        "source": sample.source,
        "source_file": sample.source_file,
        "recipe_id": sample.recipe_id or "",
        "title": sample.title or "",
        "line_position": "" if sample.line_position is None else str(sample.line_position),
        "raw_line": sample.raw_line,
        "names": "; ".join(name.text for name in parsed.names),
        "name_count": str(len(parsed.names)),
        "amounts": "; ".join(
            amount.text or amount.quantity or ""
            for amount in parsed.amounts
            if amount.text or amount.quantity
        ),
        "preparation": parsed.preparation or "",
        "comment": parsed.comment or "",
        "purpose": parsed.purpose or "",
        "min_confidence": "" if parsed.min_confidence is None else f"{parsed.min_confidence:.6f}",
        "needs_review": str(parsed.needs_review).lower(),
        "error": parsed.error or "",
    }


def build_summary(
    parsed_smoke: list[ParsedSample],
    parsed_stratified: list[ParsedSample],
    parsed_performance: list[ParsedSample],
    runtime_seconds: float,
    confidence_threshold: float,
) -> dict[str, object]:
    all_parsed = parsed_smoke + parsed_stratified + parsed_performance
    source_counts = Counter(item.sample.source for item in all_parsed)
    success_count = sum(1 for item in all_parsed if item.parsed.names and not item.parsed.error)
    error_count = sum(1 for item in all_parsed if item.parsed.error)
    missing_name_count = sum(1 for item in all_parsed if not item.parsed.names)
    low_confidence_count = sum(1 for item in all_parsed if item.parsed.needs_review)
    confidence_values = [
        item.parsed.min_confidence
        for item in all_parsed
        if item.parsed.min_confidence is not None
    ]
    return {
        "sample_counts": {
            "smoke": len(parsed_smoke),
            "stratified": len(parsed_stratified),
            "performance": len(parsed_performance),
            "total_parsed_rows": len(all_parsed),
        },
        "source_counts": dict(source_counts),
        "parse_success_count": success_count,
        "parse_error_count": error_count,
        "missing_name_count": missing_name_count,
        "low_confidence_or_review_count": low_confidence_count,
        "usable_name_rate": round(success_count / len(all_parsed), 4) if all_parsed else 0,
        "average_min_confidence": (
            round(sum(confidence_values) / len(confidence_values), 6)
            if confidence_values
            else None
        ),
        "confidence_threshold": confidence_threshold,
        "runtime_seconds": round(runtime_seconds, 3),
    }


def _clean_optional_text(value: object) -> str | None:
    text = str(value or "").strip()
    return text or None


if __name__ == "__main__":
    main()
