// Tek kaynak: ../app. Mobil kopyalar bayt bayt aynı olmalı.
import { copyFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

for (const f of ["model.json", "score.js"]) {
  copyFileSync(fileURLToPath(new URL(`../../app/${f}`, import.meta.url)), fileURLToPath(new URL(`../src/${f}`, import.meta.url)));
}
