from pydantic import BaseModel, ValidationError
from datetime import datetime


def sanitize_csv(content: bytes) -> str:
    cleaned = content.replace(b'\x00', b'').lstrip(b'\xef\xbb\xbf')
    try:
        return cleaned.decode('utf-8')
    except UnicodeDecodeError:
        raise ValueError("Invalid UTF-8 encoding")


class InputSchema(BaseModel):
    device_id: str
    timestamp: datetime
    value: float

    @validator('device_id')
    def validate_id(cls, v):
        if not v.startswith('DEV-'):
            raise ValueError("Invalid device ID format")
        return v


def transform_row(row: dict) -> dict:
    validated = InputSchema(
        device_id=row['id'],
        timestamp=f"{row['date']}T{row['time']}Z",
        value=float(row['value'])
    )
    return validated.dict()
