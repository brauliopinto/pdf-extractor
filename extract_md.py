import os
import pathlib
import requests
from dotenv import load_dotenv
import tempfile
from loguru import logger

load_dotenv()

url_ocr_api = "https://ocrapi.sistemas.tce.pa/v1/azure/file/pdf"  # Mudando para o endpoint de arquivo
pdf_url = "https://app.comprasbr.com.br/licitacao/hal/public/arquivos?uri=repo1:licitacao/PE0722032025Edital2703.pdf&thumbnail=false"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "application/pdf",
    "authorization": f"Bearer {os.getenv('OCR_API_KEY')}",
}

def download_pdf_and_process():
    # Primeiro, baixe o PDF
    logger.info("Baixando o PDF...")
    pdf_response = requests.get(
        pdf_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        verify=False,
    )

    if pdf_response.status_code != 200:
        logger.error(f"Falha ao baixar o PDF: {pdf_response.status_code}")
        logger.info(pdf_response.text)
        return {"error": f"Failed to download PDF: {pdf_response.status_code}"}

    # Verifica se o conteúdo é realmente um PDF
    if not pdf_response.headers.get('Content-Type', '').lower().startswith('application/pdf'):
        logger.info(f"O conteúdo não parece ser um PDF. Content-Type: {pdf_response.headers.get('Content-Type')}")

        # Salva o conteúdo para depuração
        with open("debug_content.txt", "wb") as f:
            f.write(pdf_response.content)

        # Tenta verificar se o conteúdo começa com %PDF (assinatura de PDF)
        if not pdf_response.content.startswith(b'%PDF'):
            logger.error("O conteúdo não começa com a assinatura de PDF")
            return {"error": "Content is not a PDF"}

    # Salva o PDF temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(pdf_response.content)
        temp_pdf_path = tmp.name

    logger.info(f"PDF baixado e salvo em {temp_pdf_path}")

    # Agora envia o arquivo para a API OCR
    logger.info("Enviando o arquivo para a API OCR...")
    with open(temp_pdf_path, 'rb') as pdf_file:
        files = {'file': ('document.pdf', pdf_file, 'application/pdf')}
        ocr_response = requests.post(
            url_ocr_api,
            files=files,
            headers={"Authorization": f"Bearer {os.getenv('OCR_API_KEY')}"},
            verify=False
        )

    # Limpa o arquivo temporário
    os.unlink(temp_pdf_path)

    if ocr_response.status_code != 200:
        print(f"Falha na API OCR: {ocr_response.status_code}")
        print(ocr_response.text)
        return {"error": f"OCR API failed: {ocr_response.status_code}", "detail": ocr_response.text}

    return ocr_response.json()

# # Executa o processamento
# response_json = download_pdf_and_process()

def process_local_pdf(pdf_filename):
    """
    Processa um arquivo PDF local da pasta PDFs/

    Args:
        pdf_filename: Nome do arquivo PDF na pasta PDFs/

    Returns:
        dict: JSON com os dados extraídos pela API OCR
    """
    # Constrói o caminho completo para o arquivo PDF
    pdf_path = pathlib.Path("PDFs") / pdf_filename

    # Verifica se o arquivo existe
    if not pdf_path.exists():
        logger.error(f"Arquivo não encontrado: {pdf_path}")
        return {"error": f"File not found: {pdf_path}"}

    logger.info(f"Processando arquivo local: {pdf_path}")

    # Verifica se o arquivo é um PDF
    with open(pdf_path, 'rb') as pdf_file:
        # Lê os primeiros bytes para verificar a assinatura PDF
        header = pdf_file.read(4)
        if header != b'%PDF':
            logger.error(f"O arquivo {pdf_filename} não parece ser um PDF válido")
            return {"error": "File is not a valid PDF"}

    # Envia o arquivo para a API OCR
    logger.info(f"Enviando o arquivo {pdf_filename} para a API OCR...")
    with open(pdf_path, 'rb') as pdf_file:
        files = {'file': (pdf_filename, pdf_file, 'application/pdf')}
        ocr_response = requests.post(
            url_ocr_api,
            files=files,
            headers={"Authorization": f"Bearer {os.getenv('OCR_API_KEY')}"},
            verify=False
        )

    if ocr_response.status_code != 200:
        logger.error(f"Falha na API OCR: {ocr_response.status_code}")
        logger.error(ocr_response.text)
        return {"error": f"OCR API failed: {ocr_response.status_code}", "detail": ocr_response.text}

    logger.success(f"Processamento do arquivo {pdf_filename} concluído com sucesso")
    return ocr_response.json()

# Exemplo de uso
if __name__ == "__main__":
    # Processa o arquivo PDF específico
    pdf_filename = "PE_90014_2025_OPME_cirurgia_coluna.pdf"
    result = process_local_pdf(pdf_filename)

    # Access a specific key
    specific_key_value = result.get("pages", "Key not found")
    print(specific_key_value)