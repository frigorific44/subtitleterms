import gettext
import pathlib
from anki.lang import current_lang

dirpath = pathlib.Path(__file__).parent.joinpath("locales")
t = gettext.translation(
    "subtitleterms", dirpath, fallback=True, languages=[current_lang]
)
_ = t.gettext
