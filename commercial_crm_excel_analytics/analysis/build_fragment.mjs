import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=process.env.OLIST_PROJECT_ROOT;
const d=JSON.parse(await fs.readFile(root+'/analysis/outputs/workbook_input.json','utf8'));
const [kind,startText,sizeText,dest]=process.argv.slice(2);const start=Number(startText),size=Number(sizeText);
const wb=Workbook.create();const sheet=wb.worksheets.add(kind);const look=wb.worksheets.add('Lookups');look.getRange('B3').values=[[30]];look.getRange('B5').values=[['VALID']];
const serial=s=>s?(new Date(s.replace(' ','T')+(s.includes('T')||s.includes(' ')?'Z':'T00:00:00Z')).getTime()/86400000+25569):null;
const rows=(kind==='Leads'?d.leads:d.items).slice(start,start+size);const first=start+2,last=start+rows.length+1;
if(kind==='Leads'){
 const values=rows.map((o,i)=>{const p=d.lead_prepared[start+i];return [...Object.keys(d.leads[0]).map(k=>['first_contact_date','won_date'].includes(k)?serial(o[k]):o[k]),p.Channel,p.Observed_win,p.Observed_win?'Won recorded':'No won record',null,null,p.SR_label,p.SDR_label,serial(p.Contact_month+'-01'),p.Win_month?serial(p.Win_month+'-01'):null,null];});
 sheet.getRange(`A${first}:AA${last}`).values=values;
 sheet.getRange(`U${first}:V${last}`).formulas=rows.map((_,i)=>{const r=first+i;return[`=IF(S${r}=0,"",IF(H${r}<B${r},"",INT(H${r})-B${r}))`,`=IF(S${r}=0,"",IF(H${r}<B${r},"Won before contact",""))`];});
 sheet.getRange(`AA${first}:AA${last}`).formulas=rows.map((_,i)=>{const r=first+i;return[`=IF(Lookups!$B$5<>"VALID",NA(),IF(U${r}="","",IF(U${r}>Lookups!$B$3,1,0)))`];});
 sheet.getRange(`U${first}:U${last}`).setNumberFormat('#,##0');sheet.getRange(`AA${first}:AA${last}`).setNumberFormat('#,##0');
 sheet.getRange(`B${first}:B${last}`).setNumberFormat('yyyy-mm-dd');sheet.getRange(`H${first}:H${last}`).setNumberFormat('yyyy-mm-dd hh:mm');sheet.getRange(`Y${first}:Z${last}`).setNumberFormat('mmm yyyy');
}else{
 const values=rows.map((o,i)=>{const p=d.item_prepared[start+i];return [...Object.keys(d.items[0]).map(k=>['shipping_limit_date','order_purchase_timestamp'].includes(k)?serial(o[k]):o[k]),serial(p.Won_date),null,null,p.First_seller_order,null,serial(p.Purchase_month+'-01')];});
 sheet.getRange(`A${first}:O${last}`).values=values;
 sheet.getRange(`K${first}:L${last}`).formulas=rows.map((_,i)=>{const r=first+i;return[`=IF(AND(H${r}="delivered",I${r}>=J${r}),1,0)`,`=IF(K${r}=1,F${r},0)`];});
 sheet.getRange(`N${first}:N${last}`).formulas=rows.map((_,i)=>{const r=first+i;return[`=K${r}*M${r}`];});
 for(const range of [`E${first}:E${last}`,`I${first}:J${last}`])sheet.getRange(range).setNumberFormat('yyyy-mm-dd hh:mm');sheet.getRange(`O${first}:O${last}`).setNumberFormat('mmm yyyy');sheet.getRange(`F${first}:G${last}`).setNumberFormat('#,##0.00');sheet.getRange(`L${first}:L${last}`).setNumberFormat('#,##0.00');
}
wb.recalculate();await (await SpreadsheetFile.exportXlsx(wb)).save(dest);console.log(kind,first,last,'exported');
