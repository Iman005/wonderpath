"""NotebookService — trip notes, photo attachments, and packing lists."""
import uuid
from pathlib import Path

from app.infrastructure.db.models import NoteAttachment, PackingItem, PackingList, TripNote
from app.modules.notebook.dtos import NoteAttachmentOut, NoteOut, PackingItemOut, PackingListOut
from app.modules.notebook.repository import UPLOAD_ROOT, NotebookRepository
from app.modules.trip.service import TripService
from app.shared.exceptions import NotFoundError, ValidationDomainError

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_BYTES = 5 * 1024 * 1024
MIME_EXT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


class NotebookService:
    def __init__(self, trip_service: TripService, repo: NotebookRepository) -> None:
        self.trip_service = trip_service
        self.repo = repo

    def list_notes(self, trip_id: str, owner_device_id: str, trip_day_id: str | None = None) -> list[NoteOut]:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        self._ensure_day(trip, trip_day_id)
        return [self._note_out(note, trip) for note in self.repo.list_notes(trip.id, trip_day_id)]

    def public_snapshot(self, trip) -> tuple[list[NoteOut], list[PackingListOut]]:
        notes = [
            self._note_out(note, trip).model_copy(update={"attachments": []})
            for note in self.repo.list_notes(trip.id)
        ]
        lists = [self._list_out(item, trip) for item in self.repo.list_packing_lists(trip.id)]
        return notes, lists

    def create_note(
        self,
        trip_id: str,
        owner_device_id: str,
        body: str,
        trip_day_id: str | None = None,
    ) -> NoteOut:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        self._ensure_day(trip, trip_day_id)
        cleaned = body.strip()
        if not cleaned:
            raise ValidationDomainError("Note text is required.")
        note = TripNote(trip_id=trip.id, trip_day_id=trip_day_id, body=cleaned)
        return self._note_out(self.repo.create_note(note), trip)

    def update_note(self, trip_id: str, owner_device_id: str, note_id: str, body: str) -> NoteOut:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        note = self._owned_note(trip.id, note_id)
        cleaned = body.strip()
        if not cleaned:
            raise ValidationDomainError("Note text is required.")
        note.body = cleaned
        return self._note_out(note, trip)

    def delete_note(self, trip_id: str, owner_device_id: str, note_id: str) -> None:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        note = self._owned_note(trip.id, note_id)
        self.repo.delete_note(note)

    def add_attachment(
        self,
        trip_id: str,
        owner_device_id: str,
        note_id: str,
        *,
        data: bytes,
        mime: str,
    ) -> NoteAttachmentOut:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        note = self._owned_note(trip.id, note_id)
        if mime not in ALLOWED_MIME:
            raise ValidationDomainError("Only JPEG, PNG, WebP, or GIF images are allowed.")
        if not data:
            raise ValidationDomainError("Empty file.")
        if len(data) > MAX_BYTES:
            raise ValidationDomainError("Image must be 5MB or smaller.")

        UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
        attachment_id = str(uuid.uuid4())
        filename = f"{attachment_id}{MIME_EXT[mime]}"
        abs_path = UPLOAD_ROOT / filename
        abs_path.write_bytes(data)
        relative = f"uploads/notes/{filename}"
        created = self.repo.create_attachment(
            NoteAttachment(id=attachment_id, note_id=note.id, file_path=relative, mime=mime)
        )
        return self._attachment_out(created, trip.id)

    def delete_attachment(
        self,
        trip_id: str,
        owner_device_id: str,
        note_id: str,
        attachment_id: str,
    ) -> None:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        note = self._owned_note(trip.id, note_id)
        attachment = self.repo.get_attachment(attachment_id)
        if not attachment or attachment.note_id != note.id:
            raise NotFoundError(f"Attachment '{attachment_id}' not found.")
        self.repo.delete_attachment(attachment)

    def resolve_attachment_file(
        self,
        trip_id: str,
        owner_device_id: str,
        note_id: str,
        attachment_id: str,
    ) -> tuple[Path, str]:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        note = self._owned_note(trip.id, note_id)
        attachment = self.repo.get_attachment(attachment_id)
        if not attachment or attachment.note_id != note.id:
            raise NotFoundError(f"Attachment '{attachment_id}' not found.")
        path = Path(attachment.file_path)
        if not path.is_absolute():
            path = Path(__file__).resolve().parents[3] / attachment.file_path
        if not path.is_file():
            raise NotFoundError(f"Attachment '{attachment_id}' file missing.")
        return path, attachment.mime

    def list_packing_lists(
        self,
        trip_id: str,
        owner_device_id: str,
        trip_day_id: str | None = None,
    ) -> list[PackingListOut]:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        self._ensure_day(trip, trip_day_id)
        return [self._list_out(item, trip) for item in self.repo.list_packing_lists(trip.id, trip_day_id)]

    def create_packing_list(
        self,
        trip_id: str,
        owner_device_id: str,
        title: str,
        items: list[dict],
        trip_day_id: str | None = None,
    ) -> PackingListOut:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        self._ensure_day(trip, trip_day_id)
        cleaned_title = title.strip()
        if not cleaned_title:
            raise ValidationDomainError("List title is required.")
        packing_list = PackingList(trip_id=trip.id, trip_day_id=trip_day_id, title=cleaned_title)
        packing_list.items = [
            PackingItem(
                label=(item.get("label") or "").strip(),
                is_checked=bool(item.get("is_checked")),
                order_index=index,
            )
            for index, item in enumerate(items)
            if (item.get("label") or "").strip()
        ]
        created = self.repo.create_packing_list(packing_list)
        return self._list_out(self.repo.get_packing_list(created.id) or created, trip)

    def update_packing_list(
        self,
        trip_id: str,
        owner_device_id: str,
        list_id: str,
        fields: dict,
    ) -> PackingListOut:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        packing_list = self._owned_list(trip.id, list_id)
        if "title" in fields and fields["title"] is not None:
            title = str(fields["title"]).strip()
            if not title:
                raise ValidationDomainError("List title is required.")
            packing_list.title = title
        if "items" in fields and fields["items"] is not None:
            packing_list.items.clear()
            packing_list.items.extend(
                [
                    PackingItem(
                        label=(item.get("label") or "").strip(),
                        is_checked=bool(item.get("is_checked")),
                        order_index=index,
                    )
                    for index, item in enumerate(fields["items"])
                    if (item.get("label") or "").strip()
                ]
            )
        return self._list_out(self.repo.get_packing_list(packing_list.id) or packing_list, trip)

    def delete_packing_list(self, trip_id: str, owner_device_id: str, list_id: str) -> None:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        packing_list = self._owned_list(trip.id, list_id)
        self.repo.delete_packing_list(packing_list)

    def update_packing_item(
        self,
        trip_id: str,
        owner_device_id: str,
        item_id: str,
        fields: dict,
    ) -> PackingItemOut:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        item = self.repo.get_packing_item(item_id)
        if not item:
            raise NotFoundError(f"Packing item '{item_id}' not found.")
        packing_list = self._owned_list(trip.id, item.packing_list_id)
        if packing_list.id != item.packing_list_id:
            raise NotFoundError(f"Packing item '{item_id}' not found.")
        if "label" in fields and fields["label"] is not None:
            label = str(fields["label"]).strip()
            if not label:
                raise ValidationDomainError("Item label is required.")
            item.label = label
        if "is_checked" in fields and fields["is_checked"] is not None:
            item.is_checked = bool(fields["is_checked"])
        return PackingItemOut.model_validate(item)

    def _owned_note(self, trip_id: str, note_id: str) -> TripNote:
        note = self.repo.get_note(note_id)
        if not note or note.trip_id != trip_id:
            raise NotFoundError(f"Note '{note_id}' not found.")
        return note

    def _owned_list(self, trip_id: str, list_id: str) -> PackingList:
        packing_list = self.repo.get_packing_list(list_id)
        if not packing_list or packing_list.trip_id != trip_id:
            raise NotFoundError(f"Packing list '{list_id}' not found.")
        return packing_list

    @staticmethod
    def _ensure_day(trip, trip_day_id: str | None) -> None:
        if not trip_day_id:
            return
        if not any(day.id == trip_day_id for day in trip.days):
            raise NotFoundError(f"Trip day '{trip_day_id}' not found.")

    @staticmethod
    def _day_number(trip, trip_day_id: str | None) -> int | None:
        if not trip_day_id:
            return None
        for day in trip.days:
            if day.id == trip_day_id:
                return day.day_number
        return None

    def _attachment_out(self, attachment: NoteAttachment, trip_id: str) -> NoteAttachmentOut:
        note_id = attachment.note_id
        return NoteAttachmentOut(
            id=attachment.id,
            mime=attachment.mime,
            created_at=attachment.created_at,
            url=f"/trips/{trip_id}/notes/{note_id}/attachments/{attachment.id}/file",
        )

    def _note_out(self, note: TripNote, trip) -> NoteOut:
        attachments = sorted(note.attachments or [], key=lambda item: item.created_at)
        return NoteOut(
            id=note.id,
            trip_id=note.trip_id,
            trip_day_id=note.trip_day_id,
            day_number=self._day_number(trip, note.trip_day_id),
            body=note.body,
            created_at=note.created_at,
            attachments=[self._attachment_out(item, trip.id) for item in attachments],
        )

    def _list_out(self, packing_list: PackingList, trip) -> PackingListOut:
        items = sorted(packing_list.items or [], key=lambda item: item.order_index)
        return PackingListOut(
            id=packing_list.id,
            trip_id=packing_list.trip_id,
            trip_day_id=packing_list.trip_day_id,
            day_number=self._day_number(trip, packing_list.trip_day_id),
            title=packing_list.title,
            items=[PackingItemOut.model_validate(item) for item in items],
            created_at=packing_list.created_at,
        )
