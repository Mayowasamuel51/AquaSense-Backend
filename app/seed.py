from app.database import SessionLocal, engine
from app.models import Base, Module, Video, Test, Option

# ✅ Create tables
Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ---- Insert module ----
module = Module(
    title="Introduction to Aquaculture",
    description="Learn the basics of aquaculture, including carrying capacity, water quality, and fish management.",
    total_coins=100,  # 10 questions * 10 coins
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

# ---- Questions + Options ----
questions = [
    {
        "question": "According to the document, carrying capacity in aquaculture should be defined around what?",
        "options": [
            "The maximum biomass a system can sustain.",
            "The total amount of feed a system can handle per day.",
            "The standing crop or biomass at a point in time.",
            "The number of fish in the pond."
        ],
        "correct": 2
    },
    {
        "question": "What is the primary factor that influences water quality problems and fish health in a feed-based aquaculture system?",
        "options": ["Water temperature", "Feed quantity and quality", "Fish genetics", "The presence of algae"],
        "correct": 2
    },
    {
        "question": "A fingerling pond has a lower carrying capacity in terms of total biomass compared to a food-fish pond because:",
        "options": [
            "Fingerlings require more oxygen.",
            "Fingerlings are usually fed at a higher percentage of their body weight per day.",
            "Fingerlings produce more waste.",
            "Fingerlings are more susceptible to disease."
        ],
        "correct": 2
    },
    {
        "question": "According to the document, what is the first limiting factor in aquaculture after food needs have been met?",
        "options": ["Water quantity", "Light", "Oxygen", "Fish health"],
        "correct": 3
    },
    {
        "question": "Which of the following is a sign that a farmer is reaching the carrying capacity of their system, based on observation?",
        "options": [
            "Fish are eating more vigorously.",
            "Fish are swimming closer to the surface.",
            "The water starts to smell like sewage.",
            "The water color becomes very dark."
        ],
        "correct": 3
    },
    {
        "question": "What is a key difference between earthen ponds and lined ponds regarding carrying capacity?",
        "options": [
            "Lined ponds can handle more phosphorus.",
            "Earthen ponds have more unstable phytoplankton blooms.",
            "Earthen ponds can adsorb some of the phosphorus from the water.",
            "Lined ponds are more efficient for nutrient cycling."
        ],
        "correct": 3
    },
    {
        "question": "If a farmer has limited water and cannot aerate, how can they increase production according to the document?",
        "options": ["Stocking more fish per pond.", "Using more efficient feeding techniques.", "Adding probiotics to the water.", "Making more ponds."],
        "correct": 4
    },
    {
        "question": "According to the first example provided, if you have an expected yield of 3,000 kg and a desired average weight of 300 g per fish, what is the stocking rate?",
        "options": ["3,000 fingerlings", "4,285 fingerlings", "10,000 fingerlings", "11,000 fingerlings"],
        "correct": 3
    },
    {
        "question": "When should a farmer who chooses the aeration and water exchange option begin these practices?",
        "options": [
            "On the first day after stocking.",
            "When the fish start to show signs of stress.",
            "When the daily feed inputs are about half of the recommended limit.",
            "When the water begins to get smelly."
        ],
        "correct": 3
    },
    {
        "question": "What concept is illustrated by Liebig's barrel?",
        "options": [
            "Partial harvesting allows for higher yields.",
            "Growth is limited by the scarcest available resource.",
            "All nutrients must be present in equal amounts.",
            "Earthen ponds are more effective than lined ponds."
        ],
        "correct": 2
    },
]

# ---- Insert tests + options ----
for q in questions:
    test = Test(module_id=module.id, question=q["question"], coins=10)  # ✅ coins added
    db.add(test)
    db.commit()
    db.refresh(test)

    option_objects = []
    for idx, opt_text in enumerate(q["options"], start=1):
        option = Option(test_id=test.id, text=opt_text)
        db.add(option)
        db.commit()
        option_objects.append(option)

    # Set correct option
    correct_option = option_objects[q["correct"] - 1]
    test.correct_option_id = correct_option.id
    db.commit()

db.close()

print("✅ Module, video, and 10 test questions (with coins) inserted successfully!")
