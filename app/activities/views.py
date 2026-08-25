from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from .models import Activity
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST


# ==================================================
# HELPERS
# ==================================================

def activity_return_url(request):

    next_url = request.POST.get(
        "next",
        "",
    )

    if (
        next_url
        and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={
                request.get_host(),
            },
            require_https=request.is_secure(),
        )
    ):
        return next_url

    return reverse(
        "activities:list"
    )

# ==================================================
# ACTIVITY LIST
# ==================================================

@login_required
def activity_list_view(request):

    # ==============================================
    # BASE QUERYSET
    # ==============================================

    base_activities = (
        Activity.objects
        .filter(
            user=request.user,
        )
        .select_related(
            "vehicle",
        )
    )


    # ==============================================
    # KPI STATISTICS
    # ==============================================

    today = timezone.localdate()


    total_activities = (
        base_activities
        .count()
    )


    today_activities = (
        base_activities
        .filter(
            created_at__date=today,
        )
        .count()
    )


    warning_activities = (
        base_activities
        .filter(
            level=Activity.Level.WARNING,
        )
        .count()
    )


    unread_activities = (
        base_activities
        .filter(
            is_read=False,
        )
        .count()
    )


    # ==============================================
    # FILTERED QUERYSET
    # ==============================================

    activities = base_activities


    # ==============================================
    # SEARCH
    # ==============================================

    search_query = request.GET.get(
        "search",
        "",
    ).strip()


    if search_query:

        activities = activities.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(vehicle__name__icontains=search_query)
        )


    # ==============================================
    # PERIOD FILTER
    # ==============================================

    period_filter = request.GET.get(
        "period",
        "",
    )


    if period_filter == "today":

        activities = activities.filter(
            created_at__date=today,
        )

    elif period_filter == "7days":

        period_start = (
            today
            - timedelta(days=6)
        )

        activities = activities.filter(
            created_at__date__gte=period_start,
        )

    elif period_filter == "30days":

        period_start = (
            today
            - timedelta(days=29)
        )

        activities = activities.filter(
            created_at__date__gte=period_start,
        )


    # ==============================================
    # ACTIVITY TYPE FILTER
    # ==============================================

    type_filter = request.GET.get(
        "type",
        "",
    )


    if type_filter:

        activities = activities.filter(
            activity_type=type_filter,
        )


    # ==============================================
    # ORDERING
    # ==============================================

    activities = activities.order_by(
        "-created_at",
    )


    # ==============================================
    # PAGINATION
    # ==============================================

    paginator = Paginator(
        activities,
        8,
    )


    page_obj = paginator.get_page(
        request.GET.get("page")
    )


    # ==============================================
    # GROUP ACTIVITIES BY DATE
    # ==============================================

    grouped_activities = []


    for activity in page_obj:

        activity_date = timezone.localtime(
            activity.created_at
        ).date()


        if activity_date == today:

            group_label = "Danas"

        elif activity_date == today - timedelta(days=1):

            group_label = "Jučer"

        else:

            group_label = activity_date.strftime(
                "%d.%m.%Y."
            )


        if (
            not grouped_activities
            or grouped_activities[-1]["label"] != group_label
        ):

            grouped_activities.append(
                {
                    "label": group_label,
                    "activities": [],
                }
            )


        grouped_activities[-1]["activities"].append(
            activity
        )


    # ==============================================
    # CONTEXT
    # ==============================================

    context = {
        # KPI
        "total_activities": total_activities,
        "today_activities": today_activities,
        "warning_activities": warning_activities,
        "unread_activities": unread_activities,

        # FILTERS
        "search_query": search_query,
        "period_filter": period_filter,
        "type_filter": type_filter,

        "activity_type_choices": (
            Activity.ActivityType.choices
        ),

        # LIST
        "grouped_activities": grouped_activities,
        "page_obj": page_obj,
        "total_filtered": paginator.count,
    }


    return render(
        request,
        "activities/activity_list.html",
        context,
    )

# ==================================================
# MARK ACTIVITY AS READ
# ==================================================

@login_required
@require_POST
def activity_mark_read_view(
    request,
    pk,
):

    activity = get_object_or_404(
        Activity,
        pk=pk,
        user=request.user,
    )

    if not activity.is_read:

        activity.is_read = True

        activity.save(
            update_fields=[
                "is_read",
            ]
        )

    return redirect(
        activity_return_url(
            request
        )
    )

# ==================================================
# MARK ALL ACTIVITIES AS READ
# ==================================================

@login_required
@require_POST
def activity_mark_all_read_view(request):

    (
        Activity.objects
        .filter(
            user=request.user,
            is_read=False,
        )
        .update(
            is_read=True,
        )
    )

    return redirect(
        activity_return_url(
            request
        )
    )