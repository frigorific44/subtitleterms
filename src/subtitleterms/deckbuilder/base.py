import collections

import anki.collection
import genanki
from aqt import mw
from aqt.operations import CollectionOp
from htpy import div, h1, hr

from .entrystore import EntryStore

lang_css = """
.card {
    font-family: sans-serif;
    font-size: 24px;
    line-height: 1.5;
    text-align: center;
}

hr {
    background-color: #000000;
    height: 2px;
    margin: 0;
}

h1 {
    font-size: 36px;
}

.gloss h2 {
    font-size: 24px;
    text-decoration-line: underline;
    text-decoration-thickness: 2px;
    text-underline-offset: 0.5em;
    margin: 0;
}

.gloss p {
    margin: 0;
    margin-top: 0.5em;
}

.recognition.front .hide-rcg-f {
    opacity: 0;
}

.recognition.back .hide-rcg-b {
    opacity: 0;
}

.recollection.front .hide-rcl-f {
    opacity: 0;
}

.recollection.back .hide-rcl-b {
    opacity: 0;
}
"""


class LangNote(anki.collection.Note):
    def __init__(
        self,
        collection: anki.collection.Collection,
        model: anki.collection.NotetypeDict | anki.collection.NotetypeId,
        fields: list[str],
    ):
        super().__init__(collection, model, None)
        # GUID is generated on the term only, to allow updating deck information.
        self.guid = genanki.guid_for(self.fields[0])


class BaseDeck:
    fields = ["term", "gloss"]
    template = [
        h1(".hide-rcl-f")["{{term}}"],
        hr,
        div(".hide-rcg-f")["{{gloss}}"],
    ]

    def __init__(self, model_id: int, name, db_initialization):
        """
        Args:
        model_id: An integer which should be generated once for the note type and hardcoded.
        name: A unique name.
        db_initialization: A function which returns a dictionary of terms to construct cards on.
        """
        self.model_id = model_id
        self.name = name
        self.db_initialization = db_initialization
        self._entrystore = None
        self.model_id_cached = False

    @property
    def model(self) -> anki.collection.NotetypeId:
        notetypeid = anki.collection.NotetypeId(self.model_id)
        # Cached means we've already checked or added the model to the collection.
        if self.model_id_cached:
            notetypeid
        modelmanager = anki.collection.ModelManager(mw.col)

        # Check if the model is in the collection.
        # TODO: Otherwise, might want to check the present model fulfills our needs.
        # TODO: Set an option to update model.
        if not modelmanager.get(notetypeid):
            newmodel = modelmanager.new(self.name)
            newmodel["id"] = notetypeid
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

            newmodel["css"] = lang_css

            modelmanager.add_dict(newmodel)

        self.model_id_cached = True
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

            segments = self.segment(subs)
            entries = self.lookup(segments)
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
        new_deck = collection.decks.new_deck()
        new_deck.name = f"SubtitleTerms::{deckname}"
        result = collection.decks.add_deck(new_deck)
        new_deck_id = anki.collection.DeckId(result.id)
        print(f"Notes: {len(entries)}")
        notes = [
            anki.collection.AddNoteRequest(
                LangNote(collection, self.model, list(entry)), new_deck_id
            )
            for entry in entries
        ]
        collection.add_notes(notes)
        return new_deck
