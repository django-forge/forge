from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag("sentry/js.html", takes_context=True)
def sentry_js(context):
    if not (settings.SENTRY_DSN and settings.SENTRY_JS_ENABLED):
        return {
            "sentry_js_enabled": False,
        }

    sentry_public_key = settings.SENTRY_DSN.split("//")[1].split("@")[0]

    sentry_context = {
        "sentry_js_enabled": True,
        "sentry_public_key": sentry_public_key,
        "sentry_dialog_event_id": context.get("sentry_dialog_event_id", None),
        "sentry_init": {
            "release": settings.SENTRY_RELEASE,
            "environment": settings.SENTRY_ENVIRONMENT,
            "sendDefaultPii": bool(settings.SENTRY_PII_ENABLED),
        },
    }

    request = context.get("request", None)

    if (
        settings.SENTRY_PII_ENABLED
        and hasattr(request, "user")
        and request.user.is_authenticated
    ):
        sentry_context["sentry_init"]["initialScope"] = {
            "user": {
                "id": request.user.id,
                "email": request.user.email,
                "username": request.user.get_username(),
            }
        }

    return sentry_context
