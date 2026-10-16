"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
from pathlib import Path

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def load_prompt_data():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data[PROMPT_KEY]


class TestPrompts:
    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        prompt_data = load_prompt_data()
        assert "system_prompt" in prompt_data
        assert prompt_data["system_prompt"].strip()

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        prompt_data = load_prompt_data()
        system = prompt_data["system_prompt"].lower()
        assert "você é um" in system or "voce e um" in system
        assert "product manager" in system

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        prompt_data = load_prompt_data()
        system = prompt_data["system_prompt"].lower()
        assert "como um" in system
        assert "critérios de aceitação" in system or "criterios de aceitacao" in system
        assert "markdown" in system or "user story" in system

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        prompt_data = load_prompt_data()
        system = prompt_data["system_prompt"].lower()
        assert "few-shot" in system or "exemplo" in system
        assert "entrada" in system and ("saída" in system or "saida" in system)

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        raw_text = PROMPT_FILE.read_text(encoding="utf-8")
        assert "[TODO]" not in raw_text
        assert "[todo]" not in raw_text.lower()

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        prompt_data = load_prompt_data()
        techniques = prompt_data.get("techniques_applied", [])
        assert len(techniques) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
