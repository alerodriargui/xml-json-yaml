#!/usr/bin/env python3
"""
merge_json_yaml_to_xml.py
Merge JSON and YAML files into a single XML file. Streamed output.
"""
import json, yaml
from pathlib import Path
from xml.sax.saxutils import XMLGenerator
import argparse

try:
    import ijson
    IJSON = True
except Exception:
    IJSON = False

def write_record_as_xml(gen, tagname, data):
    gen.startElement(tagname, {})
    if isinstance(data, dict):
        for k, v in data.items():
            safe_k = str(k).replace(' ', '_')
            if v is None:
                gen.startElement(safe_k, {}); gen.endElement(safe_k)
            elif isinstance(v, (str, int, float)):
                gen.startElement(safe_k, {}); gen.characters(str(v)); gen.endElement(safe_k)
            elif isinstance(v, dict):
                write_record_as_xml(gen, safe_k, v)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, (dict, list)):
                        write_record_as_xml(gen, safe_k, item)
                    else:
                        gen.startElement(safe_k, {}); gen.characters(str(item)); gen.endElement(safe_k)
            else:
                gen.startElement(safe_k, {}); gen.characters(str(v)); gen.endElement(safe_k)
    else:
        gen.characters(str(data))
    gen.endElement(tagname)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--indir', default='out_by_year')
    ap.add_argument('--out', default='merged_people.xml')
    args = ap.parse_args()

    indir = Path(args.indir)
    out = Path(args.out)

    with open(out, 'w', encoding='utf-8') as f:
        gen = XMLGenerator(f, encoding='utf-8')
        gen.startDocument()
        gen.startElement('People', {})
        for p in sorted(indir.iterdir()):
            if p.suffix.lower() == '.json':
                try:
                    if IJSON:
                        with open(p, 'r', encoding='utf-8') as r:
                            for rec in ijson.items(r, 'item'):
                                write_record_as_xml(gen, 'Person', rec)
                    else:
                        with open(p, 'r', encoding='utf-8') as r:
                            arr = json.load(r)
                        for rec in arr:
                            write_record_as_xml(gen, 'Person', rec)
                except Exception as e:
                    print(f'Error reading {p}: {e}')
            elif p.suffix.lower() in ('.yml', '.yaml'):
                try:
                    with open(p, 'r', encoding='utf-8') as r:
                        for rec in yaml.safe_load_all(r):
                            if rec:
                                write_record_as_xml(gen, 'Person', rec)
                except Exception as e:
                    print(f'Error reading {p}: {e}')
        gen.endElement('People')
        gen.endDocument()

    print(f'Merged XML written to {out}')

if __name__ == '__main__':
    main()
