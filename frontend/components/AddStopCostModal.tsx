"use client";

import { useEffect, useState } from "react";
import fa from "@/i18n/fa";
import AppOverlay from "@/components/AppOverlay";
import { groupedTomanFromAmount, parseTomanInput, toPersianDigits } from "@/shared/format";
import TomanAmountField from "@/components/TomanAmountField";

export type StopCostDraft = {
  unitFee: number | null;
  partySize: number;
};

export default function AddStopCostModal({
  placeName,
  catalogFee,
  defaultPartySize,
  onConfirm,
  onCancel,
}: {
  placeName: string;
  catalogFee: number | null | undefined;
  defaultPartySize: number;
  onConfirm: (draft: StopCostDraft) => void | Promise<void>;
  onCancel: () => void;
}) {
  const [unitFeeText, setUnitFeeText] = useState(() => groupedTomanFromAmount(catalogFee ?? null));
  const [partySizeText, setPartySizeText] = useState(String(Math.max(1, defaultPartySize)));
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") onCancel();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel]);

  const partySize = Math.max(1, Number(partySizeText) || 1);
  const unitFee = unitFeeText.trim() === "" ? null : parseTomanInput(unitFeeText);
  const lineTotal = unitFee == null ? null : unitFee * partySize;

  async function handleConfirm() {
    const parsedSize = Number(partySizeText);
    if (!Number.isInteger(parsedSize) || parsedSize < 1) {
      setFormError(fa.trip.costPartySizeRequired);
      return;
    }
    setFormError(null);
    setSaving(true);
    try {
      await onConfirm({
        unitFee,
        partySize: Math.min(50, parsedSize),
      });
    } catch (err) {
      setFormError(err instanceof Error ? err.message : fa.errors.generic);
    } finally {
      setSaving(false);
    }
  }

  return (
    <AppOverlay
      className="notebook-overlay cost-prompt-overlay"
      role="presentation"
      onClick={onCancel}
    >
      <div
        className="notebook-panel cost-prompt-panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="cost-prompt-title"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="notebook-head">
          <h2 id="cost-prompt-title">{placeName}</h2>
          <button type="button" className="icon-btn" onClick={onCancel} aria-label={fa.common.close}>
            ×
          </button>
        </div>

        <label className="cost-prompt-field">
          {fa.trip.costUnitFee}
          <TomanAmountField
            value={unitFeeText}
            onChange={setUnitFeeText}
            placeholder={fa.common.toman}
            ariaLabel={fa.trip.costUnitFee}
          />
        </label>

        <label className="cost-prompt-field">
          {fa.trip.costPartySize}
          <input
            className="input input-light"
            type="number"
            min={1}
            max={50}
            value={partySizeText}
            onChange={(event) => setPartySizeText(event.target.value)}
            aria-label={fa.trip.costPartySize}
          />
        </label>

        {lineTotal == null || unitFee == null ? (
          <p className="cost-prompt-total">{fa.trip.costLineTotal}: {fa.destination.unknownMetric}</p>
        ) : (
          <p className="cost-prompt-total">
            <span>{fa.trip.costLineTotal}:</span>
            <span className="num cost-prompt-formula" dir="ltr">
              {toPersianDigits(partySize)} × {toPersianDigits(groupedTomanFromAmount(unitFee))} ={" "}
              {toPersianDigits(groupedTomanFromAmount(lineTotal))} {fa.common.toman}
            </span>
          </p>
        )}

        {formError ? <p className="notebook-error">{formError}</p> : null}

        <div className="notebook-composer-actions" style={{ marginTop: 16 }}>
          <button type="button" className="notebook-save" disabled={saving} onClick={() => void handleConfirm()}>
            {saving ? fa.common.loading : fa.destination.addToTrip}
          </button>
          <button type="button" className="notebook-cancel" disabled={saving} onClick={onCancel}>
            {fa.trip.cancel}
          </button>
        </div>
      </div>
    </AppOverlay>
  );
}
