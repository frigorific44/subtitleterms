from collections import defaultdict

from anki.lang import current_lang

from .localizations import safe_localizations

combined = safe_localizations["en-US"] | safe_localizations[current_lang]
localization = defaultdict(lambda: "ErrorMissing")
for k, v in combined.items():
    localization[k] = v
