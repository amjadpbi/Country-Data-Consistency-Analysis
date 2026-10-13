# Synthetic Data Testing Guide

This guide validates the folder-based CSV/XLSX ingestion and matching rules using only the generated synthetic files. Do not point the model at `Source Data/` or `Test Data/`; those local folders are intentionally excluded from publication.

## Generate the synthetic files

From a terminal with Python and `openpyxl` installed, run:

```powershell
python "Synthetic Data\generate_synthetic_country_data.py"
```

The generator writes two independently named main inputs and a duplicate-check input:

| File | Format | Data rows |
|---|---|---:|
| `synthetic_country_batch_01.csv` | CSV | 8 |
| `synthetic_country_batch_02.xlsx` | Excel | 11 |
| `synthetic_country_duplicate_check.csv` | CSV | 4 |
| **Raw input total** |  | **23** |

All files use the required logical fields `ID`, `EXG`, `FAD`, and `PUS`. The Excel worksheet is named `test` only as a sample; the query does not require that name.

## Run the Power BI refresh

1. Open `Country_Confidence.pbip` in Power BI Desktop.
2. Select **Transform data > Manage Parameters**.
3. Set `pFolderPath` to the full local path of the `Synthetic Data` folder (folder only, not a file).
4. Apply the parameter and refresh.
5. Confirm the folder combines the 23 input rows, then applies exact-row deduplication.

The model should return 18 rows. The repeated exact row is collapsed, but the distinct conflicting variants of ID `3002` remain.

## Expected matching results

| Confidence | Expected records |
|---|---:|
| High | 4 |
| Medium | 9 |
| Low | 5 |
| **Total after exact-row deduplication** | **18** |

Included cases cover commas, semicolons, slashes, pipes, blanks, `UNKNOWN`, `N/A`, `NULL`, whitespace, case normalization, multi-country values, near/partial strings that must not match, exact duplicate rows, and conflicting rows that share ID `3002`.

Expected classification by retained row:

| ID | Expected confidence | Test case |
|---:|---|---|
| 1001 | High | Three-way `USA` token match across comma/slash-delimited values |
| 1002 | High | Three-way match across semicolon-delimited values |
| 1003 | Medium | Case/whitespace-normalized `USA` match in EXG and PUS |
| 1004 | Medium | `BRA` matches only between EXG and FAD |
| 1005 | Low | `UNKNOWN` and blank treated as missing |
| 1006 | Low | `UNITED STATES`, `UNITED`, and `STATES` do not fuzzy/substring-match |
| 1007 | Medium | `FRANCE` matches only between EXG and FAD |
| 1008 | Low | `N/A` is missing, not split into matching `N`/`A` tokens |
| 2001 | Medium | `SPAIN` matches only between FAD and PUS |
| 2002 | Medium | `GERMANY` matches between EXG and FAD |
| 2003 | Medium | `AUS` matches only between FAD and PUS |
| 2004 | Medium | `TWN` matches between EXG and FAD; `UNKNOWN` is missing |
| 2005 | Low | Three distinct tokens |
| 2006 | Low | `UNKNOWN` and `NULL` are missing |
| 2007 | Medium | `NORWAY` matches between EXG and FAD |
| 3001 | High | Exact duplicate rows collapse to one row |
| 3002 | High | First conflicting-ID variant retained |
| 3002 | Medium | Second conflicting-ID variant retained |

Representative evidence expectations:

- ID `1001` is High, has `USA` in `Matching Countries`, and reports the three-way plus pairwise `USA` matches in `Match Details`.
- ID `1003` is Medium, has `USA` in `Matching Countries`, and reports only `EXG-PUS: USA`.
- IDs `1005`, `1006`, and `1008` are Low, have empty `Matching Countries`, and show `No country match across columns`.

## File-discovery checks

For separate refresh trials, use a temporary test folder containing only the desired synthetic files, then set `pFolderPath` to that folder:

1. **CSV only:** copy `synthetic_country_batch_01.csv` into the temporary folder. Expected raw/model rows: 8.
2. **Excel only:** copy `synthetic_country_batch_02.xlsx`. Expected raw rows: 11; model rows after exact deduplication: 10.
3. **Combined formats:** copy both files. Expected raw rows: 19; model rows after exact deduplication: 18.
4. **Rename:** rename one input without changing its contents and refresh. Expected count is unchanged.
5. **Add another file:** add a valid CSV/XLSX under a new filename with new IDs and distinct values. Expected raw count increases by that input's row count; exact duplicate rows may reduce the post-dedup count.
6. **Refresh again:** with the same files unchanged, expected counts remain unchanged because each refresh rediscovers the current folder contents rather than appending to a persistent store.
7. **Hidden/temporary files:** place a hidden file or a `~$...xlsx` temporary file in the folder. It should not be selected.

## Invalid schema and diagnostics

Each eligible CSV/XLSX is expected to contain exactly one unambiguous mapping for each required logical field. Missing fields, multiple alias matches, malformed rows, or Excel workbooks with zero or multiple qualifying visible worksheets should fail with a file-specific diagnostic. Do not leave an invalid file in the default synthetic folder during a normal refresh, because a validation failure in any eligible file fails the combined query.

## Validation status

The project author reports that the Power BI project works in the submitted workflow and that the Upwork milestone was approved. The synthetic CSV and Excel files were also read and their counts/classifications independently recomputed: 23 raw rows, 18 distinct `(ID, EXG, FAD, PUS)` tuples, High 4, Medium 9, Low 5. ID `3001` appears once after exact duplicate removal; ID `3002` retains two differing rows.

This repository review did not independently reproduce the author’s Power BI Desktop session or separately execute every edge-case test listed above. Treat those as documented test procedures unless you run and record them. The reviewer’s lack of a local Desktop session is a limit of this review, not evidence that the submitted project is broken.
