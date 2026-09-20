"""Notebook request/response schemas."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    body: str = Field(min_length=1, max_length=4000)
    trip_day_id: str | None = None


class NoteUpdate(BaseModel):
    body: str = Field(min_length=1, max_length=4000)


class NoteAttachmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    mime: str
    created_at: datetime
    url: str | None = None


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    trip_id: str
    trip_day_id: str | None = None
    day_number: int | None = None
    body: str
    created_at: datetime
    attachments: list[NoteAttachmentOut] = Field(default_factory=list)


class PackingItemIn(BaseModel):
    label: str = Field(min_length=1, max_length=200)
    is_checked: bool = False


class PackingListCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    trip_day_id: str | None = None
    items: list[PackingItemIn] = Field(default_factory=list)


class PackingListUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    items: list[PackingItemIn] | None = None


class PackingItemUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=200)
    is_checked: bool | None = None


class PackingItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    label: str
    is_checked: bool
    order_index: int


class PackingListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    trip_id: str
    trip_day_id: str | None = None
    day_number: int | None = None
    title: str
    items: list[PackingItemOut] = Field(default_factory=list)
    created_at: datetime
