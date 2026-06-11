from shutil import rmtree
import subprocess
import shutil
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def clean(self, versions):
        self.uninstall_vendors()

    def initialize(self, version, build_data):
        self.install_vendors()

    def finalize(self, version, build_data, artifact_path):
        # TODO: Convert to zip, and (optionally?) extract to a given path,
        # to be linked as an Anki plugin.
        pass

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
        vendor_dir = self.config["vendor-directory"]
        rmtree(vendor_dir)
