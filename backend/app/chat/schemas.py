from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatMessage(BaseModel):
    """Standardized message received from a livestream chat."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    message_id: str | None = None

    platform: Literal["youtube", "twitch", "mock"]

    user_id: str | None = None

    username: str = Field(
        min_length=1,
        max_length=100
    )

    text: str = Field(
        min_length=1,
        max_length=5000
    )

    event_timestamp: datetime | None = None

    received_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    stream_time: float | None = Field(
        default=None,
        ge=0
    )