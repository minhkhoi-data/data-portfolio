# Native failure history and CSV rebuild

Both earlier embedded loaders failed model creation on Power BI Desktop August 2026, 2.157.1354.0 x64: PFE_M_ENGINE_INTERNAL / System; Can not access a closed Stream. The JSON/Deflate change was subsequently tested by the user and FAILED with the same error. The previous binary-lifetime hypothesis was not confirmed. The logs name no particular query or stream owner. Private diagnostic logs are not bundled.

On 13 October the user's minimal Enter Data table (Test = 1) loaded and produced a chart. Basic Power Query functionality therefore works in that scenario. It does not prove the installation handles this complete project.

This rebuild eliminates all embedded Base64/Deflate/GZip payloads and both calculated-table partitions. All eight tables now use short CSV import expressions. A single DataFolder M parameter locates the eight bundled files. MO_PROJECT.cmd checks file hashes and configures that parameter locally before requesting Desktop opening; it does not modify machine-wide settings, install software or download anything. The script's Bypass flag applies to its invocation only.

All 4,295,584 source events were reprocessed and independent monthly controls matched. The six analytical tables, measure definitions, fact grains and business limitations are preserved. FunnelStage and the measure holder are tiny CSV support tables. Model metadata and M grammar are checked with Microsoft tooling. PBIR schemas and actual opener configuration are checked separately. Those checks do not run Windows M, DAX, Desktop refresh or report rendering.

The rebuilt project's native status remains NOT VERIFIED. Its different loading architecture is not a confirmed cure for the internal closed-Stream error. Keep this boundary visible until the user can open and Refresh the full report.

Primary references:
- https://learn.microsoft.com/en-us/powerquery-m/file-contents
- https://learn.microsoft.com/en-us/powerquery-m/csv-document
- https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview
- https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-enter-data-directly-into-desktop
