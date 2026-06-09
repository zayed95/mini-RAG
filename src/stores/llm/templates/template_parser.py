import os

class TemplateParser:

    def __init__(self, language: str=None, def_language='en'):
        
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.def_language = def_language
        self.language = None

        self.set_language(language=language)

    def set_language(self, language: str):
        if not language:
            self.language = self.def_language
            return None

        language_path = os.path.join(self.current_path, "locales", language)
        if os.path.exists(language_path):
            self.language = language
        
        else:
            self.language = self.def_language

    def get(self, group: str, key: str, vars: dict={}):
        if not group or not key:
            return None
        
        group_path = os.path.join(self.current_path, "locales", self.language, f"{group}.py")
        targeted_language = self.language
        if not os.path.exists(group_path):
            group_path = os.path.join(self.current_path, "locales", self.def_language, f"{group}.py")
            targeted_language = self.def_language
        
        if not os.path.exists(group_path):
            return None
        
        module = __import__(f"stores.llm.templates.locales.{targeted_language}.{group}", fromlist=[group])
        if not module:
            return None
        
        key_attr = getattr(module, key)
        return key_attr.substitute(vars)
