/* ==================================================
   FLEETMAINTAIN - DASHBOARD
   ================================================== */

document.addEventListener("DOMContentLoaded", () => {

    /* ==============================================
       CSS VARIABLES
       ============================================== */

    const rootStyles = getComputedStyle(document.documentElement);

    const colorSuccess = rootStyles
        .getPropertyValue("--color-success")
        .trim();

    const colorService = rootStyles
        .getPropertyValue("--color-service")
        .trim();

    const colorDanger = rootStyles
        .getPropertyValue("--color-danger")
        .trim();

    const blue900 = rootStyles
        .getPropertyValue("--blue-900")
        .trim();  

    const blue950 = rootStyles
        .getPropertyValue("--blue-950")
        .trim();

    const blue500 = rootStyles
        .getPropertyValue("--blue-500")
        .trim();

    const blue200 = rootStyles
        .getPropertyValue("--blue-200")
        .trim();        

    /* ==============================================
       STATUS VOZILA I STROJEVA
       ============================================== */

    const vehicleStatusCanvas = document.getElementById(
        "vehicleStatusChart"
    );

    if (vehicleStatusCanvas) {

        // ==================================================
        // VEHICLE STATUS CHART
        // ==================================================

        const vehicleStatusCanvas = document.getElementById(
            "vehicleStatusChart"
        );

        const vehicleStatusDataElement = document.getElementById(
            "vehicle-status-values"
        );


        if (
            vehicleStatusCanvas &&
            vehicleStatusDataElement &&
            typeof Chart !== "undefined"
        ) {

            const vehicleStatusValues = JSON.parse(
                vehicleStatusDataElement.textContent
            );


            new Chart(
                vehicleStatusCanvas,
                {
                    type: "doughnut",

                    data: {

                        labels: [
                            "Ispravna",
                            "U servisu",
                            "Neispravna",
                        ],

                        datasets: [
                            {
                                data: vehicleStatusValues,

                                backgroundColor: [
                                    "#02A702",
                                    "#CAD400",
                                    "#AE3D00",
                                ],

                                borderWidth: 0,

                                hoverOffset: 4,
                            },
                        ],
                    },


                    options: {

                        responsive: true,

                        maintainAspectRatio: false,

                        cutout: "52%",

                        plugins: {

                            legend: {
                                display: false,
                            },

                            tooltip: {

                                callbacks: {

                                    label: (context) => {

                                        const value =
                                            context.parsed ?? 0;

                                        return `${context.label}: ${value}`;
                                    },
                                },
                            },
                        },
                    },
                }
            );
        }

    }


    /* ==============================================
       TROŠKOVI ODRŽAVANJA
       ============================================== */

    const maintenanceCostsCanvas = document.getElementById(
        "maintenanceCostsChart"
    );

    if (maintenanceCostsCanvas) {

        // ==================================================
        // DASHBOARD COSTS CHART
        // ==================================================

        const maintenanceCostsCanvas = document.getElementById(
            "maintenanceCostsChart"
        );

        const costLabelsElement = document.getElementById(
            "dashboard-cost-chart-labels"
        );

        const costValuesElement = document.getElementById(
            "dashboard-cost-chart-values"
        );


        if (
            maintenanceCostsCanvas &&
            costLabelsElement &&
            costValuesElement &&
            typeof Chart !== "undefined"
        ) {

            const costLabels = JSON.parse(
                costLabelsElement.textContent
            );

            const costValues = JSON.parse(
                costValuesElement.textContent
            );


            const styles = getComputedStyle(
                document.documentElement
            );

            const blue900 = styles
                .getPropertyValue("--blue-900")
                .trim();

            const blue500 = styles
                .getPropertyValue("--blue-500")
                .trim();

            const blue200 = styles
                .getPropertyValue("--blue-200")
                .trim();


            new Chart(
                maintenanceCostsCanvas,
                {
                    type: "bar",

                    data: {
                        labels: costLabels,

                        datasets: [
                            {
                                data: costValues,

                                backgroundColor: blue900,

                                hoverBackgroundColor: blue500,

                                borderWidth: 0,

                                borderRadius: 4,

                                borderSkipped: false,

                                maxBarThickness: 46,
                            },
                        ],
                    },


                    options: {

                        responsive: true,

                        maintainAspectRatio: false,


                        interaction: {
                            mode: "index",
                            intersect: false,
                        },


                        plugins: {

                            legend: {
                                display: false,
                            },


                            tooltip: {

                                displayColors: false,

                                callbacks: {

                                    label: (context) => {

                                        const value =
                                            context.parsed.y ?? 0;

                                        return (
                                            value.toLocaleString(
                                                "hr-HR",
                                                {
                                                    minimumFractionDigits: 2,
                                                    maximumFractionDigits: 2,
                                                }
                                            )
                                            + " €"
                                        );
                                    },
                                },
                            },
                        },


                        scales: {

                            x: {

                                border: {
                                    display: false,
                                },

                                grid: {
                                    display: false,
                                },

                                ticks: {

                                    color: blue500,

                                    font: {
                                        family: "Montserrat",
                                        size: 11,
                                        weight: "500",
                                    },
                                },
                            },


                            y: {

                                beginAtZero: true,

                                border: {
                                    display: false,
                                },

                                grid: {
                                    color: blue200,
                                },

                                ticks: {

                                    color: blue500,

                                    padding: 10,

                                    font: {
                                        family: "Montserrat",
                                        size: 11,
                                        weight: "500",
                                    },

                                    callback: (value) => {

                                        return (
                                            value.toLocaleString(
                                                "hr-HR"
                                            )
                                            + " €"
                                        );
                                    },
                                },
                            },
                        },
                    },
                }
            );
        }

    }

});