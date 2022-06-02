def user_id_from_request(request):
    # Analytics will be tied to the impersonator if we are one
    user = getattr(request, "impersonator", request.user)
    if user.is_authenticated:
        return user.pk
    return None
