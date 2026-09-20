"""Notebook persistence — notes, attachments, and packing lists."""
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.infrastructure.db.models import NoteAttachment, PackingItem, PackingList, TripNote

UPLOAD_ROOT = Path(__file__).resolve().parents[3] / "uploads" / "notes"


class NotebookRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_notes(self, trip_id: str, trip_day_id: str | None = None) -> list[TripNote]:
        stmt = (
            select(TripNote)
            .options(selectinload(TripNote.attachments))
            .where(TripNote.trip_id == trip_id)
        )
        if trip_day_id:
            stmt = stmt.where(TripNote.trip_day_id == trip_day_id)
        stmt = stmt.order_by(TripNote.created_at.desc())
        return list(self.db.execute(stmt).scalars().unique().all())

    def get_note(self, note_id: str) -> TripNote | None:
        stmt = (
            select(TripNote)
            .options(selectinload(TripNote.attachments))
            .where(TripNote.id == note_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create_note(self, note: TripNote) -> TripNote:
        self.db.add(note)
        self.db.flush()
        return note

    def delete_note(self, note: TripNote) -> None:
        for attachment in list(note.attachments or []):
            self._unlink_file(attachment.file_path)
        self.db.delete(note)
        self.db.flush()

    def create_attachment(self, attachment: NoteAttachment) -> NoteAttachment:
        self.db.add(attachment)
        self.db.flush()
        return attachment

    def get_attachment(self, attachment_id: str) -> NoteAttachment | None:
        return self.db.get(NoteAttachment, attachment_id)

    def delete_attachment(self, attachment: NoteAttachment) -> None:
        self._unlink_file(attachment.file_path)
        self.db.delete(attachment)
        self.db.flush()

    @staticmethod
    def _unlink_file(file_path: str) -> None:
        path = Path(file_path)
        if not path.is_absolute():
            path = UPLOAD_ROOT.parent.parent / file_path
        try:
            if path.is_file():
                path.unlink()
        except OSError:
            pass

    def list_packing_lists(self, trip_id: str, trip_day_id: str | None = None) -> list[PackingList]:
        stmt = (
            select(PackingList)
            .options(selectinload(PackingList.items))
            .where(PackingList.trip_id == trip_id)
        )
        if trip_day_id:
            stmt = stmt.where(PackingList.trip_day_id == trip_day_id)
        stmt = stmt.order_by(PackingList.created_at.desc())
        return list(self.db.execute(stmt).scalars().unique().all())

    def get_packing_list(self, list_id: str) -> PackingList | None:
        stmt = (
            select(PackingList)
            .options(selectinload(PackingList.items))
            .where(PackingList.id == list_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create_packing_list(self, packing_list: PackingList) -> PackingList:
        self.db.add(packing_list)
        self.db.flush()
        return packing_list

    def delete_packing_list(self, packing_list: PackingList) -> None:
        self.db.delete(packing_list)
        self.db.flush()

    def get_packing_item(self, item_id: str) -> PackingItem | None:
        return self.db.get(PackingItem, item_id)

    def create_packing_item(self, item: PackingItem) -> PackingItem:
        self.db.add(item)
        self.db.flush()
        return item

    def delete_packing_item(self, item: PackingItem) -> None:
        self.db.delete(item)
        self.db.flush()
