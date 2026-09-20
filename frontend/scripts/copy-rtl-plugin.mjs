/**
 * Vendors the MapLibre RTL text plugin into public/ so it is served from our
 * own origin. MapLibre loads it with importScripts() inside a worker, and
 * public CDNs are unreliable from inside Iran.
 */
import { copyFile, mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = resolve(
  here,
  "../node_modules/@mapbox/mapbox-gl-rtl-text/mapbox-gl-rtl-text.min.js"
);
const target = resolve(here, "../public/mapbox-gl-rtl-text.min.js");

await mkdir(dirname(target), { recursive: true });
await copyFile(source, target);
console.log("copied RTL text plugin -> public/mapbox-gl-rtl-text.min.js");
