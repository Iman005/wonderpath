"use client";

import { useEffect, useState } from "react";
import fa from "@/i18n/fa";
import { destinationService } from "@/services/destinationService";
import { cachePlaces } from "@/modules/trip/placeCache";
import { groupedTomanFromAmount, parseTomanInput, placeImageUrls, toPersianDigits, formatToman } from "@/shared/format";
import { computeLodgingNightlyRate } from "@/shared/lodgingPrice";
import { feeLabelForKind, isLodging } from "@/shared/placeKind";
import type { Place, PlaceDetail, TripDay } from "@/shared/types";
import PlaceImage from "@/components/PlaceImage";
import PlaceKeyStats from "@/components/PlaceKeyStats";
import TomanAmountField from "@/components/TomanAmountField";
import AppOverlay from "@/components/AppOverlay";

export default function PlaceDetailModal({
  initialPlace,
  days,
  onClose,
  onBeginAddPlace,
  onAddStay,
  allowAdd = true,
  defaultPartySize = 1,
}: {
  initialPlace: Place;
  days: TripDay[];
  onClose: () => void;
  /** Opens the shared cost/party prompt (attraction & dining). */
  onBeginAddPlace?: (dayId: string, place: Place) => void;
  onAddStay?: (
    placeId: string,
    checkInDayNumber: number,
    nights: number,
    nightlyRate: number | null,
    guestCount: number,
  ) => Promise<void>;
  allowAdd?: boolean;
  defaultPartySize?: number;
}) {
  const [detail, setDetail] = useState<Place | PlaceDetail>(initialPlace);
  const [activeImage, setActiveImage] = useState(0);
  const [selectedDayId, setSelectedDayId] = useState(days[0]?.id ?? "");
  const [checkInDay, setCheckInDay] = useState(String(days[0]?.day_number ?? 1));
  const [nights, setNights] = useState("1");
  const [guests, setGuests] = useState(String(Math.max(1, defaultPartySize)));
  const [stayRate, setStayRate] = useState(() => groupedTomanFromAmount(initialPlace.estimated_entrance_fee));
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState(false);
  const [addError, setAddError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    destinationService
      .getPlace(initialPlace.id)
      .then((result) => {
        if (cancelled) return;
        cachePlaces([result]);
        setDetail({
          ...result,
          distance_from_origin_km: initialPlace.distance_from_origin_km ?? result.distance_from_origin_km,
          duration_from_origin_minutes:
            initialPlace.duration_from_origin_minutes ?? result.duration_from_origin_minutes,
          distance_is_driving: initialPlace.distance_is_driving ?? result.distance_is_driving,
        });
        setActiveImage(0);
        setStayRate((current) => current || groupedTomanFromAmount(result.estimated_entrance_fee));
      })
      .catch(() => {
        /* keep the list payload if the detail call fails */
      });
    return () => {
      cancelled = true;
    };
  }, [initialPlace.id]);

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("keydown", onKey);
    };
  }, [onClose]);

  const images = placeImageUrls(detail);
  const currentImage = images[activeImage] ?? detail.image;
  const cityName = "city_name" in detail ? detail.city_name : null;
  const provinceName = "province_name" in detail ? detail.province_name : null;
  const placeLabel = [cityName, provinceName].filter(Boolean).join(" · ");
  const guestCount = Math.max(1, Number(guests) || 1);
  const manualRate = stayRate.trim() === "" ? null : parseTomanInput(stayRate);
  const previewRate = computeLodgingNightlyRate(detail, guestCount, manualRate);

  async function handleAdd() {
    if (isLodging(detail.kind)) {
      if (!onAddStay) return;
      const nightCount = Number(nights);
      const dayNumber = Number(checkInDay);
      if (!Number.isInteger(nightCount) || nightCount < 1 || !Number.isInteger(dayNumber)) return;
      if (nightCount > 1) {
        const endDay = dayNumber + nightCount - 1;
        const msg = fa.trip.stayMultiNightConfirm
          .replace("{start}", toPersianDigits(dayNumber))
          .replace("{end}", toPersianDigits(endDay))
          .replace("{nights}", toPersianDigits(nightCount));
        if (!window.confirm(msg)) return;
      }
      setAdding(true);
      setAddError(null);
      try {
        await onAddStay(detail.id, dayNumber, nightCount, previewRate, guestCount);
        setAdded(true);
      } catch (err) {
        if (err instanceof Error && (err as Error & { code?: string }).code === "ADD_CANCELLED") return;
        setAddError(err instanceof Error ? err.message : fa.errors.generic);
      } finally {
        setAdding(false);
      }
      return;
    }
    if (!selectedDayId || !onBeginAddPlace) return;
    onBeginAddPlace(selectedDayId, { ...detail, id: detail.id });
  }

  return (
    <AppOverlay className="modal-overlay" onClick={onClose} role="presentation">
      <div
        className="place-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="place-modal-title"
        onClick={(event) => event.stopPropagation()}
      >
        <button className="place-modal-close" type="button" onClick={onClose} aria-label={fa.common.close}>
          ×
        </button>

        {images.length > 0 && (
          <div className="place-modal-gallery">
            <PlaceImage src={currentImage} alt={detail.name} className="place-modal-hero" />
            {images.length > 1 && (
              <div className="place-modal-thumbs">
                {images.map((src, index) => (
                  <button
                    key={src}
                    type="button"
                    className={`place-modal-thumb ${index === activeImage ? "is-active" : ""}`}
                    onClick={() => setActiveImage(index)}
                    aria-label={`${fa.destination.photos} ${toPersianDigits(index + 1)}`}
                  >
                    <PlaceImage src={src} alt="" className="place-modal-thumb-img" />
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="place-modal-body">
          <p className="place-modal-kicker">{placeLabel || detail.category}</p>
          <h2 id="place-modal-title" className="place-modal-title">
            {detail.name}
          </h2>
          {detail.catalog?.stars ? (
            <p className="place-modal-stars">
              {toPersianDigits(detail.catalog.stars)} {fa.destination.stars}
            </p>
          ) : null}
          {detail.description && <p className="place-modal-desc">{detail.description}</p>}

          {"identity" in detail && detail.identity && (
            <section className="place-modal-history">
              <h3>{fa.destination.whatItIs}</h3>
              <p>{detail.identity}</p>
            </section>
          )}

          {"historical_era" in detail && detail.historical_era && (
            <section className="place-modal-history">
              <h3>{fa.destination.historicalEra}</h3>
              <p>{detail.historical_era}</p>
            </section>
          )}

          {"notable_events" in detail && detail.notable_events.length > 0 && (
            <section className="place-modal-history">
              <h3>{fa.destination.notableEvents}</h3>
              <ul>
                {detail.notable_events.map((event) => (
                  <li key={event}>{event}</li>
                ))}
              </ul>
            </section>
          )}

          <PlaceKeyStats
            distanceKm={detail.distance_from_origin_km}
            durationMinutes={detail.duration_from_origin_minutes}
            isDriving={detail.distance_is_driving !== false}
            fee={detail.estimated_entrance_fee}
            feeLabel={feeLabelForKind(detail.kind)}
          />

          <dl className="place-modal-facts">
            {detail.category && (
              <div>
                <dt>{fa.destination.category}</dt>
                <dd>{detail.category}</dd>
              </div>
            )}
            <div>
              <dt>{fa.destination.address}</dt>
              <dd>{detail.address || fa.destination.unknownAddress}</dd>
            </div>
            {detail.opening_hours && (
              <div>
                <dt>{fa.destination.hours}</dt>
                <dd>{detail.opening_hours}</dd>
              </div>
            )}
          </dl>

          {detail.catalog?.is_demo && (
            <p className="place-modal-demo-note">{fa.destination.demoPricesNote}</p>
          )}

          {detail.catalog && detail.catalog.amenities.length > 0 && (
            <section className="place-modal-history">
              <h3>{fa.destination.amenities}</h3>
              <p>{detail.catalog.amenities.join(" · ")}</p>
            </section>
          )}

          {detail.catalog && detail.catalog.rooms.length > 0 && (
            <section className="place-modal-history">
              <h3>{fa.destination.rooms}</h3>
              <ul className="catalog-list">
                {detail.catalog.rooms.map((room) => (
                  <li key={room.name} className="catalog-row">
                    <span>{room.name}</span>
                    <span className="catalog-price">{formatToman(room.price)}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {detail.catalog && detail.catalog.menu.length > 0 && (
            <section className="place-modal-history">
              <h3>{fa.destination.menu}</h3>
              <ul className="catalog-list">
                {detail.catalog.menu.map((item) => (
                  <li key={`${item.section}-${item.name}`} className="catalog-row">
                    <span>
                      <span className="catalog-section">{item.section}</span>
                      {item.name}
                    </span>
                    <span className="catalog-price">{formatToman(item.price)}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {detail.visit_tip && (
            <p className="place-modal-tip">
              <strong>{fa.destination.visitTip}: </strong>
              {detail.visit_tip}
            </p>
          )}

          {allowAdd && (
            <div className="place-modal-actions">
              {addError ? <p className="notebook-error">{addError}</p> : null}
              {isLodging(detail.kind) && !onAddStay ? (
                <p className="muted" style={{ margin: 0 }}>
                  {fa.trip.lodgingAlreadyOnDay}
                </p>
              ) : isLodging(detail.kind) ? (
                <>
                  <select
                    className="input input-light"
                    value={checkInDay}
                    onChange={(e) => setCheckInDay(e.target.value)}
                    aria-label={fa.destination.checkInDay}
                  >
                    {days.map((d) => (
                      <option key={d.id} value={d.day_number}>
                        {fa.destination.checkInDay} {toPersianDigits(d.day_number)}
                      </option>
                    ))}
                  </select>
                  <input
                    className="input input-light"
                    type="number"
                    min={1}
                    max={60}
                    value={nights}
                    onChange={(e) => setNights(e.target.value)}
                    aria-label={fa.destination.nights}
                  />
                  <input
                    className="input input-light"
                    type="number"
                    min={1}
                    max={50}
                    value={guests}
                    onChange={(e) => setGuests(e.target.value)}
                    aria-label={fa.destination.guests}
                  />
                  <TomanAmountField
                    value={stayRate}
                    onChange={setStayRate}
                    placeholder={fa.budget.stayRatePlaceholder}
                    ariaLabel={fa.destination.nightlyRate}
                  />
                  {previewRate != null && (
                    <p className="muted" style={{ margin: 0, fontSize: "0.85rem" }}>
                      {fa.destination.nightlyRateComputed}: {formatToman(previewRate)}
                    </p>
                  )}
                </>
              ) : (
                days.length > 1 && (
                  <select
                    className="input input-light"
                    value={selectedDayId}
                    onChange={(e) => setSelectedDayId(e.target.value)}
                    aria-label={fa.trip.addingToDay}
                  >
                    {days.map((d) => (
                      <option key={d.id} value={d.id}>
                        روز {toPersianDigits(d.day_number)}
                      </option>
                    ))}
                  </select>
                )
              )}
              {added ? (
                <span className="place-result-added">{fa.destination.added}</span>
              ) : isLodging(detail.kind) && !onAddStay ? null : (
                <button
                  className="btn btn-primary"
                  type="button"
                  onClick={handleAdd}
                  disabled={adding || days.length === 0 || (isLodging(detail.kind) ? !onAddStay : !onBeginAddPlace)}
                >
                  {adding ? "…" : isLodging(detail.kind) ? fa.destination.addStay : fa.destination.addToTrip}
                </button>
              )}
              <button className="btn btn-outline" type="button" onClick={onClose}>
                {fa.common.close}
              </button>
            </div>
          )}
          {!allowAdd && (
            <div className="place-modal-actions">
              <button className="btn btn-outline" type="button" onClick={onClose}>
                {fa.common.close}
              </button>
            </div>
          )}
        </div>
      </div>
    </AppOverlay>
  );
}
