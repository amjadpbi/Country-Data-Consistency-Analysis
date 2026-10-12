# Documentation Index

- [`Testing Guide.md`](./Testing%20Guide.md): local synthetic-data refresh and validation procedure, including expected counts and the limits of validation performed here.
- [`../README.md`](../README.md): project overview, confidence rules, input behavior, duplicate handling, and privacy notes.
- [`../Synthetic Data/`](../Synthetic%20Data/): generated synthetic CSV/XLSX sample files and reproducible generator.
- [`../Country_Confidence.SemanticModel/definition/expressions.tmdl`](../Country_Confidence.SemanticModel/definition/expressions.tmdl): configurable `pFolderPath` and folder-discovery Power Query expression.
- [`../Country_Confidence.SemanticModel/definition/tables/Country%20Match.tmdl`](../Country_Confidence.SemanticModel/definition/tables/Country%20Match.tmdl): exact-row duplicate behavior and matching transformations.
- [`../Country_Confidence.SemanticModel/definition/tables/_Measures.tmdl`](../Country_Confidence.SemanticModel/definition/tables/_Measures.tmdl): existing DAX count and percentage measures.

The local `Source Data/` and `Test Data/` directories contain source/legacy files retained for local use. They are excluded from source control and are not part of the intended publication contents.
