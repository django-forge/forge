handler500 = views.server_error


# Make the error pages viewable in development
if settings.DEBUG:
    urlpatterns += [
        path(
            "400/",
            lambda request: django.views.defaults.bad_request(
                request, Exception("400 error")
            ),
        ),
        path(
            "403/",
            lambda request: django.views.defaults.permission_denied(
                request, Exception("403 error")
            ),
        ),
        path(
            "404/",
            lambda request: django.views.defaults.page_not_found(
                request, Exception("404 error")
            ),
        ),
        path(
            "500/", lambda request: views.server_error(request, Exception("500 error"))
        ),
    ]
