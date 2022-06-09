from .googleanalytics.default_settings import *
from .impersonate.default_settings import *
from .requestlog.default_settings import *
from .sentry.default_settings import *
from .stafftoolbar.default_settings import *
from .stripe.default_settings import *

FORGEPRO_APPS = [
    "forgepro.sentry",
    "forgepro.stripe",
    "forgepro.stafftoolbar",
    "forgepro.impersonate",
    "forgepro.googleanalytics",
    "forgepro.requestlog",
    "forgepro.querystats",
]

FORGEPRO_MIDDLEWARE = [
    "forgepro.querystats.QueryStatsMiddleware",
    "forgepro.sentry.SentryFeedbackMiddleware",
    "forgepro.impersonate.ImpersonateMiddleware",
    "forgepro.requestlog.RequestLogMiddleware",
]
