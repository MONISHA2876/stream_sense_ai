from abc import ABC, abstractmethod
from typing import AsyncIterator

from app.chat.schemas import ChatMessage


class ChatListener(ABC):
    """Base interface for all livestream chat listeners."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection with the chat source."""
        pass

    @abstractmethod
    async def listen(self) -> AsyncIterator[ChatMessage]:
        """Yield incoming chat messages."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the connection and release resources."""
        pass