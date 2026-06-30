FROM python:3.10-slim

# Instala o Tesseract OCR com suporte a português e o Poppler nativos do Linux
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta que o Render monitora por padrão
EXPOSE 10000

# Executa o seu arquivo principal usando o Python do servidor
CMD ["python", "app.py"]

