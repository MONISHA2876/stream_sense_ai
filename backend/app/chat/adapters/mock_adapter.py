from typing import AsyncIterator

from app.chat.interfaces import ChatListener
from app.chat.schemas import ChatMessage
from app.chat.mock_generator import MockChatGenerator


class MockChatAdapter(ChatListener):
    """Adapter that exposes mock chat through ChatListener."""

    def __init__(
        self,
        duration_seconds: int = 30,
        realtime: bool = False,
        seed: int = 42
    ):
        self.generator = MockChatGenerator(
            duration_seconds=duration_seconds,
            realtime=realtime,
            seed=seed
        )

        self.connected = False

    async def connect(self) -> None:
        """Start the mock chat connection."""

        if self.connected:
            return

        self.connected = True
        print("Mock chat connected.")

    async def listen(self) -> AsyncIterator[ChatMessage]:
        """Yield messages from the mock generator."""

        if not self.connected:
            raise RuntimeError(
                "Chat adapter is not connected. Call connect() first."
            )

        async for message in self.generator.generate():

            if not self.connected:
                break

            yield message

    async def disconnect(self) -> None:
        """Stop the mock chat connection."""

        self.connected = False
        print("Mock chat disconnected.")