document.addEventListener("DOMContentLoaded", () => {

    // ==============================================
    // ELEMENTS
    // ==============================================

    const chartCanvas = document.getElementById(
        "costsOverviewChart"
    );

    const labelsElement = document.getElementById(
        "costs-chart-labels"
    );

    const valuesElement = document.getElementById(
        "costs-chart-values"
    );


    if (
        !chartCanvas ||
        !labelsElement ||
        !valuesElement ||
        typeof Chart === "undefined"
    ) {
        return;
    }


    // ==============================================
    // DATA
    // ==============================================

    const labels = JSON.parse(
        labelsElement.textContent
    );

    const values = JSON.parse(
        valuesElement.textContent
    );


    // ==============================================
    // CSS COLORS
    // ==============================================

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


    // ==============================================
    // CHART
    // ==============================================

    new Chart(
        chartCanvas,
        {
            type: "bar",

            data: {
                labels: labels,

                datasets: [
                    {
                        data: values,

                        backgroundColor: blue900,

                        hoverBackgroundColor:
                            blue500,

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


                // ==================================
                // INTERACTION
                // ==================================

                interaction: {
                    mode: "index",
                    intersect: false,
                },


                // ==================================
                // PLUGINS
                // ==================================

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


                // ==================================
                // SCALES
                // ==================================

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

});