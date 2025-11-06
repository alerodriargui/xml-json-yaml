# 🚀 Project Execution Guide

## 📦 Install Required Libraries
```bash
pip install -r requirements.txt
```

---

## 🔁 Convert XML → JSON & YAML
```bash
python xml_to_json_yaml.py --xml "AllPeople.xml" --mapping mapping.json --outdir out_by_year
```

---

## ✅ Validate Generated Files
```bash
python validate_and_print.py --indir out_by_year
```

---

## 🔄 Merge JSON & YAML → XML
```bash
python merge_json_yaml_to_xml.py --indir out_by_year --out merged_people.xml
```

---

## 🧩 Read XML Structure with Schema
```bash
python schema_reader.py --xml AllPeople.xml --schema people_schema.json
```

---
