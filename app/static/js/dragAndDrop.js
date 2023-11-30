document.addEventListener('DOMContentLoaded', function () {
    const fileInput = document.querySelector('#file');
    const fileDropArea = document.querySelector('.file-drop-area');

    fileDropArea.addEventListener('dragover', function (e) {
        e.preventDefault();
        fileDropArea.style.backgroundColor = '#f0f0f0';
    });

    fileDropArea.addEventListener('dragleave', function () {
        fileDropArea.style.backgroundColor = '';
    });

    fileDropArea.addEventListener('drop', function (e) {
        e.preventDefault();
        fileDropArea.style.backgroundColor = '';

        const files = e.dataTransfer.files;

        if (files.length > 0) {
            fileInput.files = files;
            var fileLabel = document.querySelector('.file-label');
            fileLabel.textContent = fileInput.files[0].name;
        }
    });

    fileInput.addEventListener('change', function () {
        const fileLabel = document.querySelector('.file-label');
        fileLabel.textContent = fileInput.files[0].name;
    });
});
