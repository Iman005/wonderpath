import type { Place, PlaceCatalog } from "@/shared/types";

/** Infer room base capacity from Persian room names; default 2. */
export function lodgingBaseCapacity(catalog?: PlaceCatalog | null): number {
  const rooms = catalog?.rooms ?? [];
  for (const room of rooms) {
    const name = room.name || "";
    if (name.includes("یک") || name.includes("1")) return 1;
    if (name.includes("دو") || name.includes("2")) return 2;
    if (name.includes("سه") || name.includes("3")) return 3;
    if (name.includes("چهار") || name.includes("4")) return 4;
  }
  return 2;
}

export function lodgingExtraGuestFee(baseRate: number, catalog?: PlaceCatalog | null): number {
  const rooms = catalog?.rooms ?? [];
  if (rooms.length >= 2) {
    const sorted = [...rooms].sort((a, b) => a.price - b.price);
    const delta = sorted[1].price - sorted[0].price;
    if (delta > 0) return delta;
  }
  return Math.round(baseRate * 0.25);
}

/** Nightly rate for the whole unit given guest count. */
export function computeLodgingNightlyRate(
  place: Place,
  guests: number,
  overrideBase?: number | null,
): number | null {
  const base =
    overrideBase !== undefined && overrideBase !== null
      ? overrideBase
      : place.estimated_entrance_fee ?? place.catalog?.rooms?.[0]?.price ?? null;
  if (base == null) return null;
  const capacity = lodgingBaseCapacity(place.catalog);
  const extra = lodgingExtraGuestFee(base, place.catalog);
  const extras = Math.max(0, guests - capacity);
  return base + extras * extra;
}
