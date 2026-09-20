"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import fa from "@/i18n/fa";
import { shareService } from "@/services/shareService";
import { ApiError } from "@/services/apiClient";
import AppOverlay from "@/components/AppOverlay";

export default function TopbarShare({
  tripId: tripIdProp,
  buttonClassName,
}: {
  tripId?: string;
  buttonClassName?: string;
}) {
  const pathname = usePathname();
  const match = pathname?.match(/^\/trip\/([^/]+)/);
  const tripId = tripIdProp ?? match?.[1] ?? null;
  const [busy, setBusy] = useState(false);
  const [open, setOpen] = useState(false);
  const [url, setUrl] = useState("");
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  if (pathname?.startsWith("/share/") || !tripId) return null;

  async function copyText(value: string) {
    try {
      await navigator.clipboard.writeText(value);
      return true;
    } catch {
      try {
        const field = document.createElement("textarea");
        field.value = value;
        field.setAttribute("readonly", "");
        field.style.position = "fixed";
        field.style.opacity = "0";
        document.body.appendChild(field);
        field.select();
        const ok = document.execCommand("copy");
        document.body.removeChild(field);
        return ok;
      } catch {
        return false;
      }
    }
  }

  async function handleShare() {
    if (!tripId) return;
    setBusy(true);
    setError(null);
    setCopied(false);
    try {
      const result = await shareService.enableShare(tripId);
      const shareUrl = `${window.location.origin}${result.path}`;
      setUrl(shareUrl);
      setOpen(true);
      const ok = await copyText(shareUrl);
      setCopied(ok);
    } catch (err) {
      setUrl("");
      setOpen(true);
      setError(err instanceof ApiError ? err.message : fa.profile.shareFailed);
    } finally {
      setBusy(false);
    }
  }

  async function handleCopy() {
    if (!url) return;
    setCopied(await copyText(url));
  }

  return (
    <div className="topbar-share">
      <button
        type="button"
        className={buttonClassName ?? "topbar-share-btn"}
        onClick={handleShare}
        disabled={busy}
        title={fa.profile.shareHint}
      >
        {busy ? fa.common.loading : fa.profile.share}
      </button>

      {open && (
        <AppOverlay
          className="notebook-overlay"
          role="presentation"
          onClick={() => setOpen(false)}
        >
          <div
            className="share-dialog"
            role="dialog"
            aria-modal="true"
            aria-label={fa.profile.shareThisTrip}
            onClick={(event) => event.stopPropagation()}
          >
            <div className="share-dialog-head">
              <h2>{fa.profile.shareThisTrip}</h2>
              <button type="button" className="icon-btn" onClick={() => setOpen(false)} aria-label={fa.common.close}>
                ×
              </button>
            </div>
            <p className="muted">{fa.profile.shareHint}</p>
            {error && <p className="notebook-error">{error}</p>}
            {url && (
              <>
                <input className="input" readOnly value={url} onFocus={(event) => event.currentTarget.select()} />
                <div className="share-dialog-actions">
                  <button type="button" className="btn btn-primary" onClick={handleCopy}>
                    {copied ? fa.profile.shareCopiedShort : fa.common.copy}
                  </button>
                  <a className="btn btn-outline" href={url} target="_blank" rel="noreferrer">
                    {fa.profile.shareOpen}
                  </a>
                </div>
              </>
            )}
          </div>
        </AppOverlay>
      )}
    </div>
  );
}
