from anki.collection import Collection
from aqt import mw
from aqt.operations import QueryOp

from .deck import builders
from .ext import ext, parse_srt
from .ui import ImportDialog, ImportSettings


def importDeck() -> None:
    import_settings = ImportDialog().getSettings()
    if not import_settings:
        return
    builder = builders[import_settings.deck]

    deckname = import_settings.name

    def getSubs(col: Collection, import_settings: ImportSettings):
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
        return subs

    def onSubsSuccess(subs: list[str]):
        builder.build(subs, deckname)

    op = QueryOp(
        parent=mw, op=lambda col: getSubs(col, import_settings), success=onSubsSuccess
    )
    op.with_progress().without_collection().run_in_background()
    # builder.build(subs)


def updateModels() -> None:
    """
    In normal use, if a model has already been added, it remains untouched.
    This function is a manual intervention for the user to update their models
    in case the addon's defined models were updated, or if the user wishes to
    reset changes they had made.
    """
    pass


def updateNotes() -> None:
    """
    For the user to manually update and reset currently used SubtitleTerms notes,
    and their respective source dictionaries.
    """
    pass
