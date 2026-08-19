document.addEventListener("DOMContentLoaded", () => {

    /* ==============================================
       PASSWORD VISIBILITY TOGGLE
       ============================================== */

    const passwordToggles = document.querySelectorAll(
        "[data-password-toggle]"
    );

    passwordToggles.forEach((toggle) => {

        toggle.addEventListener("click", () => {

            const inputWrapper = toggle.closest(".input-wrapper");

            if (!inputWrapper) {
                return;
            }

            const passwordInput = inputWrapper.querySelector(
                'input[type="password"], input[data-password-visible="true"]'
            );

            const icon = toggle.querySelector(".password-toggle-icon");

            if (!passwordInput) {
                return;
            }


            /* --------------------------------------
               Prikaži lozinku
               -------------------------------------- */

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

            }


            /* --------------------------------------
               Sakrij lozinku
               -------------------------------------- */

            else {

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

});