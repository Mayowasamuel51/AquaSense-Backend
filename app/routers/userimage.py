from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import cloudinary.uploader
from ..models import User
from ..database import get_db
from ..dep.security import get_current_user  # ✅ authenticated user dependency

router = APIRouter(prefix="/profileimage", tags=["Profile Picture"])
load_dotenv()

# ✅ Configure Cloudinary
cloudinary.config(
    cloud_name="dicz9c7kk",
    api_key="948636269897915",
    api_secret="f87ZL-_tSg7eV__mVGrmOKtl-Rw",
    secure=True
)
# ✅ Upload a new profile picture

@router.post("/upload")
async def upload_or_change_profile_picture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Upload a new profile picture, or replace an existing one if it already exists.
    Automatically deletes the old Cloudinary image.
    """
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        # ✅ Delete old image if it exists
        if user.profilepicture:
            try:
                # Extract the public_id (file name without extension)
                public_id = user.profilepicture.split("/")[-1].split(".")[0]
                cloudinary.uploader.destroy(f"profile_pictures/{public_id}")
            except Exception as delete_err:
                print("Warning: could not delete old image:", delete_err)

        # ✅ Upload new image
        result = cloudinary.uploader.upload(
            file.file,
            folder="profile_pictures",
            public_id=f"user_{user.id}",
            overwrite=True,
            resource_type="image"
        )

        # ✅ Update user in database
        user.profilepicture = result.get("secure_url")
        db.commit()
        db.refresh(user)

        return {
            "message": "Profile picture uploaded successfully",
            "url": user.profilepicture
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")