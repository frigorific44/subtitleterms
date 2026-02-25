import os
import sys

from aqt import mw
from aqt.qt import QAction
from aqt.utils import qconnect, showWarning

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, "vendor")
sys.path.append(vendor_dir)

from .deck import builders  # noqa: E402
from .ui import ImportDialog  # noqa: E402
from .ext import ext, parse_srt  # noqa: E402


def importDeck() -> None:
    # get the number of cards in the current collection, which is stored in
    # the main window
    # cardCount = mw.col.card_count()
    # show a message box
    # showInfo("Card count: %d" % cardCount)
    import_settings = ImportDialog().getSettings()
    if not import_settings:
        return
    builder = builders[import_settings.deck]
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

    showWarning("".join(subs[:3]))
    # builder.build(subs)


# create a new menu item, "test"
action = QAction("AnkiSub: Import from Subbed", mw)
# set it to call testFunction when it's clicked
qconnect(action.triggered, importDeck)
mw.form.menuCol.insertAction(mw.form.menuCol.actions()[-1], action)
