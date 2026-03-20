import os
import sys

from aqt import mw
from aqt.addons import AddonManager
from aqt.qt import QAction
from aqt.utils import qconnect

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, "vendor")
sys.path.append(vendor_dir)

from .actions import importDeck, updateModels, updateNotes  # noqa: E402
from .i18n import localization  # noqa: E402

# Configure logger.
logger = AddonManager.get_logger("subtitleterms")
LOGLEVEL = os.environ.get("SUBTERMS_LOGLEVEL", "").upper()
if LOGLEVEL.isdigit():
    logger.setLevel(int(LOGLEVEL))
elif LOGLEVEL:
    logger.setLevel(LOGLEVEL)
logger.info(f"SubtitleTerms log level is {logger.getEffectiveLevel()}")

# Create menu actions.
actionImport = QAction(f"SubtitleTerms: {localization['toolbar_import']}", mw)
qconnect(actionImport.triggered, importDeck)
mw.form.menuCol.insertAction(mw.form.menuCol.actions()[-1], actionImport)

actionModels = QAction(f"SubtitleTerms: {localization['toolbar_update_models']}", mw)
qconnect(actionModels.triggered, updateModels)
mw.form.menuTools.addAction(actionModels)

actionNotes = QAction(f"SubtitleTerms: {localization['toolbar_update_notes']}")
qconnect(actionNotes.triggered, updateNotes)
mw.form.menuTools.addAction(actionNotes)
