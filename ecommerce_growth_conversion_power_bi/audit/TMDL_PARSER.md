# Official TMDL metadata validation

The corrected model is deserialized locally by Microsoft's TmdlSerializer.DeserializeDatabaseFromFolder. Evidence is audit/evidence/tmdl_parser.json, including input hashes, parsed topology and two negative controls reproducing the previously observed malformed definitions. verify_project.py checks that this evidence still matches every current TMDL input. A stale stamp is rejected; it does not certify a later source/model edit.

Tested tooling: .NET runtime 8.0.31 (linux-x64), pythonnet 3.2.0, Microsoft.AnalysisServices NuGet 19.117.0. The official runtime download was checked against its published SHA-512. Dependencies are external optional validation tools and are not bundled in the project.

Metadata deserialization reads 8 tables, 8 relationships, 35 measures and compatibility level 1702. It does not evaluate DAX, execute M, run refresh, load PBIR visuals, or substitute for opening the project in Power BI Desktop. Those remain unverified.

To repeat with compatible locally installed tooling:

```bash
python scripts/verify_tmdl_parser.py --dotnet-root /path/to/dotnet --tom-lib /path/to/tom/lib/net8.0 --pythonnet-site /path/to/pythonnet
python scripts/verify_project.py
```

The default runtime version is the tested version; --runtime-version can select another installed .NET 8 patch version. If rebuilding a changed model, rerun this validator before claiming its stored parser evidence applies.

Primary references:
- https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview#tmdl-api
- https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview#indentation
- https://www.nuget.org/packages/Microsoft.AnalysisServices/19.117.0
- https://github.com/dotnet/core/blob/main/release-notes/8.0/releases.json
