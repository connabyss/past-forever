#!/usr/bin/env node
const F = require('./forever.js'), fs = require('fs');
const args = process.argv.slice(2), why = args.includes('--why');
const file = args.find((a) => !a.startsWith('--'));
if (!file) { console.log('use: node cli.js program.txt [--why]'); process.exit(1); }
console.log(F.text(fs.readFileSync(file, 'utf8'), { why }));
