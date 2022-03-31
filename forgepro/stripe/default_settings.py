from os import environ

if "STRIPE_SECRET_KEY" in environ:
    import stripe  # NOQA

    stripe.api_key = environ["STRIPE_SECRET_KEY"]
    STRIPE_WEBHOOK_SECRET = environ["STRIPE_WEBHOOK_SECRET"]
