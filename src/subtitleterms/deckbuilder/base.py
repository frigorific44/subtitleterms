import collections
import pathlib

import anki.collection
import genanki
from aqt import mw
from aqt.addons import AddonManager
from aqt.operations import CollectionOp
from htpy import div, h1, hr

from .entrystore import EntryStore


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
        fields: list[str],
    ):
        super().__init__(collection, model, None)
        self.fields = fields
        # GUID is generated on the term only, to allow updating deck information.
        self.guid = genanki.guid_for(self.fields[0])


class BaseDeck:
    fields = ["term", "gloss"]
    template = [
        h1(".hide-rcl-f")["{{term}}"],
        hr,
        div(".hide-rcg-f")["{{gloss}}"],
    ]

    def __init__(self, lang_from, lang_to, db_initialization):
        """
        Args:
        model_id: An integer which should be generated once for the note type and hardcoded.
        name: A unique name.
        db_initialization: A function which returns a dictionary of terms to construct cards on.
        """
        self.lang_from = lang_from
        self.lang_to = lang_to
        self.db_initialization = db_initialization
        self._entrystore = None

    @property
    def name(self) -> str:
        return f"{self.lang_from}_2_{self.lang_to}"

    @property
    def modelname(self) -> str:
        return f"SubtitleTerms {self.name}"

    def model(
        self, collection: anki.collection.Collection
    ) -> anki.collection.NotetypeId:
        modelmanager = collection.models
        notetypeid = modelmanager.id_for_name(self.modelname)

        # Check if the model is in the collection.
        # TODO: Otherwise, might want to check the present model fulfills our needs.
        # TODO: Set an option to update model.
        if not notetypeid:
            newmodel = modelmanager.new(self.modelname)
            for field in self.fields:
                newfield = modelmanager.new_field(field)
                modelmanager.add_field(newmodel, newfield)

            recog_template = modelmanager.new_template("Recognition")
            recog_template["qfmt"] = str(div(".recognition .front")[self.template])
            recog_template["afmt"] = str(div(".recognition .back")[self.template])
            modelmanager.add_template(newmodel, recog_template)

            recol_template = modelmanager.new_template("Recollection")
            recol_template["qfmt"] = str(div(".recollection .front")[self.template])
            recol_template["afmt"] = str(div(".recollection .back")[self.template])
            modelmanager.add_template(newmodel, recol_template)

            newmodel["css"] = get_css("all_lang.css")

            notetypeid = anki.collection.NotetypeId(modelmanager.add_dict(newmodel).id)
            logger.debug(f"Model '{self.modelname}' added: {notetypeid}")

        return notetypeid

    @property
    def Entry(self):
        return collections.namedtuple(self.name, self.fields)

    @property
    def db(self):
        """
        Returns fully-cached read-write safe copy of the term dictionary.
        """
        if not self._entrystore:
            self._entrystore = EntryStore(self.Entry, self.db_initialization)
        return self._entrystore.db

    def build(self, subs: list[str], deckname: str):
        """
        From a list of subtitle lines, constructs a deck.
        """

        def buildOp(col: anki.collection.Collection):
            undo_entry = col.add_custom_undo_entry("SubtitleTerms: Import")

            logger.debug(f"Subtitle count = {len(subs)}")
            segments = self.segment(subs)
            logger.debug(f"Segment count = {len(segments)}")
            entries = self.lookup(segments)
            logger.debug(f"Entry count = {len(entries)}")
            for entry in entries:
                logger.log(9, entry._asdict())
            self.gather(col, entries, deckname)

            return col.merge_undo_entries(undo_entry)

        op = CollectionOp(parent=mw, op=buildOp)
        op.run_in_background()

    def segment(self, subs: list[str]) -> list[str]:
        """
        Segments subtitle lines into possible memorization terms.
        """
        word_set = dict()
        for sub in subs:
            for term in sub.split():
                if term not in word_set:
                    word_set[term] = True
        return list(word_set.keys())

    def lookup(self, segments: list[str]):
        """
        Return segments confirmed to be in the term dictionary.
        """
        to_add = dict()
        entries = []
        for term in segments:
            if term not in self.db:
                for sub_term in self.lookup_fallback(term):
                    if sub_term not in to_add:
                        to_add[sub_term] = True
            elif term not in to_add:
                to_add[term] = True
        for term in to_add:
            entries.append(self.db[term])
        return entries

    def lookup_fallback(self, term: str):
        """
        Return potentionally less-accurate terms found within the database
        instead of a full lookup failure.
        """
        return []

    def gather(self, collection: anki.collection.Collection, entries, deckname: str):
        """
        Construct the deck from confirmed terms.
        """
        model_id = self.model(collection)
        new_deck = collection.decks.new_deck()
        new_deck.name = f"{deckname}"
        result = collection.decks.add_deck(new_deck)
        new_deck_id = anki.collection.DeckId(result.id)
        logger.info(f"Deck added: {new_deck_id}")
        notes = [LangNote(collection, model_id, list(entry)) for entry in entries]
        requests = [
            anki.collection.AddNoteRequest(note, new_deck_id)
            for note in notes
            if not note.fields_check()
        ]

        result_msg = f"{len(requests)} note"
        result_msg += "s" if len(requests) > 1 else ""
        result_msg += " added"
        skipped = len(notes) - len(requests)
        if skipped > 0:
            result_msg += f", {skipped} note"
            result_msg += "s" if skipped > 1 else ""
            result_msg += " skipped"
        result_msg += "."
        logger.info(result_msg)

        collection.add_notes(requests)
        return new_deck
