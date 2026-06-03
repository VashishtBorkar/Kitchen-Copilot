from fractions import Fraction
from types import SimpleNamespace

from app.ingredients.parser_adapter import parse_ingredient_line


def test_parse_ingredient_line_returns_structured_output() -> None:
    def fake_parser(line: str) -> SimpleNamespace:
        return SimpleNamespace(
            name=[
                SimpleNamespace(text="butter", confidence=0.99, starting_index=2),
            ],
            amount=[
                SimpleNamespace(
                    text="2 tablespoons",
                    quantity=Fraction(2, 1),
                    quantity_max=Fraction(2, 1),
                    unit="tablespoon",
                    confidence=0.98,
                    starting_index=0,
                ),
            ],
            preparation=None,
            comment=None,
            purpose=None,
            sentence=line,
        )

    result = parse_ingredient_line("2 tablespoons butter", parser_fn=fake_parser)

    assert result.error is None
    assert result.skipped is False
    assert result.names[0].text == "butter"
    assert result.amounts[0].quantity == "2"
    assert result.amounts[0].unit == "tablespoon"
    assert result.needs_review is False
    assert result.parser_output is not None


def test_parse_ingredient_line_handles_parser_exceptions() -> None:
    def failing_parser(_: str) -> None:
        raise ValueError("bad line")

    result = parse_ingredient_line("bad ingredient", parser_fn=failing_parser)

    assert result.error == "ValueError: bad line"
    assert result.names == []
    assert result.needs_review is True


def test_parse_ingredient_line_serializes_fraction_and_confidence() -> None:
    def fake_parser(line: str) -> SimpleNamespace:
        return SimpleNamespace(
            name=[
                SimpleNamespace(text="onion", confidence=0.95, starting_index=1),
            ],
            amount=[
                SimpleNamespace(
                    text="1 1/2 cups",
                    quantity=Fraction(3, 2),
                    quantity_max=Fraction(3, 2),
                    unit="cup",
                    confidence=0.96,
                    starting_index=0,
                ),
            ],
            preparation=SimpleNamespace(
                text="finely diced",
                confidence=0.94,
                starting_index=3,
            ),
            comment=None,
            purpose=None,
            sentence=line,
        )

    result = parse_ingredient_line("1 1/2 cups onion, finely diced", parser_fn=fake_parser)
    payload = result.to_dict()

    assert payload["amounts"][0]["quantity"] == "3/2"
    assert payload["preparation"] == "finely diced"
    assert payload["min_confidence"] == 0.94


def test_parse_ingredient_line_skips_blank_lines() -> None:
    parser_called = False

    def fake_parser(_: str) -> None:
        nonlocal parser_called
        parser_called = True

    result = parse_ingredient_line("   ", parser_fn=fake_parser)

    assert parser_called is False
    assert result.skipped is True
    assert result.needs_review is True


def test_low_confidence_or_missing_name_needs_review() -> None:
    def fake_parser(_: str) -> SimpleNamespace:
        return SimpleNamespace(
            name=[
                SimpleNamespace(text="black pepper", confidence=0.42, starting_index=3),
            ],
            amount=[],
            preparation=None,
            comment=None,
            purpose=None,
        )

    result = parse_ingredient_line(
        "Kosher salt and fresh cracked black pepper",
        parser_fn=fake_parser,
        confidence_threshold=0.8,
    )

    assert result.names[0].text == "black pepper"
    assert result.needs_review is True
