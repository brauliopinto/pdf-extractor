# PDF Extractor

## Descrição
O **PDF Extractor** é uma aplicação Python projetada para processar arquivos PDF e extrair metadados relevantes utilizando uma API OCR. O projeto suporta tanto o download de PDFs a partir de URLs quanto o processamento de arquivos locais armazenados na pasta `PDFs/`.

## Estrutura do Projeto

```
PDF Extractor/
├── extract_md.py       # Contém funções para processar PDFs e interagir com a API OCR
├── main.py             # Script principal para extração de metadados
├── metadata.json       # Arquivo gerado contendo os metadados extraídos
├── pyproject.toml      # Configurações do projeto e dependências
├── README.md           # Documentação do projeto
├── response.txt        # Resposta bruta da API OCR (opcional)
├── uv.lock             # Arquivo de bloqueio de dependências
├── __pycache__/        # Cache de arquivos Python compilados
│   └── extract_md.cpython-311.pyc
└── PDFs/               # Pasta contendo os arquivos PDF locais para processamento
    ├── Edital_90015_2025_Aquisicao_de_CONTRASTE_RADIOLOGICO.pdf
    ├── edital_generos_alimenticos_90004-2024.pdf
    └── PE_90014_2025_OPME_cirurgia_coluna.pdf
```

## Funcionalidades

- **Processamento de PDFs locais**: Processa arquivos PDF armazenados na pasta `PDFs/`.
- **Processamento de PDFs via URL**: Faz o download de PDFs a partir de URLs e os envia para a API OCR.
- **Extração de metadados**: Extrai informações específicas, como "objeto" e "índice", de documentos PDF.
- **Consolidação de resultados**: Consolida informações extraídas de diferentes partes de documentos longos.

## Requisitos

- Python 3.11 ou superior
- Dependências listadas no `pyproject.toml`

## Instalação

1. Clone o repositório:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd pdf-extractor
   ```

2. Instale as dependências:
   ```bash
   uv sync --frozen
   ```

## Uso

### Processar um PDF local

1. Coloque o arquivo PDF na pasta `PDFs/`.
2. Execute o script principal:
   ```bash
   uv run main.py
   ```
3. Os metadados extraídos serão salvos no arquivo `metadata.json`.

### Processar um PDF via URL

1. Configure a URL no script `extract_md.py`.
2. Execute o script principal:
   ```bash
   uv run main.py
   ```
3. Os metadados extraídos serão salvos no arquivo `metadata.json`.

## Configuração da API OCR

1. Crie um arquivo `.env` na raiz do projeto.
2. Adicione sua chave de API:
   ```env
   OCR_API_KEY=your_api_key_here
   ```

## Estrutura de Saída

Os metadados extraídos são salvos no arquivo `metadata.json` no seguinte formato:

```json
{
    "objeto": "Descrição do objeto extraído",
    "indice": "Índice extraído"
}
```

## Contribuição

1. Faça um fork do repositório.
2. Crie uma branch para sua feature ou correção de bug:
   ```bash
   git checkout -b minha-feature
   ```
3. Faça commit das suas alterações:
   ```bash
   git commit -m "Minha nova feature"
   ```
4. Envie para o repositório remoto:
   ```bash
   git push origin minha-feature
   ```
5. Abra um Pull Request.

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.