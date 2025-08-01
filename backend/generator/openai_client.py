import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_micro_sop(asset_type: str, prompt: str) -> str:
    # Define o sistema base conforme o tipo de conteúdo
    system_messages = {
        "email": "Gere um email profissional com base nesta situação.",
        "checklist": "Gere uma checklist passo-a-passo clara e concisa para este serviço.",
        "sms": "Gere uma SMS curta, clara e profissional para esta situação."
    }

    system_instruction = system_messages.get(asset_type.lower(), "Gere um conteúdo útil.")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()
