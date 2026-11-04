# Native DimDate parsing correction

The user supplied a Power BI screenshot showing a real parse failure in the prior delivered ZIP: UnknownKeyword isKey, ./tables/DimDate, line 13. The previous analytical/static checks did not establish that the project could open.

The prior generator emitted isKey immediately after a column annotation without a scope break. Microsoft documentation supports isKey as a column flag. The correction places column properties before annotation child objects, adds scope separation and separates date-column annotation scope. See scripts/build_model.py. Regression checks now cover that ordering and model indentation.

This is a correction to the emitted definitions, not proof of a successful Desktop run. Corrected native import/DAX/refresh/rendering remain unverified until tested. The source dataset and quantitative results are unchanged.

References: https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview and https://github.com/microsoft/Analysis-Services/tree/master/pbidevmode/fabricps-pbip/SamplePBIP/Sales.SemanticModel/definition

The first correction also indented model references, which introduced a second native failure. That change is reversed in the current revision; model-level annotations and table references are root-level, as documented in the Microsoft Learn Indentation section.
