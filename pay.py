from datetime import datetime, timezone, timedelta
import jwt

secret = "dev-secret"
user_id = 81  # example
now = datetime.now(timezone.utc)
payload = {
    "sub": str(user_id),
    "iat": int(now.timestamp()),
    "exp": int((now + timedelta(days=120)).timestamp())  # expires in 120 days
}
token = jwt.encode(payload, secret, algorithm="HS256")
print(token)

decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded)