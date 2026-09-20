"""Notebook HTTP layer."""
from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.identity.dependencies import get_current_device_id
from app.modules.notebook.dependencies import get_notebook_service
from app.modules.notebook.dtos import (
    NoteAttachmentOut,
    NoteCreate,
    NoteOut,
    NoteUpdate,
    PackingItemOut,
    PackingItemUpdate,
    PackingListCreate,
    PackingListOut,
    PackingListUpdate,
)
from app.modules.notebook.service import NotebookService

router = APIRouter(prefix="/trips", tags=["Notebook"])


@router.get("/{trip_id}/notes", response_model=list[NoteOut])
def list_notes(
    trip_id: str,
    trip_day_id: str | None = None,
    device_id: str = Depends(get_current_device_id),
    service: NotebookService = Depends(get_notebook_service),
):
    return service.list_notes(trip_id, device_id, trip_day_id)


@router.post("/{trip_id}/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(
    trip_id: str,
    payload: NoteCreate,
    device_id: str = Depends(get_current_device_id),
    service: NotebookService = Depends(get_notebook_service),
    db: Session = Depends(get_db),
):
    note = service.create_note(trip_id, device_id, payload.body, payload.trip_day_id)
    db.commit()
    return note


@router.put("/{trip_id}/notes/{note_id}", response_model=NoteOut)
def update_note(
    trip_id: str,
    note_id: str,
    payload: NoteUpdate,
    device_id: str = Depends(get_current_device_id),
    service: NotebookService = Depends(get_notebook_service),
    db: Session = Depends(get_db),
):
    note = service.update_note(trip_id, device_id, note_id, payload.body)
    db.commit()
    return note


@router.delete("/{trip_id}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    trip_id: str,
    note_id: str,
    device_id: str = Depends(get_current_device_id),
    service: NotebookService = Depends(get_notebook_service),
    db: Session = Depends(get_db),
):
    service.delete_note(trip_id, device_id, note_id)
    db.commit()


@router.post(
    "/{trip_id}/notes/{note_id}/attachments",
    response_model=NoteAttachmentOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_note_attachment(
    trip_id: str,
    note_id: str,
    file: UploadFile = File(...),
    device_id: str = Depends(get_current_device_id),
    service: NotebookService = Depends(get_notebook_service),
    db: Session = Depends(get_db),
):
    data = await file.read()
    mime = file.content_type or "application/octet-stream"
    attachment = service.add_attachment(trip_id, device_id, note_id, data=data, mime=mime)
    db.commit()
    return attachment


@router.get("/{trip_id}/notes/{note_id}/attachments/{attachment_id}/file")
def get_note_attachment_file(
    trip_id: str,
    note_id: str,
    attachment_id: str,
    device_id: str = Depends(get_current_device_id),
    service: NotebookService = Depends(get_notebook_service),
):
    path, mime = service.resolve_attachment_file(trip_id, device_id, note_id, attachment_id)
    return FileResponse(path, media_type=mime)


@router.delete(
    "/{trip_id}/notes/{note_id}/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_note_attachment(
    trip_id: str,
    note_id: str,
    attachment_id: str,
    device_id: str = Depends(get_current_device_id),
    service: NotebookService = Depends(get_notebook_service),
    db: Session = Depends(get_db),
):
    service.delete_attachment(trip_id, device_id, note_id, attachment_id)
    db.commit()


@router.get("/{trip_id}/packing-lists", response_model=list[PackingListOut])
def list_packing_lists(
    trip_id: str,
    trip_day_id: str | None = None,
    device_id: str = Depends(get_current_device_id),
    service: NotebookService = Depends(get_notebook_service),
):
    return service.list_packing_lists(trip_id, device_id, trip_day_id)


@router.post("/{trip_id}/packing-lists", response_model=PackingListOut, status_code=status.HTTP_201_CREATED)
def create_packing_list(
    trip_id: str,
    payload: PackingListCreate,
    device_id: str = Depends(get_current_device_id),
    service: NotebookService = Depends(get_notebook_service),
    db: Session = Depends(get_db),
):
    packing_list = service.create_packing_list(
        trip_id,
        device_id,
        payload.title,
        [item.model_dump() for item in payload.items],
        payload.trip_day_id,
    )
    db.commit()
    return packing_list


@router.put("/{trip_id}/packing-lists/{list_id}", response_model=PackingListOut)
def update_packing_list(
    trip_id: str,
    list_id: str,
    payload: PackingListUpdate,
    device_id: str = Depends(get_current_device_id),
    service: NotebookService = Depends(get_notebook_service),
    db: Session = Depends(get_db),
):
    fields = payload.model_dump(exclude_unset=True)
    packing_list = service.update_packing_list(trip_id, device_id, list_id, fields)
    db.commit()
    return packing_list


@router.delete("/{trip_id}/packing-lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_packing_list(
    trip_id: str,
    list_id: str,
    device_id: str = Depends(get_current_device_id),
    service: NotebookService = Depends(get_notebook_service),
    db: Session = Depends(get_db),
):
    service.delete_packing_list(trip_id, device_id, list_id)
    db.commit()


@router.put("/{trip_id}/packing-items/{item_id}", response_model=PackingItemOut)
def update_packing_item(
    trip_id: str,
    item_id: str,
    payload: PackingItemUpdate,
    device_id: str = Depends(get_current_device_id),
    service: NotebookService = Depends(get_notebook_service),
    db: Session = Depends(get_db),
):
    item = service.update_packing_item(trip_id, device_id, item_id, payload.model_dump(exclude_unset=True))
    db.commit()
    return item
