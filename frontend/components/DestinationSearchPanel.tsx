"use client";

import { useEffect, useState } from "react";
import fa from "@/i18n/fa";
import { destinationService } from "@/services/destinationService";
import { cachePlaces } from "@/modules/trip/placeCache";
import { rememberDayCity } from "@/modules/trip/dayCityMemory";
import { formatToman, groupedTomanFromAmount, parseTomanInput, placeImageUrls, toPersianDigits } from "@/shared/format";
import { computeLodgingNightlyRate } from "@/shared/lodgingPrice";
import type { City, Place, PlaceKind, TripDay } from "@/shared/types";
import CitySearchField from "@/components/CitySearchField";
import PlaceImage from "@/components/PlaceImage";
import PlaceDetailModal from "@/components/PlaceDetailModal";
import PlaceKeyStats from "@/components/PlaceKeyStats";
import TomanAmountField from "@/components/TomanAmountField";
import AddStopCostModal from "@/components/AddStopCostModal";
import { feeLabelForKind } from "@/shared/placeKind";
import { DAY_CITY_SUGGESTIONS } from "@/modules/trip/dayCitySuggestions";

const KIND_TABS: { id: PlaceKind; label: string }[] = [
  { id: "attraction", label: fa.destination.tabAttractions },
  { id: "dining", label: fa.destination.tabDining },
  { id: "lodging", label: fa.destination.tabLodging },
];

function headingFor(kind: PlaceKind, cityName: string, provinceName?: string | null): string {
  const prefix =
    kind === "lodging"
      ? fa.destination.lodgingInCity
      : kind === "dining"
        ? fa.destination.diningInCity
        : fa.destination.placesInCity;
  return `${prefix} ${cityName}${provinceName ? ` · ${provinceName}` : ""}`;
}

function emptyFor(kind: PlaceKind): string {
  if (kind === "lodging") return fa.destination.noLodgingFound;
  if (kind === "dining") return fa.destination.noDiningFound;
  return fa.destination.noPlacesFound;
}

export type AddPlaceOptions = {
  customEntranceFee?: number | null;
  partySize?: number;
};

export default function DestinationSearchPanel({
  days,
  onAddPlace,
  onAddStay,
  tripId,
  lockedDay,
  variant = "default",
  dayHasLodging = false,
  defaultPartySize = 1,
  initialCityId,
  onCityChange,
}: {
  days: TripDay[];
  onAddPlace: (dayId: string, placeId: string, opts?: AddPlaceOptions) => Promise<void>;
  onAddStay?: (
    placeId: string,
    checkInDayNumber: number,
    nights: number,
    nightlyRate: number | null,
    guestCount: number,
  ) => Promise<void>;
  tripId?: string;
  lockedDay?: TripDay;
  variant?: "default" | "planner";
  dayHasLodging?: boolean;
  defaultPartySize?: number;
  initialCityId?: string;
  onCityChange?: (city: City | null) => void;
}) {
  const [selectedCity, setSelectedCity] = useState<City | null>(null);
  const [kind, setKind] = useState<PlaceKind>("attraction");
  const [places, setPlaces] = useState<Place[]>([]);
  const [loadingPlaces, setLoadingPlaces] = useState(false);
  const [selectedDayByPlace, setSelectedDayByPlace] = useState<Record<string, string>>({});
  const [stayDraftByPlace, setStayDraftByPlace] = useState<
    Record<string, { dayNumber: string; nights: string; guests: string; rate: string }>
  >({});
  const [addingPlaceId, setAddingPlaceId] = useState<string | null>(null);
  const [justAddedId, setJustAddedId] = useState<string | null>(null);
  const [detailPlace, setDetailPlace] = useState<Place | null>(null);
  const [localError, setLocalError] = useState<string | null>(null);
  const [costPrompt, setCostPrompt] = useState<{ place: Place; dayId: string } | null>(null);
  const [pickingCityQuery, setPickingCityQuery] = useState<string | null>(null);

  const targetDays = lockedDay ? [lockedDay] : days;
  const defaultDayNumber = lockedDay?.day_number ?? days[0]?.day_number ?? 1;
  const isPlanner = variant === "planner";
  const distanceDayNumber = lockedDay?.day_number;

  function selectCity(city: City | null) {
    setSelectedCity(city);
    onCityChange?.(city);
    if (tripId && lockedDay) {
      rememberDayCity(tripId, lockedDay.id, city?.id ?? null);
    }
  }

  async function pickSuggestedCity(query: string) {
    setPickingCityQuery(query);
    setLocalError(null);
    try {
      const cities = await destinationService.searchCities(query, tripId, distanceDayNumber);
      const exact = cities.find((city) => city.name === query) ?? cities[0];
      if (exact) selectCity(exact);
      else setLocalError(fa.destination.noCitiesFound);
    } catch {
      setLocalError(fa.errors.generic);
    } finally {
      setPickingCityQuery(null);
    }
  }

  useEffect(() => {
    if (!initialCityId) return;
    let cancelled = false;
    destinationService
      .getCity(initialCityId)
      .then((city) => {
        if (!cancelled) selectCity(city);
      })
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialCityId]);

  useEffect(() => {
    if (!selectedCity) {
      setPlaces([]);
      return;
    }
    let cancelled = false;
    setLoadingPlaces(true);
    setLocalError(null);
    destinationService
      .listPlacesForCity(selectedCity.id, tripId, kind, distanceDayNumber)
      .then((results) => {
        if (cancelled) return;
        cachePlaces(results);
        setPlaces(results);
      })
      .catch(() => {
        if (!cancelled) {
          setPlaces([]);
          setLocalError(fa.errors.generic);
        }
      })
      .finally(() => {
        if (!cancelled) setLoadingPlaces(false);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedCity, tripId, kind, distanceDayNumber]);

  function stayDraft(place: Place) {
    return (
      stayDraftByPlace[place.id] ?? {
        dayNumber: String(defaultDayNumber),
        nights: "1",
        guests: String(Math.max(1, defaultPartySize)),
        rate: groupedTomanFromAmount(place.estimated_entrance_fee),
      }
    );
  }

  function markAdded(placeId: string) {
    setJustAddedId(placeId);
    window.setTimeout(() => {
      setJustAddedId((current) => (current === placeId ? null : current));
    }, 1500);
  }

  function beginAddPlace(place: Place, dayId?: string) {
    const resolvedDayId = dayId || lockedDay?.id || selectedDayByPlace[place.id] || days[0]?.id;
    if (!resolvedDayId) return;
    setLocalError(null);
    setDetailPlace(null);
    setCostPrompt({ place, dayId: resolvedDayId });
  }

  async function confirmCostPrompt(draft: { unitFee: number | null; partySize: number }) {
    if (!costPrompt) return;
    const { place, dayId } = costPrompt;
    setAddingPlaceId(place.id);
    setLocalError(null);
    try {
      await onAddPlace(dayId, place.id, {
        customEntranceFee: draft.unitFee,
        partySize: Math.max(1, draft.partySize),
      });
      markAdded(place.id);
      setCostPrompt(null);
    } catch (err) {
      if (err instanceof Error && (err as Error & { code?: string }).code === "ADD_CANCELLED") {
        setCostPrompt(null);
        return;
      }
      const message = err instanceof Error ? err.message : fa.errors.generic;
      setLocalError(message);
      throw err instanceof Error ? err : new Error(message);
    } finally {
      setAddingPlaceId(null);
    }
  }

  async function handleAdd(place: Place) {
    beginAddPlace(place);
  }

  async function handleAddStay(place: Place) {
    if (!onAddStay) return;
    const draft = stayDraft(place);
    const nights = Number(draft.nights);
    const dayNumber = Number(draft.dayNumber);
    const guests = Math.max(1, Number(draft.guests) || 1);
    const manualRate = draft.rate.trim() === "" ? null : parseTomanInput(draft.rate);
    if (!Number.isInteger(nights) || nights < 1 || !Number.isInteger(dayNumber)) return;

    if (nights > 1) {
      const endDay = dayNumber + nights - 1;
      const msg = fa.trip.stayMultiNightConfirm
        .replace("{start}", toPersianDigits(dayNumber))
        .replace("{end}", toPersianDigits(endDay))
        .replace("{nights}", toPersianDigits(nights));
      if (!window.confirm(msg)) return;
    }

    const computed = computeLodgingNightlyRate(place, guests, manualRate);
    setAddingPlaceId(place.id);
    setLocalError(null);
    try {
      await onAddStay(place.id, dayNumber, nights, computed, guests);
      markAdded(place.id);
    } catch (err) {
      setLocalError(err instanceof Error ? err.message : fa.errors.generic);
    } finally {
      setAddingPlaceId(null);
    }
  }

  const kindTabs = (
    <div className="kind-tabs" role="tablist" aria-label={fa.trip.searchPlacesToAdd}>
      {KIND_TABS.map((tab) => (
        <button
          key={tab.id}
          type="button"
          role="tab"
          aria-selected={kind === tab.id}
          className={`kind-tab ${kind === tab.id ? "is-active" : ""}`}
          onClick={() => setKind(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );

  const results = (
    <>
      {!selectedCity ? (
        isPlanner ? (
          <div className="day-city-suggest-wrap">
            <p className="day-city-suggest-hint">{fa.trip.citySuggestionsHint}</p>
            <div className="day-city-suggest">
              {DAY_CITY_SUGGESTIONS.map((city) => (
                <button
                  key={city.query}
                  type="button"
                  className="day-city-chip"
                  style={{ ["--chip-tone" as string]: city.tone }}
                  disabled={pickingCityQuery != null}
                  onClick={() => void pickSuggestedCity(city.query)}
                >
                  <PlaceImage src={city.image} alt="" className="day-city-chip-image" />
                  <span className="day-city-chip-copy">
                    <strong>{city.label}</strong>
                    <span>{city.landmark}</span>
                  </span>
                </button>
              ))}
            </div>
            {pickingCityQuery && <p className="muted">{fa.common.loading}</p>}
            {localError && <p className="notebook-error">{localError}</p>}
          </div>
        ) : (
          <p className="muted">{null}</p>
        )
      ) : (
        <div>
          <div className="row-between" style={{ marginBottom: 10 }}>
            <strong>{headingFor(kind, selectedCity.name, selectedCity.province_name)}</strong>
            <button
              className="btn-sm btn-outline btn"
              onClick={() => {
                selectCity(null);
                setPlaces([]);
              }}
            >
              {fa.destination.changeCity}
            </button>
          </div>

          {localError && <p className="notebook-error">{localError}</p>}

          {loadingPlaces ? (
            <p className="muted">{fa.common.loading}</p>
          ) : places.length === 0 ? (
            <p className="muted">{emptyFor(kind)}</p>
          ) : (
            <div className="place-result-grid">
              {places.map((place) => {
                const images = placeImageUrls(place);
                const draft = stayDraft(place);
                const guests = Math.max(1, Number(draft.guests) || 1);
                const manualRate = draft.rate.trim() === "" ? null : parseTomanInput(draft.rate);
                const previewRate = computeLodgingNightlyRate(place, guests, manualRate);
                return (
                  <article key={place.id} className="place-result">
                    <button
                      type="button"
                      className="place-result-open"
                      onClick={() => setDetailPlace(place)}
                    >
                      <div className={`place-result-photos ${images.length > 1 ? "has-extra" : ""}`}>
                        <PlaceImage src={images[0] ?? null} alt={place.name} className="place-result-image" />
                        {images[1] && (
                          <PlaceImage src={images[1]} alt="" className="place-result-image place-result-image-side" />
                        )}
                      </div>
                      <p className="place-result-name">{place.name}</p>
                      <p className="place-result-meta">
                        {[place.category, place.address || fa.destination.unknownAddress]
                          .filter(Boolean)
                          .join(" · ")}
                      </p>
                      {place.opening_hours && (
                        <p className="place-result-hours">
                          {fa.destination.hours}: {place.opening_hours}
                        </p>
                      )}
                      {place.description && <p className="place-result-desc">{place.description}</p>}
                      <p className="place-result-more">{fa.destination.tapForDetails}</p>
                    </button>
                    <PlaceKeyStats
                      distanceKm={place.distance_from_origin_km}
                      durationMinutes={place.duration_from_origin_minutes}
                      isDriving={place.distance_is_driving !== false}
                      fee={place.estimated_entrance_fee}
                      feeLabel={feeLabelForKind(place.kind ?? kind)}
                      compact
                    />
                    {kind === "lodging" ? (
                      <div className="stay-card-form">
                        {dayHasLodging ? (
                          <p className="muted" style={{ fontSize: "0.82rem", marginTop: 8 }}>
                            {fa.trip.lodgingAlreadyOnDay}
                          </p>
                        ) : (
                          <>
                            {!lockedDay && (
                              <label>
                                {fa.destination.checkInDay}
                                <select
                                  className="input input-light btn-sm"
                                  value={draft.dayNumber}
                                  onChange={(e) =>
                                    setStayDraftByPlace((prev) => ({
                                      ...prev,
                                      [place.id]: { ...stayDraft(place), dayNumber: e.target.value },
                                    }))
                                  }
                                >
                                  {days.map((d) => (
                                    <option key={d.id} value={d.day_number}>
                                      روز {toPersianDigits(d.day_number)}
                                    </option>
                                  ))}
                                </select>
                              </label>
                            )}
                            <label>
                              {fa.destination.nights}
                              <input
                                className="input input-light btn-sm"
                                type="number"
                                min={1}
                                max={60}
                                value={draft.nights}
                                onChange={(e) =>
                                  setStayDraftByPlace((prev) => ({
                                    ...prev,
                                    [place.id]: { ...stayDraft(place), nights: e.target.value },
                                  }))
                                }
                              />
                            </label>
                            <label>
                              {fa.destination.guests}
                              <input
                                className="input input-light btn-sm"
                                type="number"
                                min={1}
                                max={50}
                                value={draft.guests}
                                onChange={(e) =>
                                  setStayDraftByPlace((prev) => ({
                                    ...prev,
                                    [place.id]: { ...stayDraft(place), guests: e.target.value },
                                  }))
                                }
                              />
                            </label>
                            <TomanAmountField
                              value={draft.rate}
                              onChange={(next) =>
                                setStayDraftByPlace((prev) => ({
                                  ...prev,
                                  [place.id]: { ...stayDraft(place), rate: next },
                                }))
                              }
                              placeholder={fa.budget.stayRatePlaceholder}
                              ariaLabel={fa.destination.nightlyRate}
                            />
                            {previewRate != null && (
                              <p className="muted" style={{ fontSize: "0.8rem", marginTop: 4 }}>
                                {fa.destination.nightlyRateComputed}: {formatToman(previewRate)}
                              </p>
                            )}
                            {justAddedId === place.id ? (
                              <span className="place-result-added">{fa.destination.added}</span>
                            ) : (
                              <button
                                className="btn btn-primary btn-sm"
                                onClick={() => handleAddStay(place)}
                                disabled={addingPlaceId === place.id || days.length === 0}
                              >
                                {addingPlaceId === place.id ? "…" : fa.destination.addStay}
                              </button>
                            )}
                          </>
                        )}
                      </div>
                    ) : (
                      <div className="place-result-actions">
                        {!lockedDay && days.length > 1 && (
                          <select
                            className="input input-light btn-sm"
                            style={{ padding: "8px 10px" }}
                            value={selectedDayByPlace[place.id] || days[0]?.id}
                            onChange={(e) =>
                              setSelectedDayByPlace((prev) => ({ ...prev, [place.id]: e.target.value }))
                            }
                            onClick={(e) => e.stopPropagation()}
                          >
                            {days.map((d) => (
                              <option key={d.id} value={d.id}>
                                روز {d.day_number}
                              </option>
                            ))}
                          </select>
                        )}
                        {justAddedId === place.id ? (
                          <span className="place-result-added">{fa.destination.added}</span>
                        ) : (
                          <button
                            className="btn btn-primary btn-sm"
                            onClick={() => handleAdd(place)}
                            disabled={addingPlaceId === place.id || days.length === 0}
                          >
                            {addingPlaceId === place.id ? "…" : fa.destination.addToTrip}
                          </button>
                        )}
                      </div>
                    )}
                  </article>
                );
              })}
            </div>
          )}
        </div>
      )}
    </>
  );

  return (
    <div className={isPlanner ? "day-search-panel search-pill-wrap" : "search-panel search-pill-wrap"}>
      {isPlanner ? (
        <>
          <div className="day-search-toolbar">
            <p className="day-search-heading">{fa.trip.searchPlacesToAdd}</p>
            {kindTabs}
          </div>
          <div className="day-search-field">
            <CitySearchField
              placeholder={
                selectedCity ? fa.destination.searchPlaceholder : fa.destination.searchOtherCities
              }
              selected={selectedCity}
              onSelect={selectCity}
              tripId={tripId}
              dayNumber={distanceDayNumber}
            />
          </div>
          <div className="day-search-results">{results}</div>
        </>
      ) : (
        <>
          <CitySearchField
            placeholder={fa.destination.searchPlaceholder}
            selected={selectedCity}
            onSelect={selectCity}
            tripId={tripId}
            dayNumber={distanceDayNumber}
          />
          {kindTabs}
          {selectedCity && <div style={{ marginTop: 16 }}>{results}</div>}
        </>
      )}

      {detailPlace && (
        <PlaceDetailModal
          initialPlace={detailPlace}
          days={targetDays}
          onClose={() => setDetailPlace(null)}
          onBeginAddPlace={(dayId, place) => beginAddPlace(place, dayId)}
          onAddStay={
            dayHasLodging
              ? undefined
              : onAddStay
                ? async (placeId, checkInDayNumber, nights, nightlyRate, guestCount) => {
                    setLocalError(null);
                    try {
                      await onAddStay(placeId, checkInDayNumber, nights, nightlyRate, guestCount);
                      markAdded(placeId);
                    } catch (err) {
                      const message = err instanceof Error ? err.message : fa.errors.generic;
                      setLocalError(message);
                      throw err instanceof Error ? err : new Error(message);
                    }
                  }
                : undefined
          }
          defaultPartySize={defaultPartySize}
        />
      )}

      {costPrompt && (
        <AddStopCostModal
          placeName={costPrompt.place.name}
          catalogFee={costPrompt.place.estimated_entrance_fee}
          defaultPartySize={defaultPartySize}
          onCancel={() => setCostPrompt(null)}
          onConfirm={confirmCostPrompt}
        />
      )}
    </div>
  );
}
