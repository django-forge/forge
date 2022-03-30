from django.conf import settings
from django.urls import reverse_lazy


class StaffToolbarLink:
    def __init__(self, *, text, url):
        self.text = text

        if not url.startswith("/") and not url.startswith("http"):
            self.url = reverse_lazy(url)
        else:
            self.url = url


DEFAULT_LINKS = [
    StaffToolbarLink(text="Admin", url="admin:index"),
]


class StaffToolbar:
    def __init__(self, *, request):
        # Callable or list of StaffToolbarLink
        self.links = getattr(settings, "STAFFTOOLBAR_LINKS", DEFAULT_LINKS)

        if callable(self.links):
            self.links = self.links(request)
