"use client";

import { useState } from "react";
import fa from "@/i18n/fa";
import { formatToman, toPersianDigits } from "@/shared/format";
import { asPlaceKind } from "@/shared/placeKind";
import type { TripDay, TripStay } from "@/shared/types";

export type DayItineraryItem =
  | { kind: "place"; id: string; name: string; placeKind: string; fee: number | null }
  | { kind: "stay"; id: string; name: string; placeKind: "lodging"; fee: number | null };

function stayCoversDay(stay: TripStay, dayNumber: number): boolean {
  return stay.check_in_day_number <= dayNumber && dayNumber < stay.check_in_day_number + stay.nights;
}

export function buildDayItinerary(day: TripDay, stays: TripStay[]): DayItineraryItem[] {
  const slots: { index: number; item: DayItineraryItem }[] = [];
  for (const tp of day.trip_places) {
    slots.push({
      index: tp.order_index,
      item: {
        kind: "place",
        id: tp.id,
        name: tp.place_name || fa.budget.unnamedPlace,
        placeKind: asPlaceKind(tp.place_kind),
        fee: tp.custom_entrance_fee,
      },
    });
  }
  for (const stay of stays) {
    if (!stayCoversDay(stay, day.day_number)) continue;
    slots.push({
      index: stay.sort_index ?? 0,
      item: {
        kind: "stay",
        id: stay.id,
        name: stay.place_name || fa.budget.unnamedPlace,
        placeKind: "lodging",
        fee: stay.nightly_rate,
      },
    });
  }
  return slots.sort((a, b) => a.index - b.index).map((slot) => slot.item);
}

function kindLabel(kind: string): string {
  if (kind === "dining") return fa.trip.kindDining;
  if (kind === "lodging") return fa.trip.kindLodging;
  return fa.trip.kindAttraction;
}

function moveItem(items: DayItineraryItem[], from: number, to: number): DayItineraryItem[] {
  const next = [...items];
  const [moved] = next.splice(from, 1);
  next.splice(to, 0, moved);
  return next;
}

export default function DayPlanColumn({
  items,
  onReorder,
  onRemove,
  variant = "preview",
  onOpenTicket,
}: {
  items: DayItineraryItem[];
  onReorder: (items: DayItineraryItem[]) => Promise<void>;
  onRemove: (item: DayItineraryItem) => Promise<void>;
  variant?: "preview" | "ticket";
  onOpenTicket?: () => void;
}) {
  const [dragIndex, setDragIndex] = useState<number | null>(null);
  const [overIndex, setOverIndex] = useState<number | null>(null);
  const isTicket = variant === "ticket";

  return (
    <section
      className={`day-plan-group day-plan-unified${onOpenTicket && !isTicket ? " is-expandable" : ""}${isTicket ? " is-ticket" : ""}`}
      onClick={
        onOpenTicket && !isTicket
          ? (event) => {
              const target = event.target as HTMLElement;
              if (target.closest(".stop-actions, button, a")) return;
              onOpenTicket();
            }
          : undefined
      }
    >
      <div className="day-plan-head">
        <h3>{fa.trip.selectedStops}</h3>
        {onOpenTicket && !isTicket ? (
          <button
            type="button"
            className="day-plan-expand-btn"
            onClick={(event) => {
              event.stopPropagation();
              onOpenTicket();
            }}
            aria-label={fa.trip.expandDayPlan}
            title={fa.trip.expandDayPlan}
          >
            ↗
          </button>
        ) : null}
      </div>
      {items.length === 0 ? (
        <p className="muted">{fa.trip.dayStopsEmpty}</p>
      ) : (
        <>
          <p className="day-plan-hint">{fa.trip.reorderHint}</p>
          <ol className="day-plan-track route-stitch">
            {items.map((item, index) => (
              <li
                key={`${item.kind}-${item.id}`}
                className={`day-plan-item${dragIndex === index ? " is-dragging" : ""}${overIndex === index ? " is-drop-target" : ""}`}
                style={{ animationDelay: `${index * 50}ms` }}
                draggable
                onDragStart={(event) => {
                  setDragIndex(index);
                  event.dataTransfer.effectAllowed = "move";
                  event.dataTransfer.setData("text/plain", String(index));
                }}
                onDragOver={(event) => {
                  event.preventDefault();
                  event.dataTransfer.dropEffect = "move";
                  if (overIndex !== index) setOverIndex(index);
                }}
                onDragLeave={() => {
                  if (overIndex === index) setOverIndex(null);
                }}
                onDrop={(event) => {
                  event.preventDefault();
                  const from = dragIndex ?? Number(event.dataTransfer.getData("text/plain"));
                  setDragIndex(null);
                  setOverIndex(null);
                  if (Number.isNaN(from) || from === index) return;
                  void onReorder(moveItem(items, from, index));
                }}
                onDragEnd={() => {
                  setDragIndex(null);
                  setOverIndex(null);
                }}
              >
                <span className="stop-marker">{toPersianDigits(index + 1)}</span>
                <div className="day-plan-item-body">
                  <p className="day-plan-item-name">{item.name}</p>
                  <p className="day-plan-item-meta">
                    <span className={`kind-pill kind-pill-${item.placeKind}`}>{kindLabel(item.placeKind)}</span>
                    <span className="num">{formatToman(item.fee)}</span>
                  </p>
                </div>
                <div
                  className="stop-actions"
                  onPointerDown={(event) => event.stopPropagation()}
                >
                  <button
                    className="icon-btn"
                    type="button"
                    aria-label={fa.trip.moveUp}
                    disabled={index === 0}
                    onClick={() => void onReorder(moveItem(items, index, index - 1))}
                  >
                    ↑
                  </button>
                  <button
                    className="icon-btn"
                    type="button"
                    aria-label={fa.trip.moveDown}
                    disabled={index === items.length - 1}
                    onClick={() => void onReorder(moveItem(items, index, index + 1))}
                  >
                    ↓
                  </button>
                  <button
                    className="icon-btn danger"
                    type="button"
                    aria-label={fa.trip.removePlace}
                    onClick={() => void onRemove(item)}
                  >
                    ×
                  </button>
                </div>
              </li>
            ))}
          </ol>
        </>
      )}
    </section>
  );
}
