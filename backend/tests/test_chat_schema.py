from datetime import datetime, timezone

from pydantic import ValidationError

from app.chat.schemas import ChatMessage


# Test 1: Create a valid message
message = ChatMessage(
    message_id="msg_001",
    platform="youtube",
    user_id="user_123",
    username="Alice",
    text="OMG THAT WAS INSANE!"
)

print("Message created successfully:")
print(message)

print("\nMessage as JSON:")
print(message.model_dump_json(indent=2))


# Test 2: Check default timestamp
print("\nReceived at:", message.received_at)

assert message.received_at.tzinfo is not None


# Test 3: Reject an invalid platform
try:
    ChatMessage(
        platform="instagram",
        username="Alice",
        text="Hello!"
    )
except ValidationError as exc:
    print("\nInvalid platform rejected:")
    print(exc)


# Test 4: Reject an empty message
try:
    ChatMessage(
        platform="twitch",
        username="Alice",
        text="   "
    )
except ValidationError as exc:
    print("\nEmpty message rejected:")
    print(exc)


# Test 5: Verify stream timestamp
message_with_stream_time = ChatMessage(
    platform="mock",
    username="Bob",
    text="CLIP THAT!",
    stream_time=120.5
)

assert message_with_stream_time.stream_time == 120.5

print("\nAll schema tests passed!")