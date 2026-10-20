// usage: node stills.mjs <compId> <frame> [frame...]   -> out/stills/<compId>_<frame>.jpg
// frames may be given as seconds with an "s" suffix, e.g. 12.5s
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";
import fs from "node:fs";

const [id, ...frames] = process.argv.slice(2);
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts"), publicDir: path.resolve("public") });
const composition = await selectComposition({ serveUrl, id, inputProps: {} });
fs.mkdirSync("out/stills", { recursive: true });
for (const fr of frames) {
  const frame = fr.endsWith("s") ? Math.round(parseFloat(fr) * composition.fps) : parseInt(fr, 10);
  const output = `out/stills/${id}_${frame}.jpg`;
  await renderStill({ serveUrl, composition, frame, output, imageFormat: "jpeg", jpegQuality: 85, scale: Number(process.env.SCALE ?? 0.5) });
  console.log(output);
}

