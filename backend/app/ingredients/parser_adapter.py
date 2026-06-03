from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any, Callable


ParserFunction = Callable[[str], Any]


@dataclass(frozen=True)
class IngredientNameResult:
    text: str
    confidence: float | None
    starting_index: int | None


@dataclass(frozen=True)
class IngredientAmountResult:
    text: str | None
    quantity: str | None
    quantity_max: str | None
    unit: str | None
    confidence: float | None
    starting_index: int | None


@dataclass(frozen=True)
class ParsedIngredientLine:
    raw_line: str
    skipped: bool
    names: list[IngredientNameResult]
    amounts: list[IngredientAmountResult]
    preparation: str | None
    preparation_confidence: float | None
    comment: str | None
    purpose: str | None
    min_confidence: float | None
    needs_review: bool
    parser_output: dict[str, Any] | None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def parse_ingredient_line(
    raw_line: str,
    parser_fn: ParserFunction | None = None,
    confidence_threshold: float = 0.8,
) -> ParsedIngredientLine:
    cleaned_line = raw_line.strip()
    if not cleaned_line:
        return ParsedIngredientLine(
            raw_line=raw_line,
            skipped=True,
            names=[],
            amounts=[],
            preparation=None,
            preparation_confidence=None,
            comment=None,
            purpose=None,
            min_confidence=None,
            needs_review=True,
            parser_output=None,
            error=None,
        )

    if parser_fn is None:
        parser_fn = _load_default_parser()

    try:
        parsed = parser_fn(cleaned_line)
    except Exception as exc:  # pragma: no cover - exercised with injected parser in tests.
        return ParsedIngredientLine(
            raw_line=raw_line,
            skipped=False,
            names=[],
            amounts=[],
            preparation=None,
            preparation_confidence=None,
            comment=None,
            purpose=None,
            min_confidence=None,
            needs_review=True,
            parser_output=None,
            error=f"{type(exc).__name__}: {exc}",
        )

    names = [_name_result(item) for item in _as_list(getattr(parsed, "name", []))]
    amounts = [_amount_result(item) for item in _as_list(getattr(parsed, "amount", []))]
    preparation = getattr(parsed, "preparation", None)
    confidence_values = [
        item.confidence
        for item in names
        if item.confidence is not None
    ] + [
        item.confidence
        for item in amounts
        if item.confidence is not None
    ]

    preparation_confidence = _safe_float(getattr(preparation, "confidence", None))
    if preparation_confidence is not None:
        confidence_values.append(preparation_confidence)

    min_confidence = min(confidence_values) if confidence_values else None
    needs_review = not names or (
        min_confidence is not None and min_confidence < confidence_threshold
    )

    return ParsedIngredientLine(
        raw_line=raw_line,
        skipped=False,
        names=names,
        amounts=amounts,
        preparation=_safe_text(getattr(preparation, "text", None)),
        preparation_confidence=preparation_confidence,
        comment=_safe_text(getattr(getattr(parsed, "comment", None), "text", None)),
        purpose=_safe_text(getattr(getattr(parsed, "purpose", None), "text", None)),
        min_confidence=min_confidence,
        needs_review=needs_review,
        parser_output=_json_safe(parsed),
        error=None,
    )


def _load_default_parser() -> ParserFunction:
    try:
        from ingredient_parser import parse_ingredient
    except ImportError as exc:  # pragma: no cover - depends on optional dependency state.
        raise RuntimeError(
            "ingredient-parser-nlp is not installed. "
            "Install backend eval dependencies with `pip install -e .[eval]`."
        ) from exc
    return parse_ingredient


def _name_result(item: Any) -> IngredientNameResult:
    return IngredientNameResult(
        text=_safe_text(getattr(item, "text", None)) or "",
        confidence=_safe_float(getattr(item, "confidence", None)),
        starting_index=_safe_int(getattr(item, "starting_index", None)),
    )


def _amount_result(item: Any) -> IngredientAmountResult:
    return IngredientAmountResult(
        text=_safe_text(getattr(item, "text", None)),
        quantity=_quantity_to_text(getattr(item, "quantity", None)),
        quantity_max=_quantity_to_text(getattr(item, "quantity_max", None)),
        unit=_safe_text(getattr(item, "unit", None)),
        confidence=_safe_float(getattr(item, "confidence", None)),
        starting_index=_safe_int(getattr(item, "starting_index", None)),
    )


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _quantity_to_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, Fraction):
        return str(value)
    return str(value)


def _safe_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, list | tuple | set):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if hasattr(value, "__dict__"):
        return {
            key: _json_safe(item)
            for key, item in vars(value).items()
            if not key.startswith("_")
        }
    return str(value)
