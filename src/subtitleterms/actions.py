import dataclasses

from anki.collection import Collection
from aqt import mw
from aqt.addons import AddonManager
from aqt.operations import CollectionOp, QueryOp, ResultWithChanges
from aqt.utils import showText

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
def updateModels() -> None:
    """
    In normal use, if a model has already been added, it remains untouched.
    This function is a manual intervention for the user to update their models
    in case the addon's defined models were updated, or if the user wishes to
    reset changes they had made.
    """

    def updateModelsOp(collection: Collection, log: list[str]):
        undo_entry = collection.add_custom_undo_entry(
            f"SubtitleTerms: {localization['toolbar_update_models']}"
        )
        for builder in builders.values():
            modelmanager = collection.models
            # Update only if model is present.
            notetypeid = modelmanager.id_for_name(builder.modelname)
            if not notetypeid:
                continue
            model = modelmanager.get(notetypeid)
            if not model:
                continue
            model_log = [f"\n{model['name']}"]

            ref = builder.model(collection)

            # Update CSS
            if model["css"] != ref["css"]:
                model["css"] = ref["css"]
                model_log.append(" - CSS updated")

            # Update templates.
            # TODO: Something less manual than this, but I've been burned before.
            for i in range(len(ref["tmpls"])):
                for j in range(len(model["tmpls"])):
                    if ref["tmpls"][i]["name"] == model["tmpls"][j]["name"]:
                        if model["tmpls"][j]["qfmt"] != ref["tmpls"][i]["qfmt"]:
                            model["tmpls"][j]["qfmt"] = ref["tmpls"][i]["qfmt"]
                            model_log.append(
                                f' - "{ref["tmpls"][i]["name"]}" qfmt updated'
                            )
                        if model["tmpls"][j]["afmt"] != ref["tmpls"][i]["afmt"]:
                            model["tmpls"][j]["afmt"] = ref["tmpls"][i]["afmt"]
                            model_log.append(
                                f' - "{ref["tmpls"][i]["name"]}" afmt updated'
                            )

            # Add missing fields.
            for field_name in set(modelmanager.field_names(ref)) - set(
                modelmanager.field_names(model)
            ):
                missing_field = modelmanager.new_field(field_name)
                modelmanager.add_field(model, missing_field)
                model_log.append(f' - field "{field_name}" added')

            if len(model_log) == 1:
                model_log.append(" - No properties updated")
            log.extend(model_log)
            modelmanager.update_dict(model)

        return collection.merge_undo_entries(undo_entry)

    def updateModelsSuccess(result: ResultWithChanges, log: list[str]):
        log_str = "\n".join(log)
        showText(log_str, plain_text_edit=True)

    log = ["SubtitleTerms", "\nModels Updated:"]
    op = CollectionOp(parent=mw, op=lambda col: updateModelsOp(col, log))
    op.success(lambda result: updateModelsSuccess(result, log)).run_in_background()


def updateNotes() -> None:
    """
    For the user to manually update and reset currently used SubtitleTerms notes,
    and their respective source dictionaries.
    """

    def updateNotesOp(collection: Collection, log: list[str]):
        undo_entry = collection.add_custom_undo_entry(
            f"SubtitleTerms: {localization['toolbar_update_notes']}"
        )
        for builder in builders.values():
            modelmanager = collection.models
            notetypeid = modelmanager.id_for_name(builder.modelname)
            # Update only if model is present.
            if not notetypeid:
                continue
            builder.entrystore.update_cache()
            log.append(f'\n"{builder.modelname}" entries refreshed.')

            changed_notes = []
            for noteid in modelmanager.nids(notetypeid):
                note = collection.get_note(noteid)

                logger.log(9, f"Note to update: {note.fields}")

                index = "term"
                if index in note:
                    note_log = [f"\n{note[index]}"]
                    if note[index] in builder.entrystore:
                        entry = builder.entrystore[note[index]]
                        for field_key, field_val in dataclasses.asdict(entry).items():
                            if field_key in note and note[field_key] != field_val:
                                note[field_key] = field_val
                                note_log.append(f' - Field "{field_key}" updated')
                    else:
                        note_log.append(" - Term not found in dictionary")
                    if len(note_log) > 1:
                        log.extend(note_log)

                    changed_notes.append(note)
            collection.update_notes(changed_notes)

        return collection.merge_undo_entries(undo_entry)

    def updateNotesSuccess(result: ResultWithChanges, log: list[str]):
        log_str = "\n".join(log)
        showText(log_str, plain_text_edit=True)

    log = ["SubtitleTerms", "\nNotes Updated:"]
    op = CollectionOp(parent=mw, op=lambda col: updateNotesOp(col, log))
    op.success(lambda result: updateNotesSuccess(result, log)).run_in_background()
