document.addEventListener("DOMContentLoaded", () => {

    const imageInput = document.querySelector(
        "#id_image"
    );

    const uploadLabel = document.querySelector(
        "[data-image-upload-label]"
    );

    if (!imageInput || !uploadLabel) {
        return;
    }

    const defaultContent = uploadLabel.innerHTML;


    imageInput.addEventListener("change", () => {

        const file = imageInput.files[0];

        if (file) {

            uploadLabel.innerHTML = "";

            uploadLabel.classList.add(
                "has-file"
            );


            const fileName = document.createElement(
                "span"
            );

            fileName.classList.add(
                "vehicle-image-file-name"
            );

            fileName.textContent = file.name;

            uploadLabel.appendChild(
                fileName
            );

            return;
        }

        uploadLabel.innerHTML = defaultContent;

        uploadLabel.classList.remove(
            "has-file"
        );

    });

});