from app.database import SessionLocal, engine
from app.models import Base, Module, Video, Test, Option
# ✅ Create tables if not already created
Base.metadata.create_all(bind=engine)

db = SessionLocal()
# ---- Insert sample module ----
module = Module(
    title="Introduction to Aquaculture",
    description="Learn the basics of aquaculture",
    total_coins=120,
    completion_bonus_coins=30
)
db.add(module)
db.commit()
db.refresh(module)

# ---- Insert video ----
video = Video(
    module_id=module.id,
    title="Getting Started with Aquaculture",
    description="Overview of aquaculture and why it matters.",
    video_url="https://example.com/videos/intro.mp4",
    thumbnail_url="https://example.com/thumbnails/intro.png",
    coins=50,
    duration_in_seconds=600
)
db.add(video)
db.commit()

# ---- Insert test ----
test = Test(
    module_id=module.id,
    question="What is the ideal pH range for most aquaculture species?"
)
db.add(test)
db.commit()
db.refresh(test)

# ---- Insert options ----
option1 = Option(test_id=test.id, text="3.0 - 4.0")
option2 = Option(test_id=test.id, text="6.5 - 8.5")
option3 = Option(test_id=test.id, text="9.0 - 11.0")
db.add_all([option1, option2, option3])
db.commit()

# ✅ Update correct option
test.correct_option_id = option2.id
db.commit()

db.close()

print("✅ Seed data inserted successfully!")




BATCH ----- UNITS  ---- RECORD ----- OTHER





