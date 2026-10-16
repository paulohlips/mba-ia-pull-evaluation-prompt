"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

DICAS DE IMPLEMENTAÇÃO:

- O push é feito pelo cliente do LangSmith:

      from langsmith import Client
      from langchain_core.prompts import ChatPromptTemplate

      client = Client()
      prompt = ChatPromptTemplate.from_messages([
          ("system", system_prompt),
          ("user", user_prompt),
      ])
      url = client.push_prompt(
          f"{username}/bug_to_user_story_v2",
          object=prompt,
          is_public=True,
          description="...",
          tags=[...],
      )

- `username` vem de USERNAME_LANGSMITH_HUB no .env e precisa ser o seu handle
  do Hub. Se você ainda não tem um handle, veja as instruções no .env.example.

- A variável do template precisa ser {bug_report}, que é a chave de entrada
  usada no dataset de avaliação.

- Use `load_yaml` de utils.py para ler o arquivo .yml.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()

PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"
HUB_PROMPT_NAME = "bug_to_user_story_v2"


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    is_valid, errors = validate_prompt_structure(prompt_data)

    user_prompt = prompt_data.get("user_prompt", "")
    if "{bug_report}" not in user_prompt:
        errors.append("user_prompt deve conter a variável {bug_report}")

    return (len(errors) == 0, errors)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    username = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
    if not username:
        print("❌ USERNAME_LANGSMITH_HUB não configurado no .env")
        return False

    system_prompt = prompt_data["system_prompt"]
    user_prompt = prompt_data.get("user_prompt", "{bug_report}")

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt),
    ])

    description = prompt_data.get(
        "description",
        "Prompt otimizado para converter relatos de bugs em User Stories",
    )
    tags = prompt_data.get("tags", ["bug-analysis", "user-story", "optimized"])
    techniques = prompt_data.get("techniques_applied", [])
    if techniques:
        tags = list(dict.fromkeys([*tags, *techniques]))

    client = Client()
    hub_id = f"{username}/{prompt_name}"
    url = client.push_prompt(
        hub_id,
        object=prompt_template,
        is_public=True,
        description=description,
        tags=tags,
    )

    print(f"✅ Prompt publicado: {hub_id}")
    print(f"   URL: {url}")
    return True


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS AO LANGSMITH HUB")

    required = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required):
        return 1

    raw = load_yaml(str(PROMPT_FILE))
    if not raw or PROMPT_KEY not in raw:
        print(f"❌ Arquivo inválido ou chave '{PROMPT_KEY}' ausente: {PROMPT_FILE}")
        return 1

    prompt_data = raw[PROMPT_KEY]
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    try:
        if push_prompt_to_langsmith(HUB_PROMPT_NAME, prompt_data):
            return 0
        return 1
    except Exception as exc:
        print(f"❌ Erro ao fazer push: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
