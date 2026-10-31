def is_manager(user):
    """Менеджер — член группы «Менеджеры»."""
    return (
        user.is_authenticated
        and user.groups.filter(name="Менеджеры").exists()
    )