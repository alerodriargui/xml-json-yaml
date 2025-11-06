#!/usr/bin/env python3
"""
xml_to_json_yaml.py
Stream AllPeople.xml and create one JSON + one YAML file per birth year.
Translate tag names using an external mapping file (json/yaml/xml).
"""
import json, xml.etree.ElementTree as ET
from pathlib import Path
import argparse
import yaml
import re

# ---------- Mapping loader ----------
def load_mapping(path: Path):
    if not path:
        return {}
    suf = path.suffix.lower()
    if suf == '.json':
        return json.loads(path.read_text(encoding='utf-8'))
    if suf in ('.yml', '.yaml'):
        return yaml.safe_load(path.read_text(encoding='utf-8'))
    if suf == '.xml':
        tree = ET.parse(path)
        root = tree.getroot()
        mapping = {}
        # support <map from="name" to="nombre"/>
        for m in root:
            if 'from' in m.attrib and 'to' in m.attrib:
                mapping[m.attrib['from']] = m.attrib['to']
            else:
                src = m.find('source')
                tgt = m.find('target')
                if src is not None and tgt is not None:
                    mapping[src.text] = tgt.text
        return mapping
    raise ValueError('Unsupported mapping file type')

# ---------- JSON streaming writer ----------
class JsonArrayWriter:
    def __init__(self, p: Path):
        self.f = open(p, 'w', encoding='utf-8')
        self.first = True
        self.f.write('[\n')

    def write(self, obj):
        if not self.first:
            self.f.write(',\n')
        else:
            self.first = False
        json.dump(obj, self.f, ensure_ascii=False, indent=2)

    def close(self):
        self.f.write('\n]\n')
        self.f.close()

# ---------- YAML simple writer (one document per person) ----------
# Many YAML consumers accept multiple documents in one file; this is streaming-friendly.
def yaml_write(f, obj):
    # write one document per record
    yaml.safe_dump(obj, f, allow_unicode=True)
    f.write('\n')

# ---------- helpers ----------
YEAR_RE = re.compile(r'(18\d{2}|19\d{2}|20\d{2})')

def extract_year_from_birth(birth_str):
    if not birth_str:
        return None
    m = YEAR_RE.search(birth_str)
    if m:
        return m.group(1)
    # fallback: might be YYYY-M-D or D-M-YYYY
    parts = birth_str.split('-')
    if len(parts) >= 1 and len(parts[0]) == 4 and parts[0].isdigit():
        return parts[0]
    # try last part
    if len(parts) >= 1 and len(parts[-1]) == 4 and parts[-1].isdigit():
        return parts[-1]
    return None

def map_tag(tag, mapping):
    return mapping.get(tag, tag)

# Convert an Element to a dict (shallow for children of <person>)
def person_elem_to_dict(elem: ET.Element, mapping):
    d = {}
    # attributes of person (unlikely in this file)
    for k, v in elem.attrib.items():
        d[map_tag(k, mapping)] = v
    for child in elem:
        key = map_tag(child.tag, mapping)
        if len(child) == 0:
            d[key] = child.text.strip() if child.text else ''
        else:
            # nested children -> convert to dict
            sub = {}
            for g in child:
                sub[map_tag(g.tag, mapping)] = g.text.strip() if g.text else ''
            d[key] = sub
    return d

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xml', required=True, help='Input AllPeople XML file')
    ap.add_argument('--mapping', required=False, help='mapping file (json/yaml/xml)')
    ap.add_argument('--outdir', default='out_by_year', help='output directory')
    ap.add_argument('--record-tag', default='person', help='record element tag (default person)')
    args = ap.parse_args()

    xml_path = Path(args.xml)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    mapping = {}
    if args.mapping:
        mapping = load_mapping(Path(args.mapping)) or {}

    json_writers = {}
    yaml_files = {}

    # iterparse the XML (streaming)
    context = ET.iterparse(str(xml_path), events=('end',))
    for event, elem in context:
        if elem.tag != args.record_tag:
            # free memory on non-records (optional)
            continue

        record = person_elem_to_dict(elem, mapping)

        # get year from birth field (the file uses <birth>YYYY-M-D</birth>)
        birth_val = None
        # try common key names (after mapping)
        for candidate in ('birth', 'fecha', 'fechaNacimiento', 'birthdate', 'birth_date'):
            if candidate in record:
                birth_val = record[candidate]
                break
        if birth_val is None:
            # try unmapped tag name 'birth'
            birth_val = record.get(mapping.get('birth','birth'))
        year = extract_year_from_birth(str(birth_val or 'unknown')) or 'unknown'
        year_str = str(year)

        # write to JSON writer for that year (create if needed)
        if year_str not in json_writers:
            json_writers[year_str] = JsonArrayWriter(outdir / f'people_{year_str}.json')
        json_writers[year_str].write(record)

        # write YAML (one or more YAML documents per file)
        if year_str not in yaml_files:
            yaml_files[year_str] = open(outdir / f'people_{year_str}.yaml', 'w', encoding='utf-8')
        yaml_write(yaml_files[year_str], record)

        # free memory for element
        elem.clear()
        # also remove references from parent (if present)
        # works on CPython's ElementTree: try to delete previous siblings
        # (safe to ignore if unsupported)
        # Optional deeper cleanup (only if lxml available)
        try:
            while elem.getprevious() is not None:
                del elem.getparent()[0]
        except AttributeError:
            pass  # standard ElementTree does not support getprevious/getparent


    # close writers
    for w in json_writers.values():
        w.close()
    for f in yaml_files.values():
        f.close()

    print(f'Done. Files written to {outdir}')

if __name__ == '__main__':
    main()
