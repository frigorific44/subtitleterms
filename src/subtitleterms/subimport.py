from aqt.utils import showWarning

from .deck import builders
from .ext import ext, parse_srt
from .ui import ImportDialog


def importDeck() -> None:
    import_settings = ImportDialog().getSettings()
    if not import_settings:
        return
    builder = builders[import_settings.deck]
    if import_settings.subtitle_stream > -1:
        sub_text = ext(import_settings.path, import_settings.subtitle_stream)
        subs = parse_srt(sub_text)
    else:
        # TODO: Better determine the encoding.
        # TODO: utf-8-sig instead?
        sub_text = import_settings.path.read_text(encoding="utf-8")
        if import_settings.path.suffix == ".srt":
            subs = parse_srt(sub_text)
        else:
            subs = sub_text.split("\n\r")

    showWarning("".join(subs[:3]))
    # builder.build(subs)
