def parse_fields(value: str | None) -> list[str] | None:
    if not value:
        return None
    fields = [field.strip() for field in value.split(",") if field.strip()]
    return fields or None
