import sentry_sdk
from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token


@requires_csrf_token
def server_error(request, test_exception=None):
    if test_exception:
        sentry_sdk.capture_exception(test_exception)

    context = {
        "sentry_dialog_event_id": sentry_sdk.last_event_id(),
    }
    return render(request, "500.html", context, status=500)
