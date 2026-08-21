document.addEventListener("DOMContentLoaded", () => {

    const uploadField = document.querySelector(
        ".document-upload-field"
    );

    if (!uploadField) {
        return;
    }

    const fileInput = uploadField.querySelector(
        'input[type="file"]'
    );

    const uploadTitle = uploadField.querySelector(
        ".document-upload-title"
    );

    if (!fileInput || !uploadTitle) {
        return;
    }

    fileInput.addEventListener("change", () => {

        const file = fileInput.files[0];

        if (file) {
            uploadTitle.textContent = file.name;
        } else {
            uploadTitle.textContent = "Odaberite datoteku";
        }

    });

});