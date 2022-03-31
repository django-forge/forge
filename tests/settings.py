from forge.default_settings import *

from forgepro.default_settings import *

INSTALLED_APPS = INSTALLED_APPS + [
    "forgepro.sentry",
    "forgepro.stripe",
    "forgepro.stafftoolbar",
]

AUTH_USER_MODEL = "auth.User"
