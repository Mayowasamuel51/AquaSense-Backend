
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy.exc import SQLAlchemyError

# ✅ Import MySQL connection and models
from app.database import SessionLocal, engine
from app.models import Base, TestItem, TestCategory

# ✅ Create tables in MySQL (if not exist)
Base.metadata.create_all(bind=engine)

# ✅ Test data to seed
testListAsMap = [
    {
        "title": "Water Quality Test",
        "tests": [
            {"name": "pH level", "price": 2000},
            {"name": "Dissolved Oxygen (DO)", "price": 2500},
            {"name": "Temperature", "price": 1500},
            {"name": "Ammonia (NH₃)", "price": 3000},
            {"name": "Nitrite (NO₂⁻)", "price": 2500},
            {"name": "Nitrate (NO₃⁻)", "price": 2500},
            {"name": "Alkalinity", "price": 2000},
            {"name": "Hardness", "price": 2000},
            {"name": "Turbidity", "price": 1800},
        ],
    },
    {
        "title": "Soil Test",
        "tests": [
            {"name": "Soil pH", "price": 2000},
            {"name": "Organic Matter Content", "price": 2500},
            {"name": "Nitrogen (N)", "price": 3000},
            {"name": "Phosphorus (P)", "price": 3000},
            {"name": "Potassium (K)", "price": 3000},
            {"name": "Soil Texture/Clay Content", "price": 2500},
            {"name": "Sulphide/Acid Sulphate Test", "price": 3500},
        ],
    },
    {
        "title": "Feed Quality Check",
        "tests": [
            {"name": "Crude Protein %", "price": 3000},
            {"name": "Crude Fat %", "price": 3000},
            {"name": "Crude Fiber %", "price": 2500},
            {"name": "Ash Content", "price": 2000},
            {"name": "Moisture Content", "price": 2000},
            {"name": "Mycotoxin Test (Aflatoxin)", "price": 4000},
            {"name": "Feed Pellet Water Stability", "price": 2500},
        ],
    },
    {
        "title": "Fingerling Quality Check",
        "tests": [
            {"name": "Size Uniformity", "price": 2000},
            {"name": "Activity Level", "price": 1500},
            {"name": "Stress/Mortality Test", "price": 2000},
            {"name": "Physical Examination (wounds, deformities)", "price": 2500},
            {"name": "Feeding Response", "price": 2000},
            {"name": "Swim Bladder Check", "price": 2500},
        ],
    },
    {
        "title": "Fish Health/Disease Tests",
        "tests": [
            {"name": "Parasitology (skin/gill scraping)", "price": 3000},
            {"name": "Intestinal Parasite Check", "price": 3000},
            {"name": "Bacteriology (culture & sensitivity)", "price": 4000},
            {"name": "Fungal Identification", "price": 3500},
            {"name": "Viral Screening", "price": 5000},
            {"name": "Hematology (blood test)", "price": 4000},
        ],
    },
]


# ✅ Lifespan event handler — runs once on app startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        print("🔗 Connected to:", engine.url)  # Check your MySQL URL in terminal
        count = db.query(TestCategory).count()

        if count == 0:
            print("🌱 Seeding MySQL database...")
            for cat in testListAsMap:
                category = TestCategory(title=cat["title"])
                for t in cat["tests"]:
                    category.tests.append(TestItem(name=t["name"], price=t["price"]))
                db.add(category)

            db.commit()
            print("✅ Database seeded successfully!")
        else:
            print(f"ℹ️ {count} categories already exist — skipping seeding.")
    except SQLAlchemyError as e:
        db.rollback()
        print("❌ Error during seeding:", e)
    finally:
        db.close()

    yield  # 👈 app runs here
    print("👋 App shutting down...")


# ✅ Create FastAPI app and attach the lifespan
app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "MySQL seeding ready ✅"}



#
# # ---- Insert module ----
# module = Module(
#     title="Introduction to Aquaculture",
#     description="Learn the basics of aquaculture, including carrying capacity, water quality, and fish management.",
#     total_coins=100,  # 10 questions * 10 coins
#     completion_bonus_coins=30
# )
# db.add(module)
# db.commit()
# db.refresh(module)
#
# # ---- Insert video ----
# video = Video(
#     module_id=module.id,
#     title="Getting Started with Aquaculture",
#     description="Overview of aquaculture and why it matters.",
#     video_url="https://example.com/videos/intro.mp4",
#     thumbnail_url="https://example.com/thumbnails/intro.png",
#     coins=50,
#     duration_in_seconds=600
# )
# db.add(video)
# db.commit()
#
# # ---- Questions + Options ----
# questions = [
#     {
#         "question": "According to the document, carrying capacity in aquaculture should be defined around what?",
#         "options": [
#             "The maximum biomass a system can sustain.",
#             "The total amount of feed a system can handle per day.",
#             "The standing crop or biomass at a point in time.",
#             "The number of fish in the pond."
#         ],
#         "correct": 2
#     },
#     {
#         "question": "What is the primary factor that influences water quality problems and fish health in a feed-based aquaculture system?",
#         "options": ["Water temperature", "Feed quantity and quality", "Fish genetics", "The presence of algae"],
#         "correct": 2
#     },
#     {
#         "question": "A fingerling pond has a lower carrying capacity in terms of total biomass compared to a food-fish pond because:",
#         "options": [
#             "Fingerlings require more oxygen.",
#             "Fingerlings are usually fed at a higher percentage of their body weight per day.",
#             "Fingerlings produce more waste.",
#             "Fingerlings are more susceptible to disease."
#         ],
#         "correct": 2
#     },
#     {
#         "question": "According to the document, what is the first limiting factor in aquaculture after food needs have been met?",
#         "options": ["Water quantity", "Light", "Oxygen", "Fish health"],
#         "correct": 3
#     },
#     {
#         "question": "Which of the following is a sign that a farmer is reaching the carrying capacity of their system, based on observation?",
#         "options": [
#             "Fish are eating more vigorously.",
#             "Fish are swimming closer to the surface.",
#             "The water starts to smell like sewage.",
#             "The water color becomes very dark."
#         ],
#         "correct": 3
#     },
#     {
#         "question": "What is a key difference between earthen ponds and lined ponds regarding carrying capacity?",
#         "options": [
#             "Lined ponds can handle more phosphorus.",
#             "Earthen ponds have more unstable phytoplankton blooms.",
#             "Earthen ponds can adsorb some of the phosphorus from the water.",
#             "Lined ponds are more efficient for nutrient cycling."
#         ],
#         "correct": 3
#     },
#     {
#         "question": "If a farmer has limited water and cannot aerate, how can they increase production according to the document?",
#         "options": ["Stocking more fish per pond.", "Using more efficient feeding techniques.", "Adding probiotics to the water.", "Making more ponds."],
#         "correct": 4
#     },
#     {
#         "question": "According to the first example provided, if you have an expected yield of 3,000 kg and a desired average weight of 300 g per fish, what is the stocking rate?",
#         "options": ["3,000 fingerlings", "4,285 fingerlings", "10,000 fingerlings", "11,000 fingerlings"],
#         "correct": 3
#     },
#     {
#         "question": "When should a farmer who chooses the aeration and water exchange option begin these practices?",
#         "options": [
#             "On the first day after stocking.",
#             "When the fish start to show signs of stress.",
#             "When the daily feed inputs are about half of the recommended limit.",
#             "When the water begins to get smelly."
#         ],
#         "correct": 3
#     },
#     {
#         "question": "What concept is illustrated by Liebig's barrel?",
#         "options": [
#             "Partial harvesting allows for higher yields.",
#             "Growth is limited by the scarcest available resource.",
#             "All nutrients must be present in equal amounts.",
#             "Earthen ponds are more effective than lined ponds."
#         ],
#         "correct": 2
#     },
# ]
#
# # ---- Insert tests + options ----
# for q in questions:
#     test = Test(module_id=module.id, question=q["question"], coins=10)  # ✅ coins added
#     db.add(test)
#     db.commit()
#     db.refresh(test)
#
#     option_objects = []
#     for idx, opt_text in enumerate(q["options"], start=1):
#         option = Option(test_id=test.id, text=opt_text)
#         db.add(option)
#         db.commit()
#         option_objects.append(option)
#
#     # Set correct option
#     correct_option = option_objects[q["correct"] - 1]
#     test.correct_option_id = correct_option.id
#     db.commit()
#
# db.close()
#
# print("✅ Module, video, and 10 test questions (with coins) inserted successfully!")
