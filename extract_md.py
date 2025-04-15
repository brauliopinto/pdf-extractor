import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = "https://ocrapi.sistemas.tce.pa/v1/azure/url"
example_pdf_url = (
    "https://github.com/cpatrickalves/simprev/files/12432062/example02_livro.pdf"
)
example_pdf_url = (
    "https://app.comprasbr.com.br/licitacao/hal/public/arquivos?uri=repo1:licitacao/PE0722032025Edital2703.pdf&thumbnail=false"
)

headers = {
    "user-agent": "vscode-restclient",
    "content-type": "application/json",
    "authorization": f"Bearer {os.getenv('OCR_API_KEY')}",
}

response = requests.post(
    url,
    json={"url": example_pdf_url},
    headers={"Authorization": f"Bearer {os.getenv('OCR_API_KEY')}"},
    verify=False,
)

# Parse the response as JSON
response_json = response.json()


if __name__ == "__main__":
    # Access a specific key
    specific_key_value = response_json.get("pages", "Key not found")
    print(response_json)