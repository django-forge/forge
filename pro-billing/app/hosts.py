from django.conf import settings

from django_hosts import host, patterns

host_patterns = patterns(
    "",
    host(r"pypi", "pypi_urls", name="packages"),
    host(r".*", settings.ROOT_URLCONF, name="billing"),
)
