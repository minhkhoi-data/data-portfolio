// Author the ordinary base format used to repair an orphan checkbox style.
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const output=process.argv[2];if(!output)throw new Error('Usage: repair_styles.mjs <base-style-fragment.xlsx>');
const wb=Workbook.create();const s=wb.worksheets.add('BaseFormat');
s.getRange('A1').values=[[0]];
wb.recalculate();
const file=await SpreadsheetFile.exportXlsx(wb);await file.save(output);
console.log('Ordinary native style fragment exported.');
