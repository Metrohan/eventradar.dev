"""Reversible technical-content scope; format words alone are not technical evidence."""

import re
import unicodedata


def _normalise(value: str) -> str:
    value = value.lower().replace("c++", "cplusplus").replace("c#", "csharp")
    value = value.translate(str.maketrans("ıİşŞğĞüÜöÖçÇ", "iIsSgGuUoOcC"))
    return (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    )


_TECHNICAL = re.compile(
    r"\b(?:yazilim\w*|kodlama|kodluyoruz|python|javascript|typescript|java|kotlin|swift|"
    r"rust|golang|cplusplus|csharp|veri|data|yapay zeka|artificial intelligence|ai|ml|claude|chatgpt|machine learning|"
    r"deep learning|generative|agentic|siber|cyber\w*|bilgisayar|computer science|"
    r"elektronik|electronics|gomulu|embedded|robotik|robotics|iot|devops|cloud|bulut|"
    r"teknoloji|technology|no[ -]?code|low[ -]?code|sql|linux|network engineering|network security|ag teknolojileri|sebeke|"
    r"blockchain|web3|software|programlama|programming)\b"
)
_GENERAL_TITLE = re.compile(
    r"\b(?:career summit|talent summit|business strategy|future of hr|retail challenge|"
    r"youth academy|mentor|case maratonu|fellowship|girisimcilik okulu|cool chain|"
    r"payroll|youtalkz|hikaye hasadi)\b"
)


def is_technical_event(title: str | None, description: str | None = None) -> bool:
    title_text = _normalise(title or "")
    if _GENERAL_TITLE.search(title_text):
        return False
    return bool(_TECHNICAL.search(title_text + " " + _normalise(description or "")))
