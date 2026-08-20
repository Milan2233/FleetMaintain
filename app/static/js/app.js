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

});