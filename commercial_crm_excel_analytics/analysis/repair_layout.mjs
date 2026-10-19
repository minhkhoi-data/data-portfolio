// Author bounded layout/control fragments with the Codex Artifact Tool.
// The matching Python utility transfers only these authored native properties.
import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const output=process.argv[2];
if(!output)throw new Error('Usage: repair_layout.mjs <layout-fragment.xlsx>');
const wb=Workbook.create();
const d=wb.worksheets.add('Dashboard');
d.getRange('A1:N60').format.columnWidth=12;
d.getRange('A1:N60').format.rowHeight=21;
d.getRange('A1:B3').values=[['Category','Value'],['A',1],['B',2]];
const positions=[['A11','G29'],['H11','N29'],['A33','G51'],['H33','N51']];
for(const [start,end] of positions){
 const c=d.charts.add('bar',d.getRange('A1:B3'));
 c.setPosition(start,end);
}
const widths={
 Seller_Value:{C:29,F:26,H:22,I:24,J:22,K:22,L:28,M:24},
 Leads:{A:37,B:20,C:37,D:22,E:37,F:37,G:37,H:26,R:29,S:18,T:24,U:22,V:26,W:15,X:15,Y:20,Z:20,AA:22},
 Sales_Items:{A:37,C:37,D:37,E:26,I:28,J:26,L:23,M:24,N:26,O:20},
};
for(const [name,columns] of Object.entries(widths)){
 const s=wb.worksheets.add(name);
 for(const [column,width] of Object.entries(columns))s.getRange(column+'1').format.columnWidth=width;
 s.getRange('A1').format.rowHeight=48;
}
// Native typed controls for disposable scenario checks. Never transferred
// into the delivered workbook by apply_layout_fragment.py.
for(const [name,b2,b3] of [['Slow14',20,14],['InvalidSlow',20,0],['Support1',1,30],['InvalidSupport',0,30]]){
 const s=wb.worksheets.add(name);s.getRange('B2:B3').values=[[b2],[b3]];
}
wb.recalculate();
const native=await SpreadsheetFile.exportXlsx(wb);await native.save(output);
console.log('Bounded native layout fragment exported.');
