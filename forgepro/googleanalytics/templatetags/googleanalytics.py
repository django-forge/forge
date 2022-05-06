from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag("googleanalytics/js.html", takes_context=True)
def googleanalytics_js(context):
    ctx = {
        "googleanalytics_measurement_id": settings.GOOGLEANALYTICS_MEASUREMENT_ID,
    }

    if "request" in context:
        request = context["request"]
        # Analytics will be tied to the impersonator if we are one
        user = getattr(request, "impersonator", request.user)
        if user.is_authenticated:
            ctx["googleanalytics_user_id"] = user.pk

    return ctx
