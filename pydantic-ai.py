from typing import Union, Dict, Optional
from pydantic import BaseModel
from pydantic_ai import Agent

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from dotenv import load_dotenv
import os

from extract_md import process_local_pdf

load_dotenv()

model = OpenAIModel('gpt-4.1-nano', provider=OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY")))

pdf_filename = "PE_90014_2025_OPME_cirurgia_coluna.pdf"

def main():

    class DadosLicitacoes(BaseModel):
        objeto: str
        indice: Optional[str] = None
        valor_item: Optional[Dict[str, str]] = None
        exclusividade_item: Optional[Dict[str, str]] = None


    agent: Agent[None, Union[DadosLicitacoes, str]] = Agent(
        model=model,
        output_type=Union[DadosLicitacoes, str],  # type: ignore
        system_prompt=(
            """
            Você é um assistente de IA especializado em extrair dados de documentos.
            Seja o mais conciso e claro possível.
            1. O campo objeto deve conter apenas o objeto da licitação.
            2. O campo indice deve conter apenas o índice de reajuste de preços (por exemplo: IPCA, INPC, IGP-M ou outro).
            3. O campo valor_item deve conter o valor total estimado por item, relacionando todos os itens. (por exemplo: {'item_1': '1000', 'item_2': '2000'})
            4. O campo exclusividade_item deve dizer se determinado item é exclusivo para micro-empresas ou empresas de pequeno porte, onde 'Sim' significa que o item é exclusivo e 'Não' significa que não é. Exemplo de saída: {'item_1': 'Sim', 'item_2': 'Não'}.
            """
        ),
    )

    response_json = process_local_pdf(pdf_filename)
    specific_response = response_json.get("pages", "Key not found")

    result = agent.run_sync(specific_response)
    print(result.output.model_dump_json())
    #> width=10 height=20 depth=30 units='cm'


if __name__ == "__main__":
    main()