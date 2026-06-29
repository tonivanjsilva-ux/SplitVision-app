from flask import Flask, render_template, request, Response, send_file
import time, os, re, io, zipfile
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
import pytesseract

app = Flask(__name__)

# Configura caminhos do Tesseract e Poppler
pytesseract.pytesseract.tesseract_cmd = r"tesseract\\tesseract.exe"
poppler_path = r"poppler\\bin"

# Variáveis globais
last_pdf_path = None
last_zip_bytes = None

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload', methods=["POST"])
def upload_file():
    global last_pdf_path
    pdf = request.files.get('pdf')

    if pdf:
        os.makedirs("uploads", exist_ok=True)
        upload_path = os.path.join("uploads", pdf.filename)
        pdf.save(upload_path)

        last_pdf_path = upload_path
        return "Arquivo recebido!"
    return "Nenhum arquivo enviado", 400

@app.route('/process')
def process_pdf():
    def generate():
        global last_pdf_path, last_zip_bytes
        if not last_pdf_path or not os.path.exists(last_pdf_path):
            yield "data:0\n\n"
            yield "data:done\n\n"
            return

        reader = PdfReader(last_pdf_path)
        pages_img = convert_from_path(last_pdf_path, poppler_path=poppler_path)
        total_pages = len(reader.pages)

        # 🔹 cria ZIP em memória
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            for i, page in enumerate(reader.pages):
                texto = pytesseract.image_to_string(pages_img[i], lang="por")

                padrao = re.search(r"(Documento\s*[:\-]?\s*(\d+)|O\s*\.?\s*S\s*\.?\s*[:\-]?\s*(\d+))", texto, re.IGNORECASE)
                if padrao:
                    numero = padrao.group(2) if padrao.group(2) else padrao.group(3)
                    prefixo = "Documento" if padrao.group(2) else "OS"
                    nome_arquivo = f"{prefixo}_{numero}.pdf"
                else:
                    nome_arquivo = f"pagina_{i+1}.pdf"

                writer = PdfWriter()
                writer.add_page(page)

                pdf_bytes = io.BytesIO()
                writer.write(pdf_bytes)
                pdf_bytes.seek(0)

                # 🔹 adiciona direto no ZIP (sem pasta)
                zipf.writestr(nome_arquivo, pdf_bytes.read())

                time.sleep(0.5)
                percent = int((i+1) / total_pages * 100)
                yield f"data:{percent}\n\n"

        # guarda ZIP em memória
        zip_buffer.seek(0)
        last_zip_bytes = zip_buffer.read()

        yield "data:done\n\n"

    return Response(generate(), mimetype="text/event-stream")

@app.route('/download')
def download_zip():
    global last_zip_bytes
    if last_zip_bytes:
        return send_file(
            io.BytesIO(last_zip_bytes),
            as_attachment=True,
            download_name="SplitVision_Output.zip",
            mimetype="application/zip"
        )
    return "Arquivo ZIP não encontrado", 404

if __name__ == "__main__":
    app.run(debug=True)
