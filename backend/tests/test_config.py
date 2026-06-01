from app.core.config import Settings


def test_settings_have_safe_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.app_name == "KitchenCopilot API"
    assert settings.environment == "development"
    assert settings.api_cors_origins == ["http://localhost:3000"]
    assert "kitchen_copilot" in settings.database_url


def test_settings_parse_comma_separated_cors_origins() -> None:
    settings = Settings(
        _env_file=None,
        api_cors_origins="http://localhost:3000,http://localhost:3001",
    )

    assert settings.api_cors_origins == [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
