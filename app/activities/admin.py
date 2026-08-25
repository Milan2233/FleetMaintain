from django.contrib import admin

from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "activity_type",
        "user",
        "vehicle",
        "created_at",
    )

    list_filter = (
        "activity_type",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "user__email",
        "vehicle__name",
    )

    readonly_fields = (
        "user",
        "vehicle",
        "activity_type",
        "title",
        "description",
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"