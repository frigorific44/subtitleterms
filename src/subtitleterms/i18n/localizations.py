from collections import defaultdict

from anki.lang import lang_to_disk_lang

localizations = {
    # en-US is treated as the fallback for any missing localizations.
    "en-US": {
        ### Interface ###
        ## Toolbar ##
        # Button under "File" which opens a dialog to generate a deck from a video or text file.
        "toolbar_import": "Import",
        # Button under "Tools" which updates notetypes/models provided by this add-on.
        "toolbar_update_models": "Update Note Types",
        # Button under "Tools" which updates notes of types provided by this add-on.
        "toolbar_update_notes": "Update Notes",
        #
        ## Dialog ##
        # The file selected from which the deck will be generated.
        "dialog_file": "File",
        # Button which opens a file browser.
        "dialog_browse": "Browse",
        # The name of the deck to be created.
        "dialog_deck_name": "Deck Name",
        # Refers to choosing a subtitle stream parsed from the file, if a video.
        "dialog_subtitle": "Subtitle",
        # Refers to choosing a the bilingual/translation dictionary.
        "dialog_dictionary": "Dictionary",
        #
        ### Languages ###
        "en": "English",
        "zh-Hans": "Chinese (Simplified)",
        "zh-Hant": "Chinese (Traditional)",
    },
    "af-ZA": {},
    "ms-MY": {},
    "ca-ES": {},
    "da-DK": {},
    "de-DE": {},
    "et-EE": {},
    "en-GB": {},
    "es-ES": {},
    "eo-UY": {},
    "eu-ES": {},
    "fr-FR": {},
    "gl-ES": {},
    "hr-HR": {},
    "it-IT": {},
    "jbo-EN": {},
    "oc-FR": {},
    "kk-KZ": {},
    "hu-HU": {},
    "nl-NL": {},
    "nb-NO": {},
    "pl-PL": {},
    "pt-BR": {},
    "pt-PT": {},
    "ro-RO": {},
    "sk-SK": {},
    "sl-SI": {},
    "fi-FI": {},
    "sv-SE": {},
    "vi-VN": {},
    "tr-TR": {},
    "zh-CN": {},
    "ja-JP": {},
    "zh-TW": {},
    "ko-KR": {},
    "cs-CZ": {},
    "el-GR": {},
    "bg-BG": {},
    "mn-MN": {},
    "ru-RU": {},
    "sr-SP": {},
    "uk-UA": {},
    "hy-AM": {},
    "he-IL": {},
    "yi": {},
    "ar-SA": {},
    "fa-IR": {},
    "th-TH": {},
    "la-LA": {},
    "ga-IE": {},
    "be-BY": {},
    "or-OR": {},
    "tl": {},
    "ug": {},
    "uz-UZ": {},
}
safe_localizations = defaultdict(dict)
for k, v in localizations.items():
    safe_localizations[lang_to_disk_lang(k)] = v
