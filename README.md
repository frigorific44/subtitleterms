# Subtitle Terms

An Anki plug-in for turning subtitles, or more broadly any text document, into flashcards for language learning. If [FFmpeg](https://ffmpeg.org/download.html) is installed and present in the PATH, subtitles can be extracted by the plug-in, or the plug-in can import from SubRip `.srt` files or other text files.

## Development

The project is built with [hatching](https://hatch.pypa.io) to serve the unique requirements for distributing an Anki plug-in, while [uv](https://docs.astral.sh/uv/) is still used as the package manager. Use the following command to build the distributable, as well as to vendor packages for use in local development when testing in Anki.

```sh
hatch build -t zipped-directory
```

Currently the conversion of Qt user-interface files into Python is not automated. Changes should only be made to `.ui` files with QtCreator, and Python files generated with the following command:

```sh
uv run pyuic6 -o src/subtitleterms/ui/importdialog.py src/subtitleterms/ui/importdialog.ui
```