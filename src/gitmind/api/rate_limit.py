from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

INDEX_LIMIT = "10/hour"
CHAT_LIMIT = "20/minute"