"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull do prompt semente do desafio
3. Salva localmente em prompts/bug_to_user_story_v1.yml

DICAS DE IMPLEMENTAÇÃO:

- O pull é feito pelo cliente do LangSmith:

      from langsmith import Client
      client = Client()
      prompt = client.pull_prompt(
          "leonanluppi/bug_to_user_story_v1",
          dangerously_pull_public_prompt=True,
      )

- O parâmetro `dangerously_pull_public_prompt=True` é obrigatório sempre que o
  identificador tem dono explícito ("owner/nome"). O LangSmith bloqueia esse pull
  por padrão porque um prompt do Hub é um objeto LangChain serializado, que pode
  vir de terceiros. Aqui o prompt é o do desafio, então o risco é conhecido.

- O retorno é um ChatPromptTemplate. Para extrair o conteúdo das mensagens,
  use a serialização nativa do LangChain (`prompt.messages`, e o atributo
  `.prompt.template` de cada mensagem).

- Use `save_yaml` de utils.py para gravar o resultado no arquivo .yml.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

SEED_PROMPT_ID = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "bug_to_user_story_v1.yml"


def _template_from_message(message) -> str:
    if isinstance(message, (SystemMessagePromptTemplate, HumanMessagePromptTemplate)):
        return message.prompt.template
    prompt_part = getattr(message, "prompt", None)
    if prompt_part is not None and hasattr(prompt_part, "template"):
        return prompt_part.template
    return str(message)


def chat_prompt_to_yaml_dict(prompt) -> dict:
    """Converte ChatPromptTemplate em estrutura YAML do projeto."""
    system_prompt = ""
    user_prompt = ""

    for message in prompt.messages:
        template = _template_from_message(message)
        if isinstance(message, SystemMessagePromptTemplate):
            system_prompt = template
        elif isinstance(message, HumanMessagePromptTemplate):
            user_prompt = template

    return {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "created_at": "2025-01-15",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }


def pull_prompts_from_langsmith() -> bool:
    client = Client()
    prompt = client.pull_prompt(
        SEED_PROMPT_ID,
        dangerously_pull_public_prompt=True,
    )
    data = chat_prompt_to_yaml_dict(prompt)
    return save_yaml(data, str(OUTPUT_PATH))


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    print(f"Baixando prompt: {SEED_PROMPT_ID}")

    try:
        if pull_prompts_from_langsmith():
            print(f"✅ Prompt salvo em: {OUTPUT_PATH}")
            return 0
        print("❌ Falha ao salvar o prompt localmente.")
        return 1
    except Exception as exc:
        print(f"❌ Erro ao fazer pull do prompt: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
