const uploadArea = document.querySelector('.upload-area');
        const fileInput = document.getElementById('pdf');
        const fileNameDisplay = document.getElementById('file-name');
        const progressContainer = document.getElementById('progress-container');
        const progress = document.getElementById('progress');
        const uploadForm = document.getElementById('uploadForm');

        // Preview começa oculto
        fileNameDisplay.style.display = "none";
        progressContainer.style.display = "none";

        // Mostrar preview só depois que o arquivo for carregado
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                fileNameDisplay.style.display = "block";
                fileNameDisplay.textContent = "Arquivo carregado: " + fileInput.files[0].name;
            } else {
                fileNameDisplay.style.display = "none";
                fileNameDisplay.textContent = "";
            }
        });

        // Arrastar e soltar
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.backgroundColor = '#e6f0fa';
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.style.backgroundColor = '#f9f9f9';
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            fileInput.files = e.dataTransfer.files;
            if (fileInput.files.length > 0) {
                fileNameDisplay.style.display = "block";
                fileNameDisplay.textContent = "Arquivo carregado: " + fileInput.files[0].name;
            }
        });

        // Fluxo: upload primeiro, depois processamento
        uploadForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = new FormData(uploadForm);

            // 1. Envia o arquivo para /upload
            fetch('/upload', {
                method: 'POST',
                body: formData
            }).then(response => {
                if (response.ok) {
                    // 2. Só depois mostra a barra e conecta ao SSE
                    progressContainer.style.display = "block";

                    // conecta ao endpoint SSE do servidor
                    const eventSource = new EventSource('/process');

                    eventSource.onmessage = function (e) {
                        if (e.data === "done") {
                            progress.style.width = "100%";
                            progress.textContent = "Concluído!";
                            eventSource.close();

                            // 🔹 Força o download automático do ZIP
                            window.location.href = "/download";
                        } else {
                            progress.style.width = e.data + "%";
                            progress.textContent = e.data + "%";
                        }
                    };

                } else {
                    alert("Erro ao enviar PDF!");
                }
            });
        });