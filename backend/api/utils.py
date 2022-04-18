def get_user_from_serializer_context(serializer):
    if 'request' in serializer.context:
        request = serializer.context['request']
        if hasattr(request, 'user'):
            return request.user

    return None
