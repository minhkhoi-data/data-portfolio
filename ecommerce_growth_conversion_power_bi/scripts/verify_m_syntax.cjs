// Optional official Microsoft M syntax validator. Does not execute M functions.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '..');
const modulePath = process.argv[2];
if (!modulePath) throw new Error('Pass the installed @microsoft/powerquery-parser directory');
const PQ = require(path.resolve(modulePath));
const pkg = JSON.parse(fs.readFileSync(path.join(path.resolve(modulePath), 'package.json'), 'utf8'));
(async () => {
 const dir = path.join(root, 'powerbi/EcommerceGrowth.Model/definition/tables');
 const results=[];
 for (const name of fs.readdirSync(dir).filter(x=>x.endsWith('.tmdl')).sort()) {
  const bytes=fs.readFileSync(path.join(dir,name)); const text=bytes.toString('utf8');
  if (!/\tpartition \w+ = m\n/.test(text)) continue;
  const expression=text.split('\t\tsource =\n')[1].split('\n').map(x=>x.startsWith('\t\t\t\t')?x.slice(4):x).join('\n').trim();
  const task=await PQ.TaskUtils.tryLexParse(PQ.DefaultSettings, expression);
  if (PQ.TaskUtils.isError(task)) throw new Error(name+': '+String(task.error?.message||task.error||'M parsing failed'));
  PQ.TaskUtils.assertIsParseStageOk(task);
  results.push({table:name.slice(0,-5),status:'PASS',tmdl_sha256:crypto.createHash('sha256').update(bytes).digest('hex')});
 }
 if(results.length!==8)throw new Error('Expected eight imported M tables');
 const parameterFile=path.join(root,'powerbi/EcommerceGrowth.Model/definition/expressions.tmdl');
 const parameterBytes=fs.readFileSync(parameterFile);
 const parameter=parameterBytes.toString('utf8').split('\n')[0].split('expression DataFolder = ')[1];
 const parameterTask=await PQ.TaskUtils.tryLexParse(PQ.DefaultSettings,parameter);
 if(PQ.TaskUtils.isError(parameterTask))throw new Error('DataFolder M parameter parsing failed');
 PQ.TaskUtils.assertIsParseStageOk(parameterTask);
 const proof={status:'PASS',validator:'Microsoft @microsoft/powerquery-parser',version:pkg.version,tables:results,parameter_sha256:crypto.createHash('sha256').update(parameterBytes).digest('hex'),scope:'Lexing and grammar parsing only. Does not evaluate functions, execute Windows M, refresh data or validate DAX.',native_m_engine:'NOT_VERIFIED'};
 fs.writeFileSync(path.join(root,'audit/evidence/m_syntax_parser.json'),JSON.stringify(proof,null,2));
 console.log(JSON.stringify({status:proof.status,version:proof.version,parsed_tables:results.length,scope:proof.scope},null,2));
})().catch(e=>{console.error(e.message);process.exit(1);});
