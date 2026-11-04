import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=process.env.OLIST_PROJECT_ROOT || path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const d=JSON.parse(await fs.readFile(path.join(root,'analysis/outputs/workbook_input.json'),'utf8'));
const wb=Workbook.create();
const skeleton=process.env.OLIST_BUILD_MODE==='skeleton';
const names=['Dashboard','Channel_Performance','Rep_Performance','Monthly_Trend','Seller_Value','Action_List','Lookups','Leads','Sales_Items','Data_Dictionary','Project_Overview','Quality_Review'];
const sheets=Object.fromEntries(names.map(n=>[n,wb.worksheets.add(n)]));
const C={navy:'#19375A',blue:'#1C6D8C',pale:'#E8F2F9',ink:'#19375A',amber:'#FFF0BC',red:'#FCE5E5',muted:'#536778'};
const col=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const serial=s=>s ? (new Date(s.replace(' ','T')+(s.includes('T')||s.includes(' ')?'Z':'T00:00:00Z')).getTime()/86400000+25569) : null;
const nl=d.leads.length+1,ni=d.items.length+1,nw=d.sellers.length+1;
const lr=c=>`Leads!$${c}$2:$${c}$${skeleton?2:nl}`,ir=c=>`Sales_Items!$${c}$2:$${c}$${skeleton?2:ni}`,vr=c=>`Seller_Value!$${c}$2:$${c}$${nw}`;
function setup(s,max,row){s.showGridLines=false; s.getRange(`A1:${max}${row}`).format.font={name:'Arial',size:10,color:C.ink};s.getRange(`A1:${max}${row}`).format.rowHeight=21;s.getRange(`A1:${max}${row}`).format.verticalAlignment='center';s.getRange(`A1:${max}${row}`).format.columnWidth=17;}
function table(s,headers,rows,name,start=1){const end=start+rows.length,w=col(headers.length);setup(s,w,rows.length>200?10:end+4);s.getRange(`A${start}:${w}${start}`).values=[headers];if(rows.length&&!(skeleton&&rows.length>1000))s.getRange(`A${start+1}:${w}${end}`).values=rows.map(r=>Array.from({length:headers.length},(_,i)=>r[i]??null));s.tables.add(`A${start}:${w}${skeleton&&rows.length>1000?2:end}`,true,name).style='TableStyleMedium2';s.getRange(`A${start}:${w}${start}`).format={fill:C.navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,horizontalAlignment:'center',rowHeight:38};if(rows.length<=200){s.getRange(`B${start+1}:${w}${end}`).format.horizontalAlignment='right';s.getRange(`A${start+1}:A${end}`).format.horizontalAlignment='left';}s.freezePanes.freezeRows(start);return end;}
function note(s,row,text,width='N'){s.mergeCells(`A${row}:${width}${row+1}`);s.getRange(`A${row}`).values=[[text]];s.getRange(`A${row}:${width}${row+1}`).format={fill:C.pale,wrapText:true,font:{name:'Arial',size:10,color:C.muted},rowHeight:22};}
function input(s,range){s.getRange(range.replace(/:\w+\d+$/,':'+range.split(':')[1].replace(/\d+$/, '10'))).format.font.color='#245F9A';}
function countFormat(s,range){s.getRange(range).setNumberFormat('#,##0');}
function moneyFormat(s,range){s.getRange(range).setNumberFormat('#,##0.00');}
function pct(s,range){s.getRange(range).setNumberFormat('0.0%');}
// One small control area plus source-ID display aliases, not invented identities.
const look=sheets.Lookups;setup(look,'I',45);
look.getRange('A1:B4').values=[['Control','Value'],['Minimum valid cycles for support flag',20],['Slow won-cycle threshold (calendar days)',30],['Display aliases','Stable order of anonymized source IDs']];
look.getRange('A1:B1').format={fill:C.navy,font:{bold:true,color:'#FFFFFF'}};look.getRange('A2:A4').format.columnWidth=48;look.getRange('B2:B3').format.fill=C.amber;
look.getRange('B2:B3').dataValidation={rule:{type:'whole',operator:'between',formula1:1,formula2:365}};
look.getRange('A5:A6').values=[['Slow threshold validity'],['Support threshold validity']];look.getRange('B5:B6').formulas=[[ '=IFERROR(IF(AND(ISNUMBER(B3),B3=INT(B3),B3>=1,B3<=365),"VALID","INVALID"),"INVALID")'],['=IFERROR(IF(AND(ISNUMBER(B2),B2=INT(B2),B2>=1,B2<=365),"VALID","INVALID"),"INVALID")']];
look.getRange('A7:B7').values=[['Raw origin','Channel display']];look.getRange('A8:B17').values=d.channel_map;
look.getRange('E7:F7').values=[['Source SR ID','Display alias']];look.getRange('E8:F29').values=d.sr;
look.getRange('H7:I7').values=[['Source SDR ID','Display alias']];look.getRange('H8:I39').values=d.sdr;
for(const r of ['E8:E29','H8:H39'])look.getRange(r).format.columnWidth=37;
note(look,42,'Controls flag review thresholds, not sales quotas or measured business targets. SR/SDR labels identify anonymized source IDs only.');
// Leads: unchanged source fields after a validated 1:1 left join; derived fields stay separate.
const leadHeaders=[...Object.keys(d.leads[0]),'Channel','Observed_win','Recorded_result','Valid_cycle_days','Date_issue','SR_label','SDR_label','Contact_month','Win_month','Slow_won_cycle'];
const lrows=d.leads.map((o,i)=>{const p=d.lead_prepared[i];return [...Object.keys(d.leads[0]).map(k=>['first_contact_date','won_date'].includes(k)?serial(o[k]):o[k]),p.Channel,p.Observed_win,p.Observed_win?'Won recorded':'No won record',null,null,p.SR_label,p.SDR_label,serial(p.Contact_month+'-01'),p.Win_month?serial(p.Win_month+'-01'):null,null];});
table(sheets.Leads,leadHeaders,lrows,'OlistLeads');if(!skeleton){input(sheets.Leads,`A2:Q${nl}`);
for(const c of ['A','C','E','F','G'])sheets.Leads.getRange(`${c}1:${c}${nl}`).format.columnWidth=37;
sheets.Leads.getRange(`B2:B${nl}`).setNumberFormat('yyyy-mm-dd');sheets.Leads.getRange(`H2:H${nl}`).setNumberFormat('yyyy-mm-dd hh:mm');
const lf=Array.from({length:d.leads.length},(_,i)=>{const r=i+2;return[
 `=IF(D${r}="","Missing origin",VLOOKUP(D${r},Lookups!$A$8:$B$17,2,FALSE))`,
 `=IF(E${r}="",0,1)`, `=IF(S${r}=1,"Won recorded","No won record")`,
 `=IF(S${r}=0,"",IF(H${r}<B${r},"",INT(H${r})-B${r}))`,
 `=IF(S${r}=0,"",IF(H${r}<B${r},"Won before contact",""))`,
 `=IF(S${r}=0,"",VLOOKUP(G${r},Lookups!$E$8:$F$29,2,FALSE))`,
 `=IF(S${r}=0,"",VLOOKUP(F${r},Lookups!$H$8:$I$39,2,FALSE))`,
 `=DATE(YEAR(B${r}),MONTH(B${r}),1)`,
 `=IF(S${r}=0,"",DATE(YEAR(H${r}),MONTH(H${r}),1))`,
 `=IF(Lookups!$B$5<>"VALID",NA(),IF(U${r}="","",IF(U${r}>Lookups!$B$3,1,0)))`];});
sheets.Leads.getRange(`U2:V${nl}`).formulas=lf.map(r=>r.slice(3,5));sheets.Leads.getRange(`AA2:AA${nl}`).formulas=lf.map(r=>[r[9]]);sheets.Leads.getRange(`Y2:Z${nl}`).setNumberFormat('mmm yyyy');sheets.Leads.freezePanes.freezeColumns(1);}
// Every item belonging to a won seller is retained, before status/date eligibility.
const iheaders=[...Object.keys(d.items[0]),'Won_date','Eligible_item','Eligible_item_value','First_seller_order','Eligible_seller_order','Purchase_month'];
table(sheets.Sales_Items,iheaders,d.items.map((o,i)=>{const p=d.item_prepared[i];return [...Object.keys(d.items[0]).map(k=>['shipping_limit_date','order_purchase_timestamp'].includes(k)?serial(o[k]):o[k]),serial(p.Won_date),null,null,p.First_seller_order,null,serial(p.Purchase_month+'-01')];}),'OlistLinkedItems');
if(!skeleton){for(const c of ['A','C','D'])sheets.Sales_Items.getRange(`${c}1:${c}${ni}`).format.columnWidth=37;
input(sheets.Sales_Items,`A2:I${ni}`);sheets.Sales_Items.getRange(`E2:E${ni}`).setNumberFormat('yyyy-mm-dd hh:mm');sheets.Sales_Items.getRange(`I2:J${ni}`).setNumberFormat('yyyy-mm-dd hh:mm');moneyFormat(sheets.Sales_Items,`F2:G${ni}`);moneyFormat(sheets.Sales_Items,`L2:L${ni}`);
const ifs=Array.from({length:d.items.length},(_,i)=>{const r=i+2;return[
 `=INDEX(${lr('H')},MATCH(D${r},${lr('E')},0))`,
 `=IF(AND(H${r}="delivered",I${r}>=J${r}),1,0)`,
 `=IF(K${r}=1,F${r},0)`,
 `=IF(COUNTIFS($A$2:A${r},A${r},$D$2:D${r},D${r})=1,1,0)`,
 `=K${r}*M${r}`, `=DATE(YEAR(I${r}),MONTH(I${r}),1)`];});
sheets.Sales_Items.getRange(`K2:L${ni}`).formulas=ifs.map(r=>r.slice(1,3));sheets.Sales_Items.getRange(`N2:N${ni}`).formulas=ifs.map(r=>[r[4]]);sheets.Sales_Items.getRange(`O2:O${ni}`).setNumberFormat('mmm yyyy');sheets.Sales_Items.freezePanes.freezeColumns(1);}
console.log('Source placeholders authored.');
// Seller-grain build avoids multiplying lead counts by order-item rows.
const vheaders=['mql_id','seller_id','Channel','SR_label','SDR_label','Won_date','Seller_state','Linked_source_items','Eligible_delivered_items','Seller_order_links','Linked_item_value','First_delivered_purchase','Days_to_first_purchase','Sample_linkage'];
table(sheets.Seller_Value,vheaders,d.sellers.map(o=>[o.mql_id,o.seller_id,o.Channel,o.SR_label,o.SDR_label,serial(o.won_date),o.seller_state]),'OlistSellerValue');
input(sheets.Seller_Value,`A2:G${nw}`);sheets.Seller_Value.getRange(`A1:B${nw}`).format.columnWidth=37;sheets.Seller_Value.getRange(`F2:F${nw}`).setNumberFormat('yyyy-mm-dd hh:mm');
const vf=Array.from({length:d.sellers.length},(_,i)=>{const r=i+2;return[
 `=COUNTIFS(${ir('D')},B${r})`, `=SUMIFS(${ir('K')},${ir('D')},B${r})`, `=SUMIFS(${ir('N')},${ir('D')},B${r})`,
 `=IF(I${r}=0,"",SUMIFS(${ir('L')},${ir('D')},B${r}))`,
 `=IF(I${r}=0,"",_xlfn.MINIFS(${ir('I')},${ir('D')},B${r},${ir('K')},1))`,
 `=IF(L${r}="","",INT(L${r})-INT(F${r}))`,
 `=IF(H${r}=0,"No linked sample items",IF(I${r}=0,"Linked; no eligible delivered item","Linked delivered activity"))`];});
sheets.Seller_Value.getRange(`H2:N${nw}`).formulas=vf;moneyFormat(sheets.Seller_Value,`K2:K${nw}`);sheets.Seller_Value.getRange(`M2:M${nw}`).setNumberFormat('#,##0');sheets.Seller_Value.getRange(`L2:L${nw}`).setNumberFormat('yyyy-mm-dd hh:mm');sheets.Seller_Value.getRange(`N1:N${nw}`).format.columnWidth=34;
console.log('Seller-grain build authored.');
const ch=sheets.Channel_Performance,ce=d.channels.length+1;
table(ch,['Channel','MQLs','Observed wins','No won record','Recorded won share','Valid cycles','Avg cycle days','Slow won cycles','Sales-linked wins','Delivered-linked wins','Linked item value','Sales sample linkage','Cycle support'],d.channels.map(c=>[c]),'OlistChannels');
ch.getRange(`A1:A${ce}`).format.columnWidth=29;
const cf=d.channels.map((_,i)=>{const r=i+2;return[
 `=COUNTIFS(${lr('R')},A${r})`,`=SUMIFS(${lr('S')},${lr('R')},A${r})`,`=B${r}-C${r}`,`=IF(B${r}=0,"",C${r}/B${r})`,
 `=C${r}-COUNTIFS(${lr('R')},A${r},${lr('V')},"Won before contact")`,
 `=IF(F${r}=0,"",SUMIFS(${lr('U')},${lr('R')},A${r})/F${r})`,
 `=SUMIFS(${lr('AA')},${lr('R')},A${r})`,
 `=COUNTIFS(${vr('C')},A${r},${vr('H')},">0")`,`=COUNTIFS(${vr('C')},A${r},${vr('I')},">0")`,
 `=IF(J${r}=0,"",SUMIFS(${vr('K')},${vr('C')},A${r}))`, `=IF(C${r}=0,"",I${r}/C${r})`,
 `=IF(Lookups!$B$6<>"VALID",NA(),IF(F${r}<Lookups!$B$2,"Small won sample","Meets review threshold"))`];});
ch.getRange(`B2:M${ce}`).formulas=cf;pct(ch,`E2:E${ce}`);pct(ch,`L2:L${ce}`);moneyFormat(ch,`K2:K${ce}`);ch.getRange(`G2:G${ce}`).setNumberFormat('0.0');ch.getRange(`M1:M${ce}`).format.columnWidth=27;
ch.getRange(`E2:E${ce}`).conditionalFormats.add('dataBar',{color:C.blue});
note(ch,ce+3,'Recorded won share = observed won records / sampled MQLs. No won record is not Lost or Open. Linked item value uses an independently sampled commercial dataset; unequal sample linkage and follow-up prevent ROI or causal channel ranking.');
const rep=sheets.Rep_Performance;
const repHeaders=['Anonymized rep','Observed wins','Valid cycles','Avg cycle days','Slow won cycles','Slow / valid cycles','Sales-linked wins','Delivered-linked wins','Linked item value','Cycle support'];
function repBlock(labels,start,isSDR){const end=table(rep,repHeaders,labels.map(x=>[x]),isSDR?'OlistSDRs':'OlistSRs',start);const key=isSDR?'X':'W',vk=isSDR?'E':'D';
 const f=labels.map((_,i)=>{const r=start+i+1;return[
 `=COUNTIFS(${lr(key)},A${r})`,`=B${r}-COUNTIFS(${lr(key)},A${r},${lr('V')},"Won before contact")`,`=IF(C${r}=0,"",SUMIFS(${lr('U')},${lr(key)},A${r})/C${r})`,`=SUMIFS(${lr('AA')},${lr(key)},A${r})`,`=IF(C${r}=0,"",E${r}/C${r})`,`=COUNTIFS(${vr(vk)},A${r},${vr('H')},">0")`,`=COUNTIFS(${vr(vk)},A${r},${vr('I')},">0")`,`=IF(H${r}=0,"",SUMIFS(${vr('K')},${vr(vk)},A${r}))`,`=IF(Lookups!$B$6<>"VALID",NA(),IF(C${r}<Lookups!$B$2,"Small won sample","Meets review threshold"))`];});
 rep.getRange(`B${start+1}:J${end}`).formulas=f;pct(rep,`F${start+1}:F${end}`);moneyFormat(rep,`I${start+1}:I${end}`);rep.getRange(`D${start+1}:D${end}`).setNumberFormat('0.0');return end;}
const re=repBlock(d.sr_order,1,false),sdrStart=re+6,se=repBlock(d.sdr_order,sdrStart,true);rep.getRange('A1:J1').format.font.color='#FFFFFF';rep.getRange('A1:J1').format.rowHeight=38;rep.getRange(`J1:J${se}`).format.columnWidth=27;
note(rep,re+2,'SR table: observed wins only. Assigned non-won leads, quotas and account mix are absent. These are descriptive counts and cycles, not rep win rates or causal skill rankings.','J');
note(rep,se+3,'Lower table: SDR observed-win composition. Display aliases map to source IDs in Lookups. Missing cycles remain blank; the chronology anomaly stays in won counts.','J');
const mon=sheets.Monthly_Trend,me=d.months.length+1;
table(mon,['Month','MQLs received','Calendar wins','Contact-cohort wins','Recorded cohort won share','Linked item value','Valid calendar cycles','Avg cycle days','Month label'],d.months.map(m=>[serial(m+'-01')]),'OlistMonthly');
const mf=d.months.map((_,i)=>{const r=i+2;return[
 `=COUNTIFS(${lr('Y')},A${r})`,`=COUNTIFS(${lr('Z')},A${r})`,`=SUMIFS(${lr('S')},${lr('Y')},A${r})`,`=IF(B${r}=0,"",D${r}/B${r})`,`=SUMIFS(${ir('L')},${ir('O')},A${r})`,`=C${r}-COUNTIFS(${lr('Z')},A${r},${lr('V')},"Won before contact")`,`=IF(G${r}=0,"",SUMIFS(${lr('U')},${lr('Z')},A${r})/G${r})`,`=TEXT(A${r},"mmm yyyy")`];});
mon.getRange(`B2:I${me}`).formulas=mf;mon.getRange(`A2:A${me}`).setNumberFormat('mmm yyyy');pct(mon,`E2:E${me}`);moneyFormat(mon,`F2:F${me}`);mon.getRange(`H2:H${me}`).setNumberFormat('0.0');
note(mon,me+3,'Calendar wins use won_date; contact-cohort wins use first_contact_date with all recorded future wins. Cohorts have unequal observation windows. Zero sampled item value in a calendar month is not proof of zero company sales.','I');
// Action proposals have evidence, an owner and a specific next measurement.
const act=sheets.Action_List;
table(act,['Review','Owner role','Live evidence','Next step','Window','Success measure','Limit'],[
 ['Origin completeness','Marketing Ops',null,'Inspect landing-page capture and preserve explicit unknown separately','2 weeks','Missing-origin rate on new records','No causal attribution from origin'],
 ['Chronology exception','Sales Ops / data owner',null,'Verify the source timestamps; keep the recorded win, exclude only its cycle','Before reuse','Resolved date exception with provenance','No guessed replacement date'],
 ['Non-won outcomes','CRM data owner',null,'Request current status and stage-entry timestamps for sampled leads','Next extract','Outcome and event coverage','Do not infer Lost or Open'],
 ['Commercial sample coverage','Analytics / data owner',null,'Reconcile seller IDs and extraction windows before value comparisons','Next extract','Matched-seller coverage with denominators','No match is not zero sales'],
 ['Slow observed wins','Sales Ops',null,'Review won-only long-cycle cases and collect non-won comparison data','4 weeks','Cycle distributions within comparable groups','No measured lift or contact consent']
 ],'OlistActions');
act.getRange('C2:C6').formulas=[[`=COUNTBLANK(${lr('D')})&" missing; "&COUNTIFS(${lr('D')},"unknown")&" source-unknown"`],[`=COUNTIFS(${lr('V')},"Won before contact")&" won-before-contact record"`],[`=COUNTIFS(${lr('S')},0)&" leads without a won record"`],[`=COUNTIFS(${vr('H')},0)&" / "&COUNTA(${vr('A')})&" wins have no linked sample items"`],[`=SUM(${lr('AA')})&" observed wins exceed "&Lookups!$B$3&" days"`]];
for(const c of ['A','C','D','F','G'])act.getRange(`${c}1:${c}6`).format.columnWidth=c==='D'?52:35;act.getRange('A2:G6').format.wrapText=true;act.getRange('A2:G6').format.rowHeight=66;
// Seven KPI cards, four native editable charts, same blue visual language.
const dash=sheets.Dashboard;setup(dash,'N',60);dash.getRange('A1:N60').format.columnWidth=12;
dash.mergeCells('A1:N2');dash.getRange('A1').values=[['OLIST CRM | ACQUISITION & SELLER VALUE']];dash.getRange('A1:N2').format={fill:C.navy,font:{name:'Arial',size:19,bold:true,color:'#FFFFFF'},rowHeight:25};
dash.mergeCells('A3:N3');dash.getRange('A3').values=[['Real, anonymized Olist samples | Contacts Jun 2017–May 2018 | Observed wins Dec 2017–Nov 2018']];dash.getRange('A3:N3').format={fill:C.pale,font:{size:10,color:C.ink},rowHeight:24};
const cards=[['MQLs',`=COUNTA(${lr('A')})`,'#,##0'],['Observed wins',`=SUM(${lr('S')})`,'#,##0'],['Recorded won share',`=C6/A6`,'0.0%'],['Median cycle days',`=MEDIAN(${lr('U')})`,'0'],['Sales-linked wins',`=COUNTIFS(${vr('H')},">0")`,'#,##0'],['Linked item value',`=SUM(${vr('K')})`,'#,##0'],['Slow won cycles',`=SUM(${lr('AA')})`,'#,##0']];
cards.forEach(([label,f,fmt],i)=>{const c=col(2*i+1),next=col(2*i+2);dash.mergeCells(`${c}5:${next}5`);dash.getRange(`${c}5`).values=[[label]];dash.getRange(`${c}5:${next}5`).format={fill:C.pale,font:{bold:true,size:10,color:C.ink},horizontalAlignment:'center',rowHeight:28};dash.mergeCells(`${c}6:${next}7`);dash.getRange(`${c}6`).formulas=[[f]];dash.getRange(`${c}6:${next}7`).format={font:{bold:true,size:22,color:C.ink},horizontalAlignment:'center',rowHeight:25};dash.getRange(`${c}6`).setNumberFormat(fmt);});
dash.mergeCells('A9:N9');dash.getRange('A9').formulas=[[`=COUNTIFS(${lr('V')},"Won before contact")&" chronology exception excluded from cycles | Slow threshold: "&Lookups!$B$3&" days | Item value: original price units; no FX"`]];dash.getRange('A9:N9').format={fill:C.pale,font:{size:10,color:C.muted},rowHeight:24};
function chart(type,ranges,title,start,end,valueFmt){const c=dash.charts.add(type,ranges);c.title=title;c.titleTextStyle.fontSize=13;c.titleTextStyle.typeface='Arial';c.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:10}};c.yAxis={numberFormatCode:valueFmt,numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};c.setPosition(start,end);for(const [i,s] of c.series.items.entries()){s.fill=i? '#DA825E':C.blue;if(type==='line')s.line={fill:i?'#DA825E':C.blue,style:'solid',width:2};}c.hasLegend=c.series.items.length>1;c.legend={position:'bottom',textStyle:{typeface:'Arial',fontSize:10}};return c;}
chart('bar',[ch.getRange(`A1:A${ce}`),ch.getRange(`C1:C${ce}`)],'Observed wins by origin','A11','G29','#,##0');
chart('line',[mon.getRange(`I1:I${me}`),mon.getRange(`B1:B${me}`),mon.getRange(`C1:C${me}`)],'Contacts and wins by calendar month','H11','N29','#,##0');
chart('bar',[rep.getRange('A1:A11'),rep.getRange('B1:B11')],'Top 10 SRs by observed won count','A33','G51','#,##0');
chart('bar',[ch.getRange(`A1:A${ce}`),ch.getRange(`K1:K${ce}`)],'Linked delivered item value by origin','H33','N51','0,"K"');
note(dash,30,'Origin is a recorded lead source. Won share is descriptive; non-won status and equal follow-up are not available.');
note(dash,52,'Sales-linked wins: 380 / 842; 376 link to eligible Delivered items. Item value excludes freight and is not Olist revenue, profit, LTV or CRM deal value.');
note(dash,56,'Won-only rep counts and cycles do not measure win rates. One date anomaly remains visible; missing origin and source-unknown labels are preserved.');
// Terminal quality checks: no output depends on this sheet.
const checks=[['MQL count',`=COUNTA(${lr('A')})`,8000],['Observed win count',`=SUM(${lr('S')})`,842],['No won record',`=COUNTIFS(${lr('S')},0)`,7158],['Channel leads reconcile',`=SUM(Channel_Performance!B2:B${ce})-COUNTA(${lr('A')})`,0],['Channel wins reconcile',`=SUM(Channel_Performance!C2:C${ce})-SUM(${lr('S')})`,0],['SR wins reconcile',`=SUM(Rep_Performance!B2:B${re})-SUM(${lr('S')})`,0],['SDR wins reconcile',`=SUM(Rep_Performance!B${sdrStart+1}:B${se})-SUM(${lr('S')})`,0],['Monthly leads reconcile',`=SUM(Monthly_Trend!B2:B${me})-COUNTA(${lr('A')})`,0],['Monthly wins reconcile',`=SUM(Monthly_Trend!C2:C${me})-SUM(${lr('S')})`,0],['Item value / seller value',`=SUM(${ir('L')})-SUM(${vr('K')})`,0],['Item value / channel value',`=SUM(${ir('L')})-SUM(Channel_Performance!K2:K${ce})`,0],['Item value / months',`=SUM(${ir('L')})-SUM(Monthly_Trend!F2:F${me})`,0],['Valid cycles',`=SUM(Channel_Performance!F2:F${ce})`,841],['Known date exceptions',`=COUNTIFS(${lr('V')},"Won before contact")`,1],['Missing origin',`=COUNTBLANK(${lr('D')})`,60],['Explicit source unknown',`=COUNTIFS(${lr('D')},"unknown")`,1099],['Eligible delivered items',`=SUM(${ir('K')})`,4984],['Seller-order links',`=SUM(${ir('N')})`,4463]];
table(sheets.Quality_Review,['Check','Actual','Expected source result','Reconciliation'],checks.map(x=>[x[0],null,x[2]]),'OlistQuality');sheets.Quality_Review.getRange(`B2:B${checks.length+1}`).formulas=checks.map(x=>[x[1]]);sheets.Quality_Review.getRange(`D2:D${checks.length+1}`).formulas=checks.map((_,i)=>[`=IF(ABS(B${i+2}-C${i+2})<0.000001,"MATCH","REVIEW")`]);sheets.Quality_Review.getRange('A1:A20').format.columnWidth=36;note(sheets.Quality_Review,23,'Expected values come from the bundled unchanged-source analysis. Matching known exceptions does not mean the source is perfect. This sheet is a terminal review; input/output logic does not depend on its labels.','D');
const definitions=[
 ['MQL','One sampled contact request identified by mql_id','Leads A:D','Not one order or one verified customer'],
 ['Observed win','A lead linked to a published closed-deal record','Leads S','842 observed; the 7,158 remaining outcomes are unobserved'],
 ['Recorded won share','Observed wins / sampled MQLs','Channel E','Unequal follow-up; not a mature cohort conversion estimate'],
 ['Valid cycle days','INT(won_date) - first_contact_date when chronological','Leads U','Calendar days; date-only contacts; 841 valid observations'],
 ['Slow won cycle','Valid cycle exceeds editable day threshold','Leads AA','Review heuristic, not inactivity or forecast'],
 ['SR / SDR aliases','Stable labels for sorted anonymized source IDs','Lookups E:I','No fabricated real names; won-only observation'],
 ['Linked source items','Order items whose seller_id is in observed wins','Seller H','380/842 matches; unmatched does not prove zero sales'],
 ['Eligible delivered item','Delivered status; purchase timestamp >= won timestamp','Sales_Items K','Observed sample only; no inferred treatment effect'],
 ['Linked item value','Sum eligible item price; excludes freight','Seller K','Original recorded units; currency code not asserted; no FX'],
 ['Seller-order link','Distinct seller_id + order_id among eligible items','Sales_Items N','4,463 links vs 4,457 distinct global orders'],
 ['No linked activity','No eligible recorded item in the joined samples','Seller N','Blank monetary result; not a verified zero-sales seller'],
 ['Declared monthly revenue','Seller-reported field preserved in raw joined input','Leads Q','797 zeros; zero/default/missing meaning not documented'],
 ['Contact cohort','Month of the first recorded contact date','Leads Y','Use all observed wins; follow-up is unequal'],
 ['Calendar wins','Month of recorded won timestamp','Leads Z','Not interchangeable with contact-cohort outcomes'],
 ['Missing vs unknown','Missing origin kept distinct from literal unknown','Leads D/R','60 missing; 1,099 explicit unknown'],
 ['Source processing','1:1 MQL/deal merge; m:1 item/order merge; seller grain','analysis/run_analysis.py','All original CSV bytes remain in data/source'],
 ['Timezones','Source timestamps used as recorded','Leads / Sales_Items','No UTC or regional timezone inferred'],
 ['Data rights','Olist data: CC BY-NC-SA 4.0','docs/SOURCES.md','Publisher attribution retained; not relicensed as unrestricted'],
];
table(sheets.Data_Dictionary,['Term','Definition','Trace','Interpretation'],definitions,'OlistDictionary');for(const [c,w] of [['A',30],['B',64],['C',32],['D',66]])sheets.Data_Dictionary.getRange(`${c}1:${c}19`).format.columnWidth=w;sheets.Data_Dictionary.getRange('A2:D19').format.wrapText=true;sheets.Data_Dictionary.getRange('A2:D19').format.rowHeight=42;
const overview=sheets.Project_Overview;setup(overview,'L',48);overview.mergeCells('A1:L2');overview.getRange('A1').values=[['OLIST CRM | PROJECT & SOURCE NOTES']];overview.getRange('A1:L2').format={fill:C.navy,font:{size:17,bold:true,color:'#FFFFFF'}};
const paragraphs=[
 ['Business question','Which recorded acquisition sources and observed won cohorts are associated with seller onboarding, closing speed and merchandise value visible in the linked sample?'],
 ['Sources','Olist Marketing Funnel and Brazilian E-Commerce Public Dataset. Real anonymized samples published by Olist and collaborators on Kaggle. Original source CSVs, URLs and hashes are bundled.'],
 ['Analysis scope','8,000 MQLs, 842 observed wins, 5,044 candidate item records. A validated seller-grain build prevents lead multiplication in commercial joins.'],
 ['What changed','The prior synthetic CRM pipeline has been replaced. No made-up Lost/Open states, deal probabilities, quotas, last-contact fields or USD amounts are carried over.'],
 ['Commercial interpretation','376 observed wins link to eligible Delivered item activity; source item prices sum to 664,858.00 recorded units. This is merchandise value in a sampled order set, not Olist revenue or profit.'],
 ['Limitations','Non-won states and assigned owners are absent. Samples have unequal temporal coverage. Currency code is not explicitly verified in the reviewed publisher pages, so original units are retained. No causal, ROI or LTV claim is made.'],
 ['Use and refresh','Start at Dashboard, then Channel/Rep/Monthly/Seller views. Amber controls in Lookups change review flags. Raw input tabs are prepared joins; replacing sources requires rerunning the documented preparation and rebuild, not appending unvalidated rows.'],
 ['Reproduction','Run python analysis/run_analysis.py to reproduce analytical CSVs and source hashes. The authoring script uses @oai/artifact-tool; native Excel recalculation and application checks are a separate gate.'],
 ['Contribution','AI assisted the artifact construction and verification. A user can demonstrate ownership by tracing joins, explaining missing outcomes and reproducing figures; the artifact does not establish independent mastery.'],
];
paragraphs.forEach(([label,text],i)=>{const r=4+i*4;overview.mergeCells(`A${r}:C${r+2}`);overview.getRange(`A${r}`).values=[[label]];overview.getRange(`A${r}:C${r+2}`).format={fill:C.pale,font:{bold:true},wrapText:true};overview.mergeCells(`D${r}:L${r+2}`);overview.getRange(`D${r}`).values=[[text]];overview.getRange(`D${r}:L${r+2}`).format.wrapText=true;});
await fs.mkdir(path.join(root,'preview'),{recursive:true});
console.log('All inputs, formulas, native tables and four charts authored. Recalculating.');
wb.recalculate();
console.log((await wb.inspect({kind:'region',sheetId:'Dashboard',range:'A5:N9',maxChars:1800,tableMaxRows:5,tableMaxCols:14})).ndjson);
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!',options:{useRegex:true,maxResults:30},maxChars:2500});
await fs.writeFile(path.join(root,'audit/artifact_inspection.ndjson'),errors.ndjson);
const output=await SpreadsheetFile.exportXlsx(wb);await output.save(path.join(root,'Olist_CRM_Acquisition_Seller_Value.xlsx'));
console.log('Workbook exported. Rendering overview.');
const ranges=skeleton?{}:{Dashboard:'A1:N59',Channel_Performance:'A1:M17',Rep_Performance:'A1:J26',Monthly_Trend:'A1:I24',Seller_Value:'A1:N7',Action_List:'A1:G6',Lookups:'A1:I12',Leads:'R1:AA7',Sales_Items:'J1:O7',Data_Dictionary:'A1:D19',Project_Overview:'A1:L42',Quality_Review:'A1:D25'};
for(const [name,range] of Object.entries(ranges)){try{const preview=await wb.render({sheetName:name,range,scale:1.25,format:'png'});await fs.writeFile(path.join(root,'preview',name+'.png'),new Uint8Array(await preview.arrayBuffer()));console.log('Rendered '+name);}catch(e){console.log('RENDER_ERROR '+name+': '+e.message);}}
await fs.writeFile(path.join(root,'audit/authoring_dimensions.json'),JSON.stringify({leadRows:d.leads.length,itemRows:d.items.length,sellerRows:d.sellers.length,sheets:names,channels:d.channels,srEnd:re,sdrStart,sdrEnd:se,monthEnd:me},null,2));
