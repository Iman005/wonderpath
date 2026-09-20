"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import fa from "@/i18n/fa";
import { tripService, tripUpdatePayload } from "@/services/tripService";
import { budgetService } from "@/services/budgetService";
import { destinationService } from "@/services/destinationService";
import { ApiError } from "@/services/apiClient";
import { removeLocalTripId } from "@/modules/trip/localTrips";
import {
  dayDateIso,
  formatJalaliSlash,
  formatToman,
  groupedTomanFromAmount,
  inclusiveDayCount,
  formatDayOrdinal,
  parseTomanInput,
  toPersianDigits,
} from "@/shared/format";
import { normalizeBudget } from "@/modules/budget/normalizeBudget";
import type { City, Trip, TripBudget } from "@/shared/types";
import { buildDayItinerary } from "@/components/DayPlanColumn";
import CitySearchField from "@/components/CitySearchField";
import ErrorNotice from "@/components/ErrorNotice";
import JalaliDatePicker from "@/components/JalaliDatePicker";
import NotebookDrawer from "@/components/NotebookDrawer";
import AppOverlay from "@/components/AppOverlay";
import TomanAmountField from "@/components/TomanAmountField";
import DayInfoHover from "@/components/DayInfoHover";
import TopbarShare from "@/components/TopbarShare";
import { applySuggestedPlan } from "@/modules/tours/applySuggestedPlan";

function isTripInfoComplete(trip: Trip): boolean {
  return trip.origin_latitude != null && trip.budget_cap != null;
}

export default function TripEditorPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const searchParams = useSearchParams();
  const suggestedPlanId = searchParams.get("plan");
  const tripId = params.id;

  const [trip, setTrip] = useState<Trip | null>(null);
  const [budget, setBudget] = useState<TripBudget | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [editingName, setEditingName] = useState(false);
  const [nameDraft, setNameDraft] = useState("");
  const [savingName, setSavingName] = useState(false);

  const [addingDay, setAddingDay] = useState(false);
  const [removingDayId, setRemovingDayId] = useState<string | null>(null);
  const [travelerDraft, setTravelerDraft] = useState("1");
  const [confirmingDays, setConfirmingDays] = useState(false);
  const [skippingToHub, setSkippingToHub] = useState(false);
  const [editingRange, setEditingRange] = useState(false);
  const [rangeStart, setRangeStart] = useState("");
  const [rangeEnd, setRangeEnd] = useState("");
  const [savingRange, setSavingRange] = useState(false);

  const [originLabel, setOriginLabel] = useState("");
  const [selectedOriginCity, setSelectedOriginCity] = useState<City | null>(null);
  const [budgetCapDraft, setBudgetCapDraft] = useState("");
  const [notebookDayId, setNotebookDayId] = useState<string | null | undefined>(undefined);
  const [editingInfo, setEditingInfo] = useState(false);
  const [savingInfo, setSavingInfo] = useState(false);

  async function loadTrip(opts?: { silent?: boolean }) {
    if (!opts?.silent) {
      setLoading(true);
      setError(null);
    }
    try {
      const [result, budgetResult] = await Promise.all([
        tripService.getTrip(tripId),
        budgetService.getTripBudget(tripId).catch(() => null),
      ]);
      setTrip(result);
      setNameDraft(result.name);
      setBudget(normalizeBudget(budgetResult, result));
      if (result.budget_cap != null) {
        setBudgetCapDraft((current) => current || groupedTomanFromAmount(result.budget_cap));
      }
      if (!opts?.silent) {
        setOriginLabel(result.origin_label || "");
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    } finally {
      if (!opts?.silent) setLoading(false);
    }
  }

  useEffect(() => {
    loadTrip();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tripId]);

  async function handleSaveName() {
    if (!nameDraft.trim() || !trip) return;
    setSavingName(true);
    setError(null);
    try {
      const updated = await tripService.updateTrip(trip.id, { name: nameDraft.trim() });
      setTrip(updated);
      setEditingName(false);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : fa.errors.generic;
      if (err instanceof ApiError && /name|نام/i.test(err.message)) {
        setError(fa.errors.tripNameDuplicate);
      } else {
        setError(message);
      }
    } finally {
      setSavingName(false);
    }
  }

  async function handleDeleteTrip() {
    if (!trip) return;
    if (!window.confirm(fa.trip.confirmDeleteTrip)) return;
    try {
      await tripService.deleteTrip(trip.id);
      removeLocalTripId(trip.id);
      router.push("/app");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    }
  }

  async function handleAddDay() {
    if (!trip) return;
    setAddingDay(true);
    try {
      const nextDayNumber = trip.days.length > 0 ? Math.max(...trip.days.map((d) => d.day_number)) + 1 : 1;
      await tripService.addDay(trip.id, nextDayNumber);
      await loadTrip({ silent: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    } finally {
      setAddingDay(false);
    }
  }

  async function handleRemoveDay(dayId: string) {
    if (!trip) return;
    if (trip.days.length <= 1) {
      setError(fa.trip.keepAtLeastOneDay);
      return;
    }
    if (!window.confirm(fa.trip.confirmDeleteDay)) return;
    setRemovingDayId(dayId);
    setError(null);
    try {
      await tripService.removeDay(trip.id, dayId);
      await loadTrip({ silent: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    } finally {
      setRemovingDayId(null);
    }
  }

  function openRangeEditor() {
    if (!trip) return;
    setRangeStart(trip.start_date?.slice(0, 10) || "");
    setRangeEnd(trip.end_date?.slice(0, 10) || trip.start_date?.slice(0, 10) || "");
    setEditingRange(true);
  }

  async function handleSaveRange() {
    if (!trip || !rangeStart || !rangeEnd) {
      setError(fa.errors.endDateRequired);
      return;
    }
    if (rangeEnd < rangeStart) {
      setError(fa.errors.endDateBeforeStart);
      return;
    }
    const nextCount = inclusiveDayCount(rangeStart, rangeEnd);
    if (nextCount > 30) {
      setError(fa.trip.rangeTooLong);
      return;
    }
    if (nextCount < trip.days.length && !window.confirm(fa.trip.confirmShrinkRange)) return;
    setSavingRange(true);
    setError(null);
    try {
      await tripService.updateTrip(trip.id, {
        start_date: `${rangeStart}T00:00:00`,
        end_date: `${rangeEnd}T00:00:00`,
      });
      setEditingRange(false);
      await loadTrip({ silent: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    } finally {
      setSavingRange(false);
    }
  }

  async function addHubDays(current: Trip) {
    const startIso = current.start_date?.slice(0, 10);
    const endIso = current.end_date?.slice(0, 10) || startIso;
    const count = startIso && endIso ? inclusiveDayCount(startIso, endIso) : 1;
    await tripService.addDaysBulk(current.id, Math.min(Math.max(count, 1), 30));
  }

  async function fillSuggestedPlan(current: Trip) {
    if (!suggestedPlanId) return;
    const fresh = await tripService.getTrip(current.id);
    await applySuggestedPlan(fresh, suggestedPlanId);
    router.replace(`/trip/${current.id}`);
  }

  function validateTripInfo(): { cap: number; travelers: number } | null {
    const cap = parseTomanInput(budgetCapDraft);
    if (cap === null || cap <= 0) {
      setError(fa.errors.budgetCeilingRequired);
      return null;
    }
    const travelers = Number(travelerDraft);
    if (!Number.isInteger(travelers) || travelers < 1) {
      setError(fa.errors.travelersRequired);
      return null;
    }
    if (!selectedOriginCity) {
      setError(fa.errors.originRequired);
      return null;
    }
    return { cap, travelers };
  }

  async function persistTripInfo(current: Trip) {
    const parsed = validateTripInfo();
    if (!parsed || !selectedOriginCity) return false;
    const cityName = selectedOriginCity.name || "";
    const detail = originLabel.trim();
    const label = [cityName, detail].filter(Boolean).join("، ") || null;
    await tripService.updateTrip(
      current.id,
      tripUpdatePayload(current, {
        origin_label: label,
        origin_latitude: selectedOriginCity.latitude ?? null,
        origin_longitude: selectedOriginCity.longitude ?? null,
        budget_cap: parsed.cap,
        traveler_count: parsed.travelers,
      }),
    );
    return true;
  }

  async function handleConfirmDayCount() {
    if (!trip) return;
    if (!validateTripInfo()) return;
    setConfirmingDays(true);
    setError(null);
    try {
      const ok = await persistTripInfo(trip);
      if (!ok) return;
      await addHubDays(trip);
      await fillSuggestedPlan(trip);
      await loadTrip();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    } finally {
      setConfirmingDays(false);
    }
  }

  async function handleSkipToHub() {
    if (!trip) return;
    setSkippingToHub(true);
    setError(null);
    try {
      await addHubDays(trip);
      await fillSuggestedPlan(trip);
      await loadTrip();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    } finally {
      setSkippingToHub(false);
    }
  }

  async function openInfoEditor() {
    if (!trip) return;
    setError(null);
    setBudgetCapDraft(trip.budget_cap != null ? groupedTomanFromAmount(trip.budget_cap) : "");
    setTravelerDraft(String(trip.traveler_count || 1));
    const parts = (trip.origin_label || "")
      .split("،")
      .map((part) => part.trim())
      .filter(Boolean);
    const cityPart = parts[0] || "";
    setOriginLabel(parts.slice(1).join("، "));
    setSelectedOriginCity(null);
    setEditingInfo(true);
    if (!cityPart) return;
    try {
      const cities = await destinationService.searchCities(cityPart);
      const match = cities.find((city) => city.name === cityPart) ?? cities[0] ?? null;
      setSelectedOriginCity(match);
    } catch {
      /* keep the dialog usable even if city lookup fails */
    }
  }

  async function handleSaveTripInfo() {
    if (!trip) return;
    if (!validateTripInfo()) return;
    setSavingInfo(true);
    setError(null);
    try {
      const ok = await persistTripInfo(trip);
      if (!ok) return;
      setEditingInfo(false);
      await loadTrip({ silent: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    } finally {
      setSavingInfo(false);
    }
  }

  if (loading) {
    return (
      <div className="container section">
        <p className="muted">{fa.common.loading}</p>
      </div>
    );
  }

  if (error && !trip) {
    return (
      <div className="container section">
        <ErrorNotice message={error} onRetry={loadTrip} />
      </div>
    );
  }

  if (!trip) return null;

  const sortedDays = [...trip.days].sort((a, b) => a.day_number - b.day_number);
  const isSetup = sortedDays.length === 0;

  if (isSetup) {
    return (
      <div className="container container-wide section setup-shell">
        <div className="setup-layout">
          <div className="setup-page">
            {error && (
              <div style={{ marginBottom: 12 }}>
                <ErrorNotice message={error} />
              </div>
            )}
            <h1 className="setup-lead">
              {trip.name}
            </h1>
            <p className="setup-lead">{fa.trip.setupLead}</p>
            {suggestedPlanId && <p className="setup-optional-hint">{fa.trip.planFillHint}</p>}
            {trip.start_date && (
              <p className="setup-range num">
                {fa.home.tripCardRange
                  .replace("{start}", formatJalaliSlash(trip.start_date))
                  .replace("{end}", formatJalaliSlash(trip.end_date || trip.start_date))}
              </p>
            )}
            <div className="setup-block">
              <p className="setup-question">{fa.trip.budgetCapLabel}</p>
              <div className="setup-control">
                <TomanAmountField
                  value={budgetCapDraft}
                  onChange={setBudgetCapDraft}
                  placeholder={fa.trip.budgetCapPlaceholder}
                  ariaLabel={fa.trip.budgetCapLabel}
                />
                <span className="setup-unit">{fa.trip.toman}</span>
              </div>
            </div>
            <div className="setup-block">
              <p className="setup-question">{fa.trip.travelersQuestion}</p>
              <div className="setup-control">
                <input
                  className="input input-light"
                  type="number"
                  min={1}
                  max={30}
                  value={travelerDraft}
                  onChange={(e) => setTravelerDraft(e.target.value)}
                  aria-label={fa.trip.travelerCountLabel}
                />
                <span className="setup-unit">{fa.trip.travelerUnit}</span>
              </div>
            </div>
            <div className="setup-block">
              <p className="setup-question">{fa.trip.originQuestion}</p>
              <div className="setup-control">
                <CitySearchField
                  placeholder={fa.trip.originPlaceholder}
                  selected={selectedOriginCity}
                  onSelect={(city) => {
                    setSelectedOriginCity(city);
                    if (city && !originLabel.trim()) setOriginLabel("");
                  }}
                />
              </div>
            </div>
            {selectedOriginCity && (
              <div className="setup-block">
                <p className="setup-question">{fa.trip.originDetailLabel}</p>
                <input
                  className="input input-light"
                  value={originLabel}
                  onChange={(e) => setOriginLabel(e.target.value)}
                  placeholder={fa.trip.originDetailPlaceholder}
                />
                <p className="setup-optional-hint">{fa.trip.originDetailOptionalHint}</p>
              </div>
            )}
            <div className="setup-actions">
              <button className="btn btn-primary" onClick={handleConfirmDayCount} disabled={confirmingDays || skippingToHub}>
                {confirmingDays ? fa.common.loading : fa.trip.confirmDays}
              </button>
              <button
                className="btn btn-outline"
                type="button"
                onClick={handleSkipToHub}
                disabled={confirmingDays || skippingToHub}
              >
                {skippingToHub ? fa.common.loading : fa.trip.skipToHub}
              </button>
            </div>
          </div>
          <Link href="/app" className="nav-text-btn setup-back">
            ← {fa.trip.backToHome}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container container-wide section hub-page">
      <Link href="/app" className="nav-text-btn">
        ← {fa.trip.backToHome}
      </Link>

      <div className="hub-top">
        <div className="hub-top-identity">
          {editingName ? (
            <div className="row" style={{ flex: 1, minWidth: 220 }}>
              <input
                className="input input-light"
                value={nameDraft}
                onChange={(e) => setNameDraft(e.target.value)}
                placeholder={fa.trip.renamePlaceholder}
                autoFocus
              />
              <button className="btn btn-primary btn-sm" onClick={handleSaveName} disabled={savingName}>
                {fa.trip.save}
              </button>
              <button
                className="btn btn-outline btn-sm"
                onClick={() => {
                  setEditingName(false);
                  setNameDraft(trip.name);
                }}
              >
                {fa.trip.cancel}
              </button>
            </div>
          ) : (
            <h1 className="hub-title" onClick={() => setEditingName(true)} title="برای ویرایش نام کلیک کن">
              {trip.name}
            </h1>
          )}
          <Link href={`/trip/${trip.id}/summary`} className="oval-action oval-action-summary">
            {fa.trip.viewSummary}
          </Link>
          <button type="button" className="oval-action oval-action-notes" onClick={() => setNotebookDayId(null)}>
            {fa.notebook.hubButton}
          </button>
          <button
            type="button"
            className={`oval-action ${isTripInfoComplete(trip) ? "oval-action-info" : "oval-action-info-needed"}`}
            onClick={() => void openInfoEditor()}
          >
            {isTripInfoComplete(trip) ? fa.trip.editTripInfo : fa.trip.completeTripInfo}
          </button>
        </div>
        <div className="hub-top-end">
          <TopbarShare tripId={trip.id} buttonClassName="oval-action oval-action-share" />
          <button type="button" className="oval-action oval-action-delete" onClick={handleDeleteTrip}>
            {fa.trip.deleteTrip}
          </button>
        </div>
      </div>

      {error && (
        <div style={{ marginTop: 12 }}>
          <ErrorNotice message={error} />
        </div>
      )}

      {budget?.is_over_budget && (
        <div className="hub-over-budget" role="status">
          <p className="hub-over-budget-title">{fa.budget.overBudgetWarning}</p>
          <p className="hub-over-budget-msg">
            {fa.budget.overBudgetMessage.replace("{amount}", formatToman(budget.over_budget_amount))}
          </p>
          <Link href={`/trip/${trip.id}/budget`} className="btn btn-outline btn-sm">
            {fa.trip.viewBudget}
          </Link>
        </div>
      )}

      <div className="hub-split">
        <section className="hub-days-panel">
          <div className="hub-day-controls">
            <button className="hub-day-chip hub-day-chip-add" type="button" onClick={handleAddDay} disabled={addingDay}>
              {addingDay ? "…" : fa.trip.addOneDay}
            </button>
            <button className="hub-day-chip hub-day-chip-edit" type="button" onClick={openRangeEditor}>
              {fa.trip.editDateRange}
            </button>
          </div>
          <div className={`hub-days${sortedDays.length > 4 ? " is-scrollable" : ""}`}>
            {sortedDays.map((day, index) => {
              const itinerary = buildDayItinerary(day, trip.stays ?? []);
              const stopCount = itinerary.length;
              const preview = itinerary.slice(0, 3);
              const extraStops = stopCount - preview.length;
              const canDelete = sortedDays.length > 1;
              return (
                <Link
                  key={day.id}
                  href={`/trip/${trip.id}/day/${day.id}`}
                  className="hub-day-card"
                  style={{ animationDelay: `${index * 60}ms` }}
                >
                  <DayInfoHover
                    tripId={trip.id}
                    dayId={day.id}
                    onOpen={() => setNotebookDayId(day.id)}
                  />
                  {canDelete ? (
                    <button
                      type="button"
                      className="hub-day-delete"
                      aria-label={fa.trip.deleteThisDay}
                      disabled={removingDayId === day.id}
                      onClick={(event) => {
                        event.preventDefault();
                        event.stopPropagation();
                        void handleRemoveDay(day.id);
                      }}
                    >
                      {removingDayId === day.id ? "…" : "×"}
                    </button>
                  ) : null}
                  <span className="hub-day-title">{formatDayOrdinal(day.day_number)}</span>
                  {dayDateIso(trip.start_date, day.day_number, day.date) && (
                    <span className="hub-day-date num">
                      {formatJalaliSlash(dayDateIso(trip.start_date, day.day_number, day.date))}
                    </span>
                  )}
                  {preview.length > 0 ? (
                    <p className="hub-day-stops">
                      {preview.map((item) => item.name).join(" · ")}
                      {extraStops > 0
                        ? ` ${fa.trip.stopsPreviewMore.replace("{n}", toPersianDigits(extraStops))}`
                        : ""}
                    </p>
                  ) : (
                    <>
                      <span className="chip">
                        {fa.trip.stopsCount.replace("{n}", toPersianDigits(stopCount))}
                      </span>
                      <span className="hub-day-cta">{fa.trip.clickToPlanDay}</span>
                    </>
                  )}
                </Link>
              );
            })}
          </div>
        </section>

        <section className={`hub-budget-panel ${budget?.is_over_budget ? "is-over" : ""}`}>
          {(
            [
              [fa.trip.metricCap, budget?.budget_cap],
              [fa.trip.metricAttractions, budget?.attractions_total ?? 0],
              [fa.trip.metricFood, budget?.dining_total ?? 0],
              [fa.trip.metricLodging, budget?.lodging_total ?? 0],
              [fa.trip.metricExtras, budget?.expenses_total ?? 0],
            ] as const
          ).map(([label, amount]) => (
            <div className="hub-budget-row" key={label}>
              <span>{label}</span>
              <i className="hub-budget-rule" aria-hidden />
              <strong className="hub-budget-value num">{formatToman(amount)}</strong>
            </div>
          ))}
          <div className="hub-budget-row">
            <span className="hub-budget-total-head">
              <Link href={`/trip/${trip.id}/budget`} className="hub-budget-settings">
                {fa.trip.viewBudget}
              </Link>
              {fa.trip.metricTotal}
            </span>
            <i className="hub-budget-rule" aria-hidden />
            <strong className="hub-budget-value num">{formatToman(budget?.grand_total ?? 0)}</strong>
          </div>
        </section>
      </div>
      {editingRange && (
        <AppOverlay className="notebook-overlay" role="dialog" aria-modal="true" aria-label={fa.trip.editDateRange}>
          <div className="notebook-panel range-editor">
            <div className="notebook-head">
              <h2>{fa.trip.editDateRange}</h2>
              <button type="button" className="icon-btn" onClick={() => setEditingRange(false)} aria-label={fa.common.close}>
                ×
              </button>
            </div>
            <JalaliDatePicker
              range
              label={fa.home.dateRangeLabel}
              value={rangeStart}
              endValue={rangeEnd}
              onRangeChange={(start, end) => {
                setRangeStart(start);
                setRangeEnd(end);
              }}
            />
            <div className="notebook-composer-actions" style={{ marginTop: 16 }}>
              <button type="button" className="notebook-save" disabled={savingRange} onClick={handleSaveRange}>
                {savingRange ? fa.common.loading : fa.trip.save}
              </button>
              <button type="button" className="notebook-cancel" onClick={() => setEditingRange(false)}>
                {fa.trip.cancel}
              </button>
            </div>
          </div>
        </AppOverlay>
      )}
      {editingInfo && (
        <AppOverlay className="notebook-overlay" role="dialog" aria-modal="true" aria-label={fa.trip.editTripInfo}>
          <div className="notebook-panel range-editor">
            <div className="notebook-head">
              <h2>{isTripInfoComplete(trip) ? fa.trip.editTripInfo : fa.trip.completeTripInfo}</h2>
              <button type="button" className="icon-btn" onClick={() => setEditingInfo(false)} aria-label={fa.common.close}>
                ×
              </button>
            </div>
            {error && (
              <div style={{ marginBottom: 12 }}>
                <ErrorNotice message={error} />
              </div>
            )}
            <div className="setup-block">
              <p className="setup-question">{fa.trip.budgetCapLabel}</p>
              <div className="setup-control">
                <TomanAmountField
                  value={budgetCapDraft}
                  onChange={setBudgetCapDraft}
                  placeholder={fa.trip.budgetCapPlaceholder}
                  ariaLabel={fa.trip.budgetCapLabel}
                />
                <span className="setup-unit">{fa.trip.toman}</span>
              </div>
            </div>
            <div className="setup-block">
              <p className="setup-question">{fa.trip.travelersQuestion}</p>
              <div className="setup-control">
                <input
                  className="input input-light"
                  type="number"
                  min={1}
                  max={30}
                  value={travelerDraft}
                  onChange={(e) => setTravelerDraft(e.target.value)}
                  aria-label={fa.trip.travelerCountLabel}
                />
                <span className="setup-unit">{fa.trip.travelerUnit}</span>
              </div>
            </div>
            <div className="setup-block">
              <p className="setup-question">{fa.trip.originQuestion}</p>
              <div className="setup-control">
                <CitySearchField
                  placeholder={fa.trip.originPlaceholder}
                  selected={selectedOriginCity}
                  onSelect={(city) => {
                    setSelectedOriginCity(city);
                    if (city && !originLabel.trim()) setOriginLabel("");
                  }}
                />
              </div>
            </div>
            <div className="setup-block">
              <p className="setup-question">{fa.trip.originDetailLabel}</p>
              <input
                className="input input-light"
                value={originLabel}
                onChange={(e) => setOriginLabel(e.target.value)}
                placeholder={fa.trip.originDetailPlaceholder}
              />
              <p className="setup-optional-hint">{fa.trip.originDetailOptionalHint}</p>
            </div>
            <div className="notebook-composer-actions" style={{ marginTop: 8 }}>
              <button type="button" className="notebook-save" disabled={savingInfo} onClick={() => void handleSaveTripInfo()}>
                {savingInfo ? fa.common.loading : fa.trip.save}
              </button>
              <button type="button" className="notebook-cancel" onClick={() => setEditingInfo(false)}>
                {fa.trip.cancel}
              </button>
            </div>
          </div>
        </AppOverlay>
      )}
      {notebookDayId !== undefined && (
        <NotebookDrawer
          tripId={trip.id}
          days={sortedDays}
          lockedDayId={notebookDayId ?? undefined}
          onClose={() => setNotebookDayId(undefined)}
        />
      )}
    </div>
  );
}
