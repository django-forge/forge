IMPERSONATE_ALLOWED = lambda user: user.is_superuser or user.is_staff
