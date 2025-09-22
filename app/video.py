from app.database import SessionLocal
from app.models import Video

db = SessionLocal()

# get the module id (e.g. first module)
module_id = 1

new_video = Video(
    module_id=module_id,
    title="Water Quality Management",
    description="Learn the basics of aquaculture, including carrying capacity, water quality, and fish management.",
    video_url="https://res.cloudinary.com/dicz9c7kk/video/upload/v1758572512/mypromosphere/videos/sja2sywtvzfooomaehay.mp4",
    thumbnail_url="https://example.com/thumbnails/water.png",
    coins=10,
    duration_in_seconds=900
)

db.add(new_video)
db.commit()
db.refresh(new_video)

db.close()

print("✅ New video added to module successfully!")
