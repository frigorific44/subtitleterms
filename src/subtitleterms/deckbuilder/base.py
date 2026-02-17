import collections

import genanki
from aqt import mw
from anki.collection import DeckManager, DeckId
from htpy import div, h1, hr

from .entrystore import EntryStore
from .models.base import LangModel


class LangNote(genanki.Note):
    # GUID is generated on the term only, to allow updating deck information.
    @property
    def guid(self):
        if self.fields is not None:
            return genanki.guid_for(self.fields[0])
        return super().guid()


class BaseDeck:
    fields = ["term", "gloss"]
    template = [
        h1(".hide-rcl-f")["{{term}}"],
        hr,
        div(".hide-rcg-f")["{{gloss}}"],
    ]

    def __init__(self, model_id, name, db_initialization):
        """
        Args:
        model_id: An integer which should be generated once for the card type and hardcoded.
        name: A unique name.
        db_initialization: A function which returns a dictionary of terms to construct cards on.
        """
        self.model_id = model_id
        self.name = name
        self.db_initialization = db_initialization
        self._entrystore = None

    @property
    def model(self):
        model = LangModel(
            model_id=self.model_id,
            name=self.name,
            fields=self.fields,
            template=self.template,
        )
        return model

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

    def build(self, subs: list[str]):
        """
        From a list of subtitle lines, constructs a deck.
        """
        segments = self.segment(subs)
        entries = self.lookup(segments)
        deck = self.gather(entries)
        self.write(deck)

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

    def gather(self, entries):
        """
        Construct the deck from confirmed terms.
        """
        collection = mw.col
        deckmanager = DeckManager(collection)
        new_deck = deckmanager.new_deck()
        new_deck.name = f"SubtitleTerms::{self.name}"
        result = deckmanager.add_deck(new_deck)
        new_deck_id = DeckId(result.id)
        # new_deck = genanki.Deck(
        #     deck_id=random.randrange(1 << 30, 1 << 31),
        #     name=f"SubtitleTerms::{self.name}",
        # )
        print(f"Notes: {len(entries)}")
        for entry in entries:
            new_note = LangNote(model=self.model, fields=list(entry))
            collection.add_note(new_note, new_deck_id)
        return new_deck

    def write(self, deck):
        genanki.Package(deck).write_to_file("output.apkg")
