import csv
import re
from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parent


def normalize_tokens(value):
    text = (value or '').strip().upper()
    if not text or text in {'UNKNOWN', 'N/A', 'NA', 'NULL', 'NONE'}:
        return []
    protected_text = text.replace('N/A', '__MISSING_VALUE_NA__')
    tokens = re.split(r'[;,/|]', protected_text)
    cleaned = []
    for token in tokens:
        t = token.strip()
        if t and t not in {'UNKNOWN', 'N/A', 'NA', 'NULL', 'NONE', '__MISSING_VALUE_NA__'}:
            cleaned.append(t)
    return list(dict.fromkeys(cleaned))


def intersect(left, right):
    return [token for token in left if token in right]


def match_evidence(row):
    exg = normalize_tokens(row['EXG'])
    fad = normalize_tokens(row['FAD'])
    pus = normalize_tokens(row['PUS'])
    all_match = intersect(intersect(exg, fad), pus)
    exg_fad = intersect(exg, fad)
    exg_pus = intersect(exg, pus)
    fad_pus = intersect(fad, pus)
    pair_match = list(dict.fromkeys(exg_fad + exg_pus + fad_pus))
    confidence = 'High' if all_match else 'Medium' if pair_match else 'Low'
    matching_countries = all_match or pair_match
    details = []
    if all_match:
        details.append('EXG-FAD-PUS: ' + ', '.join(all_match))
    if exg_fad:
        details.append('EXG-FAD: ' + ', '.join(exg_fad))
    if exg_pus:
        details.append('EXG-PUS: ' + ', '.join(exg_pus))
    if fad_pus:
        details.append('FAD-PUS: ' + ', '.join(fad_pus))
    return confidence, matching_countries, details or ['No country match across columns']


rows = [
    {'ID': 1001, 'EXG': 'USA, CAN', 'FAD': 'USA', 'PUS': 'MEX / USA'},
    {'ID': 1002, 'EXG': 'FRANCE; GERMANY', 'FAD': 'FRANCE', 'PUS': 'GERMANY; FRANCE'},
    {'ID': 1003, 'EXG': '  usa ', 'FAD': 'CAN', 'PUS': 'USA'},
    {'ID': 1004, 'EXG': 'BRA; ARG', 'FAD': 'BRA', 'PUS': 'CHL'},
    {'ID': 1005, 'EXG': 'UNKNOWN', 'FAD': '', 'PUS': 'IND'},
    {'ID': 1006, 'EXG': 'UNITED STATES', 'FAD': 'UNITED', 'PUS': 'STATES'},
    {'ID': 1007, 'EXG': ' france  ', 'FAD': 'FRANCE; JAPAN', 'PUS': ' germany '},
    {'ID': 1008, 'EXG': 'A', 'FAD': 'N/A', 'PUS': 'USA | CAN'},
    {'ID': 2001, 'EXG': 'ITA', 'FAD': 'ITA; SPAIN', 'PUS': 'SPAIN'},
    {'ID': 2002, 'EXG': '  GERMANY ', 'FAD': 'GERMANY', 'PUS': 'USA'},
    {'ID': 2003, 'EXG': 'JPN', 'FAD': 'AUS / NZL', 'PUS': 'AUS'},
    {'ID': 2004, 'EXG': 'TWN', 'FAD': 'TWN', 'PUS': 'UNKNOWN'},
    {'ID': 2005, 'EXG': 'BEL', 'FAD': 'NLD', 'PUS': 'DEU'},
    {'ID': 2006, 'EXG': 'UNKNOWN', 'FAD': 'NULL', 'PUS': 'SWE'},
    {'ID': 2007, 'EXG': '  sweden ; norway  ', 'FAD': 'NORWAY', 'PUS': 'SWEDEN'},
]

# Duplicate test rows with literal exact duplicates and ID conflicts.
rows.extend([
    {'ID': 3001, 'EXG': 'USA', 'FAD': 'USA', 'PUS': 'USA'},
    {'ID': 3001, 'EXG': 'USA', 'FAD': 'USA', 'PUS': 'USA'},
    {'ID': 3002, 'EXG': 'USA', 'FAD': 'USA', 'PUS': 'USA'},
    {'ID': 3002, 'EXG': 'USA', 'FAD': 'CAN', 'PUS': 'USA'},
])

def write_csv(path, records):
    with open(path, 'w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=['ID', 'EXG', 'FAD', 'PUS'],
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()
        writer.writerows(records)


csv_file = ROOT / 'synthetic_country_batch_01.csv'
write_csv(csv_file, rows[:8])

xlsx_file = ROOT / 'synthetic_country_batch_02.xlsx'
wb = Workbook()
ws = wb.active
ws.title = 'test'
ws.append(['ID', 'EXG', 'FAD', 'PUS'])
for row in rows[8:]:
    ws.append([row['ID'], row['EXG'], row['FAD'], row['PUS']])
wb.save(xlsx_file)

# Additional duplicate-only CSV for validation of exact duplicate rows and ID conflicts.
duplicate_csv = ROOT / 'synthetic_country_duplicate_check.csv'
write_csv(duplicate_csv, rows[-4:])

raw_rows = rows + rows[-4:]
unique_rows = []
seen = set()
for row in raw_rows:
    key = tuple(str(row[field] or '') for field in ('ID', 'EXG', 'FAD', 'PUS'))
    if key not in seen:
        seen.add(key)
        unique_rows.append(row)

summary = {}
for row in unique_rows:
    level, _, _ = match_evidence(row)
    summary[level] = summary.get(level, 0) + 1

expected = {'High': 4, 'Medium': 9, 'Low': 5}
if len(raw_rows) != 23 or len(unique_rows) != 18 or summary != expected:
    raise AssertionError(
        f'Unexpected synthetic test results: raw={len(raw_rows)}, '
        f'unique={len(unique_rows)}, classifications={summary}'
    )

by_id = {int(row['ID']): row for row in unique_rows if int(row['ID']) != 3002}
assert match_evidence(by_id[1001]) == (
    'High',
    ['USA'],
    ['EXG-FAD-PUS: USA', 'EXG-FAD: USA', 'EXG-PUS: USA', 'FAD-PUS: USA'],
)
assert match_evidence(by_id[1003]) == ('Medium', ['USA'], ['EXG-PUS: USA'])
for test_id in (1005, 1006, 1008):
    assert match_evidence(by_id[test_id]) == (
        'Low',
        [],
        ['No country match across columns'],
    )

print('Synthetic raw input rows:', len(raw_rows))
print('Rows after exact tuple deduplication:', len(unique_rows))
print('Expected post-deduplication summary:', summary)
print('Matching Countries and Match Details checks: OK')
print('CSV file:', csv_file)
print('Excel file:', xlsx_file)
print('Duplicate csv file:', duplicate_csv)
