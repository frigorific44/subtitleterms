import pathlib
from dataclasses import dataclass

from anki.collection import Collection
from aqt import mw
from aqt.operations import QueryOp
from aqt.qt import QDialog, QFileDialog
from aqt.utils import showWarning

from ..deck import decks
from . import videoextensions
from ..ext import get_subtitle_streams
from .importdialog import Ui_ImportDialog


@dataclass
class ImportSettings:
    """Class for storing import settings."""

    path: pathlib.Path
    subtitle_stream: int
    deck: str
    name: str


class ImportDialog(QDialog, Ui_ImportDialog):
    file_path: pathlib.Path | None = None

    def __init__(self):
        QDialog.__init__(self, mw)
        self.setupUi(self)
        self.filePushButton.clicked.connect(self.onBrowse)
        self.fileLineEdit.editingFinished.connect(self.onFileEditFinish)
        self.dictionaryComboBox.addItem("-")
        self.dictionaryComboBox.addItems(decks.keys())
        self.exec()

    def onBrowse(self):
        """Handles a browse call with a file dialog and update to fileLineEdit."""
        fileDialog = QFileDialog(self)
        fileDialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if fileDialog.exec():
            filenames = fileDialog.selectedFiles()
            if filenames:
                self.fileLineEdit.setText(filenames[0])
                self.onFileEditFinish()

    def onFileEditFinish(self):
        """Handles a significant update to fileLineEdit."""
        new_file_path = pathlib.Path(self.fileLineEdit.text())
        if (
            self.file_path == new_file_path
            or not new_file_path.exists()
            or not new_file_path.is_file()
        ):
            return
        self.file_path = new_file_path

        # So long as there's no current name, use the file name stem.
        if not self.nameLineEdit.text():
            self.nameLineEdit.setText(self.file_path.stem)
        # If the file has a video extension, asynchronously get its subtitle streams.
        file_extension = self.file_path.suffix[1:]
        if file_extension not in videoextensions.extensions:
            self.subtitleComboBox.setEnabled(False)
            self.subtitleComboBox.clear()
        else:
            # TODO: Could change cursor, but text in combo box is a good indicator for now.
            # mw.app.setOverrideCursor(Qt.CursorShape.BusyCursor)
            def subtitleExtract(col: Collection) -> dict:
                streams = get_subtitle_streams(self.file_path)  # ty:ignore[invalid-argument-type]
                return streams

            def onSubtitleExtractSuccess(streams: dict) -> None:
                self.subtitleComboBox.addItems(streams.values())
                self.subtitleComboBox.setEnabled(True)

            op = QueryOp(
                parent=mw,
                op=subtitleExtract,
                success=onSubtitleExtractSuccess,
            )
            op.without_collection().run_in_background()

    def getSettings(self) -> ImportSettings | None:
        """Get the import settings of the dialog's form."""
        # Cancel
        if not self.result():
            return None
        # File Path
        if not self.file_path:
            showWarning("Please select a valid file.")
            return None
        # Sub Choice
        sub_choice = self.subtitleComboBox.currentIndex()
        if self.subtitleComboBox.count() > 0 and sub_choice < 0:
            showWarning("Please select a subtitle stream.")
            return None
        # Dict Choice
        dict_choice = self.dictionaryComboBox.currentText()
        if dict_choice not in decks:
            showWarning("Please select a dictionary.")
            return None
        # Deck Name
        deck_name = self.nameLineEdit.text()
        if not deck_name:
            showWarning("Please enter a name.")
            return None

        return ImportSettings(self.file_path, sub_choice, dict_choice, deck_name)
