import dataclasses
import json
import pathlib
import re
from collections.abc import Callable, Mapping


@dataclasses.dataclass
class BaseEntry:
    term: str
    gloss: str


class EntryStore(Mapping):
    """
    entry: contstructor
    get_entries: should return a dictionary of entries, or None on failure
    """

    def __init__(
        self,
        identifier: str,
        entry: type[BaseEntry],
        get_entries: Callable[type[BaseEntry], dict[str, BaseEntry]],
    ):
        self.Entry = entry
        self.dirpath = pathlib.Path(__file__).parent.joinpath("data")
        valid_identifier = re.sub(r"\W|^(?=\d)", "_", identifier)
        self.datapath = self.dirpath.joinpath(valid_identifier + ".json")
        self.get_entries = get_entries
        self.cached_db = None

    @property
    def db(self) -> dict[str, BaseEntry]:
        if not self.datapath.exists():
            self.update_cache()
        if not self.cached_db:
            with self.datapath.open(mode="r") as f:
                self.cached_db = dict[str, BaseEntry](
                    {k: self.Entry(*v) for k, v in json.load(f).items()}
                )
        return self.cached_db

    def update_cache(self):
        """
        Attempts to retrieve up-to-date entries and persist them to disk and memory.
        """
        entries = self.get_entries(self.Entry)
        # get_entries should return None on failure so we don't overwrite
        # with blank data.
        if entries:
            self.cached_db = entries
            self.dirpath.mkdir(exist_ok=True)
            with self.datapath.open(mode="w") as f:
                json.dump(
                    {k: dataclasses.astuple(v) for k, v in entries.items()},
                    f,
                    ensure_ascii=False,
                    sort_keys=True,
                    indent=4,
                )

    def __getitem__(self, k):
        return self.db[k]

    def __iter__(self):
        yield from self.db

    def __len__(self):
        return len(self.db)
