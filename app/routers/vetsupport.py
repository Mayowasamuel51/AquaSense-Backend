from fastapi.templating import Jinja2Templates
import os
import hmac
import hashlib
import requests
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, Form ,  File
from sqlalchemy.orm import Session, joinedload
from uuid import uuid4
from typing import List, Optional
from pydantic import BaseModel
from starlette.responses import HTMLResponse
from ..database import get_db
from ..models import User, Labs, LabTest, VetSupport, VetImage, VetVideo
from ..dep.security import get_current_user
from ..schemas import UserOut, VetSupportCreate, VetSupportResponse
import cloudinary
# from dotenv import load_dotenv
import cloudinary.uploader
router = APIRouter(prefix="/vetsupport", tags=["vetsupport"])


# ✅ Configure Cloudinary
cloudinary.config(
    cloud_name="dicz9c7kk",
    api_key="948636269897915",
    api_secret="f87ZL-_tSg7eV__mVGrmOKtl-Rw",
    secure=True
)



MAX_VIDEO_SIZE_MB = 5



@router.post("/create", response_model=VetSupportResponse)
async def create_vet_support(
    helpwith: str = Form(...),
    date: str = Form(...),
    issue :str = Form(...),
    modeofsupport: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),  # all in one field
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate inputs
    # try:
    #     validated = VetSupportCreate(helpwith=helpwith, date=date)
    # except Exception as e:
    #     raise HTTPException(status_code=422, detail=str(e))
    if not helpwith or not date or not issue  or not modeofsupport:
        raise HTTPException(status_code=400, detail="one of the feilds  are required.")

    # No files uploaded
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="You must upload at least one image or video.")

    if len(files) > 3:
        raise HTTPException(status_code=400, detail="You can upload a maximum of 3 files total.")

    # Separate into images and videos
    image_files = []
    video_files = []

    for f in files:
        if f.content_type.startswith("image/"):
            image_files.append(f)
        elif f.content_type.startswith("video/"):
            video_files.append(f)
        else:
            raise HTTPException(status_code=400, detail=f"{f.filename} is not a valid image or video.")

    # Validate video file sizes
    for video in video_files:
        video.file.seek(0, 2)
        size_mb = video.file.tell() / (1024 * 1024)
        video.file.seek(0)
        if size_mb > MAX_VIDEO_SIZE_MB:
            raise HTTPException(status_code=400, detail=f"{video.filename} exceeds 5MB limit.")

    # Create VetSupport record
    vet_support = VetSupport(
        # helpwith=validated.helpwith,
        # date=validated.date,
        # user_id=current_user.id,
        issue= issue,
        helpwith=helpwith,
        date=date,
        modeofsupport= modeofsupport,
        user_id=current_user.id,
    )

    db.add(vet_support)
    db.commit()
    db.refresh(vet_support)

    # Upload to Cloudinary
    for img in image_files:
        upload = cloudinary.uploader.upload(img.file, folder="vetsupport/images")
        db.add(VetImage(url=upload["secure_url"], vetsupport_id=vet_support.id))

    for vid in video_files:
        upload = cloudinary.uploader.upload_large(
            vid.file, folder="vetsupport/videos", resource_type="video"
        )
        db.add(VetVideo(url=upload["secure_url"], vetsupport_id=vet_support.id))

    db.commit()
    db.refresh(vet_support)

    return vet_support


class MainOutVetSupport(BaseModel):
    data:List[VetSupportResponse]
    message:str

@router.get("/me", response_model=MainOutVetSupport)
def get_my_vet_supports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    ✅ Get all vet support requests created by the logged-in user
    Includes all image and video URLs.
    """

    supports = (
        db.query(VetSupport)
        .options(joinedload(VetSupport.images), joinedload(VetSupport.videos))
        .filter(VetSupport.user_id == current_user.id)
        .order_by(VetSupport.id.desc())
        .all()
    )

    if not supports:
        raise HTTPException(status_code=404, detail="No vet support records found.")

    return {"message":"Displaying my Vet support" ,   "data":supports}




@router.get("/all", response_model=MainOutVetSupport)
def get_all_vet_supports(db: Session = Depends(get_db)):
    """
    🟢 Public route: Get all vet support requests
    Includes related images, videos, and user info.
    """

    supports = (
        db.query(VetSupport)
        .options(
            joinedload(VetSupport.images),
            joinedload(VetSupport.videos),
            joinedload(VetSupport.user),
        )
        .order_by(VetSupport.id.desc())
        .all()
    )

    if not supports:
        raise HTTPException(status_code=404, detail="No vet support data found.")

    return {"message":"showing all vet support on the database", "data":supports}
