import redis
import random
import string
from datetime import timedelta

redis_client = redis.Redis(host="0.0.0.0", port=6379, db=0, decode_responses=True)


def generate_verification_code():
    """Generate 6 character verification code with mixed letters and numbers"""
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=6))


def store_verification_code(email: str, code: str):
    """Store verification code with 15 minute expiry"""
    redis_client.setex(f"verify:{email}", timedelta(minutes=15), code)
    redis_client.setex(f"ratelimit:{email}", timedelta(minutes=5), "1")


def can_send_new_code(email: str) -> bool:
    """Check if enough time has passed to send new code"""
    return not redis_client.exists(f"ratelimit:{email}")


def verify_code(email: str, code: str) -> bool:
    """Verify the code matches"""
    stored_code = redis_client.get(f"verify:{email}")
    if stored_code and stored_code == code:
        redis_client.delete(f"verify:{email}")
        return True
    return False
