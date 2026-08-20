document.addEventListener("DOMContentLoaded", () => {

    const modal = document.querySelector(
        "[data-delete-modal]"
    );

    const openButtons = document.querySelectorAll(
        "[data-delete-open]"
    );

    const closeButtons = document.querySelectorAll(
        "[data-delete-close]"
    );

    const deleteForm = document.querySelector(
        "[data-delete-form]"
    );

    const vehicleName = document.querySelector(
        "[data-delete-vehicle-name]"
    );

    if (
        !modal ||
        !deleteForm ||
        !vehicleName
    ) {
        return;
    }


    let lastFocusedElement = null;


    /* ==============================================
       OPEN
       ============================================== */

    openButtons.forEach((button) => {

        button.addEventListener("click", () => {

            lastFocusedElement = button;

            vehicleName.textContent =
                button.dataset.deleteName;

            deleteForm.action =
                button.dataset.deleteUrl;

            modal.hidden = false;

            requestAnimationFrame(() => {
                modal.classList.add("is-open");
            });

            modal.classList.add(
                "is-open"
            );

            modal.setAttribute(
                "aria-hidden",
                "false"
            );

            document.body.style.overflow = "hidden";


            const cancelButton = modal.querySelector(
                "[data-delete-close]:not(.delete-modal-backdrop)"
            );

            if (cancelButton) {
                cancelButton.focus();
            }

        });

    });


    /* ==============================================
       CLOSE
       ============================================== */

    function closeModal() {

        modal.classList.remove("is-open");

        modal.setAttribute(
            "aria-hidden",
            "true"
        );

        document.body.style.overflow = "";

        setTimeout(() => {
            modal.hidden = true;
        }, 250);

        document.body.style.overflow = "";

        deleteForm.removeAttribute(
            "action"
        );

        if (lastFocusedElement) {
            lastFocusedElement.focus();
        }

    }


    closeButtons.forEach((button) => {

        button.addEventListener(
            "click",
            closeModal
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
                modal.classList.contains("is-open")
            ) {
                closeModal();
            }

        }
    );

});