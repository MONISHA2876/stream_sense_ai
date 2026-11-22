import asyncio
from collections import Counter

from app.chat.mock_generator import MockChatGenerator


async def main():
    generator = MockChatGenerator(
        duration_seconds=30,
        realtime=False
    )

    messages = []

    async for message in generator.generate():
        messages.append(message)

    print(f"Total messages generated: {len(messages)}")

    # Check platform
    assert all(m.platform == "mock" for m in messages)

    # Check message IDs are unique
    ids = [m.message_id for m in messages]
    assert len(ids) == len(set(ids))

    # Count messages per simulated second
    counts = Counter(
        int(m.stream_time) for m in messages
    )

    print("\nMessages per second:")
    for second in range(30):
        print(f"{second:02d}s: {counts[second]} messages")

    # Validate excitement spike
    spike_count = sum(
        counts[second] for second in range(10, 16)
    )
    assert 36 <= spike_count <= 60

    # Validate spam burst
    spam_messages = [
        m for m in messages if m.user_id == "spam_user"
    ]
    assert len(spam_messages) == 24

    # Validate quiet period
    quiet_count = sum(
        counts[second] for second in range(25, 28)
    )
    assert quiet_count == 0

    print("\nAll mock generator tests passed!")


if __name__ == "__main__":
    asyncio.run(main())