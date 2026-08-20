document.addEventListener("DOMContentLoaded", () => {

    const modal = document.querySelector(
        "[data-delete-modal]"
    );

    const openButton = document.querySelector(
        "[data-delete-open]"
    );

    const closeButtons = document.querySelectorAll(
        "[data-delete-close]"
    );

    if (!modal || !openButton) {
        return;
    }


    let lastFocusedElement = null;


    /* ==============================================
       OPEN MODAL
       ============================================== */

    function openDeleteModal() {

        lastFocusedElement = document.activeElement;

        modal.hidden = false;

        requestAnimationFrame(() => {

            modal.classList.add("is-open");

            modal.setAttribute(
                "aria-hidden",
                "false"
            );

        });

        document.body.style.overflow = "hidden";


        const cancelButton = modal.querySelector(
            "[data-delete-close]:not(.delete-modal-backdrop)"
        );

        if (cancelButton) {
            cancelButton.focus();
        }
    }


    /* ==============================================
       CLOSE MODAL
       ============================================== */

    function closeDeleteModal() {

        modal.classList.remove("is-open");

        modal.setAttribute(
            "aria-hidden",
            "true"
        );

        document.body.style.overflow = "";

        setTimeout(() => {
            modal.hidden = true;
        }, 250);


        if (lastFocusedElement) {
            lastFocusedElement.focus();
        }
    }


    /* ==============================================
       EVENTS
       ============================================== */

    openButton.addEventListener(
        "click",
        openDeleteModal
    );


    closeButtons.forEach((button) => {

        button.addEventListener(
            "click",
            closeDeleteModal
        );

    });


    document.addEventListener(
        "keydown",
        (event) => {

            if (
                event.key === "Escape" &&
                modal.classList.contains("is-open")
            ) {
                closeDeleteModal();
            }

        }
    );

});