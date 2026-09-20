"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import fa from "@/i18n/fa";
import { budgetService } from "@/services/budgetService";
import { tripService, tripUpdatePayload } from "@/services/tripService";
import { ApiError } from "@/services/apiClient";
import { formatToman, formatDayLabel, parseTomanInput, groupedTomanFromAmount } from "@/shared/format";
import { stayService } from "@/services/stayService";
import { feeLabelForKind } from "@/shared/placeKind";
import { normalizeBudget } from "@/modules/budget/normalizeBudget";
import type { DayBudget, Trip, TripBudget } from "@/shared/types";
import ErrorNotice from "@/components/ErrorNotice";
import TomanAmountField from "@/components/TomanAmountField";
import BudgetWarning from "@/components/BudgetWarning";

function feeDraftsFrom(budget: TripBudget): Record<string, string> {
  const drafts: Record<string, string> = {};
  for (const day of budget.days ?? []) {
    for (const place of day.places ?? []) {
      drafts[place.trip_place_id] = groupedTomanFromAmount(place.fee);
    }
  }
  return drafts;
}

export default function TripBudgetPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const tripId = params.id;

  const [trip, setTrip] = useState<Trip | null>(null);
  const [budget, setBudget] = useState<TripBudget | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [editingCap, setEditingCap] = useState(false);
  const [capDraft, setCapDraft] = useState("");
  const [savingCap, setSavingCap] = useState(false);
  const capCardRef = useRef<HTMLDivElement | null>(null);

  const [expenseLabel, setExpenseLabel] = useState("");
  const [expenseAmount, setExpenseAmount] = useState("");
  const [savingExpense, setSavingExpense] = useState(false);

  const [feeDrafts, setFeeDrafts] = useState<Record<string, string>>({});
  const [stayRateDrafts, setStayRateDrafts] = useState<Record<string, string>>({});
  const [savingFeeId, setSavingFeeId] = useState<string | null>(null);
  const [travelerDraft, setTravelerDraft] = useState("1");
  const [savingTravelers, setSavingTravelers] = useState(false);

  async function load(opts?: { silent?: boolean }) {
    if (!opts?.silent) {
      setLoading(true);
      setError(null);
    }
    try {
      const [tripResult, budgetResult] = await Promise.all([
        tripService.getTrip(tripId),
        budgetService.getTripBudget(tripId),
      ]);
      const next = normalizeBudget(budgetResult, tripResult);
      if (!next) throw new Error("empty budget");
      setTrip(tripResult);
      setBudget(next);
      setFeeDrafts(feeDraftsFrom(next));
      const stayDrafts: Record<string, string> = {};
      for (const stay of next.stays ?? []) {
        stayDrafts[stay.stay_id] = groupedTomanFromAmount(stay.nightly_rate);
      }
      setStayRateDrafts(stayDrafts);
      setCapDraft(groupedTomanFromAmount(next.budget_cap));
      setTravelerDraft(String(next.traveler_count ?? tripResult.traveler_count ?? 1));
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    } finally {
      if (!opts?.silent) setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tripId]);

  useEffect(() => {
    if (!editingCap) return;
    capCardRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
    document.getElementById("budget-cap-edit")?.focus();
  }, [editingCap]);

  async function handleSaveCap() {
    if (!trip) return;
    const cap = parseTomanInput(capDraft);
    if (cap === null || cap <= 0) {
      setError(fa.errors.budgetCeilingRequired);
      return;
    }
    setSavingCap(true);
    setError(null);
    try {
      const updated = await tripService.updateTrip(trip.id, tripUpdatePayload(trip, { budget_cap: cap }));
      setTrip(updated);
      setEditingCap(false);
      await load({ silent: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    } finally {
      setSavingCap(false);
    }
  }

  async function handleAddExpense(e: React.FormEvent) {
    e.preventDefault();
    const amount = parseTomanInput(expenseAmount);
    if (!expenseLabel.trim() || amount === null || amount <= 0) {
      setError(fa.errors.sideExpenseRequired);
      return;
    }
    setSavingExpense(true);
    setError(null);
    try {
      await budgetService.addExpense(tripId, { label: expenseLabel.trim(), amount });
      setExpenseLabel("");
      setExpenseAmount("");
      await load({ silent: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    } finally {
      setSavingExpense(false);
    }
  }

  async function handleRemoveExpense(expenseId: string) {
    setError(null);
    try {
      await budgetService.removeExpense(tripId, expenseId);
      await load({ silent: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    }
  }

  async function handleSaveTravelers() {
    if (!trip) return;
    const count = Number(travelerDraft);
    if (!Number.isInteger(count) || count < 1) {
      setError(fa.errors.travelersRequired);
      return;
    }
    setSavingTravelers(true);
    setError(null);
    try {
      const updated = await tripService.updateTrip(trip.id, tripUpdatePayload(trip, { traveler_count: count }));
      setTrip(updated);
      await load({ silent: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    } finally {
      setSavingTravelers(false);
    }
  }

  async function handleSaveStayRate(stayId: string) {
    const raw = stayRateDrafts[stayId] ?? "";
    const parsed = raw.trim() === "" ? null : parseTomanInput(raw);
    if (raw.trim() !== "" && parsed === null) {
      setError(fa.errors.sideExpenseRequired);
      return;
    }
    setSavingFeeId(stayId);
    setError(null);
    try {
      await stayService.updateStay(tripId, stayId, { nightly_rate: parsed });
      await load({ silent: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    } finally {
      setSavingFeeId(null);
    }
  }
  async function handleSaveFee(day: DayBudget, tripPlaceId: string, placeId: string) {
    const raw = feeDrafts[tripPlaceId] ?? "";
    const parsed = raw.trim() === "" ? null : parseTomanInput(raw);
    if (raw.trim() !== "" && parsed === null) {
      setError(fa.errors.sideExpenseRequired);
      return;
    }
    setSavingFeeId(tripPlaceId);
    setError(null);
    try {
      await tripService.updatePlaceFee(day.trip_day_id, placeId, parsed);
      await load({ silent: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    } finally {
      setSavingFeeId(null);
    }
  }

  const remaining =
    budget && budget.budget_cap != null ? budget.budget_cap - budget.grand_total : null;

  const warningMessage = budget
    ? fa.budget.overBudgetMessage.replace("{amount}", formatToman(budget.over_budget_amount))
    : "";

  return (
    <div className="container section">
      <Link href={`/trip/${tripId}`} className="nav-text-btn">
        ← {fa.trip.backToTrip}
      </Link>

      <h1 style={{ fontSize: "1.6rem", fontWeight: 800, margin: "14px 0 24px" }}>{fa.budget.title}</h1>

      {loading && <p className="muted">{fa.common.loading}</p>}
      {error && <ErrorNotice message={error} onRetry={() => load()} />}

      {budget && trip && (
        <>
          {budget.is_over_budget && (
            <BudgetWarning
              message={warningMessage}
              onIncreaseCap={() => {
                setCapDraft(groupedTomanFromAmount(budget.grand_total));
                setEditingCap(true);
              }}
              onReviewTrip={() => router.push(`/trip/${tripId}`)}
            />
          )}

          <div className="card budget-card" style={{ marginBottom: 20 }} ref={capCardRef}>
            <div className="row-between" style={{ gap: 12 }}>
              <p className="muted" style={{ margin: 0 }}>
                {fa.trip.budgetCapLabel}
              </p>
              {!editingCap && (
                <button className="btn btn-outline btn-sm" type="button" onClick={() => setEditingCap(true)}>
                  {budget.budget_cap != null ? fa.budget.editCap : fa.budget.setCap}
                </button>
              )}
            </div>

            {editingCap ? (
              <form
                className="budget-side-form budget-ceiling-form"
                style={{ marginTop: 12 }}
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSaveCap();
                }}
              >
                <TomanAmountField
                  id="budget-cap-edit"
                  value={capDraft}
                  onChange={setCapDraft}
                  placeholder={fa.trip.budgetCapPlaceholder}
                  ariaLabel={fa.trip.budgetCapLabel}
                />
                <div className="row" style={{ gap: 8 }}>
                  <button className="btn btn-primary btn-sm" type="submit" disabled={savingCap}>
                    {savingCap ? "…" : fa.trip.save}
                  </button>
                  <button
                    className="btn btn-outline btn-sm"
                    type="button"
                    onClick={() => {
                      setEditingCap(false);
                      setCapDraft(groupedTomanFromAmount(budget.budget_cap));
                      setError(null);
                    }}
                    disabled={savingCap}
                  >
                    {fa.trip.cancel}
                  </button>
                </div>
              </form>
            ) : budget.budget_cap != null ? (
              <>
                <p className="budget-total" style={{ margin: "6px 0 0" }}>
                  {formatToman(budget.budget_cap)}
                </p>
                {remaining != null && (
                  <p
                    className="muted"
                    style={{
                      margin: "6px 0 0",
                      color: remaining < 0 ? "var(--terracotta)" : undefined,
                      fontWeight: remaining < 0 ? 700 : undefined,
                    }}
                  >
                    {remaining < 0
                      ? `${fa.budget.overBy}: ${formatToman(-remaining)}`
                      : `${fa.budget.remainingTotal}: ${formatToman(remaining)}`}
                  </p>
                )}
              </>
            ) : (
              <p className="muted" style={{ margin: "6px 0 0" }}>
                {fa.budget.noCeiling}
              </p>
            )}
          </div>

          <div className="card budget-card" style={{ marginBottom: 20 }}>
            <div className="row-between" style={{ gap: 12, marginBottom: 8 }}>
              <div>
                <p className="muted" style={{ margin: 0 }}>
                  {fa.budget.travelersLabel}
                </p>
                <p className="muted" style={{ margin: "4px 0 0", fontSize: "0.82rem" }}>
                  {fa.budget.travelersHint}
                </p>
              </div>
            </div>
            <form
              className="budget-side-form"
              onSubmit={(e) => {
                e.preventDefault();
                handleSaveTravelers();
              }}
            >
              <input
                className="input input-light"
                type="number"
                min={1}
                max={30}
                value={travelerDraft}
                onChange={(e) => setTravelerDraft(e.target.value)}
                aria-label={fa.budget.travelersLabel}
              />
              <button className="btn btn-outline btn-sm" type="submit" disabled={savingTravelers}>
                {savingTravelers ? "…" : fa.budget.saveTravelers}
              </button>
            </form>
          </div>

          <div className="card budget-card" style={{ marginBottom: 20 }}>
            <div className="budget-row">
              <span>{fa.budget.placesTotal}</span>
              <span className="num" style={{ fontWeight: 700 }}>
                {formatToman(budget.attractions_total ?? 0)}
              </span>
            </div>
            <div className="budget-row">
              <span>{fa.budget.diningTotal}</span>
              <span className="num" style={{ fontWeight: 700 }}>
                {formatToman(budget.dining_total ?? 0)}
              </span>
            </div>
            <div className="budget-row">
              <span>{fa.budget.lodgingTotal}</span>
              <span className="num" style={{ fontWeight: 700 }}>
                {formatToman(budget.lodging_total ?? 0)}
              </span>
            </div>
            <div className="budget-row">
              <span>{fa.budget.expensesTitle}</span>
              <span className="num" style={{ fontWeight: 700 }}>
                {formatToman(budget.expenses_total)}
              </span>
            </div>
            <div className="budget-row" style={{ borderBottom: "none" }}>
              <strong>{fa.budget.grandTotal}</strong>
              <strong className="budget-total" style={{ fontSize: "1.4rem" }}>
                {formatToman(budget.grand_total)}
              </strong>
            </div>
            {budget.places_with_unknown_fee > 0 && (
              <p className="muted" style={{ margin: "4px 0 0", color: "var(--terracotta)" }}>
                {fa.budget.unknownFeeWarning}
              </p>
            )}
            {(budget.stays_with_unknown_rate ?? 0) > 0 && (
              <p className="muted" style={{ margin: "4px 0 0", color: "var(--terracotta)" }}>
                {fa.budget.unknownStayWarning}
              </p>
            )}
          </div>

          <div className="card budget-card" style={{ marginBottom: 20 }}>
            <h2 style={{ fontSize: "1.05rem", fontWeight: 800, margin: "0 0 6px" }}>{fa.budget.expensesTitle}</h2>
            <p className="muted" style={{ margin: "0 0 14px" }}>
              {fa.budget.sideExpensesHint}
            </p>
            <div className="budget-chip-row">
              {fa.budget.suggestions.map((suggestion) => (
                <button
                  className="chip"
                  type="button"
                  key={suggestion}
                  onClick={() => setExpenseLabel(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
            <form className="budget-side-form" onSubmit={handleAddExpense}>
              <input
                className="input input-light"
                value={expenseLabel}
                onChange={(e) => setExpenseLabel(e.target.value)}
                placeholder={fa.budget.expenseLabelPlaceholder}
                aria-label={fa.budget.expenseLabelPlaceholder}
              />
              <TomanAmountField
                value={expenseAmount}
                onChange={setExpenseAmount}
                placeholder={fa.budget.expenseAmountPlaceholder}
                ariaLabel={fa.budget.expenseAmountPlaceholder}
              />
              <button className="btn btn-primary" type="submit" disabled={savingExpense}>
                {savingExpense ? "…" : fa.budget.addExpense}
              </button>
            </form>
            {(budget.expenses ?? []).length === 0 ? (
              <p className="muted" style={{ marginTop: 12 }}>
                {fa.budget.noExpenses}
              </p>
            ) : (
              (budget.expenses ?? []).map((item) => (
                <div className="budget-row" key={item.id}>
                  <span>{item.label}</span>
                  <span className="row" style={{ gap: 10 }}>
                    <span className="num" style={{ fontWeight: 700 }}>
                      {formatToman(item.amount)}
                    </span>
                    <button
                      className="icon-btn danger"
                      type="button"
                      aria-label={fa.budget.removeSide}
                      onClick={() => handleRemoveExpense(item.id)}
                    >
                      ×
                    </button>
                  </span>
                </div>
              ))
            )}
          </div>

          <div className="card budget-card">
            <h2 style={{ fontSize: "1.05rem", fontWeight: 800, margin: "0 0 6px" }}>{fa.budget.placeFees}</h2>
            <p className="muted" style={{ margin: "0 0 14px" }}>
              {fa.budget.placeFeeHint}
            </p>
            {(budget.days ?? []).length === 0 ? (
              <p className="muted">{fa.budget.noDaysYet}</p>
            ) : (
              [...(budget.days ?? [])]
                .sort((a, b) => a.day_number - b.day_number)
                .map((day) => (
                  <div className="budget-day-block" key={day.trip_day_id}>
                    <div className="budget-row">
                      <strong>{formatDayLabel(day.day_number)}</strong>
                      <span className="num" style={{ fontWeight: 700 }}>
                        {formatToman(day.estimated_total)}
                      </span>
                    </div>
                    {(day.places ?? []).length === 0 ? (
                      <p className="muted" style={{ margin: "10px 0 0" }}>
                        {fa.budget.noPlacesOnDay}
                      </p>
                    ) : (
                      <div style={{ marginTop: 12 }}>
                        {(day.places ?? []).map((place) => (
                          <div className="budget-place-row" key={place.trip_place_id}>
                            <div className="budget-place-copy">
                              <span>{place.name || fa.budget.unnamedPlace}</span>
                              <span className="chip">{feeLabelForKind(place.kind)}</span>
                              {place.fee == null && <span className="chip">{fa.budget.unknownShort}</span>}
                            </div>
                            <TomanAmountField
                              value={feeDrafts[place.trip_place_id] ?? ""}
                              onChange={(next) =>
                                setFeeDrafts((prev) => ({ ...prev, [place.trip_place_id]: next }))
                              }
                              placeholder={fa.budget.placeFeePlaceholder}
                              ariaLabel={`${fa.budget.placeFees} — ${place.name}`}
                            />
                            <button
                              className="btn btn-outline btn-sm"
                              type="button"
                              onClick={() => handleSaveFee(day, place.trip_place_id, place.place_id)}
                              disabled={savingFeeId === place.trip_place_id}
                            >
                              {savingFeeId === place.trip_place_id ? "…" : fa.budget.savePlaceFee}
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))
            )}
          </div>

          <div className="card budget-card" style={{ marginBottom: 20 }}>
            <h2 style={{ fontSize: "1.05rem", fontWeight: 800, margin: "0 0 6px" }}>{fa.budget.lodgingFees}</h2>
            <p className="muted" style={{ margin: "0 0 14px" }}>
              {fa.budget.lodgingFeeHint}
            </p>
            {(budget.stays ?? []).length === 0 ? (
              <p className="muted">{fa.trip.staysEmpty}</p>
            ) : (
              (budget.stays ?? []).map((stay) => (
                <div className="budget-place-row" key={stay.stay_id}>
                  <div className="budget-place-copy">
                    <span>{stay.name || fa.budget.unnamedPlace}</span>
                    <span className="chip">
                      {fa.trip.stayNights
                        .replace("{nights}", String(stay.nights))
                        .replace("{day}", String(stay.check_in_day_number))}
                    </span>
                    {stay.nightly_rate == null && <span className="chip">{fa.budget.unknownShort}</span>}
                  </div>
                  <TomanAmountField
                    value={stayRateDrafts[stay.stay_id] ?? ""}
                    onChange={(next) => setStayRateDrafts((prev) => ({ ...prev, [stay.stay_id]: next }))}
                    placeholder={fa.budget.stayRatePlaceholder}
                    ariaLabel={`${fa.budget.lodgingFees} — ${stay.name}`}
                  />
                  <button
                    className="btn btn-outline btn-sm"
                    type="button"
                    onClick={() => handleSaveStayRate(stay.stay_id)}
                    disabled={savingFeeId === stay.stay_id}
                  >
                    {savingFeeId === stay.stay_id ? "…" : fa.budget.saveStayRate}
                  </button>
                </div>
              ))
            )}
          </div>
        </>
      )}
    </div>
  );
}
