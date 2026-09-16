# Project scripts

Run both commands from the repository root:

```bash
python -m pip install -r requirements.txt
python scripts/build_outputs.py
python scripts/validate_project.py
```

`build_outputs.py` rebuilds the summary CSV files in `outputs/` from the bundled data.

`validate_project.py` checks the dataset and the Power BI source definition. It does not replace opening, refreshing, and visually reviewing the report in Power BI Desktop.

The raw demo-data generation code is not included. The bundled CSV files are treated as fixed, versioned project inputs.
