import argparse
import pathlib

from . import deck, ext


def cli():
    parser = argparse.ArgumentParser(
        prog="subtitleterms",
        description="Build Anki decks from subtitles for Chinese language-learning.",
    )
    subparsers = parser.add_subparsers(
        required=True, dest="cmd", help="one of the subcommands must be provided"
    )

    parser_ext = subparsers.add_parser(
        "ext", help="extract subtitles from a video file"
    )
    parser_ext.add_argument(
        "-i", "--input", required=True, help="video file to extract subtitle from"
    )
    parser_ext.add_argument(
        "-o",
        "--output",
        help="output file to write subtitles to if provided, otherwise they're written to stdout",
    )

    parser_dec = subparsers.add_parser(
        "dec", help="generate an Anki deck from subtitles."
    )
    parser_dec.add_argument(
        "-i",
        "--input",
        required=True,
        help="either an .srt file or a video file with a text subtitle stream",
    )
    parser_dec.add_argument("-n", "--name", required=True, help="the name of the deck")

    args = parser.parse_args()
    # print(args)
    if args.cmd == "ext":
        ext_command(parser_ext, args)
    elif args.cmd == "dec":
        dec_command(parser_dec, args)


def ext_command(parser, args):
    input_path = pathlib.Path(args.input)
    if not input_path.is_file():
        parser.print_usage()
        print("Input to extract from is not a file.")
        return
    subs = ext.ext(
        input_path, list_prompt(list(ext.get_subtitle_streams(input_path).values()))
    )
    if args.output:
        output_path = pathlib.Path(args.output)
        output_path.write_text(subs, encoding="utf-8")
    else:
        print(subs)


def list_prompt(prompt_list):
    for i in range(len(prompt_list)):
        print(f"{i}: {prompt_list[i]}")
    chosen = -1
    while chosen < 0 or chosen >= len(prompt_list):
        input_str = input(f"Choose (0 - {len(prompt_list) - 1}): ")
        try:
            chosen = int(input_str)
        except ValueError:
            pass
    return chosen


def dec_command(parser, args):
    input_path = pathlib.Path(args.input)
    if not input_path.is_file():
        parser.print_usage()
        print("Input is not a file.")
        return
    if args.name == "":
        parser.print_usage()
        print("Deck name cannot be an empty string.")
        return
    if input_path.suffix == ".srt":
        sub_text = input_path.read_text(encoding="utf-8")
    else:
        sub_text = ext.ext(
            input_path, list_prompt(list(ext.get_subtitle_streams(input_path).values()))
        )
    subs = ext.parse_srt(sub_text)
    deck_choices = list(deck.builders.keys())
    deck_choice = list_prompt(deck_choices)
    deck.builders[deck_choices[deck_choice]].build(subs)


if __name__ == "__main__":
    cli()
