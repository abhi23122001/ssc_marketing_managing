// scripts/validate_dashboard_js.js
const fs = require('fs');
const vm = require('vm');

const html = fs.readFileSync('foundation/dashboard/dashboard.html', 'utf8');
const scriptMatches = html.match(/<script[\s\S]*?>([\s\S]*?)<\/script>/gi);

if (!scriptMatches || scriptMatches.length === 0) {
  console.error("No script tag found!");
  process.exit(1);
}

let hasError = false;
scriptMatches.forEach((s, idx) => {
  const code = s.replace(/<script[\s\S]*?>/i, '').replace(/<\/script>/i, '');
  try {
    new vm.Script(code);
    console.log(`Script block #${idx + 1} (${code.length} chars): Syntax OK!`);
  } catch (err) {
    console.error(`Script block #${idx + 1} Syntax Error:`, err);
    hasError = true;
  }
});

if (hasError) {
  process.exit(1);
} else {
  console.log("ALL DASHBOARD JAVASCRIPT SYNTAX FULLY VALIDATED!");
}
