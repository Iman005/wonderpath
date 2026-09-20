"use client";

import { useRef, useState } from "react";
import fa from "@/i18n/fa";
import { notebookService } from "@/services/notebookService";
import type { PackingList, TripNote } from "@/shared/types";

export default function DayInfoHover({
  tripId,
  dayId,
  onOpen,
}: {
  tripId: string;
  dayId: string;
  onOpen: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [notes, setNotes] = useState<TripNote[]>([]);
  const [lists, setLists] = useState<PackingList[]>([]);
  const [loaded, setLoaded] = useState(false);
  const timer = useRef<number | null>(null);

  async function loadPreview() {
    if (loaded) return;
    try {
      const [nextNotes, nextLists] = await Promise.all([
        notebookService.listNotes(tripId, dayId),
        notebookService.listPackingLists(tripId, dayId),
      ]);
      setNotes(nextNotes.slice(0, 3));
      setLists(nextLists.slice(0, 2));
      setLoaded(true);
    } catch {
      setLoaded(true);
    }
  }

  function show() {
    if (timer.current) window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => {
      setOpen(true);
      void loadPreview();
    }, 180);
  }

  function hide() {
    if (timer.current) window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => setOpen(false), 120);
  }

  return (
    <span
      className="hub-day-info-wrap"
      onMouseEnter={show}
      onMouseLeave={hide}
      onFocus={show}
      onBlur={hide}
    >
      <button
        type="button"
        className="hub-day-info"
        aria-label={fa.notebook.dayInfo}
        onClick={(event) => {
          event.preventDefault();
          event.stopPropagation();
          onOpen();
        }}
      >
        i
      </button>
      {open && (
        <div className="hub-day-cloud" role="tooltip">
          {!loaded ? (
            <p className="muted">{fa.common.loading}</p>
          ) : notes.length === 0 && lists.length === 0 ? (
            <p className="muted">{fa.notebook.hoverEmpty}</p>
          ) : (
            <>
              {notes.map((note) => (
                <p key={note.id} className="hub-day-cloud-line">
                  {note.body.slice(0, 80)}
                  {note.body.length > 80 ? "…" : ""}
                </p>
              ))}
              {lists.map((list) => (
                <p key={list.id} className="hub-day-cloud-line">
                  {list.title}: {list.items.slice(0, 3).map((item) => item.label).join("، ")}
                  {list.items.length > 3 ? "…" : ""}
                </p>
              ))}
            </>
          )}
        </div>
      )}
    </span>
  );
}
