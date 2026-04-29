import dataclasses
import gzip
import re
import unicodedata
from collections import defaultdict

import jieba.posseg
import requests
from aqt.addons import AddonManager
from htpy import Element, div, h1, h2, hr, li, rt, ruby, span, ul

from .base import BaseDeck, BaseEntry

logger = AddonManager.get_logger("subtitleterms")

tones = ["\u0304", "\u0301", "\u030c", "\u0300", "\u200b"]


@dataclasses.dataclass
class HanEntry(BaseEntry):
    pinyin: str


class ZH_Deck(BaseDeck):
    # TODO: ruby should be per character rather than whole term.
    template = [
        h1(".hide-rcl-f")[ruby["{{term}}", rt(".hide-rcg-f")["{{pinyin}}"]]],
        hr,
        div(".hide-rcg-f")["{{gloss}}"],
    ]

    @property
    def Entry(self) -> type[BaseEntry]:
        return HanEntry

    def segment(self, subs: list[str]) -> list[str]:
        word_set = dict()
        for sub in subs:
            for term, tag in jieba.posseg.cut(sub):
                if tag not in set(["x"]) and not term.isdigit():
                    if term not in word_set:
                        word_set[term] = True
        return list(word_set)

    def lookup_fallback(self, term: str):
        # Calculate combinations of substrings contained in the dictionary.
        def defined_combinations(runes: str) -> list[list[str]]:
            if runes == "":
                return [[]]
            combinations = []
            for i in range(len(runes)):
                curr = runes[: i + 1]
                if curr in self.entrystore:
                    remainder = defined_combinations(runes[i + 1 :])
                    for r_combo in remainder:
                        combinations.append([curr, *r_combo])
            # If all failed, the common denominator being the first character
            # means excluding it may give at least partial combinations.
            if len(combinations) == 0:
                remainder = defined_combinations(runes[i + 1 :])
                combinations.extend(remainder)
                logger.info(
                    f"No matches found for substring '{runes}' of term '{term}'."
                )
            return combinations

        # Longer substrings are favored.
        def combination_metric(substring_combination: list[str]) -> int:
            return sum([len(w) ** 2 for w in substring_combination])

        all_combinations = defined_combinations(term)
        if not all_combinations:
            return []
        best_combination = max(
            [combination_metric(w_combo) for w_combo in all_combinations]
        )
        best_combinations_flat = [
            s
            for combination in all_combinations
            if combination_metric(combination) == best_combination
            for s in combination
        ]
        return best_combinations_flat


def zh_initialize(char_set) -> dict[str, HanEntry]:
    # Download dictionary text into string
    req = requests.get(
        "https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz"
    )
    dict_text = gzip.decompress(req.content).decode(encoding="utf-8")
    # Entries are not one-to-one with the representative character,
    # so we deal with that first.
    ce_dict: dict[str, list[tuple[str, list[Element], str]]] = defaultdict(list)
    for line in dict_text.split("\n"):
        try:
            if line.startswith("#"):
                continue
            stripped_line = line.strip()
            toned_line = tone_numbers_to_marks(stripped_line)
            sense_boundary = toned_line.strip("/").split("/")
            senses = sense_boundary[1:]
            pinyin_boundary = sense_boundary[0].split("[")
            pinyin = pinyin_boundary[-1].rstrip("] ")
            term_boundary = pinyin_boundary[0].split()
            traditional = term_boundary[0]
            simplified = term_boundary[1]
            if char_set == "traditional":
                key_char = traditional
                other_char = simplified
            else:
                key_char = simplified
                other_char = traditional
            gloss = [
                h2[span[other_char], " ", span[pinyin]],
                ul[(li[sense] for sense in senses)],
            ]
            intermediate = (key_char, gloss, pinyin)
            ce_dict[key_char].append(intermediate)
        except IndexError as err:
            logger.error(f"Unhandled line: {line}")
            logger.error(err)
    return {k: reconcile_entries(v) for k, v in ce_dict.items()}


def tone_numbers_to_marks(s: str) -> str:
    brackets_exp = re.compile(r"(?<=\[).+?(?=\])")
    syllable_exp = re.compile(r"[a-z:]+[1-5](?!\d)", re.IGNORECASE)
    tone_exp = re.compile(r"(a|e|o(?=u)|[oiuü](?=$|n))", re.IGNORECASE)

    def pinyin_repl(match: re.Match) -> str:
        syllable = match[0]
        if len(syllable) < 1 or not syllable[-1].isdigit():
            logger.debug(syllable)
            return syllable
        tone_num = int(syllable[-1]) - 1
        if tone_num < 0 or tone_num >= len(tones):
            logger.debug(syllable)
            return syllable
        tone = tones[tone_num]
        syllable = syllable[:-1]
        syllable = syllable.replace("u:", "ü")
        syllable = tone_exp.sub(r"\1" + tone, syllable, 1)
        return syllable

    def syllable_repl(match: re.Match) -> str:
        return syllable_exp.sub(pinyin_repl, match[0])

    # Give pinyin number-toned syllables diacritics instead.
    return unicodedata.normalize("NFC", brackets_exp.sub(syllable_repl, s))


def reconcile_entries(intermediaries: list[tuple[str, list[Element], str]]) -> HanEntry:
    # Sort by pinyin, with proper nouns last.
    intermediaries = sorted(intermediaries, key=lambda t_entry: t_entry[2].swapcase())

    # Set the pinyin if it's the same (barring capitalization) for all entries.
    all_pinyin = intermediaries[0][2]
    for intermediary in intermediaries[1:]:
        if all_pinyin.lower() != intermediary[2].lower():
            all_pinyin = ""
            break

    # Set gloss.
    if len(intermediaries) == 1:
        gloss = str(div[intermediaries[0][1][1]])
    else:
        gloss = str(div[[intermediary[1] for intermediary in intermediaries]])
    return HanEntry(intermediaries[0][0], gloss, all_pinyin)
