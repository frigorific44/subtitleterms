from collections.abc import Mapping
import json
import pathlib


# TODO: Enforce types (add typing)
class EntryStore(Mapping):
    """
    entry: contstructor
    get_entries: should return a dictionary of entries, or None on failure
    """

    def __init__(self, entry, get_entries):
        self.Entry = entry
        self.dirpath = pathlib.Path(__file__).parent.joinpath("data")
        self.datapath = self.dirpath.joinpath(entry.__name__ + ".json")
        self.get_entries = get_entries
        self.cached_db = None

    @property
    def db(self):
        if self.cached_db:
            return self.cached_db
        if not self.datapath.exists():
            self.update_cache()
        else:
            with self.datapath.open(mode="r") as f:
                self.cached_db = {k: self.Entry(*v) for k, v in json.load(f).items()}
        return self.cached_db

    def update_cache(self):
        """
        Attemps to retrieve up-to-date entries and persist them to disk and memory.
        """
        entries = self.get_entries(self.Entry)
        # get_entries should return None on failure so we don't overwrite
        # with blank data.
        if entries:
            self.cached_db = entries
            self.dirpath.mkdir(exist_ok=True)
            with self.datapath.open(mode="w") as f:
                json.dump(entries, f, ensure_ascii=False, sort_keys=True, indent=4)

    def __getitem__(self, k):
        return self.db[k]

    def __iter__(self):
        yield from self.db

    def __len__(self):
        return len(self.db)
