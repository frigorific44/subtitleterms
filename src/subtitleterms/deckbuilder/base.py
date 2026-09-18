import dataclasses
import pathlib

import anki.collection
from aqt import mw
from aqt.addons import AddonManager
from aqt.operations import CollectionOp
from htpy import div, h1, hr

from ..i18n import _
from .entrystore import BaseEntry, EntryStore

logger = AddonManager.get_logger("subtitleterms")


def get_css(file_name: str) -> str:
    dir_path = pathlib.Path(__file__).parent.joinpath("css")
    file_path = dir_path.joinpath(file_name)
    return file_path.read_text(encoding="utf-8")


class LangNote(anki.collection.Note):
    def __init__(
        self,
        collection: anki.collection.Collection,
        model: anki.collection.NotetypeDict | anki.collection.NotetypeId,
        fields: list,
    ):
        super().__init__(collection, model, None)
        self.fields = [str(field) for field in fields]


class BaseDeck:
    def __init__(self, lang_from, lang_to, entry_init):
        """
        Args:
        lang_from: IETF language tag of the language subtitles are in.
        lang_to: IETF language tag of the language subtitles are translated to.
        entry_init: A function which returns a dictionary of terms to construct cards on.
        """
        self.lang_from = lang_from
        self.lang_to = lang_to
        self.entrystore = EntryStore(self.name, self.Entry, entry_init)

    @property
    def template(self):
        template = [
            h1(".hide-rcl-f")["{{term}}"],
            hr,
            div(".hide-rcg-f")["{{gloss}}"],
        ]
        return template

    @property
    def name(self) -> str:
        return f"{self.lang_from}_2_{self.lang_to}"

    @property
    def modelname(self) -> str:
        return f"SubtitleTerms {self.name}"

    @property
    def Entry(self) -> type[BaseEntry]:
        return BaseEntry

    def model(
        self, collection: anki.collection.Collection
    ) -> anki.collection.NotetypeDict:
        modelmanager = collection.models
        newmodel = modelmanager.new(self.modelname)
        for field in dataclasses.fields(self.Entry):
            newfield = modelmanager.new_field(field.name)
            modelmanager.add_field(newmodel, newfield)

        recog_template = modelmanager.new_template("Recognition")
        recog_template["qfmt"] = str(div(".recognition.front")[self.template])
        recog_template["afmt"] = str(div(".recognition.back")[self.template])
        modelmanager.add_template(newmodel, recog_template)

        recol_template = modelmanager.new_template("Recollection")
        recol_template["qfmt"] = str(div(".recollection.front")[self.template])
        recol_template["afmt"] = str(div(".recollection.back")[self.template])
        modelmanager.add_template(newmodel, recol_template)

        newmodel["css"] = get_css("all_lang.css")
        return newmodel

    def model_id(
        self, collection: anki.collection.Collection
    ) -> anki.collection.NotetypeId:
        modelmanager = collection.models
        notetypeid = modelmanager.id_for_name(self.modelname)

        # Check if the model is in the collection.
        # TODO: Otherwise, might want to check the present model fulfills our needs.
        # TODO: Set an option to update model.
        if not notetypeid:
            newmodel = self.model(collection)
            notetypeid = anki.collection.NotetypeId(modelmanager.add_dict(newmodel).id)
            logger.debug(f"Model '{self.modelname}' added: {notetypeid}")

        return notetypeid

    def build(self, subs: list[str], deckname: str, update_freq: bool):
        """
        From a list of subtitle lines, constructs a deck.
        """

        def buildOp(col: anki.collection.Collection):
            undo_entry = col.add_custom_undo_entry(f"SubtitleTerms: {_('Import')}")

            logger.debug(f"Subtitle count = {len(subs)}")
            segments = self.segment(subs)
            logger.debug(f"Segment count = {len(segments)}")
            entries = self.lookup(segments)
            logger.debug(f"Entry count = {len(entries)}")
            for entry in entries:
                logger.log(9, dataclasses.asdict(entry))
            skipped = self.gather(col, entries, deckname)
            if update_freq:
                self.frequencies(col, skipped)

            return col.merge_undo_entries(undo_entry)

        op = CollectionOp(parent=mw, op=buildOp)
        op.run_in_background()

    def segment(self, subs: list[str]) -> list[str]:
        """
        Segments subtitle lines into possible memorization terms.
        """
        word_set = {}
        for sub in subs:
            for term in sub.split():
                if term not in word_set:
                    word_set[term] = True
        return list(word_set.keys())

    def lookup(self, segments: list[str]) -> list[BaseEntry]:
        """
        Returns matching term dictionary entries.
        """
        # Insertion order should be preserved.
        entries: dict[str, BaseEntry] = {}
        for term in segments:
            if term not in self.entrystore:
                for sub_term in self.lookup_fallback(term):
                    if sub_term not in entries:
                        entries[sub_term] = self.entrystore[sub_term]
                    else:
                        entries[sub_term].frequency += 1
            elif term not in entries:
                entries[term] = self.entrystore[term]
            else:
                entries[term].frequency += 1
        return list(entries.values())

    def lookup_fallback(self, term: str) -> list[str]:
        """
        Return potentionally less-accurate terms found within the database
        instead of a full lookup failure.
        """
        return []

    def gather(
        self,
        collection: anki.collection.Collection,
        entries: list[BaseEntry],
        deckname: str,
    ) -> list[BaseEntry]:
        """
        Construct the deck from confirmed terms.
        """
        model_id = self.model_id(collection)
        new_deck = collection.decks.new_deck()
        new_deck.name = f"{deckname}"
        result = collection.decks.add_deck(new_deck)
        new_deck_id = anki.collection.DeckId(result.id)
        logger.info(f"Deck added: {new_deck_id}")

        requests, skipped = [], []
        for entry in entries:
            note = LangNote(collection, model_id, list(dataclasses.astuple(entry)))
            if not note.fields_check():
                requests.append(anki.collection.AddNoteRequest(note, new_deck_id))
            else:
                skipped.append(entry)

        result_msg = f"{len(requests)} note"
        result_msg += "s" if len(requests) > 1 else ""
        result_msg += " added"
        if len(skipped) > 0:
            result_msg += f", {len(skipped)} note"
            result_msg += "s" if len(skipped) > 1 else ""
            result_msg += " skipped"
        result_msg += "."
        logger.info(result_msg)

        collection.add_notes(requests)
        return skipped

    def frequencies(
        self, collection: anki.collection.Collection, existing: list[BaseEntry]
    ):
        changed_notes = []
        for entry in existing:
            found = collection.find_notes(
                f'"term:{entry.term}" AND "note:{self.modelname}"'
            )
            if len(found) == 0:
                logger.error(f"Skipped note not found: {entry}")
                continue

            if len(found) > 1:
                logger.warning("Multiple notes found.")
            for note_id in found:
                note = collection.get_note(note_id)
                if "frequency" not in note:
                    continue
                try:
                    frequency = 0 if note["frequency"] == "" else int(note["frequency"])
                    note["frequency"] = str(frequency + entry.frequency)
                    changed_notes.append(note)
                except ValueError:
                    logger.error(f"Could not convert frequency: {note['frequency']}")
        collection.update_notes(changed_notes)
