import os
import base64
import httpx
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..dep.security import get_current_user  # ✅ your JWT auth dependency
from dotenv import load_dotenv
# ✅ Load environment variables
load_dotenv()
router = APIRouter(
    prefix="/profileimage",
    tags=["Profile Picture"]
)

# ===========================
# 🖼️ Upload Profile Picture
# ===========================
@router.post("/upload")
async def upload_profile_picture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    api_key = "b250634f93da9f6857fcf390924230c4"
    if not api_key:
        raise HTTPException(status_code=500, detail="IMGBB API key not configured")
    try:
        contents = await file.read()
        encoded = base64.b64encode(contents).decode('utf-8')

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.imgbb.com/1/upload",
                data={"key": api_key, "image": encoded}
            )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="ImgBB upload failed")

        data = response.json()
        url = data.get("data", {}).get("url")

        if not url:
            raise HTTPException(status_code=500, detail="Failed to retrieve image URL")

        # Save URL in the user’s record
        user.profilepicture = url
        db.commit()
        db.refresh(user)

        return {"message": "Profile picture uploaded successfully", "url": url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# ♻️ Change / Replace Picture
# ===========================
@router.put("/change")
async def change_profile_picture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    api_key = os.getenv("IMGBB_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="IMGBB API key not configured")
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        contents = await file.read()
        encoded = base64.b64encode(contents).decode('utf-8')

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.imgbb.com/1/upload",
                data={"key": api_key, "image": encoded}
            )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="ImgBB upload failed")

        data = response.json()
        url = data.get("data", {}).get("url")

        if not url:
            raise HTTPException(status_code=500, detail="Failed to retrieve image URL")

        # Optionally: Delete old image (ImgBB free plan doesn’t really allow it)
        # So we’ll just overwrite the URL in the DB

        user.profilepicture = url
        db.commit()
        db.refresh(user)

        return {"message": "Profile picture changed successfully", "url": url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
