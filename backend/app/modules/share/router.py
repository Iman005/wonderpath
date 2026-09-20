"""Share controller — enable a link (auth) and read the snapshot (public)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.identity.dependencies import get_current_device_id
from app.modules.share.dependencies import get_share_service
from app.modules.share.dtos import SharedTripOut, ShareLinkOut
from app.modules.share.service import ShareService

router = APIRouter(tags=["Share"])


@router.post("/trips/{trip_id}/share", response_model=ShareLinkOut)
def enable_trip_share(
    trip_id: str,
    device_id: str = Depends(get_current_device_id),
    service: ShareService = Depends(get_share_service),
    db: Session = Depends(get_db),
):
    result = service.enable_share(trip_id, device_id)
    db.commit()
    return result


@router.get("/share/{token}", response_model=SharedTripOut)
def get_shared_trip(
    token: str,
    service: ShareService = Depends(get_share_service),
):
    return service.get_shared_trip(token)
