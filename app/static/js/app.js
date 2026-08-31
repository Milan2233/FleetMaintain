document.addEventListener("DOMContentLoaded", () => {

    /* ==============================================
       PASSWORD VISIBILITY TOGGLE
       ============================================== */

    const passwordToggles = document.querySelectorAll(
        "[data-password-toggle]"
    );

    passwordToggles.forEach((toggle) => {

        toggle.addEventListener("click", () => {

            const inputWrapper = toggle.closest(
                ".input-wrapper, .settings-password-input"
            );

            if (!inputWrapper) {
                return;
            }

            const passwordInput = inputWrapper.querySelector(
                'input[type="password"], input[data-password-visible="true"]'
            );

            const icon = toggle.querySelector(
                ".password-toggle-icon"
            );

            if (!passwordInput) {
                return;
            }


            if (passwordInput.type === "password") {

                passwordInput.type = "text";

                passwordInput.dataset.passwordVisible = "true";

                toggle.setAttribute(
                    "aria-label",
                    "Sakrij lozinku"
                );

                if (icon) {
                    icon.classList.remove("icon-eye");
                    icon.classList.add("icon-eye-off");
                }

            } else {

                passwordInput.type = "password";

                delete passwordInput.dataset.passwordVisible;

                toggle.setAttribute(
                    "aria-label",
                    "Prikaži lozinku"
                );

                if (icon) {
                    icon.classList.remove("icon-eye-off");
                    icon.classList.add("icon-eye");
                }

            }

        });

    });




    /* ==============================================
    RESPONSIVE SIDEBAR
    ============================================== */

    const sidebarToggle = document.querySelector(
        "[data-sidebar-toggle]"
    );

    const sidebarClose = document.querySelector(
        "[data-sidebar-close]"
    );

    const sidebarLinks = document.querySelectorAll(
        ".sidebar a.sidebar-link"
    );


    function openSidebar() {

        document.body.classList.add("sidebar-open");

        if (sidebarToggle) {
            sidebarToggle.setAttribute(
                "aria-expanded",
                "true"
            );
        }

        document.body.style.overflow = "hidden";

    }


    function closeSidebar() {

        document.body.classList.remove("sidebar-open");

        if (sidebarToggle) {
            sidebarToggle.setAttribute(
                "aria-expanded",
                "false"
            );
        }

        document.body.style.overflow = "";

    }


    /* Otvori */

    if (sidebarToggle) {

        sidebarToggle.addEventListener(
            "click",
            openSidebar
        );

    }


    /* Zatvori preko X */

    if (sidebarClose) {

        sidebarClose.addEventListener(
            "click",
            closeSidebar
        );

    }


    /* Zatvori nakon klika na link */

    sidebarLinks.forEach((link) => {

        link.addEventListener(
            "click",
            closeSidebar
        );

    });


    /* Escape */

    document.addEventListener("keydown", (event) => {

        if (
            event.key === "Escape" &&
            document.body.classList.contains("sidebar-open")
        ) {
            closeSidebar();
        }

    });


    /* Ako korisnik proširi ekran nazad na desktop */

    window.addEventListener("resize", () => {

        if (window.innerWidth >= 1366) {
            closeSidebar();
        }

    }); 
    
/* ==================================================
   GLOBAL DELETE MODAL
   ================================================== */

const deleteModal = document.querySelector(
    "[data-delete-modal]"
);

const deleteOpenButtons = document.querySelectorAll(
    "[data-delete-open]"
);

if (deleteModal && deleteOpenButtons.length) {

    const deleteCloseButtons = deleteModal.querySelectorAll(
        "[data-delete-close]"
    );

    const deleteForm = deleteModal.querySelector(
        "[data-delete-form]"
    );

    const deleteName = deleteModal.querySelector(
        "[data-delete-name]"
    );

    let lastFocusedElement = null;


    /* ==============================================
       OPEN
       ============================================== */

    function openDeleteModal(button) {

        lastFocusedElement = button;


        /* Dynamic name */

        if (
            deleteName &&
            button.dataset.deleteName
        ) {
            deleteName.textContent =
                button.dataset.deleteName;
        }


        /* Dynamic delete URL */

        if (
            deleteForm &&
            button.dataset.deleteUrl
        ) {
            deleteForm.action =
                button.dataset.deleteUrl;
        }


        deleteModal.hidden = false;

        requestAnimationFrame(() => {

            deleteModal.classList.add(
                "is-open"
            );

            deleteModal.setAttribute(
                "aria-hidden",
                "false"
            );

        });


        document.body.style.overflow = "hidden";


        const cancelButton = deleteModal.querySelector(
            "[data-delete-close]:not(.delete-modal-backdrop)"
        );

        if (cancelButton) {
            cancelButton.focus();
        }

    }


    /* ==============================================
       CLOSE
       ============================================== */

    function closeDeleteModal() {

        deleteModal.classList.remove(
            "is-open"
        );

        deleteModal.setAttribute(
            "aria-hidden",
            "true"
        );

        document.body.style.overflow = "";


        setTimeout(() => {

            deleteModal.hidden = true;

        }, 250);


        if (lastFocusedElement) {
            lastFocusedElement.focus();
        }

    }


    /* ==============================================
       OPEN BUTTONS
       ============================================== */

    deleteOpenButtons.forEach((button) => {

        button.addEventListener(
            "click",
            () => openDeleteModal(button)
        );

    });


    /* ==============================================
       CLOSE BUTTONS
       ============================================== */

    deleteCloseButtons.forEach((button) => {

        button.addEventListener(
            "click",
            closeDeleteModal
        );

    });


    /* ==============================================
       ESCAPE
       ============================================== */

    document.addEventListener(
        "keydown",
        (event) => {

            if (
                event.key === "Escape" &&
                deleteModal.classList.contains("is-open")
            ) {
                closeDeleteModal();
            }

        }
    );

} 

/* ==================================================
   REPORTS CHARTS
   ================================================== */

const reportCostsCanvas = document.getElementById(
    "reportCostsChart"
);

const reportDistributionCanvas = document.getElementById(
    "reportDistributionChart"
);


/* ==================================================
   REPORTS CHART COLORS
   ================================================== */

const reportStyles = getComputedStyle(
    document.documentElement
);

const reportBlue950 = reportStyles
    .getPropertyValue("--blue-950")
    .trim();

const reportBlue900 = reportStyles
    .getPropertyValue("--blue-900")
    .trim();

const reportBlue500 = reportStyles
    .getPropertyValue("--blue-500")
    .trim();

const reportBlue300 = reportStyles
    .getPropertyValue("--blue-300")
    .trim();

const reportBlue200 = reportStyles
    .getPropertyValue("--blue-200")
    .trim();

const reportWhite = reportStyles
    .getPropertyValue("--color-white")
    .trim();


/* ==================================================
   CURRENCY FORMAT
   ================================================== */

const reportCurrencyFormatter = new Intl.NumberFormat(
    "hr-HR",
    {
        style: "currency",
        currency: "EUR",
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
    }
);


/* ==================================================
   COSTS THROUGH TIME
   ================================================== */

if (reportCostsCanvas) {

    const labelsElement = document.getElementById(
        "report-chart-labels"
    );

    const costsElement = document.getElementById(
        "report-chart-costs"
    );

    const reportLabels = labelsElement
        ? JSON.parse(labelsElement.textContent)
        : [];

    const reportCosts = costsElement
        ? JSON.parse(costsElement.textContent)
        : [];


    new Chart(
        reportCostsCanvas,
        {
            type: "bar",

            data: {
                labels: reportLabels,

                datasets: [
                    {
                        label: "Troškovi",
                        data: reportCosts,

                        backgroundColor: reportBlue900,
                        borderColor: reportBlue900,

                        borderWidth: 0,
                        borderRadius: 6,
                        borderSkipped: false,

                        maxBarThickness: 38,
                    },
                ],
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                interaction: {
                    intersect: false,
                    mode: "index",
                },

                plugins: {

                    legend: {
                        display: false,
                    },

                    tooltip: {
                        displayColors: false,

                        backgroundColor: reportBlue950,
                        titleColor: reportWhite,
                        bodyColor: reportWhite,

                        padding: 10,
                        cornerRadius: 6,

                        titleFont: {
                            family: "Montserrat",
                            size: 12,
                            weight: "600",
                        },

                        bodyFont: {
                            family: "Montserrat",
                            size: 12,
                            weight: "500",
                        },

                        callbacks: {

                            label(context) {
                                return reportCurrencyFormatter.format(
                                    context.raw || 0
                                );
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
                            display: false,
                        },

                        ticks: {
                            color: reportBlue500,

                            maxRotation: 0,
                            minRotation: 0,

                            autoSkip: true,

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
                            color: reportBlue200,
                            drawTicks: false,
                        },

                        ticks: {
                            padding: 10,

                            color: reportBlue500,

                            font: {
                                family: "Montserrat",
                                size: 11,
                                weight: "500",
                            },

                            callback(value) {
                                return (
                                    new Intl.NumberFormat(
                                        "hr-HR",
                                        {
                                            maximumFractionDigits: 0,
                                        }
                                    ).format(value)
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


/* ==================================================
   COST DISTRIBUTION
   ================================================== */

if (reportDistributionCanvas) {

    const maintenanceCostElement =
        document.getElementById(
            "report-maintenance-cost"
        );

    const registrationCostElement =
        document.getElementById(
            "report-registration-cost"
        );

    const technicalCostElement =
        document.getElementById(
            "report-technical-cost"
        );


    const maintenanceCost =
        maintenanceCostElement
            ? JSON.parse(
                maintenanceCostElement.textContent
            )
            : 0;

    const registrationCost =
        registrationCostElement
            ? JSON.parse(
                registrationCostElement.textContent
            )
            : 0;

    const technicalCost =
        technicalCostElement
            ? JSON.parse(
                technicalCostElement.textContent
            )
            : 0;


    new Chart(
        reportDistributionCanvas,
        {
            type: "doughnut",

            data: {
                labels: [
                    "Održavanje",
                    "Registracija",
                    "Tehnički pregled",
                ],

                datasets: [
                    {
                        data: [
                            maintenanceCost,
                            registrationCost,
                            technicalCost,
                        ],

                        backgroundColor: [
                            reportBlue900,
                            reportBlue500,
                            reportBlue300,
                        ],

                        borderWidth: 0,
                        hoverOffset: 5,
                    },
                ],
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                cutout: "55%",

                plugins: {

                    legend: {
                        display: false,
                    },

                    tooltip: {
                        displayColors: true,

                        backgroundColor: reportBlue950,
                        titleColor: reportWhite,
                        bodyColor: reportWhite,

                        padding: 10,
                        cornerRadius: 6,

                        titleFont: {
                            family: "Montserrat",
                            size: 12,
                            weight: "600",
                        },

                        bodyFont: {
                            family: "Montserrat",
                            size: 12,
                            weight: "500",
                        },

                        callbacks: {

                            label(context) {
                                return (
                                    context.label
                                    + ": "
                                    + reportCurrencyFormatter.format(
                                        context.raw || 0
                                    )
                                );
                            },

                        },
                    },
                },
            },
        }
    );

}

/* ==================================================
   COSTS BY VEHICLE
   ================================================== */

const reportVehicleCostsCanvas =
    document.getElementById(
        "reportVehicleCostsChart"
    );


if (reportVehicleCostsCanvas) {

    const vehicleLabelsElement =
        document.getElementById(
            "report-vehicle-cost-labels"
        );

    const vehicleCostsElement =
        document.getElementById(
            "report-vehicle-costs"
        );


    const vehicleLabels =
        vehicleLabelsElement
            ? JSON.parse(
                vehicleLabelsElement.textContent
            )
            : [];


    const vehicleCosts =
        vehicleCostsElement
            ? JSON.parse(
                vehicleCostsElement.textContent
            )
            : [];


    new Chart(
        reportVehicleCostsCanvas,
        {
            type: "bar",

            data: {

                labels: vehicleLabels,

                datasets: [
                    {
                        label: "Trošak",

                        data: vehicleCosts,

                        backgroundColor:
                            reportBlue900,

                        borderColor:
                            reportBlue900,

                        borderWidth: 0,

                        borderRadius: 6,

                        borderSkipped: false,

                        maxBarThickness: 30,
                    },
                ],

            },


            options: {

                indexAxis: "y",

                responsive: true,

                maintainAspectRatio: false,

                layout: {
                    padding: {
                        left: 12,
                        right: 12,
                    },
                },


                interaction: {
                    intersect: false,
                    mode: "index",
                },


                plugins: {

                    legend: {
                        display: false,
                    },


                    tooltip: {

                        displayColors: false,

                        backgroundColor:
                            reportBlue950,

                        titleColor:
                            reportWhite,

                        bodyColor:
                            reportWhite,

                        padding: 10,

                        cornerRadius: 6,

                        titleFont: {
                            family: "Montserrat",
                            size: 12,
                            weight: "600",
                        },

                        bodyFont: {
                            family: "Montserrat",
                            size: 12,
                            weight: "500",
                        },

                        callbacks: {

                            label(context) {

                                return (
                                    reportCurrencyFormatter
                                    .format(
                                        context.raw || 0
                                    )
                                );

                            },

                        },

                    },

                },


                scales: {

                    x: {

                        beginAtZero: true,

                        border: {
                            display: false,
                        },

                        grid: {

                            color:
                                reportBlue200,

                            drawTicks: false,
                        },

                        ticks: {

                            padding: 10,

                            color:
                                reportBlue500,

                            font: {
                                family: "Montserrat",
                                size: 11,
                                weight: "500",
                            },

                            callback(value) {

                                return (
                                    new Intl.NumberFormat(
                                        "hr-HR",
                                        {
                                            maximumFractionDigits: 0,
                                        }
                                    ).format(value)
                                    + " €"
                                );

                            },

                        },

                    },


                    y: {

                        grid: {
                            display: false,
                        },

                        border: {
                            display: false,
                        },

                        ticks: {

                            color:
                                reportBlue500,

                            font: {
                                family: "Montserrat",
                                size: 12,
                                weight: "600",
                            },

                        },

                    },

                },

            },

        }
    );

}


});