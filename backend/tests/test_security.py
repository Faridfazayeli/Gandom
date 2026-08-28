from uuid import uuid4
from datetime import timedelta
from app.core.security import create_token, decode_token

def test_token_roundtrip():
    uid=uuid4(); t=create_token(uid,"general","access",timedelta(minutes=5)); p=decode_token(t)
    assert p["sub"]==str(uid); assert p["type"]=="access"
