/**
 * Map style helpers — prefer Persian labels in vector tiles and hide
 * unreliable third-party place/city labels so our own pins carry names.
 */

const PERSIAN_NAME_FIELD: unknown[] = [
  "coalesce",
  ["get", "name:fa"],
  ["get", "name_fa"],
  ["get", "name"],
];

/**
 * Layer ids/substrings whose baked-in labels are often wrong for Iran.
 * Covers both the Neshan naming (`place-*`) and the OpenFreeMap /
 * OpenMapTiles naming (`label_*`) used by the fallback style.
 */
const HIDE_LABEL_LAYER_IDS = [
  "place-label",
  "city label",
  "state label",
  "country label",
  "point-label",
  "place-city",
  "place-town",
  "place-village",
  "place-suburb",
  "place-hamlet",
  "place-neighbourhood",
  "place-state",
  "place-country",
  "settlement",
  "label_city",
  "label_town",
  "label_village",
  "label_state",
  "label_country",
  "label_other",
];

type StyleLayer = {
  id?: string;
  type?: string;
  layout?: Record<string, unknown>;
};

type StyleSpec = {
  layers?: StyleLayer[];
  [key: string]: unknown;
};

/**
 * True only for text fields that render a place/road *name*. Shields and
 * similar layers read `ref` into a fixed-size icon, so swapping in a long
 * Persian name there clips the text instead of translating it.
 */
function isNameTextField(textField: unknown): boolean {
  return JSON.stringify(textField ?? null).includes("name");
}

function shouldHideLabelLayer(layerId: string): boolean {
  const normalized = layerId.toLowerCase();
  return HIDE_LABEL_LAYER_IDS.some(
    (needle) => normalized === needle || normalized.includes(needle.replace(/\s+/g, "-")) || normalized.includes(needle)
  );
}

export function patchStyleForPersianLabels(style: StyleSpec): StyleSpec {
  const layers = (style.layers ?? []).map((layer) => {
    if (layer.type !== "symbol") return layer;

    const hideThisLayer = Boolean(layer.id && shouldHideLabelLayer(layer.id));
    const translateName =
      Boolean(layer.layout && "text-field" in layer.layout) &&
      isNameTextField(layer.layout?.["text-field"]);
    if (!hideThisLayer && !translateName) return layer;

    // MapLibre validates the style object we hand it, so never introduce a
    // `layout: undefined` key on layers that legitimately have no layout.
    const layout: Record<string, unknown> = { ...(layer.layout ?? {}) };
    if (translateName) {
      layout["text-field"] = PERSIAN_NAME_FIELD;
    }
    if (hideThisLayer) {
      layout.visibility = "none";
    }
    return { ...layer, layout };
  });
  return { ...style, layers };
}

export async function loadLocalizedMapStyle(styleUrl: string): Promise<StyleSpec> {
  const response = await fetch(styleUrl);
  if (!response.ok) {
    throw new Error(`Failed to load map style (${response.status})`);
  }
  const style = (await response.json()) as StyleSpec;
  return patchStyleForPersianLabels(style);
}
