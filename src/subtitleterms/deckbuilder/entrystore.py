from collections.abc import Mapping
import json
import pathlib


class EntryStore(Mapping):
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
            self.cached_db = self.get_entries(self.Entry)
            if self.cached_db:
                self.dirpath.mkdir(exist_ok=True)
                with self.datapath.open(mode="w") as f:
                    json.dump(
                        self.cached_db, f, ensure_ascii=False, sort_keys=True, indent=4
                    )
        else:
            with self.datapath.open(mode="r") as f:
                self.cached_db = {k: self.Entry(*v) for k, v in json.load(f).items()}
        return self.cached_db

    def refresh(self):
        """
        Clears the cached data and reconstructs the EntryStore.
        """
        if self.datapath.exists():
            self.datapath.unlink()
        self.cached_db = None
        self.db

    def __getitem__(self, k):
        return self.db[k]

    def __iter__(self):
        yield from self.db

    def __len__(self):
        return len(self.db)
