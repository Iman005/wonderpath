import type { Trip, TripBudget } from "@/shared/types";

type LooseBudget = Partial<TripBudget> & {
  side_expenses?: TripBudget["expenses"];
  side_expenses_total?: number;
  budget_ceiling?: number | null;
  over_ceiling?: boolean;
  over_by?: number;
  places_total?: number;
};

export function normalizeBudget(raw: LooseBudget | null | undefined, trip?: Trip | null): TripBudget | null {
  if (!raw) return null;

  const expenses = raw.expenses ?? raw.side_expenses ?? [];
  const estimatedTotal = raw.estimated_total ?? raw.places_total ?? 0;
  const expensesTotal = raw.expenses_total ?? raw.side_expenses_total ?? 0;
  const tripCap =
    trip?.budget_cap ?? (trip as (Trip & { budget_ceiling?: number | null }) | null | undefined)?.budget_ceiling ?? null;
  const cap = raw.budget_cap ?? raw.budget_ceiling ?? tripCap ?? null;
  const grandTotal = raw.grand_total ?? estimatedTotal + expensesTotal;
  const overBy = cap != null && grandTotal > cap ? grandTotal - cap : 0;

  return {
    trip_id: raw.trip_id ?? trip?.id ?? "",
    currency: raw.currency ?? "IRT",
    estimated_total: estimatedTotal,
    expenses_total: expensesTotal,
    grand_total: grandTotal,
    budget_cap: cap,
    is_over_budget: raw.is_over_budget ?? raw.over_ceiling ?? overBy > 0,
    over_budget_amount: raw.over_budget_amount ?? raw.over_by ?? overBy,
    days: raw.days ?? [],
    stays: raw.stays ?? [],
    expenses,
    places_with_unknown_fee: raw.places_with_unknown_fee ?? 0,
    stays_with_unknown_rate: raw.stays_with_unknown_rate ?? 0,
    traveler_count: raw.traveler_count ?? trip?.traveler_count ?? 1,
    attractions_total: raw.attractions_total ?? estimatedTotal,
    dining_total: raw.dining_total ?? 0,
    lodging_total: raw.lodging_total ?? 0,
  };
}
