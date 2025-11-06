#!/usr/bin/env python3
"""
validate_and_print.py
Validate & print JSON and YAML files in a folder. Uses ijson if available for streaming JSON arrays.
"""
import json
import yaml
from pathlib import Path
import argparse

try:
    import ijson
    IJSON = True
except Exception:
    IJSON = False

def print_json_stream(path):
    print(f'--- JSON (stream): {path} ---')
    if IJSON:
        with open(path, 'r', encoding='utf-8') as f:
            # stream parse array items
            for obj in ijson.items(f, 'item'):
                print(json.dumps(obj, ensure_ascii=False, indent=2))
    else:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for rec in data:
            print(json.dumps(rec, ensure_ascii=False, indent=2))

def print_yaml(path):
    print(f'--- YAML: {path} ---')
    with open(path, 'r', encoding='utf-8') as f:
        for doc in yaml.safe_load_all(f):
            # yaml.safe_load_all yields documents; some may be None
            if doc is not None:
                print(yaml.safe_dump(doc, allow_unicode=True))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--indir', default='out_by_year')
    args = ap.parse_args()
    d = Path(args.indir)
    for p in sorted(d.iterdir()):
        if p.suffix.lower() == '.json':
            try:
                print_json_stream(p)
            except Exception as e:
                print(f'Error parsing JSON {p}: {e}')
        elif p.suffix.lower() in ('.yml', '.yaml'):
            try:
                print_yaml(p)
            except Exception as e:
                print(f'Error parsing YAML {p}: {e}')

if __name__ == '__main__':
    main()
