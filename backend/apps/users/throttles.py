
from rest_framework.throttling import ScopedRateThrottle


class LoginRateThrottle(ScopedRateThrottle):
    scope = "login"


class RegistrationRateThrottle(ScopedRateThrottle):
    scope = "registration"


class PasswordResetRateThrottle(ScopedRateThrottle):
    scope = "password_reset"


class PasswordResetConfirmRateThrottle(ScopedRateThrottle):
    scope = "password_reset_confirm"



"DEFAULT_THROTTLE_CLASSES": [
    "rest_framework.throttling.AnonRateThrottle",
    "rest_framework.throttling.UserRateThrottle",
    "rest_framework.throttling.ScopedRateThrottle",
],

"DEFAULT_THROTTLE_RATES": {
    "anon": "100/hour",
    "user": "1000/hour",
    "login": "5/minute",
    "registration": "3/hour",
    "password_reset": "3/hour",
    "password_reset_confirm": "5/hour",
},

throttle_classes = [LoginRateThrottle]

@throttle_classes([LoginRateThrottle])