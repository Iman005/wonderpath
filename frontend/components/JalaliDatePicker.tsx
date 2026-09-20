"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import fa from "@/i18n/fa";
import AppOverlay from "@/components/AppOverlay";
import { formatJalaliSlash, toPersianDigits } from "@/shared/format";
import {
  JALALI_MONTHS,
  JALALI_WEEKDAYS,
  gregorianToJalali,
  isoToJalali,
  jalaliMonthLength,
  jalaliToGregorian,
  jalaliToIso,
} from "@/shared/jalali";

function weekdayOfJalali(jy: number, jm: number, jd: number): number {
  const [gy, gm, gd] = jalaliToGregorian(jy, jm, jd);
  return (new Date(gy, gm - 1, gd).getDay() + 1) % 7;
}

function jalaliLessThan(a: [number, number, number], b: [number, number, number]): boolean {
  if (a[0] !== b[0]) return a[0] < b[0];
  if (a[1] !== b[1]) return a[1] < b[1];
  return a[2] < b[2];
}

function jalaliEqual(a: [number, number, number], b: [number, number, number]): boolean {
  return a[0] === b[0] && a[1] === b[1] && a[2] === b[2];
}

function jalaliInRange(
  day: [number, number, number],
  start: [number, number, number],
  end: [number, number, number],
): boolean {
  return !jalaliLessThan(day, start) && !jalaliLessThan(end, day);
}

function orderedIso(a: string, b: string): [string, string] {
  return a <= b ? [a, b] : [b, a];
}

export default function JalaliDatePicker({
  value,
  onChange,
  endValue,
  onRangeChange,
  label,
  minDate,
  range = false,
}: {
  value: string;
  onChange?: (isoDate: string) => void;
  endValue?: string;
  onRangeChange?: (startIso: string, endIso: string) => void;
  label: string;
  minDate?: string;
  range?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [draftStart, setDraftStart] = useState<string | null>(null);
  const [draftEnd, setDraftEnd] = useState<string | null>(null);
  const [hoverIso, setHoverIso] = useState<string | null>(null);
  const wrapRef = useRef<HTMLDivElement | null>(null);
  const popRef = useRef<HTMLDivElement | null>(null);
  const selected = value
    ? isoToJalali(value)
    : gregorianToJalali(new Date().getFullYear(), new Date().getMonth() + 1, new Date().getDate());
  const [viewYear, setViewYear] = useState(selected[0]);
  const [viewMonth, setViewMonth] = useState(selected[1]);

  useEffect(() => {
    if (!open) return;
    function onDocClick(event: MouseEvent) {
      const target = event.target as Node;
      if (wrapRef.current?.contains(target) || popRef.current?.contains(target)) return;
      setOpen(false);
    }
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onDocClick);
    window.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDocClick);
      window.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const cells = useMemo(() => {
    const length = jalaliMonthLength(viewYear, viewMonth);
    const offset = weekdayOfJalali(viewYear, viewMonth, 1);
    const blanks = Array.from({ length: offset }, () => 0);
    const days = Array.from({ length }, (_, i) => i + 1);
    return [...blanks, ...days];
  }, [viewYear, viewMonth]);

  const [sy, sm, sd] = selected;
  const today = gregorianToJalali(new Date().getFullYear(), new Date().getMonth() + 1, new Date().getDate());
  const minJalali = minDate ? isoToJalali(minDate) : null;

  let rangeStartJalali: [number, number, number] | null = null;
  let rangeEndJalali: [number, number, number] | null = null;
  if (range && draftStart) {
    const pair = draftEnd
      ? orderedIso(draftStart, draftEnd)
      : hoverIso
        ? orderedIso(draftStart, hoverIso)
        : [draftStart, draftStart];
    rangeStartJalali = isoToJalali(pair[0]);
    rangeEndJalali = isoToJalali(pair[1]);
  } else if (range && value && endValue) {
    rangeStartJalali = isoToJalali(value);
    rangeEndJalali = isoToJalali(endValue);
  }

  function shiftMonth(delta: number) {
    let month = viewMonth + delta;
    let year = viewYear;
    if (month < 1) {
      month = 12;
      year -= 1;
    } else if (month > 12) {
      month = 1;
      year += 1;
    }
    setViewYear(year);
    setViewMonth(month);
  }

  function resetDraft() {
    setDraftStart(null);
    setDraftEnd(null);
    setHoverIso(null);
  }

  function pick(day: number) {
    if (minJalali && jalaliLessThan([viewYear, viewMonth, day], minJalali)) return;
    const iso = jalaliToIso(viewYear, viewMonth, day);
    if (!range) {
      onChange?.(iso);
      setOpen(false);
      return;
    }
    if (!draftStart || draftEnd) {
      setDraftStart(iso);
      setDraftEnd(null);
      return;
    }
    const [start, end] = orderedIso(draftStart, iso);
    setDraftStart(start);
    setDraftEnd(end);
  }

  function confirmRange() {
    if (!draftStart || !draftEnd) return;
    onRangeChange?.(draftStart, draftEnd);
    resetDraft();
    setOpen(false);
  }

  function cancelDraft() {
    resetDraft();
    setOpen(false);
  }

  const canConfirm = Boolean(range && draftStart && draftEnd);
  const triggerText = range
    ? value && endValue
      ? `${formatJalaliSlash(value)} تا ${formatJalaliSlash(endValue)}`
      : fa.trip.dateRangeHint
    : toPersianDigits(`${sy}/${String(sm).padStart(2, "0")}/${String(sd).padStart(2, "0")}`);

  return (
    <div className="jalali-field" ref={wrapRef}>
      <span className="hero-field-label">{label}</span>
      <button
        type="button"
        className="input jalali-trigger"
        onClick={() => {
          setViewYear(sy);
          setViewMonth(sm);
          resetDraft();
          if (range && value && endValue) {
            setDraftStart(value);
            setDraftEnd(endValue);
          }
          setOpen((prev) => !prev);
        }}
        aria-label={label}
      >
        {triggerText}
        {!range && <span className="jalali-trigger-month">{JALALI_MONTHS[sm - 1]}</span>}
      </button>
      {open && (
        <AppOverlay
          className="jalali-pop-overlay"
          role="presentation"
          onClick={() => {
            resetDraft();
            setOpen(false);
          }}
        >
            <div
              className="jalali-pop"
              ref={popRef}
              role="dialog"
              aria-modal="true"
              aria-label={label}
              onClick={(event) => event.stopPropagation()}
            >
              <div className="jalali-pop-head">
                <strong>{label}</strong>
                <button
                  type="button"
                  className="icon-btn"
                  onClick={() => {
                    resetDraft();
                    setOpen(false);
                  }}
                  aria-label={fa.common.close}
                >
                  ×
                </button>
              </div>
              {range && (
                <p className="jalali-range-hint">
                  {draftStart && !draftEnd ? fa.trip.pickEndDate : fa.trip.dateRangeHint}
                </p>
              )}
              <div className="jalali-nav">
                <button type="button" className="icon-btn" onClick={() => shiftMonth(1)} aria-label="ماه بعد">
                  ‹
                </button>
                <strong>
                  {JALALI_MONTHS[viewMonth - 1]} {toPersianDigits(viewYear)}
                </strong>
                <button type="button" className="icon-btn" onClick={() => shiftMonth(-1)} aria-label="ماه قبل">
                  ›
                </button>
              </div>
              <div className="jalali-grid">
                {JALALI_WEEKDAYS.map((d) => (
                  <span key={d} className="jalali-dow">
                    {d}
                  </span>
                ))}
                {cells.map((day, index) => {
                  if (day === 0) return <span key={`e-${index}`} />;
                  const current: [number, number, number] = [viewYear, viewMonth, day];
                  const iso = jalaliToIso(viewYear, viewMonth, day);
                  const disabled = Boolean(minJalali && jalaliLessThan(current, minJalali));
                  const isStart = Boolean(rangeStartJalali && jalaliEqual(current, rangeStartJalali));
                  const isEnd = Boolean(rangeEndJalali && jalaliEqual(current, rangeEndJalali));
                  const inRange = Boolean(
                    range && rangeStartJalali && rangeEndJalali && jalaliInRange(current, rangeStartJalali, rangeEndJalali),
                  );
                  const isToday = jalaliEqual(current, today);
                  return (
                    <button
                      key={day}
                      type="button"
                      disabled={disabled}
                      className={`jalali-day${isStart || isEnd ? " is-selected" : ""}${inRange && !isStart && !isEnd ? " is-in-range" : ""}${isToday ? " is-today" : ""}${disabled ? " is-disabled" : ""}`}
                      onClick={() => pick(day)}
                      onMouseEnter={() => {
                        if (range && draftStart && !draftEnd) setHoverIso(iso);
                      }}
                      onMouseLeave={() => setHoverIso(null)}
                    >
                      {toPersianDigits(day)}
                    </button>
                  );
                })}
              </div>
              {range && (
                <div className="jalali-confirm-row">
                  <button type="button" className="btn btn-primary btn-sm" disabled={!canConfirm} onClick={confirmRange}>
                    {fa.trip.confirmRange}
                  </button>
                  <button type="button" className="btn btn-outline btn-sm" onClick={cancelDraft}>
                    {fa.trip.cancel}
                  </button>
                </div>
              )}
            </div>
        </AppOverlay>
      )}
    </div>
  );
}
