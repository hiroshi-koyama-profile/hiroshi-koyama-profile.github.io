// Offline build helper. KaTeX 0.19.1 is vendored under its MIT license.
const fs=require('node:fs');
const katex=require('./vendor/katex.cjs');
const records=JSON.parse(fs.readFileSync(0,'utf8'));
const rendered=Object.fromEntries(records.map(record=>[record.id,record.formula.map(tex=>katex.renderToString(tex,{
  displayMode:true,throwOnError:true,strict:'error',trust:false,output:'htmlAndMathml'
}))]));
process.stdout.write(JSON.stringify({renderer:'KaTeX',version:katex.version,rendered}));
