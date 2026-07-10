#!/usr/bin/env node
/** 剥离 NT-TEST 围栏 → 生成干净的 dashboard.server.html */
const fs = require('fs');
const path = require('path');

const SRC = 'dashboard.html';
const OUT = 'dashboard.server.html';
const START = 'NT-TEST:START';
const END   = 'NT-TEST:END';

const lines = fs.readFileSync(SRC, 'utf-8').split('\n');
const out = [];
let depth = 0;
let startLn = 0;

for (let i = 0; i < lines.length; i++) {
    const ln = i + 1;
    const raw = lines[i];
    const hasStart = raw.includes(START);
    const hasEnd   = raw.includes(END);

    if (hasStart && hasEnd) {
        console.error(`❌ 行 ${ln}: START 和 END 不能在同一行`);
        process.exit(1);
    }
    if (hasStart) {
        if (depth === 0) startLn = ln;
        depth++;
        continue;
    }
    if (hasEnd) {
        if (depth === 0) {
            console.error(`❌ 行 ${ln}: 多余的 END（前面没有 START）`);
            process.exit(1);
        }
        depth--;
        continue;
    }
    if (depth === 0) out.push(raw);
}

if (depth > 0) {
    console.error(`❌ 行 ${startLn}: START 缺少对应的 END（嵌套层数 ${depth}）`);
    process.exit(1);
}

fs.writeFileSync(OUT, out.join('\n'), 'utf-8');
console.log(`✅ ${OUT} 已生成（${out.length} 行，剥离 ${lines.length - out.length} 行）`);

// 自检：node --check
const script = out.join('\n');
const m = script.match(/<script[^>]*>([\s\S]*?)<\/script>/);
if (!m) {
    console.error('❌ 生成文件中未找到 <script> 块');
    process.exit(1);
}
const tmpFile = OUT + '.check.js';
fs.writeFileSync(tmpFile, m[1], 'utf-8');

try {
    require('child_process').execSync(`node --check "${tmpFile}"`, { stdio: 'pipe' });
    console.log('✅ node --check JS 语法通过');
} catch (e) {
    console.error('❌ JS 语法错误：');
    console.error(e.stderr ? e.stderr.toString() : e.message);
    fs.unlinkSync(tmpFile);
    process.exit(1);
}
fs.unlinkSync(tmpFile);

// 内容验证
const outText = fs.readFileSync(OUT, 'utf-8');
const forbidden = ['btnDevtools', '_frozenMs', '内测世界', 'devtoolsSidebar', 'nt_virtual_ms'];
for (const kw of forbidden) {
    if (outText.includes(kw)) {
        console.error(`❌ 验证失败：产出中仍包含 "${kw}"`);
        process.exit(1);
    }
}
console.log('✅ 内容验证通过（无内测关键字残留）');
