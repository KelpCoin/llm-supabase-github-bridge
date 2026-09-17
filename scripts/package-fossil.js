#!/usr/bin/env node
/**
 * Minimal local fossil packager.
 * Works offline. Produces a content-addressed JSON fossil that can later be
 * inserted into the fossils table or pushed as a Git artifact.
 *
 * Usage:
 *   node scripts/package-fossil.js --run-id <uuid> --silo experiment --payload path/to/payload.json
 *
 * No network required. No secrets. Pure packaging.
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

function sha256(obj) {
  const canonical = JSON.stringify(obj, Object.keys(obj).sort());
  return crypto.createHash('sha256').update(canonical).digest('hex');
}

function parseArgs() {
  const args = process.argv.slice(2);
  const out = {};
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace(/^--/, '');
    out[key] = args[i + 1];
  }
  return out;
}

function main() {
  const args = parseArgs();
  if (!args['run-id'] || !args.silo || !args.payload) {
    console.error('Required: --run-id <uuid> --silo <id> --payload <file.json>');
    process.exit(1);
  }

  const payload = JSON.parse(fs.readFileSync(args.payload, 'utf8'));
  const fossil = {
    run_id: args['run-id'],
    silo_id: args.silo,
    created_at: new Date().toISOString(),
    content: payload,
  };

  fossil.package_hash = sha256(fossil);

  const outDir = path.join(process.cwd(), 'fossils');
  fs.mkdirSync(outDir, { recursive: true });
  const outPath = path.join(outDir, `${fossil.run_id}.json`);
  fs.writeFileSync(outPath, JSON.stringify(fossil, null, 2));

  console.log(JSON.stringify({
    status: 'packaged',
    path: outPath,
    package_hash: fossil.package_hash,
    run_id: fossil.run_id,
  }, null, 2));
}

main();
