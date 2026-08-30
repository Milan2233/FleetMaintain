from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import timedelta
from django.utils import timezone

from maintenance.models import Maintenance
from vehicles.models import Vehicle
from django.core.paginator import Paginator
from django.db.models import Case, DateField, F, Q, When, Sum
from registrations.models import RegistrationInspection
from decimal import Decimal
from activities.models import Activity

@login_required
def dashboard_view(request):

    # ==============================================
    # USER VEHICLES
    # ==============================================

    vehicles = Vehicle.objects.filter(
        user=request.user
    )


    # ==============================================
    # VEHICLE STATISTICS
    # ==============================================

    total_vehicles = vehicles.count()


    # ==============================================
    # VEHICLE STATUS CHART
    # ==============================================

    operational_vehicles = vehicles.filter(
        status=Vehicle.Status.OPERATIONAL,
    ).count()

    vehicles_in_service = vehicles.filter(
        status=Vehicle.Status.IN_SERVICE,
    ).count()

    out_of_order_vehicles = vehicles.filter(
        status=Vehicle.Status.OUT_OF_ORDER,
    ).count()

    # ==============================================
    # MAINTENANCE STATISTICS
    # ==============================================

    today = timezone.localdate()

    upcoming_limit = (
        today
        + timedelta(days=30)
    )


    user_maintenances = Maintenance.objects.filter(
        vehicle__user=request.user
    )

    # Servisni rokovi koji su već prošli

    overdue_maintenances = (
        user_maintenances
        .filter(
            scheduled_date__lt=today,
        )
        .exclude(
            status__in=[
                Maintenance.Status.COMPLETED,
                Maintenance.Status.CANCELED,
            ]
        )
        .count()
    )

    # ==============================================
    # UPCOMING MAINTENANCE TABLE
    # ==============================================

    upcoming_maintenance_items = (
        user_maintenances
        .filter(
            Q(
                status=Maintenance.Status.PLANNED,
                scheduled_date__gte=today,
            )
            |
            Q(
                next_service_date__gte=today,
            )
        )
        .annotate(
            upcoming_date=Case(
                When(
                    status=Maintenance.Status.PLANNED,
                    scheduled_date__gte=today,
                    then=F("scheduled_date"),
                ),
                default=F("next_service_date"),
                output_field=DateField(),
            )
        )
        .select_related("vehicle")
        .order_by("upcoming_date")
        .distinct()
    )


    # Servisi čiji preporučeni sljedeći datum
    # dolazi unutar narednih 30 dana

    upcoming_maintenances = (
        upcoming_maintenance_items
        .filter(
            upcoming_date__lte=upcoming_limit,
        )
        .count()
    )


    upcoming_paginator = Paginator(
        upcoming_maintenance_items,
        3,
    )


    upcoming_page_obj = upcoming_paginator.get_page(
        request.GET.get("upcoming_page")
    )  

    # ==============================================
    # COSTS CHART
    # ==============================================

    maintenance_costs = (
        Maintenance.objects
        .filter(
            vehicle__user=request.user,
            cost__isnull=False,
        )
        .select_related("vehicle")
    )

    registration_costs = (
        RegistrationInspection.objects
        .filter(
            vehicle__user=request.user,
            cost__isnull=False,
        )
        .select_related("vehicle")
    )


    # ==============================================
    # UNIFIED COST ITEMS
    # ==============================================

    dashboard_cost_items = []


    for maintenance in maintenance_costs:

        cost_date = (
            maintenance.completed_date
            or maintenance.scheduled_date
            or maintenance.created_at.date()
        )

        dashboard_cost_items.append({
            "date": cost_date,
            "amount": maintenance.cost,
        })


    for registration in registration_costs:

        dashboard_cost_items.append({
            "date": registration.date,
            "amount": registration.cost,
        })


    # ==============================================
    # LAST 12 MONTHS
    # ==============================================

    month_names = [
        "Sij", "Velj", "Ožu", "Tra",
        "Svi", "Lip", "Srp", "Kol",
        "Ruj", "Lis", "Stu", "Pro",
    ]

    months = []

    year = today.year
    month = today.month


    for _ in range(12):

        months.append((year, month))

        month -= 1

        if month == 0:
            month = 12
            year -= 1


    months.reverse()


    cost_chart_labels = []
    cost_chart_values = []


    for year, month in months:

        cost_chart_labels.append(
            f"{month_names[month - 1]} {str(year)[2:]}"
        )

        month_total = sum(
            (
                item["amount"]
                for item in dashboard_cost_items
                if (
                    item["date"].year == year
                    and item["date"].month == month
                )
            ),
            Decimal("0.00"),
        )

        cost_chart_values.append(
            float(month_total)
        )      

    # ==================================================
    # RECENT ACTIVITIES
    # ==================================================

    recent_activities = (
        Activity.objects
        .filter(
            user=request.user,
        )
        .select_related(
            "vehicle",
        )
        .order_by(
            "-created_at",
        )[:5]
    )

    # ==============================================
    # CONTEXT
    # ==============================================

    context = {
        "total_vehicles": total_vehicles,
        "vehicles_in_service": vehicles_in_service,
        "upcoming_maintenances": upcoming_maintenances,
        "overdue_maintenances": overdue_maintenances,

        "upcoming_page_obj": upcoming_page_obj,

        "operational_vehicles": operational_vehicles,
        "vehicles_in_service": vehicles_in_service,
        "out_of_order_vehicles": out_of_order_vehicles,        

        "vehicle_status_values": [
            operational_vehicles,
            vehicles_in_service,
            out_of_order_vehicles,
        ],

        "cost_chart_labels": cost_chart_labels,
        "cost_chart_values": cost_chart_values,
        "recent_activities": recent_activities,
    }


    return render(
        request,
        "core/dashboard.html",
        context,
    )