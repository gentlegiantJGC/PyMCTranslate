import json
import gzip
import os
import glob


def main(pymct_path: str):
    atlas = []
    versions = {}

    def get_add_atlas(obj) -> int:
        try:
            return atlas.index(obj)
        except ValueError:
            atlas.append(obj)
            return len(atlas) - 1

    versions_dir = os.path.join(pymct_path, "json", "versions")
    min_json_dir = os.path.join(pymct_path, "min_json")

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


if __name__ == "__main__":
    main("./PyMCTranslate")
