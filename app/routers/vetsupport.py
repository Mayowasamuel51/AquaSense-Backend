from fastapi.templating import Jinja2Templates
import os
import hmac
import hashlib
import requests
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, Form ,  File
from sqlalchemy.orm import Session
from uuid import uuid4
from typing import List, Optional
from pydantic import BaseModel
from starlette.responses import HTMLResponse
from ..database import get_db
from ..models import User, Labs, LabTest, VetSupport, VetImage
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
    issue: str = Form(...),
    images: Optional[List[UploadFile]] = File(None),
    video: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ✅ Validate text inputs
    try:
        validated = VetSupportCreate(helpwith=helpwith, date=date, issue=issue)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    # ✅ Validate image count
    if images and len(images) > 3:
        raise HTTPException(status_code=400, detail="You can upload up to 3 images only.")

    image_urls = []

    # ✅ Upload images to Cloudinary
    if images:
        for img in images:
            if not img.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail=f"{img.filename} is not a valid image.")
            upload = cloudinary.uploader.upload(img.file, folder="vetsupport/images")
            image_urls.append(upload["secure_url"])

    # ✅ Validate and upload video
    video_url = None
    if video:
        if not video.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="Only video files are allowed.")

        video.file.seek(0, 2)
        file_size_mb = video.file.tell() / (1024 * 1024)
        video.file.seek(0)

        if file_size_mb > MAX_VIDEO_SIZE_MB:
            raise HTTPException(status_code=400, detail="Video must be 5 MB or smaller.")

        upload = cloudinary.uploader.upload_large(
            video.file, folder="vetsupport/videos", resource_type="video"
        )
        video_url = upload["secure_url"]

    # ✅ Create VetSupport entry
    vet_support = VetSupport(
        helpwith=validated.helpwith,
        date=validated.date,
        issue=validated.issue,
        video=video_url,
        user_id=current_user.id,
    )

    db.add(vet_support)
    db.commit()
    db.refresh(vet_support)

    # ✅ Add image records
    for url in image_urls:
        vet_image = VetImage(url=url, vetsupport_id=vet_support.id)
        db.add(vet_image)
    db.commit()

    db.refresh(vet_support)
    return vet_support