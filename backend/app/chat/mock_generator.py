import asyncio
import random

from datetime import datetime, timedelta, timezone
from typing import AsyncIterator

from app.chat.schemas import ChatMessage


class MockChatGenerator:
    """Generate realistic mock livestream chat messages."""

    def __init__(
        self,
        duration_seconds: int = 30,
        realtime: bool = False,
        seed: int = 42
    ):
        self.duration_seconds = duration_seconds
        self.realtime = realtime

        # Reproducible random behaviour for testing
        self.rng = random.Random(seed)

        self.users = [
            ("user_1", "Alice"),
            ("user_2", "Bob"),
            ("user_3", "Charlie"),
            ("user_4", "David"),
            ("user_5", "Emma"),
            ("user_6", "Sophia"),
            ("user_7", "Ryan"),
        ]

        self.normal_messages = [
            "Hello everyone!",
            "Nice stream!",
            "How is everyone doing?",
            "Interesting!",
            "Watching from Delhi!",
            "Keep going!",
        ]

        self.excited_messages = [
            "OMG!!!",
            "THAT WAS INSANE 🔥",
            "LET'S GOOOO!",
            "NO WAYYYYY",
            "WHAT JUST HAPPENED 😂",
            "CLIP THAT!",
            "WOOOOOO!",
        ]

    async def generate(self) -> AsyncIterator[ChatMessage]:
        """Generate chat messages over a simulated stream timeline."""

        stream_start = datetime.now(timezone.utc)
        message_counter = 0

        for second in range(self.duration_seconds):

            # Decide how active the chat is during this second
            if 10 <= second < 16:
                # Excitement spike
                message_count = self.rng.randint(6, 10)

            elif 20 <= second < 23:
                # Spam burst
                message_count = 8

            elif 25 <= second < 28:
                # Quiet period
                message_count = 0

            else:
                # Normal chat
                message_count = self.rng.randint(1, 2)

            for _ in range(message_count):

                message_counter += 1

                # Generate a timestamp within this second
                offset = self.rng.random()
                stream_time = second + offset

                # Simulate a repeated spammer
                if 20 <= second < 23:
                    user_id = "spam_user"
                    username = "SpamBot"
                    message_text = "CLICK THE LINK NOW!!!"

                else:
                    user_id, username = self.rng.choice(self.users)

                    if 10 <= second < 16:
                        message_text = self.rng.choice(
                            self.excited_messages
                        )
                    else:
                        message_text = self.rng.choice(
                            self.normal_messages
                        )

                event_timestamp = stream_start + timedelta(
                    seconds=stream_time
                )

                message = ChatMessage(
                    message_id=f"mock_{message_counter:05d}",
                    platform="mock",
                    user_id=user_id,
                    username=username,
                    text=message_text,
                    event_timestamp=event_timestamp,
                    stream_time=stream_time
                )

                yield message

                # Optional real-time simulation
                if self.realtime:
                    await asyncio.sleep(1)
                else:
                    await asyncio.sleep(0)

            # Yield control to other async tasks
            if not self.realtime:
                await asyncio.sleep(0)
