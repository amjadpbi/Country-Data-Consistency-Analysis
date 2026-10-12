# Country Data Consistency Analysis

A Power BI reporting and data-consistency solution that standardizes country values across three fields, identifies exact and pairwise matches, and classifies records by confidence level using dynamic Excel and CSV folder ingestion.

<!-- Add verified synthetic-data dashboard screenshot here -->

## Business problem and solution

Country values from different sources can vary in formatting, contain multiple countries, or disagree. This report standardizes the text for exact token comparison and helps analysts see where the values agree (and where they do not) across the three source fields `EXG`, `FAD`, and `PUS`.

The model produces `ID`, `EXG`, `FAD`, `PUS`, `Confidence Level`, `Matching Countries`, and `Match Details`. The existing report and DAX measures present the record-level results and confidence counts for analyst review. This project is a reporting and analysis solution — it surfaces agreement/disagreement; it does not attempt automated reconciliation of conflicting values.

## Confidence rules

- **High:** at least one valid token occurs in all three fields.
- **Medium:** there is no three-way match, but a valid token matches across any two fields.
- **Low:** no valid token matches between any pair.

Blank values and the missing-value tokens `UNKNOWN`, `N/A`, `NA`, `NULL`, and `NONE` do not match. Case and surrounding whitespace are normalized. Values are split on commas, semicolons, slashes, pipes, and similar delimiters; exact token (not fuzzy or substring) matching is used. Missing or explicit-missing tokens are treated as missing and excluded from token lists.

`Matching Countries` lists the matching tokens. `Match Details` identifies which pair(s) or all three fields agreed.

## Folder-based input

The Power Query parameter `pFolderPath` points to a folder, not a filename. On refresh, the query discovers visible `.csv` and `.xlsx` files, excludes hidden files and Excel temporary files (`~$...`), validates headers and column aliases, and combines their rows for processing. This is refresh-time folder discovery and combination; it is not persistent incremental processing.

Known input column aliases are explicit: `ID`/`NDC9`, `EXG`/`Exiger`, `FAD`/`FDA New`, and `PUS`/`USP`. A CSV is parsed as comma-delimited UTF-8. For Excel, the query probes visible worksheets and uses the first worksheet that matches the required logical fields.

The `pFolderPath` parameter is configurable; the checked-in value is a neutral example. Change it to the full local path of your `Synthetic Data` folder after cloning; do not commit a machine-specific path.

## Duplicate handling

After standardization, the model applies exact-row deduplication (`Table.Distinct`) on the tuple `(ID, EXG, FAD, PUS)`. Identical rows therefore collapse across files. `ID` is not assumed to be a unique key: different rows sharing an ID are retained as separate records (conflicting values are surfaced, not automatically resolved).

## Synthetic sample and expected results

All data intentionally included for publication is generated from scratch under `Synthetic Data/`. It uses fictional numeric IDs and artificial country combinations; it is not client data.

The default synthetic folder has three input files: an 8-row CSV, an 11-row Excel workbook, and a 4-row duplicate-check CSV. The folder therefore contains **23 raw rows**. Exact-row deduplication reduces the set to **18** distinct `(ID, EXG, FAD, PUS)` tuples.

Expected post-deduplication classifications:

| Result | Count |
|---|---:|
| High | 4 |
| Medium | 9 |
| Low | 5 |
| **Total** | **18** |

See `Synthetic Data/generate_synthetic_country_data.py` and `Documentation/Testing Guide.md` for reproducible generation, setup, and validation steps.

## Project structure

- `Country_Confidence.pbip` — Power BI project file (open in Power BI Desktop).
- `Country_Confidence.Report/` — PBIR report definition and native visuals.
- `Country_Confidence.SemanticModel/` — TMDL model, Power Query definitions, and DAX measures.
- `Synthetic Data/` — intentionally included synthetic CSV/XLSX inputs and generator.
- `Documentation/` — setup and validation guide.
- `Source Data/` and `Test Data/` — local-only original/source material and old test copies; excluded by `.gitignore` and not intended for publication.

## Setup and refresh

1. Open `Country_Confidence.pbip` in Power BI Desktop.
2. In **Transform data > Manage Parameters**, set `pFolderPath` to the full local path of the `Synthetic Data` folder (folder only, not a file).
3. Apply the parameter change and refresh.
4. Confirm the model has 18 records with the classification counts above.

The project’s checked-in parameter default is a neutral example path. Change it to the actual full path on your computer after cloning; do not commit a local machine path.

Power BI Desktop was not available during this preparation pass, so a live Desktop refresh and visual rendering check remain unverified. The expected results above were independently recalculated from the synthetic inputs and Power Query/DAX logic.

## Agentic AI-assisted development

AI assistance supported requirement analysis, project/query inspection, implementation and review of changes, debugging of ingestion logic, validation of expected results, and documentation/repository polishing. This AI-assisted work is documented as a supporting workflow and is not the project's primary identity or a replacement for manual validation.

## Security and privacy

Only the synthetic sample is intended for publication. The local source and legacy test folders are excluded by `.gitignore`; they must remain excluded. Do not publish client data, credentials, machine-specific paths, or other sensitive material.

## Limitations and future improvements

- This project measures agreement among three fields, not factual country accuracy.
- Conflicting rows with the same ID are retained and surfaced separately; a business-approved ID conflict policy would be needed for automated resolution.
- The query validates schemas during refresh, but Power BI Desktop refresh behavior should be verified on the target machine.
- The model discovers files during refresh; it does not implement persistent incremental processing.
- No license has been selected; do not add a license until the intended terms are approved.
