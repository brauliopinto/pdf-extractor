import os
from openai import OpenAI
from extract_md import response_json

# Set up OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def main():

    class Metadata:
        def __init__(self, name, prompt):
            self.name = name
            self.prompt = prompt
            self.value = None

        def extract(self, content):
            try:
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    temperature=0,
                    max_tokens=100,
                    messages=[
                        {"role": "system", "content": "You are a specialized assistant in extracting metadata."},
                        {"role": "user", "content": self.prompt.format(content=content)},
                    ],
                )
                self.value = completion.choices[0].message.content
            except Exception as e:
                self.value = f"Error: {e}"


    # Define the metadata structure
    metadata_list = [
        Metadata("title", "Extract the title from the following content:\n\n{content}"),
        Metadata("authors", "Extract the list of authors from the following content:\n\n{content}"),
        Metadata("publication_year", "Extract the publication year from the following content:\n\n{content}"),
        Metadata("isbn", "Extract the ISBN from the following content:\n\n{content}"),
    ]

    # Process each metadata
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
