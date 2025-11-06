#!/usr/bin/env python3
"""
schema_reader.py
Read a small structural schema (json/yaml) and use it to extract/display fields from the XML.
"""
import json, yaml, xml.etree.ElementTree as ET
from pathlib import Path
import argparse

def load_schema(p: Path):
    if p.suffix == '.json':
        return json.loads(p.read_text(encoding='utf-8'))
    if p.suffix in ('.yml', '.yaml'):
        return yaml.safe_load(p.read_text(encoding='utf-8'))
    raise ValueError('schema must be json or yaml')

def display(xml_path: Path, schema):
    tree = ET.parse(str(xml_path))
    root = tree.getroot()
    rec_tag = schema.get('record')
    fields = [f['name'] for f in schema.get('fields', [])]
    for rec in root.findall('.//' + rec_tag):
        out = {}
        for f in fields:
            el = rec.find(f)
            out[f] = el.text.strip() if (el is not None and el.text) else None
        print(json.dumps(out, ensure_ascii=False, indent=2))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xml', required=True)
    ap.add_argument('--schema', required=True)
    args = ap.parse_args()
    schema = load_schema(Path(args.schema))
    display(Path(args.xml), schema)

if __name__ == '__main__':
    main()
