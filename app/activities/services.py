from .models import Activity


from .models import Activity


def log_activity(
    *,
    user,
    activity_type,
    title,
    vehicle=None,
    description="",
    level=Activity.Level.INFO,
):

    return Activity.objects.create(
        user=user,
        vehicle=vehicle,
        activity_type=activity_type,
        title=title,
        description=description,
        level=level,
    )