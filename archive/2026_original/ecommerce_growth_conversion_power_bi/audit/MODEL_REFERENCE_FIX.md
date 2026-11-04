# Model ReferenceObject correction

The second user screenshot establishes a native failure in delivered revision 1: InvalidLineType / Unexpected line type ReferenceObject, ./model line 15, ref table FactSessions. The assistant's prior indentation change introduced this error; the corresponding static check also encoded the wrong rule. The check passing did not imply native correctness.

Microsoft Learn's TMDL Indentation section explicitly lists direct Model children, including tables and model-level annotations, as exceptions to ordinary child indentation. Its deterministic collection ordering example places model and ref table declarations at the same level. The current revision restores those references and annotations to root level and corrects both the generator and the check. The date-column scope correction remains.

Source data, analytical CSVs and metric results are unchanged. Corrected Desktop opening remains NOT VERIFIED. The corrected model has now passed the official Microsoft TmdlSerializer; both old malformed definitions were rejected as negative controls. Power BI Desktop and its DAX/M execution are still unavailable. A small definition-only patch is provided in addition to the complete corrected project to avoid re-downloading the source data for this repair.

Official reference: https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview#indentation
Official sample: https://github.com/microsoft/Analysis-Services/blob/master/pbidevmode/fabricps-pbip/SamplePBIP/Sales.SemanticModel/definition/model.tmdl
