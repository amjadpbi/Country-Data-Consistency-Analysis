# Country Confidence

A focused Power BI project for comparing country values in three fields (`EXG`, `FAD`, and `PUS`) and classifying each record by the level of agreement between them.

## Business problem and solution

Country values from different sources can vary in formatting, contain multiple countries, or disagree. This report standardizes the text for exact token comparison and helps analysts see where the three fields agree. The result is evidence of agreement only; it does not establish which country value is factually correct.

The model produces `ID`, `EXG`, `FAD`, `PUS`, `Confidence Level`, `Matching Countries`, and `Match Details`. The existing report and DAX measures present the record-level results and confidence counts.

## Confidence rules

- **High:** at least one valid token occurs in all three fields.
- **Medium:** there is no three-way match, but a valid token matches across any two fields.
- **Low:** no valid token matches between any pair.

Blank values and the missing-value tokens `UNKNOWN`, `N/A`, `NA`, `NULL`, and `NONE` do not match. Case and surrounding whitespace are normalized. Values are split on commas, semicolons, slashes, and pipes. Matching is exact, not fuzzy.

`Matching Countries` lists the matching tokens. `Match Details` identifies which pair(s) or all three fields agreed.

## Folder-based input

The Power Query parameter `pFolderPath` points to a folder, not a filename. On refresh, the query discovers visible `.csv` and `.xlsx` files, excludes hidden files and Excel temporary files (`~$...`), validates each file, standardizes the required logical fields, and combines the rows before applying matching logic.

Known input column aliases are explicit: `ID`/`NDC9`, `EXG`/`Exiger`, `FAD`/`FDA New`, and `PUS`/`USP`. A CSV is parsed as comma-delimited UTF-8. For Excel, the query uses the single visible worksheet whose headers resolve unambiguously to the four required fields; it errors if there are zero or multiple matching worksheets. File validation errors include the file and issue. Adding or renaming an eligible file is detected on the next refresh.

This is refresh-time folder discovery and combination; it is not persistent incremental processing.

## Duplicate handling

After standardization, the model applies `Table.Distinct` to the exact tuple `(ID, EXG, FAD, PUS)`. Identical rows therefore collapse across files. `ID` is not assumed to be a unique key: records sharing an ID but having different source values remain separate. The model does not choose a winner or resolve conflicting values. No further deduplication by ID is implemented.

## Synthetic sample and expected results

All data intentionally included for publication is generated from scratch under [`Synthetic Data/`](./Synthetic%20Data/). It uses fictional numeric IDs and artificial country combinations; it is not sampled, perturbed, or derived from the local source-data files. The examples include blanks, `UNKNOWN`, `N/A`, mixed case, whitespace, delimiter variants, and near/partial strings that should not match under exact-token comparison.

The default synthetic folder has three input files: an 8-row CSV, an 11-row Excel workbook, and a 4-row duplicate-check CSV. The folder therefore contains **23 raw rows**. Exact-row deduplication produces **18 model rows** (one repeated tuple is reduced across the files); the two different records for ID `3002` are both retained.

Expected post-deduplication classifications:

| Result | Count |
|---|---:|
| High | 4 |
| Medium | 9 |
| Low | 5 |
| **Total** | **18** |

See [`Synthetic Data/generate_synthetic_country_data.py`](./Synthetic%20Data/generate_synthetic_country_data.py) and [`Documentation/Testing Guide.md`](./Documentation/Testing%20Guide.md) for reproducible sample generation and validation steps. The generator requires Python and `openpyxl`.

## Project structure

- `Country_Confidence.pbip` — Power BI Project entry point.
- `Country_Confidence.Report/` — PBIR report definition and native visuals.
- `Country_Confidence.SemanticModel/` — TMDL model, Power Query definitions, and DAX measures.
- `Synthetic Data/` — intentionally included synthetic CSV/XLSX inputs and generator.
- `Documentation/` — setup and validation guide.
- `Source Data/` and `Test Data/` — local-only original/source material and old test copies; excluded by `.gitignore` and not intended for publication.

## Setup and refresh

1. Open `Country_Confidence.pbip` in Power BI Desktop.
2. In **Transform data > Manage Parameters**, set `pFolderPath` to the full local path of the `Synthetic Data` folder.
3. Apply the parameter change and refresh.
4. Confirm the model has 18 records with the classification counts above.

The project’s checked-in parameter default is a neutral example path. Change it to the actual full path on your computer after cloning; do not commit a local machine path.

Power BI Desktop was not available during this preparation pass, so a live Desktop refresh and visual rendering check remain unverified. The expected results above were independently recalculated from the synthetic CSV/XLSX contents using the documented rules; they are not represented as a live Power BI test. No dashboard screenshot is included because there is no verified synthetic-only Desktop rendering available.

## Agentic AI-assisted development

AI assistance supported requirement analysis, project/query inspection, implementation and review of changes, debugging of ingestion logic, validation of expected results, and documentation/repository preparation. The work was human-directed and is subject to human review; this project does not claim to be an autonomous AI system.

## Security and privacy

Only the synthetic sample is intended for publication. The local source and legacy test folders are excluded by `.gitignore`; they must remain excluded. Do not publish client data, credentials, machine-local settings, Power BI caches, or screenshots containing non-synthetic data. This project should be reviewed before publication.

## Limitations and future improvements

- This project measures agreement among three fields, not factual country accuracy.
- Conflicting rows with the same ID are retained and surfaced separately; a business-approved ID conflict policy would be needed for further resolution.
- The query validates schemas during refresh, but Power BI Desktop refresh behavior should be verified on the target machine.
- The model discovers files during refresh; it does not implement persistent incremental processing.
- No license has been selected; do not add a license until the intended terms are approved.
