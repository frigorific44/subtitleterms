from subtitleterms.deckbuilder.base import BaseDeck
from subtitleterms.deckbuilder.entrystore import BaseEntry


def base_init():
    return {"A": BaseEntry("A", "This is A.", 1), "B": BaseEntry("B", "This is B.", 1)}


base_deck = BaseDeck("from", "to", base_init)


def test_lookup_frequency_counts():
    answer = base_deck.lookup(["A", "B", "B", "A", "B", "C"])
    counts = {entry.term: entry.frequency for entry in answer}
    assert counts["A"] == 2
    assert counts["B"] == 3
    assert "C" not in counts
