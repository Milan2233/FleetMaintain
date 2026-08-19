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

        new Chart(vehicleStatusCanvas, {

            type: "doughnut",

            data: {
                labels: [
                    "Ispravna",
                    "U servisu",
                    "Neispravna",
                ],

                datasets: [
                    {
                        data: [15, 3, 2],

                        backgroundColor: [
                            colorSuccess,
                            colorService,
                            colorDanger,
                        ],

                        borderWidth: 0,
                        hoverOffset: 2,
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
                        enabled: true,
                    },
                },

                animation: {
                    duration: 500,
                },
            },

        });

    }


    /* ==============================================
       TROŠKOVI ODRŽAVANJA
       ============================================== */

    const maintenanceCostsCanvas = document.getElementById(
        "maintenanceCostsChart"
    );

    if (maintenanceCostsCanvas) {

        new Chart(maintenanceCostsCanvas, {

            type: "bar",

            data: {
                labels: [
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
                ],

                datasets: [
                    {
                        label: "Trošak održavanja",

                        data: [
                            1200,
                            1800,
                            900,
                            2200,
                            1500,
                            1100,
                            1700,
                            1350,
                            1950,
                            1250,
                            2100,
                            1600,
                        ],

                        backgroundColor: blue900,


                        borderRadius: 4,
                        borderSkipped: false,

                        barPercentage: 0.55,
                        categoryPercentage: 0.7,
                    },
                ],
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: false,
                    },

                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                return `${context.raw} €`;
                            },
                        },
                    },
                },

                scales: {

                    x: {
                        grid: {
                            display: false,
                        },

                        border: {
                            color: blue200,
                        },

                        ticks: {
                            color: blue950,

                            font: {
                                family: "Montserrat",
                                size: 12,
                                weight: "500",
                            },
                        },
                    },

                    y: {
                        beginAtZero: true,

                        grid: {
                            color: blue200,
                        },

                        border: {
                            display: false,
                        },

                        ticks: {
                            color: blue500,

                            font: {
                                family: "Montserrat",
                                size: 10,
                                weight: "500",
                            },

                            callback: (value) => {
                                return `${value} €`;
                            },
                        },
                    },

                },
            },

        });

    }

});