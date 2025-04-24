import json
import pathlib
from extract_md import process_local_pdf
from loguru import logger
import time

def process_pdfs_in_directory():
    """
    Processa todos os arquivos PDF na pasta pdf_termos/ e salva os resultados
    como arquivos JSON na pasta json_termos/
    """
    # Configurar o logger
    logger.info("Iniciando processamento de PDFs")

    # Definir diretórios de origem e destino
    pdf_dir = pathlib.Path("pdf_termos")
    json_dir = pathlib.Path("json_termos")

    # Garantir que o diretório de destino existe
    json_dir.mkdir(exist_ok=True)

    # Obter lista de arquivos PDF
    pdf_files = [f for f in pdf_dir.iterdir() if f.is_file() and f.suffix.lower() == '.pdf']

    if not pdf_files:
        logger.warning("Nenhum arquivo PDF encontrado na pasta pdf_termos/")
        return

    logger.info(f"Encontrados {len(pdf_files)} arquivos PDF para processar")

    # Processar cada arquivo PDF
    for pdf_path in pdf_files:
        pdf_filename = pdf_path.name
        json_filename = pdf_path.stem + ".json"
        json_path = json_dir / json_filename

        # Verificar se o JSON já existe para evitar reprocessamento
        if json_path.exists():
            logger.info(f"O arquivo {json_filename} já existe. Pulando processamento.")
            continue

        logger.info(f"Processando {pdf_filename}...")

        try:
            # Ajustando o caminho relativo para funcionar com process_local_pdf
            # A função espera o caminho dentro da pasta "PDFs/"
            # Criamos uma cópia do arquivo na pasta PDFs temporariamente se necessário
            pdfs_dir = pathlib.Path("PDFs")
            pdfs_dir.mkdir(exist_ok=True)

            temp_pdf_path = pdfs_dir / pdf_filename

            # Se o arquivo não existir na pasta PDFs, copiamos para lá
            if not temp_pdf_path.exists():
                with open(pdf_path, 'rb') as src_file:
                    content = src_file.read()
                    with open(temp_pdf_path, 'wb') as dest_file:
                        dest_file.write(content)
                logger.info(f"Copiado {pdf_filename} para a pasta PDFs/")

            # Processar o PDF
            result = process_local_pdf(pdf_filename)

            # Salvar o resultado como JSON
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(result, json_file, ensure_ascii=False, indent=4)

            logger.success(f"Arquivo {json_filename} salvo com sucesso!")

            # Remover o arquivo temporário
            if temp_pdf_path.exists():
                temp_pdf_path.unlink()
                logger.info(f"Arquivo temporário {pdf_filename} removido da pasta PDFs/")

            # Pausa para não sobrecarregar a API
            time.sleep(1)

        except Exception as e:
            logger.error(f"Erro ao processar {pdf_filename}: {str(e)}")

    logger.success("Processamento de todos os PDFs concluído!")

if __name__ == "__main__":
    process_pdfs_in_directory()


