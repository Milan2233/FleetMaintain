from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from maintenance.models import Maintenance
from registrations.models import RegistrationInspection
from vehicles.models import Vehicle


# ==============================================
# COSTS LIST
# ==============================================

@login_required
def cost_list_view(request):

    # ==========================================
    # BASE QUERYSETS
    # ==========================================

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


    # ==========================================
    # STATISTICS
    # ==========================================

    total_maintenance_cost = (
        maintenance_costs
        .aggregate(
            total=Sum("cost")
        )["total"]
        or Decimal("0.00")
    )

    total_registration_cost = (
        registration_costs
        .aggregate(
            total=Sum("cost")
        )["total"]
        or Decimal("0.00")
    )

    total_cost = (
        total_maintenance_cost
        + total_registration_cost
    )


    # ==========================================
    # CREATE UNIFIED COST LIST
    # ==========================================

    cost_items = []


    # MAINTENANCE

    for maintenance in maintenance_costs:

        cost_date = (
            maintenance.completed_date
            or maintenance.scheduled_date
            or maintenance.created_at.date()
        )

        cost_items.append(
            {
                "date": cost_date,

                "vehicle": maintenance.vehicle,

                "category": "Održavanje",
                "category_key": "maintenance",

                "description": maintenance.title,

                "secondary": (
                    maintenance.get_maintenance_type_display()
                ),

                "amount": maintenance.cost,

                "source_url": reverse(
                    "maintenance:detail",
                    args=[maintenance.pk],
                ),
            }
        )


    # REGISTRATION / TECHNICAL INSPECTION

    for registration in registration_costs:

        cost_items.append(
            {
                "date": registration.date,

                "vehicle": registration.vehicle,

                "category": (
                    registration.get_record_type_display()
                ),

                "category_key": "registration",

                "description": (
                    registration.get_record_type_display()
                ),

                "secondary": (
                    registration.provider
                    or "Registracija i tehnički pregled"
                ),

                "amount": registration.cost,

                "source_url": reverse(
                    "registrations:update",
                    args=[registration.pk],
                ),
            }
        )


    # ==========================================
    # THIS MONTH COST
    # ==========================================

    today = timezone.localdate()

    current_month_cost = sum(
        (
            item["amount"]
            for item in cost_items
            if (
                item["date"].year == today.year
                and item["date"].month == today.month
            )
        ),
        Decimal("0.00"),
    )

    # ==========================================
    # COST CHARTS
    # ==========================================

    month_names = [
        "Sij",
        "Velj",
        "Ožu",
        "Tra",
        "Svi",
        "Lip",
        "Srp",
        "Kol",
        "Ruj",
        "Lis",
        "Stu",
        "Pro",
    ]


    # ==========================================
    # LAST 12 MONTHS
    # ==========================================

    today = timezone.localdate()

    months = []

    year = today.year
    month = today.month

    for _ in range(12):

        months.append(
            (
                year,
                month,
            )
        )

        month -= 1

        if month == 0:
            month = 12
            year -= 1

    months.reverse()


    monthly_cost_labels = []
    monthly_cost_values = []


    for year, month in months:

        monthly_cost_labels.append(
            f"{month_names[month - 1]} {str(year)[2:]}"
        )

        month_total = sum(
            (
                item["amount"]
                for item in cost_items
                if (
                    item["date"].year == year
                    and item["date"].month == month
                )
            ),
            Decimal("0.00"),
        )

        monthly_cost_values.append(
            float(month_total)
        )

    # ==========================================
    # COST DISTRIBUTION
    # ==========================================

    cost_distribution = []


    # MAINTENANCE TYPES

    for value, label in Maintenance.MaintenanceType.choices:

        amount = (
            maintenance_costs
            .filter(
                maintenance_type=value,
            )
            .aggregate(
                total=Sum("cost")
            )["total"]
            or Decimal("0.00")
        )

        cost_distribution.append(
            {
                "label": label,
                "amount": amount,
                "type": "maintenance",
            }
        )


    # REGISTRATION

    registration_amount = (
        registration_costs
        .filter(
            record_type=(
                RegistrationInspection
                .RecordType
                .REGISTRATION
            )
        )
        .aggregate(
            total=Sum("cost")
        )["total"]
        or Decimal("0.00")
    )

    cost_distribution.append(
        {
            "label": "Registracija",
            "amount": registration_amount,
            "type": "registration",
        }
    )


    # TECHNICAL INSPECTION

    technical_amount = (
        registration_costs
        .filter(
            record_type=(
                RegistrationInspection
                .RecordType
                .TECHNICAL_INSPECTION
            )
        )
        .aggregate(
            total=Sum("cost")
        )["total"]
        or Decimal("0.00")
    )

    cost_distribution.append(
        {
            "label": "Tehnički pregled",
            "amount": technical_amount,
            "type": "technical",
        }
    )


    # ==========================================
    # SORT BY AMOUNT
    # ==========================================

    cost_distribution.sort(
        key=lambda item: item["amount"],
        reverse=True,
    )

    # ==========================================
    # FILTERS
    # ==========================================

    search_query = (
        request.GET.get("q", "")
        .strip()
        .lower()
    )

    selected_category = request.GET.get(
        "category",
        "",
    )

    selected_vehicle = request.GET.get(
        "vehicle",
        "",
    )


    # SEARCH

    if search_query:

        cost_items = [
            item
            for item in cost_items
            if (
                search_query
                in item["description"].lower()

                or search_query
                in item["secondary"].lower()

                or search_query
                in item["vehicle"].name.lower()

                or search_query
                in item["vehicle"].manufacturer.lower()

                or search_query
                in item["vehicle"].model.lower()

                or (
                    item["vehicle"].registration_number
                    and search_query
                    in item[
                        "vehicle"
                    ].registration_number.lower()
                )
            )
        ]


    # CATEGORY FILTER

    if selected_category in {
        "maintenance",
        "registration",
    }:

        cost_items = [
            item
            for item in cost_items
            if (
                item["category_key"]
                == selected_category
            )
        ]


    # VEHICLE FILTER

    if selected_vehicle:

        try:
            selected_vehicle_id = int(
                selected_vehicle
            )

            cost_items = [
                item
                for item in cost_items
                if (
                    item["vehicle"].pk
                    == selected_vehicle_id
                )
            ]

        except (TypeError, ValueError):
            selected_vehicle = ""


    # ==========================================
    # ORDERING
    # ==========================================

    cost_items.sort(
        key=lambda item: item["date"],
        reverse=True,
    )


    # ==========================================
    # PAGINATION
    # ==========================================

    paginator = Paginator(
        cost_items,
        8,
    )

    page_obj = paginator.get_page(
        request.GET.get("page")
    )


    # ==========================================
    # VEHICLES
    # ==========================================

    vehicles = (
        Vehicle.objects
        .filter(user=request.user)
        .order_by("name")
    )


    # ==========================================
    # CONTEXT
    # ==========================================

    context = {
        "page_obj": page_obj,
        "cost_items": page_obj,

        "vehicles": vehicles,

        "total_cost": total_cost,
        "total_maintenance_cost": (
            total_maintenance_cost
        ),
        "total_registration_cost": (
            total_registration_cost
        ),
        "current_month_cost": (
            current_month_cost
        ),

        "search_query": search_query,
        "selected_category": (
            selected_category
        ),
        "selected_vehicle": (
            selected_vehicle
        ),

        "monthly_cost_labels": monthly_cost_labels,
        "monthly_cost_values": monthly_cost_values,

        "cost_distribution": cost_distribution,
    }


    return render(
        request,
        "costs/cost_list.html",
        context,
    )