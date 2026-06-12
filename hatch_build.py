import shutil
import subprocess
import tarfile
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    @property
    def build_test(self):
        return self.config.get("build-test-directory") or self.metadata.name + "test"

    def clean(self, versions):
        self.uninstall_vendors()
        self.clean_dist()

    def initialize(self, version, build_data):
        self.install_vendors()

    def finalize(self, version, build_data, artifact_path):
        self.tar_to_zip(artifact_path)

    def install_vendors(self):
        dependencies = self.metadata.core.dependencies
        ignore = self.config["ignore-dependencies"]
        vendor_dir = self.config["vendor-directory"]
        vendor = [p for p in dependencies if all([ig not in p for ig in ignore])]
        print(" ".join(vendor))
        if not shutil.which("uv"):
            print("uv is not found in PATH.")
        uv_args = ["uv", "pip", "install", "-t", vendor_dir, *vendor]
        subprocess.run(uv_args)

    def uninstall_vendors(self):
        vendor_dir = Path(self.config["vendor-directory"])
        if not vendor_dir.is_absolute():
            vendor_dir = Path(self.root).joinpath(vendor_dir)
        else:
            try:
                vendor_dir.relative_to(self.root)
            except ValueError:
                return

        if vendor_dir.is_dir() and vendor_dir.exists():
            shutil.rmtree(vendor_dir)

    def clean_dist(self):
        for child in Path(self.directory).iterdir():
            if child.suffix == ".zip":
                child.unlink()
            if child.is_dir():
                shutil.rmtree(child)

    def tar_to_zip(self, path_str):
        path = Path(path_str)
        if self.target_name == "sdist" and path.name.endswith(".tar.gz"):
            with tarfile.open(path) as tar:
                tar.extractall(path.parent, filter="data")
            artifact_name = path.name[: -len(".tar.gz")]
            extracted_to = path.parent.joinpath(artifact_name + "/")
            if extracted_to.exists() and extracted_to.is_dir():
                shutil.make_archive(
                    str(path.with_name(artifact_name)),
                    "zip",
                    extracted_to,
                )
            build_test_directory = path.parent.joinpath(self.build_test)
            if not build_test_directory.exists():
                extracted_to.rename(build_test_directory)
