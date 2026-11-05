"""CSV履歴の原子的な更新。"""
import csv
import os
import tempfile
from pathlib import Path


def merge_csv(path, rows, fields, keys):
    """指定キーのレコードを置換し、それ以外の過去履歴を保持する。"""
    path = Path(path)
    old = {}
    if path.exists():
        with path.open(newline="", encoding="utf-8") as stream:
            for row in csv.DictReader(stream):
                old[tuple(row[k] for k in keys)] = row
    for row in rows:
        normalized = {field: str(row.get(field, "")) for field in fields}
        old[tuple(normalized[k] for k in keys)] = normalized
    if len(rows) == 0:
        return len(old)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=".usage-")
    try:
        with os.fdopen(descriptor, "w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for key in sorted(old):
                writer.writerow(old[key])
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return len(old)

