from rest_framework.throttling import ScopedRateThrottle


class AuthRateThrottle(ScopedRateThrottle):
    """Limits register/login/refresh attempts per IP to slow down brute-force guessing."""

    scope = 'auth'


class ChatSendRateThrottle(ScopedRateThrottle):
    """Limits chat-send requests per user to bound LLM API cost/quota usage."""

    scope = 'chat-send'
