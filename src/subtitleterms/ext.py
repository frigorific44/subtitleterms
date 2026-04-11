import itertools
import re
import subprocess
import shutil
import pathlib
from aqt.addons import AddonManager

logger = AddonManager.get_logger("subtitleterms")


# TODO: Find a way to remove the FFmpeg dependency.
def get_subtitle_streams(input_path: pathlib.Path) -> dict:
    if not shutil.which("ffprobe"):
        logger.error(
            "FFmpeg:ffprobe is not found in PATH. Install FFmpeg or use a separate utility to extract subtitles."
        )
    probe_args = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "s",
        "-show_entries",
        "stream=index:stream_tags=title",
        "-of",
        "csv=p=0",
        input_path,
    ]
    probe_p = subprocess.run(probe_args, encoding="utf-8", capture_output=True)
    # ffprobe does not respect argument order,
    # but the output ordering is hoped to be stable.
    sub_stream_dict = {
        line.split(",", maxsplit=1)[0]: line.split(",", maxsplit=1)[1]
        for line in probe_p.stdout.split("\n")
        if line != ""
    }
    return sub_stream_dict


def ext(input_path: pathlib.Path, stream_n: int) -> str:
    if not shutil.which("ffmpeg"):
        logger.error(
            "FFmpeg is not found in PATH. Install FFmpeg or use a separate utility to extract subtitles."
        )
    ff_args = [
        "ffmpeg",
        "-i",
        input_path,
        "-map",
        f"0:s:{stream_n}",
        "-loglevel",
        "quiet",
        "-f",
        "srt",
        "-",
    ]
    ff_p = subprocess.run(ff_args, encoding="utf-8", capture_output=True)
    return ff_p.stdout


def parse_srt(sub_text: str) -> list[str]:
    """
    Parse a string containing SubRip formatted subtitles and return the subtitle text.
    """
    timestammp_exp = re.compile(r"\d\d:\d\d:\d\d,\d\d\d --> \d\d:\d\d:\d\d,\d\d\d")
    subtitle_lines = []
    for k, group in itertools.groupby(sub_text.splitlines(), key=bool):
        # If grouped on Falsey value (empty strings), skip.
        if not k:
            continue
        lines = list(group)
        # Should be strictly increasing starting from 1,
        # but we'll be generous so as to not lose data.
        if not lines[0].strip().isdigit():
            logger.warning(f"Malformed subtitle, index missing: {lines}")
            continue
        if not timestammp_exp.fullmatch(lines[1].strip()):
            logger.warning(f"Malformed subtitle, incorrect timestamp: {lines}")
        else:
            subtitle_lines.extend(lines[2:])
    return subtitle_lines
