def user_role(request):
    if not request.user.is_authenticated:
        return {'is_admin': False, 'is_ustoz': False, 'is_bola': True}
    is_admin = request.user.is_superuser or request.user.is_staff
    is_ustoz = request.user.groups.filter(name='ustoz').exists()
    return {
        'is_admin': is_admin,
        'is_ustoz': is_ustoz,
        'is_bola': not is_admin and not is_ustoz,
    }
