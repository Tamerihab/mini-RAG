from pathlib import Path


class TemplateParser:
    def __init__(self, language: str = None, default_language: str = 'en'):
        self.current_path = Path(__file__).resolve().parent
        self.default_language = default_language
        self.language = None

        self.set_language(language)

    def set_language(self, language: str):
        if not language:
            self.language = self.default_language
            return None

        language_path = self.current_path / "locales" / language
        if language and language_path.exists():
            self.language = language

        else:
            self.language = self.default_language

    def get(self, group: str, key: str, vars: dict = {}):
        if not group or not key:
            return None

        group_path = self.current_path / "locales" / self.language / f"{group}.py"
        targeted_language = self.language
        if not group_path.exists():
            group_path = self.current_path / "locales" / self.default_language / f"{group}.py"
            targeted_language = self.default_language

        if not group_path.exists():
            return None

        # import the group file as a module
        module = __import__(f"stores.llm.templates.locales.{targeted_language}.{group}", fromlist=[group])

        if not module:
            return None

        key_attribute = getattr(module, key)
        return key_attribute.substitute(vars) 