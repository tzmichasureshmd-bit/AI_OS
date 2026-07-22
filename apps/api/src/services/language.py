"""Language Detection - English, Hindi, Telugu with auto-switching."""

import re
from ..core.interfaces import STTProvider

TELUGU = re.compile(r'[\u0C00-\u0C7F]')
HINDI = re.compile(r'[\u0900-\u097F]')

HINDI_WORDS = {"kya","hai","aap","mein","hum","kaise","nahi","haan","ji","accha","batao","kitna","bhai","abhi","bohot","theek","paisa"}
TELUGU_WORDS = {"entha","enti","ela","enduku","meeru","nenu","bagundi","cheppandi","randi","avunu","kaadu","ledhu","undi","chesaru","anna","akka","emiti"}


class LanguageService:
    def __init__(self):
        self.current_language = "en"

    async def detect(self, text: str) -> str:
        if not text.strip():
            return self.current_language
        t = text.lower()
        if len(TELUGU.findall(text)) > 2:
            return self._set("te")
        if len(HINDI.findall(text)) > 2:
            return self._set("hi")
        words = set(re.findall(r'\b\w+\b', t))
        if len(words & TELUGU_WORDS) >= 1:
            return self._set("te")
        if len(words & HINDI_WORDS) >= 1:
            return self._set("hi")
        return self._set("en")

    def get_language_instruction(self) -> str:
        m = {"en": "English", "hi": "Hindi (Hinglish OK)", "te": "Telugu (Tenglish OK)"}
        lang = m.get(self.current_language, "English")
        return f"LANGUAGE: Respond in {lang}. If customer switches language, follow immediately."

    def _set(self, lang: str) -> str:
        self.current_language = lang
        return lang
