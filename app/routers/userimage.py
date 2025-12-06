from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import cloudinary
# from dotenv import load_dotenv
import cloudinary.uploader
from ..models import User
from ..database import get_db
from ..dep.security import get_current_user  # ✅ authenticated user dependency
from ..schemas import UserOut

router = APIRouter(prefix="/profileimage", tags=["Profile Picture"])
# load_dotenv()

# ✅ Configure Cloudinary
cloudinary.config(
    cloud_name="dicz9c7kk",
    api_key="948636269897915",
    api_secret="f87ZL-_tSg7eV__mVGrmOKtl-Rw",
    secure=True
)
# ✅ Upload a new profile picture
class MainOutMain(BaseModel):
    data:UserOut


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
    # 🔍 Always get a fresh DB instance of the user
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # ✅ Delete old image if it exists
        if db_user.profilepicture:
            try:
                # Extract the public_id (the filename part from Cloudinary URL)
                public_id = db_user.profilepicture.split("/")[-1].split(".")[0]
                cloudinary.uploader.destroy(f"profile_pictures/{public_id}")
            except Exception as delete_err:
                print("⚠️ Warning: could not delete old image:", delete_err)

        # ✅ Upload the new image
        result = cloudinary.uploader.upload(
            file.file,
            folder="profile_pictures",
            public_id=f"user_{user.id}",
            overwrite=True,
            resource_type="image"
        )

        # ✅ Save the new image URL in the database
        db_user.profilepicture = result.get("secure_url")
        db.commit()
        db.refresh(db_user)

        return {
            "message": "Profile picture uploaded successfully",
            "url": db_user.profilepicture,
            "data":UserOut.from_orm(db_user)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")
