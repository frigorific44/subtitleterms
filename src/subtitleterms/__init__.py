import os
import sys

from aqt import mw
from aqt.qt import QAction
from aqt.addons import AddonManager
from aqt.utils import qconnect

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, "vendor")
sys.path.append(vendor_dir)

from .subimport import importDeck  # noqa: E402

# Configure logger.
logger = AddonManager.get_logger("subtitleterms")
LOGLEVEL = os.environ.get("SUBTERMS_LOGLEVEL", "").upper()
if LOGLEVEL.isdigit():
    logger.setLevel(int(LOGLEVEL))
elif LOGLEVEL:
    logger.setLevel(LOGLEVEL)
logger.info(f"SubtitleTerms log level is {logger.getEffectiveLevel()}")

# Create a menu action.
action = QAction("SubtitleTerms: Import", mw)
qconnect(action.triggered, importDeck)
mw.form.menuCol.insertAction(mw.form.menuCol.actions()[-1], action)
