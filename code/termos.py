from typing import Union, Optional
from pydantic import BaseModel
from pydantic_ai import Agent

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.azure import AzureProvider

from dotenv import load_dotenv
import os
import pathlib
import json

from loguru import logger

load_dotenv()

model = OpenAIModel('gpt-4.1-nano', provider=AzureProvider(azure_endpoint=os.getenv("AZOPENAI_API_ENDPOINT"),
                                                           api_version=os.getenv("AZOPENAI_API_VERSION"),
                                                           api_key=os.getenv("AZOPENAI_API_KEY"))
)

def extrair_metadados(json_filename: Optional[str] = None):

    class MetadadosTermos(BaseModel):
        tipo_instrumento: Optional[str] = None
        numero_ano_instrumento: Optional[str] = None
        numero_processo: Optional[str] = None
        nome_responsavel_concedente: Optional[str] = None
        cpf_responsavel_concedente: Optional[str] = None
        cpf_responsavel: Optional[str] = None
        nome_responsavel: Optional[str] = None
        data_assinatura_digital: Optional[str] = None
        data_assinatura_diario_oficial: Optional[str] = None
        inicio_vigencia: Optional[str] = None
        fim_vigencia: Optional[str] = None
        cnpj_concedente: Optional[str] = None
        razao_social_concedente: Optional[str] = None
        cnpj_convenente: Optional[str] = None
        razao_social_convenente: Optional[str] = None
        valor_repasse: Optional[str] = None
        valor_contrapartida: Optional[str] = None
        valor_contrapartida_bens_servicos: Optional[str] = None


    agent: Agent[None, Union[MetadadosTermos, str]] = Agent(
        model=model,
        output_type=Union[MetadadosTermos, str],  # type: ignore
        system_prompt=(
            """
            Você é um assistente de IA especializado em extrair dados de termos de convênio, colaboração, fomento etc.
            Seja o mais conciso e claro possível.
            1. O campo tipo_instrumento deve conter o tipo de instrumento legal. Por exemplo: "Termo de Fomento", "Convênio", "Termo de Colaboração", etc.
            2. O campo numero_ano_instrumento deve conter o número e o ano do instrumento legal. Por exemplo: "169/2022", "001/2021".
            3. O campo numero_processo deve conter o número do processo associado ao instrumento legal. Por exemplo: "123.453/2022".
            4. O campo nome_responsavel_concedente deve conter o nome completo da autoridade administrativa que representa a entidade CONCEDENTE no documento legal.
            5. O campo cpf_responsavel_concedente deve conter o CPF do representante da entidade CONCEDENTE.
            6. O campo cpf_responsavel deve conter o CPF do responsável pela entidade recebedora, CONVENENTE ou organização parceira.
            7. O campo nome_responsavel deve conter o nome do responsável pela entidade recebedora, CONVENENTE ou organização parceira.
            8. O campo data_assinatura_digital deve conter a data da assinatura digital do termo.
            9. O campo data_assinatura_diario_oficial deve conter a data da publicação no diário oficial.
            10. O campo inicio_vigencia deve conter a data de início da vigência do termo. Apresente-a no formato "dd/mm/aaaa"
            11. O campo fim_vigencia deve conter a data de fim da vigência do termo. Apresente-a no formato "dd/mm/aaaa".
            12. O campo cnpj_concedente deve conter o CNPJ da entidade concedente.
            13. O campo razao_social_concedente deve conter a razão social da entidade concedente.
            14. O campo cnpj_convenente deve conter o CNPJ da entidade recebedora ou organização parceira.
            15. O campo razao_social_convenente deve conter a razão social da entidade recebedora ou organização parceira.
            16. O campo valor_repasse deve conter apenas o valor dos recursos transferidos pela entidade concedente. Exemplo: R$ 500.000,00.
            17. O campo valor_contrapartida deve conter apenas o valor dos recursos de contrapartida da entidade recebedora. Exemplo: R$ 500.000,00.
            18. O campo valor_contrapartida_bens_servicos deve conter apenas o valor da contrapartida em bens ou serviços.
            """
        ),
    )

    # Constrói o caminho completo para o arquivo JSON
    json_folder = pathlib.Path("json_termos")
    json_file_path = json_folder / json_filename
    response_json = json_file_path.read_text(encoding="utf-8")
    response_dict = json.loads(response_json)
    specific_response = response_dict.get("pages", "Key not found")


    result = agent.run_sync(specific_response)
    # Salvar o resultado como JSON na pasta json_outputs
    json_outputs_folder = pathlib.Path("json_outputs")
    json_outputs_folder.mkdir(exist_ok=True)
    output_filename = json_filename.replace(".json", "_output.json")
    output_file_path = json_outputs_folder / output_filename
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(result.output.model_dump_json())
        logger.info(f"Arquivo {output_filename} salvo com sucesso na pasta json_outputs!")

def extrair_tudo():
    """
    Função para extrair metadados de todos os arquivos JSON na pasta json_termos
    """
    json_folder = pathlib.Path("json_termos")
    json_files = list(json_folder.glob("*.json"))

    if not json_files:
        logger.warning("Nenhum arquivo JSON encontrado na pasta json_termos/")
        return

    logger.info(f"Encontrados {len(json_files)} arquivos JSON para processar")

    for json_file in json_files:
        extrair_metadados(json_file.name)

if __name__ == "__main__":

    # # Teste com um arquivo JSON específico
    # json_filename = "TERMO FOMENTO 005-2019.json"
    # extrair_metadados(json_filename=json_filename)

    extrair_tudo()