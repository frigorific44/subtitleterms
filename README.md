# Subtitle Terms

An Anki plug-in for turning subtitles—or more broadly any text document—into flashcards for language learning. If [FFmpeg](https://ffmpeg.org/download.html) is installed and present in the PATH, subtitles can be extracted by the plug-in, or the plug-in can import from SubRip `.srt` files or other text files.

## Contributing

### Adding Dictionaries

While currently the set of translation dictionaries offered is limited, my hope is to expand the list to provide utility to learners of more languages. The primary dependency for doing so is up-to-date source dictionaries that are machine-parsable and freely available for download. As an example, [CC-CEDICT](https://cc-cedict.org/wiki/) provides a public domain, collaborative, and continually updated dictionary available through a single downloadable file formatted to be parsed and presented by other software. Suggestions of sources for other dictionaries between any two languages can be made by creating an Issue with the 'enhancement' tag.

### Localizing/Translating

While smaller in scope than the Anki platform, SubtitleTerms does support localization, targeting the same locales as available through Anki. Localizations are contained within [localizations.py](src/subtitleterms/i18n/localizations.py). In general, creating a new localization will involve copying the annotated English localization dictionary and modifying the IETF language tag ('en-US') to the target locale, and modifying the dictionary keys with their localization. More detailed guidance will likely be contained within the localization file. As this process requires familiarity with Git and Python in order to make modifications and submit a pull request, contributions in the form of opening an issue with the 'localization' label containing the localizations in the body are also welcome.

## Development

The project is built with [hatching](https://hatch.pypa.io) to serve the unique requirements for distributing an Anki plug-in, while [uv](https://docs.astral.sh/uv/) is still used as the package manager. Use the following command to build the distributable, as well as to vendor packages for use in local development when testing in Anki.

```sh
hatch build -t zipped-directory
```

Currently the conversion of Qt user-interface files into Python is not automated. Changes should only be made to `.ui` files with QtCreator, and Python files generated with the following command:

```sh
uv run pyuic6 -o src/subtitleterms/ui/importdialog.py src/subtitleterms/ui/importdialog.ui
```
