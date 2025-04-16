import os
from openai import OpenAI
from extract_md import process_local_pdf

# Set up OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Pdf filename to process
pdf_filename = "Edital_90015_2025_Aquisicao_de_CONTRASTE_RADIOLOGICO.pdf"

def process_pages(pages, max_tokens=10000):
    """Process pages list into manageable chunks"""
    # Check if pages is a list
    if not isinstance(pages, list):
        # If it's not a list, return it as a single item
        return [str(pages)]

    # Join all pages into a single text
    all_text = "\n\n----------\n\n".join([str(page) for page in pages])

    # Split into chunks
    chunks = []
    current_chunk = ""

    # Simple approximation: assume 1 character ≈ 0.25 tokens
    est_token_length = len(all_text) // 4

    if est_token_length <= max_tokens:
        return [all_text]  # Return as a single chunk

    # Otherwise, split by pages
    for page in pages:
        page_text = str(page)
        if len(current_chunk) + len(page_text) < max_tokens * 4:  # Approximate character count
            if current_chunk:
                current_chunk += "\n\n----------\n\n"
            current_chunk += page_text
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = page_text

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def main():
    class Metadata:
        def __init__(self, name, prompt, consolidation_prompt):
            self.name = name
            self.prompt = prompt
            self.consolidation_prompt = consolidation_prompt
            self.value = None

        def extract(self, pages):
            try:
                # Process pages into manageable chunks
                chunks = process_pages(pages)
                results = []

                # Primeira passagem: extrair informações de cada chunk
                for i, chunk in enumerate(chunks):
                    # Ajusta o prompt com base no número do chunk
                    if i == 0:
                        chunk_prompt = self.prompt.format(content=chunk)
                    else:
                        chunk_prompt = f"Analise este novo trecho do mesmo documento. {self.prompt.format(content=chunk)}"

                    print(f"Processando parte {i+1}/{len(chunks)} para {self.name}...")

                    completion = client.chat.completions.create(
                        model="gpt-4o-mini",
                        temperature=0,
                        max_tokens=500,  # Limita o tamanho da resposta
                        messages=[
                            {"role": "system", "content": "Você é um assistente especializado em extrair metadados de documentos de licitação."},
                            {"role": "user", "content": chunk_prompt},
                        ],
                    )

                    result = completion.choices[0].message.content
                    results.append(result)

                # Segunda passagem: consolidar os resultados
                if len(results) > 1:
                    # Só precisa consolidar se tivermos mais de um resultado
                    raw_results = "\n\n---\n\n".join(results)

                    print(f"Consolidando resultados para {self.name}...")

                    consolidation_completion = client.chat.completions.create(
                        model="gpt-4o-mini",
                        temperature=0,
                        messages=[
                            {"role": "system", "content": "Você é um assistente especializado em consolidar informações extraídas de documentos."},
                            {"role": "user", "content": self.consolidation_prompt.format(results=raw_results)},
                        ],
                    )

                    self.value = consolidation_completion.choices[0].message.content
                else:
                    # Apenas um chunk, não precisa consolidar
                    self.value = results[0]

            except Exception as e:
                self.value = f"Error: {e}"

    # Define the metadata structure with optimized prompts
    metadata_list = [
        Metadata(
            name="objeto",
            prompt="Identifique e extraia APENAS o objeto da licitação do seguinte trecho do documento. Seja conciso:\n\n{content}",
            consolidation_prompt="Abaixo estão vários trechos extraídos sobre o objeto da licitação. Consolide-os em um ÚNICO objeto conciso, eliminando repetições e redundâncias:\n\n{results}"
        ),
        Metadata(
            name="indice",
            prompt="Identifique e extraia o índice de reajuste de preços mencionado no seguinte trecho do documento:\n\n{content}",
            consolidation_prompt="Abaixo estão vários trechos extraídos sobre o índice de reajuste de preços. Consolide-os em uma resposta única e precisa, eliminando redundâncias:\n\n{results}"
        ),
        Metadata(
            name="prazo",
            prompt="Identifique e extraia o prazo de vigência do contrato ou ata mencionado no seguinte trecho do documento:\n\n{content}",
            consolidation_prompt="Abaixo estão vários trechos extraídos sobre o prazo de vigência do instrumento de contrato. Consolide-os em uma resposta única e precisa, eliminando redundâncias:\n\n{results}"
        ),
        Metadata(
            name="valor_item",
            prompt="Identifique e extraia o valor total estimado por item mencionado no seguinte trecho do documento, relacionando TODOS os itens:\n\n{content}",
            consolidation_prompt="Abaixo estão vários trechos extraídos sobre os valores de cada item ou lote. Consolide-os em uma resposta única e precisa, eliminando redundâncias:\n\n{results}"
        ),
        Metadata(
            name="ME-EPP",
            prompt="Identifique se há itens exclusivos destinados a micro-empresas e empresas de pequeno porte e extraia os respectivos itens ou lotes :\n\n{content}",
            consolidation_prompt="Abaixo estão vários trechos extraídos sobre a exclusividade de itens ou lotes a micro-empresas e empresas de pequeno porte. Consolide-os em uma resposta única e precisa, eliminando redundâncias:\n\n{results}"
        ),
    ]

    # Process each metadata
    response_json = process_local_pdf(pdf_filename)
    specific_response = response_json.get("pages", "Key not found")
    for metadata in metadata_list:
        metadata.extract(specific_response)

    # Save metadata to a file
    with open("metadata.json", "w", encoding="utf-8") as file:
        import json
        json.dump({m.name: m.value for m in metadata_list}, file, indent=4, ensure_ascii=False)

    print("Extracted Metadata:")
    for metadata in metadata_list:
        print(f"{metadata.name}: {metadata.value}")

if __name__ == "__main__":
    main()
