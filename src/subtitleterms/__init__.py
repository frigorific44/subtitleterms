import os
import sys

from aqt import mw
from aqt.qt import QAction
from aqt.utils import qconnect

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, "vendor")
sys.path.append(vendor_dir)

from .subimport import importDeck  # noqa: E402

# Create a menu action.
action = QAction("SubtitleTerms: Import", mw)
qconnect(action.triggered, importDeck)
mw.form.menuCol.insertAction(mw.form.menuCol.actions()[-1], action)
