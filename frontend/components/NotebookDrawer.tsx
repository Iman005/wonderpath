"use client";

import { useEffect, useState } from "react";
import fa from "@/i18n/fa";
import { notebookService } from "@/services/notebookService";
import { ApiError } from "@/services/apiClient";
import { formatDayOrdinal } from "@/shared/format";
import type { PackingList, TripDay, TripNote } from "@/shared/types";
import NotePhotoThumb from "@/components/NotePhotoThumb";
import AppOverlay from "@/components/AppOverlay";

type Tab = "notes" | "lists";
type Composer = "note" | "list" | null;
type Scope = "general" | "day";

export default function NotebookDrawer({
  tripId,
  days,
  lockedDayId,
  onClose,
}: {
  tripId: string;
  days: TripDay[];
  lockedDayId?: string;
  onClose: () => void;
}) {
  const lockedDay = days.find((day) => day.id === lockedDayId);
  const [tab, setTab] = useState<Tab>("notes");
  const [notes, setNotes] = useState<TripNote[]>([]);
  const [lists, setLists] = useState<PackingList[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [composer, setComposer] = useState<Composer>(null);
  const [noteBody, setNoteBody] = useState("");
  const [pendingPhotos, setPendingPhotos] = useState<File[]>([]);
  const [listTitle, setListTitle] = useState("");
  const [listItems, setListItems] = useState<string[]>([""]);
  const [scope, setScope] = useState<Scope>(lockedDayId ? "day" : "general");
  const [pickedDayId, setPickedDayId] = useState(lockedDayId || "");
  const [editingNoteId, setEditingNoteId] = useState<string | null>(null);
  const [editingListId, setEditingListId] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function load() {
    try {
      const [nextNotes, nextLists] = await Promise.all([
        notebookService.listNotes(tripId, lockedDayId),
        notebookService.listPackingLists(tripId, lockedDayId),
      ]);
      setNotes(nextNotes);
      setLists(nextLists);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tripId, lockedDayId]);

  function resetComposer() {
    setComposer(null);
    setNoteBody("");
    setPendingPhotos([]);
    setListTitle("");
    setListItems([""]);
    setScope(lockedDayId ? "day" : "general");
    setPickedDayId(lockedDayId || "");
    setEditingNoteId(null);
    setEditingListId(null);
  }

  function openCreate(next: Composer) {
    setError(null);
    setComposer(next);
    setNoteBody("");
    setPendingPhotos([]);
    setListTitle("");
    setListItems([""]);
    setScope(lockedDayId ? "day" : "general");
    setPickedDayId(lockedDayId || "");
    setEditingNoteId(null);
    setEditingListId(null);
  }

  function dayLabel(dayNumber: number | null | undefined) {
    return dayNumber ? formatDayOrdinal(dayNumber) : "";
  }

  function resolveDayId() {
    if (editingNoteId || editingListId) return null;
    if (lockedDayId) return lockedDayId;
    if (scope === "day") return pickedDayId || null;
    return null;
  }

  async function saveNote() {
    const body = noteBody.trim();
    if (!body) return;
    const dayId = resolveDayId();
    if (!editingNoteId && scope === "day" && !dayId) {
      setError(fa.notebook.pickDay);
      return;
    }
    setSaving(true);
    try {
      let noteId = editingNoteId;
      if (editingNoteId) {
        await notebookService.updateNote(tripId, editingNoteId, body);
      } else {
        const created = await notebookService.createNote(tripId, body, dayId);
        noteId = created.id;
      }
      if (noteId && pendingPhotos.length) {
        for (const file of pendingPhotos) {
          await notebookService.uploadAttachment(tripId, noteId, file);
        }
      }
      resetComposer();
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    } finally {
      setSaving(false);
    }
  }

  async function saveList() {
    const title = listTitle.trim() || fa.notebook.tabLists;
    const items = listItems.map((label) => ({ label: label.trim() })).filter((item) => item.label);
    const dayId = resolveDayId();
    if (!editingListId && scope === "day" && !dayId) {
      setError(fa.notebook.pickDay);
      return;
    }
    setSaving(true);
    try {
      if (editingListId) {
        await notebookService.updatePackingList(tripId, editingListId, { title, items });
      } else {
        await notebookService.createPackingList(tripId, title, items, dayId);
      }
      resetComposer();
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    } finally {
      setSaving(false);
    }
  }

  const title = lockedDay
    ? fa.notebook.titleDay.replace("{day}", formatDayOrdinal(lockedDay.day_number))
    : fa.notebook.titleAll;
  const isEditing = Boolean(editingNoteId || editingListId);
  const composerTitle =
    composer === "note"
      ? isEditing
        ? fa.notebook.composerEditNote
        : fa.notebook.composerNoteTitle
      : isEditing
        ? fa.notebook.composerEditList
        : fa.notebook.composerListTitle;

  return (
    <AppOverlay className="notebook-overlay" role="dialog" aria-modal="true" aria-label={title}>
      <div className="notebook-panel">
        <div className="notebook-head">
          <h2>{composer ? composerTitle : title}</h2>
          <button
            type="button"
            className="icon-btn"
            onClick={composer ? resetComposer : onClose}
            aria-label={composer ? fa.notebook.cancel : fa.common.close}
          >
            ×
          </button>
        </div>
        {!composer && (
          <div className="notebook-tabs" role="tablist">
            <button type="button" className={tab === "notes" ? "is-active" : ""} onClick={() => setTab("notes")}>
              {fa.notebook.tabNotes}
            </button>
            <button type="button" className={tab === "lists" ? "is-active" : ""} onClick={() => setTab("lists")}>
              {fa.notebook.tabLists}
            </button>
          </div>
        )}

        {error && <p className="notebook-error">{error}</p>}

        {!composer && tab === "notes" ? (
          <>
            <button type="button" className="notebook-create" onClick={() => openCreate("note")}>
              {fa.notebook.createNote}
            </button>
            <div className="notebook-scroll">
              {notes.length === 0 ? (
                <p className="muted">{fa.notebook.emptyNotes}</p>
              ) : (
                notes.map((note) => (
                  <article key={note.id} className="notebook-row">
                    <div className="notebook-row-main">
                      <p className="notebook-row-label">
                        {note.day_number
                          ? fa.notebook.dayNote.replace("{day}", dayLabel(note.day_number))
                          : fa.notebook.generalNote}
                      </p>
                      <p className="notebook-row-body">{note.body}</p>
                      {note.attachments && note.attachments.length > 0 && (
                        <div className="notebook-photos">
                          {note.attachments.map((attachment) => (
                            <NotePhotoThumb key={attachment.id} path={attachment.url} />
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="notebook-row-actions">
                      <button
                        type="button"
                        className="notebook-mini"
                        onClick={() => {
                          setError(null);
                          setComposer("note");
                          setEditingNoteId(note.id);
                          setEditingListId(null);
                          setNoteBody(note.body);
                          setScope(note.trip_day_id ? "day" : "general");
                          setPickedDayId(note.trip_day_id || lockedDayId || "");
                        }}
                      >
                        {fa.notebook.edit}
                      </button>
                      <button
                        type="button"
                        className="notebook-mini is-delete"
                        onClick={async () => {
                          if (!window.confirm(fa.notebook.confirmDelete)) return;
                          await notebookService.deleteNote(tripId, note.id);
                          await load();
                        }}
                      >
                        {fa.notebook.delete}
                      </button>
                    </div>
                  </article>
                ))
              )}
            </div>
          </>
        ) : null}

        {!composer && tab === "lists" && (
          <>
            <button type="button" className="notebook-create" onClick={() => openCreate("list")}>
              {fa.notebook.createList}
            </button>
            <div className="notebook-scroll">
              {lists.length === 0 ? (
                <p className="muted">{fa.notebook.emptyLists}</p>
              ) : (
                lists.map((list) => (
                  <article key={list.id} className="notebook-row">
                    <div className="notebook-row-main">
                      <p className="notebook-row-label">
                        {list.day_number
                          ? fa.notebook.dayList.replace("{day}", dayLabel(list.day_number))
                          : fa.notebook.generalList}
                      </p>
                      <p className="notebook-row-body">{list.title}</p>
                      <ul className="notebook-checks">
                        {list.items.map((item) => (
                          <li key={item.id}>
                            <label>
                              <input
                                type="checkbox"
                                checked={item.is_checked}
                                onChange={async (event) => {
                                  await notebookService.updatePackingItem(tripId, item.id, {
                                    is_checked: event.target.checked,
                                  });
                                  await load();
                                }}
                              />
                              <span>{item.label}</span>
                            </label>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="notebook-row-actions">
                      <button
                        type="button"
                        className="notebook-mini"
                        onClick={() => {
                          setError(null);
                          setComposer("list");
                          setEditingListId(list.id);
                          setEditingNoteId(null);
                          setListTitle(list.title);
                          setListItems(list.items.length ? list.items.map((item) => item.label) : [""]);
                          setScope(list.trip_day_id ? "day" : "general");
                          setPickedDayId(list.trip_day_id || lockedDayId || "");
                        }}
                      >
                        {fa.notebook.edit}
                      </button>
                      <button
                        type="button"
                        className="notebook-mini is-delete"
                        onClick={async () => {
                          if (!window.confirm(fa.notebook.confirmDelete)) return;
                          await notebookService.deletePackingList(tripId, list.id);
                          await load();
                        }}
                      >
                        {fa.notebook.delete}
                      </button>
                    </div>
                  </article>
                ))
              )}
            </div>
          </>
        )}

        {composer && (
          <div className="notebook-composer">
              {composer === "note" ? (
                <>
                  <textarea
                    className="input input-light notebook-notepad"
                    rows={6}
                    value={noteBody}
                    onChange={(event) => setNoteBody(event.target.value)}
                    placeholder={fa.notebook.notePlaceholder}
                  />
                  <p className="notebook-scope-hint">{fa.notebook.photosHint}</p>
                  <label className="notebook-photo-pick">
                    <span>{fa.notebook.addPhotos}</span>
                    <input
                      type="file"
                      accept="image/jpeg,image/png,image/webp,image/gif"
                      multiple
                      onChange={(event) => {
                        const files = Array.from(event.target.files || []);
                        setPendingPhotos((current) => [...current, ...files].slice(0, 8));
                      }}
                    />
                  </label>
                  {pendingPhotos.length > 0 && (
                    <div className="notebook-photos">
                      {pendingPhotos.map((file, index) => (
                        <div key={`${file.name}-${index}`} className="notebook-photo-pending">
                          <span>{file.name}</span>
                          <button
                            type="button"
                            className="notebook-mini is-delete"
                            onClick={() =>
                              setPendingPhotos((current) => current.filter((_, i) => i !== index))
                            }
                          >
                            {fa.notebook.removePhoto}
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              ) : (
                <div className="notebook-list-fields">
                  <input
                    className="input input-light"
                    value={listTitle}
                    onChange={(event) => setListTitle(event.target.value)}
                    placeholder={fa.notebook.listTitlePlaceholder}
                  />
                  {listItems.map((item, index) => (
                    <label key={index} className="notebook-item-row">
                      <span className="notebook-item-box" aria-hidden />
                      <input
                        className="input input-light"
                        value={item}
                        onChange={(event) =>
                          setListItems((current) =>
                            current.map((value, i) => (i === index ? event.target.value : value)),
                          )
                        }
                        placeholder={fa.notebook.itemPlaceholder.replace("{n}", String(index + 1))}
                      />
                    </label>
                  ))}
                  <button
                    type="button"
                    className="notebook-add-item"
                    onClick={() => setListItems((items) => [...items, ""])}
                  >
                    +
                  </button>
                </div>
              )}

              {lockedDay ? (
                <p className="notebook-scope-hint">
                  {fa.notebook.lockedDayHint.replace("{day}", formatDayOrdinal(lockedDay.day_number))}
                </p>
              ) : isEditing ? null : (
                <fieldset className="notebook-scope">
                  <legend>{fa.notebook.scopeLabel}</legend>
                  <p className="notebook-scope-hint">{fa.notebook.scopeHint}</p>
                  <label className={scope === "general" ? "is-active" : ""}>
                    <input
                      type="radio"
                      name="notebook-scope"
                      checked={scope === "general"}
                      onChange={() => {
                        setScope("general");
                        setPickedDayId("");
                      }}
                    />
                    <span>{fa.notebook.scopeGeneral}</span>
                  </label>
                  <label className={scope === "day" ? "is-active" : ""}>
                    <input
                      type="radio"
                      name="notebook-scope"
                      checked={scope === "day"}
                      onChange={() => setScope("day")}
                    />
                    <span>{fa.notebook.scopeDay}</span>
                  </label>
                  {scope === "day" && (
                    <select
                      className="input input-light"
                      value={pickedDayId}
                      onChange={(event) => setPickedDayId(event.target.value)}
                    >
                      <option value="">{fa.notebook.pickDay}</option>
                      {days.map((day) => (
                        <option key={day.id} value={day.id}>
                          {formatDayOrdinal(day.day_number)}
                        </option>
                      ))}
                    </select>
                  )}
                </fieldset>
              )}

              <div className="notebook-composer-actions">
                <button
                  type="button"
                  className="notebook-save"
                  disabled={saving}
                  onClick={() => (composer === "note" ? saveNote() : saveList())}
                >
                  {saving ? fa.common.loading : fa.notebook.save}
                </button>
                <button type="button" className="notebook-cancel" onClick={resetComposer}>
                  {fa.notebook.cancel}
                </button>
              </div>
          </div>
        )}
      </div>
    </AppOverlay>
  );
}
