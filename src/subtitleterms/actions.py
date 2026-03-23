from anki.collection import Collection
from aqt import mw
from aqt.addons import AddonManager
from aqt.operations import CollectionOp, QueryOp

from .builders import builders
from .ext import ext, parse_srt
from .i18n import localization
from .ui import ImportDialog, ImportSettings

logger = AddonManager.get_logger("subtitleterms")


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


# TODO: Add ability to select which models get updated.
# Maybe add button on note type view, if possible?
# Above probably better in addition to below.
def updateModels() -> None:
    """
    In normal use, if a model has already been added, it remains untouched.
    This function is a manual intervention for the user to update their models
    in case the addon's defined models were updated, or if the user wishes to
    reset changes they had made.
    """

    def updateModelsOp(collection: Collection):
        undo_entry = collection.add_custom_undo_entry(
            f"SubtitleTerms: {localization['toolbar_update_models']}"
        )
        for builder in builders.values():
            modelmanager = collection.models
            notetypeid = modelmanager.id_for_name(builder.modelname)
            # Update model if present.
            if notetypeid:
                model = modelmanager.get(notetypeid)
                if model:
                    logger.log(
                        9,
                        f"Model '{builder.modelname}' before: {model}",
                    )

                    reference = builder.model(collection)
                    model["css"] = reference["css"]
                    # TODO: Update fields and templates in accordance with the model.
                    modelmanager.update_dict(model)

                    logger.log(
                        9,
                        f"Model '{builder.modelname}' after: {modelmanager.get(notetypeid)}",
                    )

        # TODO: Confirmation of what was updated would be nice.
        return collection.merge_undo_entries(undo_entry)

    op = CollectionOp(parent=mw, op=updateModelsOp)
    op.run_in_background()


def updateNotes() -> None:
    """
    For the user to manually update and reset currently used SubtitleTerms notes,
    and their respective source dictionaries.
    """
    pass
