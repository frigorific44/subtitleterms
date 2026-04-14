# SubtitleTerms

An Anki plug-in for turning subtitles—or more broadly any text document—into flashcards for language learning. Once using SubtitleTerms cards, you can learn a language through your show of choice and generate cards episode by episode, adding newly encountered terms to your repoitoire as you gradually develop mastery over the language.

### Currently Supported Language Pairs

- Chinese (Simplified) → English
- Chinese (Traditional) → English

## Installation

The plug-in can be installed through the normal means by using the in-app plug-in search, or copying the code:

XXXXXX

To make full use of the plug-in, [FFmpeg](https://ffmpeg.org/download.html) must be installed and present on the PATH. FFmpeg is a free and open-source tool for handling multimedia files, and is used to extract subtitles from videos. Many guides for installing FFmpeg and adding it to your PATH are available. If you don't wish to install FFmpeg or are unable to, subtitles can be extracted into a `.srt` (SubRip Text) formatted file with another tool, and imported with SubtitleTerms from the text file.

## Usage

### Creating Decks

The dialog to create a deck can be brought up with `File > SubtitleTerms: Import` in the toolbar.

- **File**: The file from which cards will be generated, which can either by a video container or text file.

- **Deck Name**: The file name will be inserted for convenience, but this can be edited.

- **Subtitle**: If the file selected is a video container with subtitles, this will be a drop-down list from which the relevant subtitle stream can be selected. Otherwise, this option is irrelevant.

- **Dictionary**: A dropdown containing the supported translation/bilingual dictionaries of SubtitleTerms. For expanding this support, see [Contributing](#contributing). The language on the left will be the language of the subtitles/text which you're trying to learn, and the language on the right is the language terms will be translated to.

On first use, it may take some time as the relevant dictionary is downloaded, in addition to the other processes that allow the plug-in to work, so please be patient.

#### Subtitled Videos

When a video file is selected in the import dialog, SubtitleTerms will attempt to glean the subtitles available, and the relevant one can be selected from the dropdown. As per [Installation](#installation), this is reliant upon FFmpeg being installed and in the PATH. Depending on how the subtitles are stored, such as if the subtitle streams are stored as bitmap images, it may not be possible for FFmpeg to extract the text.

Depending on the video selected, it can take a long time to extract the subtitles. This is a process bounded by your own hardware, so please be patient.

#### Text Files

For text files, `.srt` (SubRip Text) is specifically supported so as to only parse the subtitle text and not the timestamp information for terms to create cards from. Other text files can also be selected, but will be parsed whole as generic text. 

### Updating

There are two actions under `Tools` in the toolbar: `SubtitleTerms: Update Note Types` and `Subtitle Terms: Update Notes`. 

`Update Note Types` will overwrite card styling and formatting as well as add missing fields, while `Update Notes` will update the source dictionaries and overwrite fields. This can be useful to ensure your notes are up to date with regards to the plugin or the source dictionaries from which the glosses are derived, in addition to being able to revert changes you may have made.

As `Update Notes` downloads new copies of translation dictionaries relevant to the note types you're using, this can take some time depending on your connection speeds, so please be patient.

#### Converting Existing Cards

Updating notes and note types is done by name, which allows for the possibility of converting pre-existing notes. To do so, you at least need to know the name of the note type you're targeting.

In order to get the note type name used by SubtitleTerms, importing to generate some temporary cards is the easiest way. Otherwise, the format is `SubtitleTerms {lang_from}_2_{lang_to}`, where `{lang_from}` and `{lang_to}` are the IETF formatted language tags for the two languages, such that Chinese (Simplified) to English would be `SubtitleTerms zh-Hans_2_en`.

Delete any temporary cards and note types you created as suggested above. Then, rename the note type for the cards you wish to convert to the name you've gathered in the methods above. Then, rename the primary field to `terms`.

Now you should be able to activate `Tools > SubtitleTerms: Update Note Types` and `Tools > SubtitleTerms: Update Notes` in that order to have your notes be fully updated. You may need to go back and delete redudant fields or edit card templates to use fields you'd created personally, but everything SubtitleTerms needs should now be present.

## Contributing

### Adding Dictionaries

While the current set of translation dictionaries offered is limited, my hope is to expand the list to provide utility to learners of more languages. The primary dependency for doing so is up-to-date source dictionaries that are machine-parsable and freely available for download. As an example, [CC-CEDICT](https://cc-cedict.org/wiki/) provides a public domain, collaborative, and continually updated dictionary available through a single downloadable file formatted to be parsed and presented by other software. Suggestions of sources for other dictionaries between any two languages can be made by creating an Issue with the 'enhancement' tag.

### Localizing/Translating

While smaller in scope than the Anki platform, SubtitleTerms does support localization, targeting the same locales as available through Anki. Localizations are contained within [localizations.py](src/subtitleterms/i18n/localizations.py). In general, creating a new localization will involve copying the annotated English localization dictionary and modifying the language tag ('en-US') to the target locale, and modifying the dictionary keys with their localization. More detailed guidance will likely be contained within the localization file. As this process requires familiarity with Git and Python in order to make modifications and submit a pull request, contributions in the form of opening an issue with the 'localization' label containing the localizations in the body are also welcome.

## Development

The project is built with [hatching](https://hatch.pypa.io) to serve the unique requirements for distributing an Anki plug-in, while [uv](https://docs.astral.sh/uv/) is still used as the package manager. Use the following command to build the distributable, as well as to vendor packages for use in local development when testing in Anki.

```sh
hatch build -t zipped-directory
```

Currently the conversion of Qt user-interface files into Python is not automated. Changes should only be made to `.ui` files with QtCreator, and Python files generated with the following command:

```sh
uv run pyuic6 -o src/subtitleterms/ui/importdialog.py src/subtitleterms/ui/importdialog.ui
```
