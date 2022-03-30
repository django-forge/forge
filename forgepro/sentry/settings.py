SENTRY_DSN = environ.get("SENTRY_DSN", None)
SENTRY_RELEASE = environ.get("SENTRY_RELEASE", environ.get("HEROKU_SLUG_COMMIT", None))
SENTRY_ENVIRONMENT = environ.get("SENTRY_ENVIRONMENT", "production")
SENTRY_PII_ENABLED = environ.get("SENTRY_PII_ENABLED", "true").lower() in ("true", "1")
SENTRY_JS_ENABLED = environ.get("SENTRY_JS_ENABLED", "true").lower() in ("true", "1")

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        SENTRY_DSN,
        release=SENTRY_RELEASE,
        environment=SENTRY_ENVIRONMENT,
        send_default_pii=SENTRY_PII_ENABLED,
        integrations=[DjangoIntegration()],
    )
