from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import DateField, Sum
from django.db.models.functions import Coalesce, TruncDate, TruncMonth
from django.shortcuts import render
from django.utils import timezone

from maintenance.models import Maintenance
from registrations.models import RegistrationInspection
from vehicles.models import Vehicle


# ==================================================
# DATE HELPERS
# ==================================================

def subtract_months(value, months):

    month_index = (
        value.year * 12
        + value.month
        - 1
        - months
    )

    year, month = divmod(
        month_index,
        12,
    )

    month += 1

    day = min(
        value.day,
        monthrange(year, month)[1],
    )

    return date(
        year,
        month,
        day,
    )


# ==================================================
# REPORTS
# ==================================================

@login_required
def report_list_view(request):

    today = timezone.localdate()


    # ==================================================
    # FILTER VALUES
    # ==================================================

    selected_period = request.GET.get(
        "period",
        "12_months",
    )

    selected_vehicle = request.GET.get(
        "vehicle",
        "",
    )


    # ==================================================
    # USER VEHICLES
    # ==================================================

    vehicles = Vehicle.objects.filter(
        user=request.user,
    ).order_by(
        "name",
    )


    # ==================================================
    # BASE QUERYSETS
    # ==================================================

    maintenances = (
        Maintenance.objects
        .filter(
            vehicle__user=request.user,
        )
        .annotate(
            report_date=Coalesce(
                "completed_date",
                "scheduled_date",
                TruncDate("created_at"),
                output_field=DateField(),
            )
        )
    )


    registration_inspections = (
        RegistrationInspection.objects
        .filter(
            vehicle__user=request.user,
        )
    )


    # ==================================================
    # VEHICLE FILTER
    # ==================================================

    if (
        selected_vehicle
        and vehicles.filter(
            pk=selected_vehicle
        ).exists()
    ):

        maintenances = maintenances.filter(
            vehicle_id=selected_vehicle,
        )

        registration_inspections = (
            registration_inspections.filter(
                vehicle_id=selected_vehicle,
            )
        )

        filtered_vehicle_count = 1

    else:

        selected_vehicle = ""

        filtered_vehicle_count = (
            vehicles.count()
        )


    # ==================================================
    # PERIOD FILTER
    # ==================================================

    start_date = None

    period_months = 1


    if selected_period == "30_days":

        start_date = (
            today
            - timedelta(days=29)
        )

        period_months = 1


    elif selected_period == "3_months":

        start_date = subtract_months(
            today,
            3,
        )

        period_months = 3


    elif selected_period == "6_months":

        start_date = subtract_months(
            today,
            6,
        )

        period_months = 6


    elif selected_period == "12_months":

        start_date = subtract_months(
            today,
            12,
        )

        period_months = 12


    elif selected_period == "year":

        start_date = date(
            today.year,
            1,
            1,
        )

        period_months = today.month


    elif selected_period == "all":

        start_date = None


    else:

        selected_period = "12_months"

        start_date = subtract_months(
            today,
            12,
        )

        period_months = 12


    # ==================================================
    # LIMIT TO REPORT PERIOD
    # ==================================================

    maintenances = maintenances.filter(
        report_date__lte=today,
    )

    registration_inspections = (
        registration_inspections.filter(
            date__lte=today,
        )
    )


    if start_date:

        maintenances = maintenances.filter(
            report_date__gte=start_date,
        )

        registration_inspections = (
            registration_inspections.filter(
                date__gte=start_date,
            )
        )


    # ==================================================
    # ALL-TIME PERIOD MONTH COUNT
    # ==================================================

    if selected_period == "all":

        first_maintenance_date = (
            maintenances
            .order_by("report_date")
            .values_list(
                "report_date",
                flat=True,
            )
            .first()
        )

        first_registration_date = (
            registration_inspections
            .order_by("date")
            .values_list(
                "date",
                flat=True,
            )
            .first()
        )


        available_dates = [
            value
            for value in [
                first_maintenance_date,
                first_registration_date,
            ]
            if value
        ]


        if available_dates:

            earliest_date = min(
                available_dates
            )

            period_months = (
                (
                    today.year
                    - earliest_date.year
                )
                * 12
                + today.month
                - earliest_date.month
                + 1
            )

        else:

            period_months = 1


    # ==================================================
    # COST TOTALS
    # ==================================================

    maintenance_cost = (
        maintenances.aggregate(
            total=Sum("cost")
        )["total"]
        or Decimal("0.00")
    )


    registration_cost = (
        registration_inspections.aggregate(
            total=Sum("cost")
        )["total"]
        or Decimal("0.00")
    )


    total_cost = (
        maintenance_cost
        + registration_cost
    )

    # ==================================================
    # COST DISTRIBUTION
    # ==================================================

    registration_only = (
        registration_inspections.filter(
            record_type=(
                RegistrationInspection
                .RecordType
                .REGISTRATION
            )
        )
    )


    technical_only = (
        registration_inspections.filter(
            record_type=(
                RegistrationInspection
                .RecordType
                .TECHNICAL_INSPECTION
            )
        )
    )


    registration_only_cost = (
        registration_only.aggregate(
            total=Sum("cost")
        )["total"]
        or Decimal("0.00")
    )


    technical_inspection_cost = (
        technical_only.aggregate(
            total=Sum("cost")
        )["total"]
        or Decimal("0.00")
    )      

    # ==================================================
    # COSTS THROUGH TIME
    # ==================================================

    chart_labels = []
    chart_cost_data = []

    # ==================================================
    # COSTS BY VEHICLE
    # ==================================================

    maintenance_vehicle_costs = (
        maintenances
        .values(
            "vehicle_id",
            "vehicle__name",
        )
        .annotate(
            total=Sum("cost")
        )
    )


    registration_vehicle_costs = (
        registration_inspections
        .values(
            "vehicle_id",
            "vehicle__name",
        )
        .annotate(
            total=Sum("cost")
        )
    )


    vehicle_cost_map = {}


    # Maintenance costs

    for item in maintenance_vehicle_costs:

        vehicle_id = item["vehicle_id"]

        vehicle_cost_map[vehicle_id] = {
            "name":
                item["vehicle__name"],

            "cost":
                item["total"]
                or Decimal("0.00"),
        }


    # Registration + technical costs

    for item in registration_vehicle_costs:

        vehicle_id = item["vehicle_id"]

        cost = (
            item["total"]
            or Decimal("0.00")
        )


        if vehicle_id in vehicle_cost_map:

            vehicle_cost_map[
                vehicle_id
            ]["cost"] += cost

        else:

            vehicle_cost_map[
                vehicle_id
            ] = {
                "name":
                    item["vehicle__name"],

                "cost":
                    cost,
            }


    # Najskuplje prvo

    vehicle_cost_items = sorted(
        vehicle_cost_map.values(),
        key=lambda item: item["cost"],
        reverse=True,
    )


    vehicle_cost_labels = [
        item["name"]
        for item in vehicle_cost_items
    ]


    vehicle_cost_data = [
        float(item["cost"])
        for item in vehicle_cost_items
    ]


    # ==================================================
    # LAST 30 DAYS - GROUP BY DAY
    # ==================================================

    if selected_period == "30_days":

        maintenance_daily = (
            maintenances
            .values("report_date")
            .annotate(
                total=Sum("cost")
            )
            .order_by("report_date")
        )        


        registration_daily = (
            registration_inspections
            .values("date")
            .annotate(
                total=Sum("cost")
            )
            .order_by("date")
        )


        maintenance_by_day = {
            item["report_date"]:
                item["total"]
                or Decimal("0.00")
            for item in maintenance_daily
            if item["report_date"]
        }


        registration_by_day = {
            item["date"]:
                item["total"]
                or Decimal("0.00")
            for item in registration_daily
            if item["date"]
        }


        current_date = (
            today
            - timedelta(days=29)
        )


        while current_date <= today:

            daily_total = (
                maintenance_by_day.get(
                    current_date,
                    Decimal("0.00"),
                )
                +
                registration_by_day.get(
                    current_date,
                    Decimal("0.00"),
                )
            )


            chart_labels.append(
                current_date.strftime(
                    "%d."
                )
            )


            chart_cost_data.append(
                float(daily_total)
            )


            current_date += timedelta(
                days=1
            )          


    # ==================================================
    # LONGER PERIODS - GROUP BY MONTH
    # ==================================================

    else:

        maintenance_monthly = (
            maintenances
            .annotate(
                month=TruncMonth(
                    "report_date"
                )
            )
            .values("month")
            .annotate(
                total=Sum("cost")
            )
            .order_by("month")
        )      

        registration_monthly = (
            registration_inspections
            .annotate(
                month=TruncMonth(
                    "date"
                )
            )
            .values("month")
            .annotate(
                total=Sum("cost")
            )
            .order_by("month")
        )


        maintenance_by_month = {
            (
                item["month"].year,
                item["month"].month,
            ):
                item["total"]
                or Decimal("0.00")
            for item in maintenance_monthly
            if item["month"]
        }


        registration_by_month = {
            (
                item["month"].year,
                item["month"].month,
            ):
                item["total"]
                or Decimal("0.00")
            for item in registration_monthly
            if item["month"]
        }


        # ==============================================
        # CHART START DATE
        # ==============================================

        chart_start_date = start_date


        if chart_start_date is None:

            available_chart_dates = []


            first_maintenance = (
                maintenances
                .order_by("report_date")
                .values_list(
                    "report_date",
                    flat=True,
                )
                .first()
            )


            first_registration = (
                registration_inspections
                .order_by("date")
                .values_list(
                    "date",
                    flat=True,
                )
                .first()
            )


            if first_maintenance:

                available_chart_dates.append(
                    first_maintenance
                )


            if first_registration:

                available_chart_dates.append(
                    first_registration
                )


            chart_start_date = (
                min(available_chart_dates)
                if available_chart_dates
                else today
            )


        # Početak prvog mjeseca

        current_month = date(
            chart_start_date.year,
            chart_start_date.month,
            1,
        )


        # Trenutni mjesec

        last_month = date(
            today.year,
            today.month,
            1,
        )


        month_names = [
            "",
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


        while current_month <= last_month:

            month_key = (
                current_month.year,
                current_month.month,
            )


            monthly_total = (
                maintenance_by_month.get(
                    month_key,
                    Decimal("0.00"),
                )
                +
                registration_by_month.get(
                    month_key,
                    Decimal("0.00"),
                )
            )


            chart_labels.append(
                (
                    f"{month_names[current_month.month]} "
                    f"{current_month.strftime('%y')}"
                )
            )


            chart_cost_data.append(
                float(monthly_total)
            )          


            # Sljedeći mjesec

            if current_month.month == 12:

                current_month = date(
                    current_month.year + 1,
                    1,
                    1,
                )

            else:

                current_month = date(
                    current_month.year,
                    current_month.month + 1,
                    1,
                )    

    # ==================================================
    # KPI
    # ==================================================

    total_maintenances = (
        maintenances.count()
    )


    average_monthly_cost = (
        total_cost
        / Decimal(period_months)
        if period_months
        else Decimal("0.00")
    )


    average_vehicle_cost = (
        total_cost
        / Decimal(filtered_vehicle_count)
        if filtered_vehicle_count
        else Decimal("0.00")
    )


    # ==================================================
    # CONTEXT
    # ==================================================

    context = {

        "vehicles": vehicles,

        "selected_period":
            selected_period,

        "selected_vehicle":
            selected_vehicle,

        "total_cost":
            total_cost,

        "total_maintenances":
            total_maintenances,

        "average_monthly_cost":
            average_monthly_cost,

        "average_vehicle_cost":
            average_vehicle_cost,

        "chart_labels":
            chart_labels,

        "chart_cost_data":
            chart_cost_data,

        "maintenance_cost":
            float(maintenance_cost),

        "registration_only_cost":
            float(registration_only_cost),

        "technical_inspection_cost":
            float(technical_inspection_cost),  

        "vehicle_cost_labels":
            vehicle_cost_labels,

        "vehicle_cost_data":
            vehicle_cost_data,              
    }


    return render(
        request,
        "reports/report_list.html",
        context,
    )