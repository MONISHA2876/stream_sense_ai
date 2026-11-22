import asyncio
from app.chat.adapters.mock_adapter import MockChatAdapter

async def main():

    adapter = MockChatAdapter(
        duration_seconds=30,
        realtime=False
    )

    # Test 1: Listener should reject listening before connection
    try:
        async for _ in adapter.listen():
            pass
        raise AssertionError("Expected RuntimeError before connect")

    except RuntimeError:
        print("Test 1 passed: Connection required.")

    # Test 2: Connect
    await adapter.connect()
    assert adapter.connected is True

    # Test 3: Receive messages
    messages = []

    try:
        async for message in adapter.listen():
            messages.append(message)
    finally:
        await adapter.disconnect()

    assert len(messages) > 0
    assert all(message.platform == "mock" for message in messages)

    # Test 4: Disconnect
    assert adapter.connected is False

    print(f"Received {len(messages)} messages.")
    print("First message:", messages[0].text)
    print("\nAll adapter tests passed!")


if __name__ == "__main__":
    asyncio.run(main())