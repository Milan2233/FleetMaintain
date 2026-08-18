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

});