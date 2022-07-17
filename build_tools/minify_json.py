import os
import json
import glob
import gzip
import shutil
from typing import Dict, Type

from setuptools import Command
from setuptools.command.build import build as build_

# Template for how to do this from here https://github.com/abravalheri/experiment-setuptools-plugin


ProjectName = "PyMCTranslate"


def register(cmdclass: Dict[str, Type[Command]]):
    # register a new command class
    cmdclass["minify_json"] = MinifyJson
    # get the build command class
    build = cmdclass.get("build", build_)
    # register our command class as a subcommand of the build command class
    build.sub_commands.append(("minify_json", None))


class MinifyJson(Command):
    def initialize_options(self):
        self.build_lib = None

    def finalize_options(self):
        self.set_undefined_options("build_py", ("build_lib", "build_lib"))

    def run(self):
        minify_json(os.path.join(self.build_lib, ProjectName), True)


def minify_json(pymct_path, remove_origin=False):
    atlas = []
    versions = {}

    def get_add_atlas(obj) -> int:
        try:
            return atlas.index(obj)
        except ValueError:
            atlas.append(obj)
            return len(atlas) - 1

    json_dir = os.path.join(pymct_path, "json")
    versions_dir = os.path.join(json_dir, "versions")
    min_json_dir = os.path.join(pymct_path, "min_json")

    shutil.rmtree(min_json_dir, ignore_errors=True)

    for version in os.listdir(versions_dir):
        meta = versions.setdefault(version, {})["meta"] = {}
        for path in os.listdir(os.path.join(versions_dir, version)):
            if os.path.isfile(os.path.join(versions_dir, version, path)):
                if path.endswith(".json"):
                    with open(os.path.join(versions_dir, version, path)) as f:
                        meta[path[:-5]] = get_add_atlas(json.load(f))

            elif os.path.isdir(os.path.join(versions_dir, version, path)):
                database = versions.setdefault(version, {})[path] = {}
                for fpath in glob.iglob(
                    os.path.join(
                        glob.escape(versions_dir), version, path, "**", "*.json"
                    ),
                    recursive=True,
                ):
                    database_ = database
                    rel_path = os.path.relpath(
                        fpath, os.path.join(versions_dir, version, path)
                    ).split(os.sep)
                    assert len(rel_path) == 5
                    for directory in rel_path[:-2]:
                        database_ = database_.setdefault(directory, {})
                    with open(fpath) as f:
                        database_[rel_path[-1][:-5]] = get_add_atlas(json.load(f))

        for path in versions[version]:
            os.makedirs(os.path.join(min_json_dir, "versions", version), exist_ok=True)
            with gzip.open(
                os.path.join(min_json_dir, "versions", version, f"{path}.json.gz"), "wb"
            ) as f:
                f.write(json.dumps(versions[version][path]).encode("utf-8"))

        print(f"Built version {version}")

    print("Writing atlas")
    with gzip.open(os.path.join(min_json_dir, "atlas.json.gz"), "wb") as f:
        f.write(json.dumps(atlas).encode("utf-8"))
    print("Written atlas")

    if remove_origin:
        shutil.rmtree(json_dir, ignore_errors=True)


if __name__ == "__main__":
    minify_json(os.path.abspath(os.path.join(__file__, "..", "..", ProjectName)))
