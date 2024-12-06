FORGEPRO_APPS = [
    "forgesentry",
    "forgestripe",
    "forgestafftoolbar",
    "forgeimpersonate",
    "forgegoogleanalytics",
    "forgerequestlog",
    "forgequerystats",
]

FORGEPRO_MIDDLEWARE = [
    "forgequerystats.QueryStatsMiddleware",
    "forgesentry.SentryFeedbackMiddleware",
    "forgeimpersonate.ImpersonateMiddleware",
    "forgerequestlog.RequestLogMiddleware",
]
