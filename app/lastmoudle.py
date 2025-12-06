from app.database import SessionLocal
from app.models import Module, Video, Test, Option

db = SessionLocal()

# ---- Insert Module 3 ----
module3 = Module(
    title="Crop Insurance Claims Process",
    description="Learn the step-by-step process of handling crop insurance claims effectively.",
    total_coins=100,  # 10 questions * 10 coins
    completion_bonus_coins=30
)
db.add(module3)
db.commit()
db.refresh(module3)

# ---- Insert Video ----
video3 = Video(
    module_id=module3.id,
    title="Understanding Crop Insurance Claims",
    description="Step-by-step guide for farmers on how to file and resolve crop insurance claims.",
    video_url="https://res.cloudinary.com/dicz9c7kk/video/upload/v1758576745/mypromosphere/videos/weqpxlk66hvuko0d4c0r.mp4",
    thumbnail_url="https://res.cloudinary.com/dicz9c7kk/image/upload/v1758576561/mypromosphere/ads/awasd6ao5n2mzeweijcq.png",
    coins=10,
    duration_in_seconds=800
)
db.add(video3)
db.commit()

# ---- Questions + Options ----
questions = [
    {
        "question": "What is the first step a farmer should take after discovering crop damage?",
        "options": [
            "Harvest the remaining crops immediately",
            "Notify their insurance provider in writing within 72 hours",
            "Fill out a claim form",
            "Contact a loss adjuster directly"
        ],
        "correct": 2
    },
    {
        "question": "How long after the crop insurance period ends might a claim be denied if not reported?",
        "options": ["72 hours", "10 days", "15 days", "30 days"],
        "correct": 3
    },
    {
        "question": "What is the role of a loss adjuster or appraiser in the claims process?",
        "options": [
            "To pay out the insurance claim",
            "To inspect the crops and assess the damage",
            "To fill out the claim form for the farmer",
            "To help the farmer with their planting records"
        ],
        "correct": 2
    },
    {
        "question": "Why is it important for a farmer to cooperate fully during the inspection?",
        "options": [
            "To avoid having to fill out a claim form",
            "To ensure the adjuster can access fields and relevant records",
            "To get a higher payment from the insurer",
            "To speed up the harvest process"
        ],
        "correct": 2
    },
    {
        "question": "What action is important to take after filling out a claim form with the adjuster's help?",
        "options": [
            "Wait for the insurer to contact you",
            "Harvest the remaining crops immediately",
            "Submit the completed form promptly to avoid delays",
            "Contact the regulator to dispute a claim"
        ],
        "correct": 3
    },
    {
        "question": "What document sets a farmer's coverage limits before a claim can be made?",
        "options": [
            "A claim form",
            "A police report",
            "A signed letter from a neighbor",
            "A completed crop insurance application and annual reports"
        ],
        "correct": 4
    },
    {
        "question": "What kind of records are vital to support your claim and help resolve disagreements?",
        "options": [
            "Social media posts about the damage",
            "Records of planting dates, inputs, harvests, and crop sales",
            "Bank statements for the last two years",
            "Receipts for purchased equipment"
        ],
        "correct": 2
    },
    {
        "question": "How can a farmer prevent coverage gaps or overpayment of premiums?",
        "options": [
            "By submitting their claim form as soon as possible",
            "By having a professional lawyer review their policy",
            "By accurately reporting their acreage and production",
            "By cooperating fully with the loss adjuster"
        ],
        "correct": 3
    },
    {
        "question": "How long should a farmer keep organized records after the crop year?",
        "options": [
            "For at least one year",
            "For at least three years",
            "Until the claim is paid",
            "Only until the next planting season"
        ],
        "correct": 2
    },
    {
        "question": "According to the video, what are your best tools for a successful claim resolution?",
        "options": [
            "Timely notification and a lawyer",
            "Cooperation and good luck",
            "Proper documentation and knowing your policy details",
            "Prompt submission and a high claim amount"
        ],
        "correct": 3
    }
]

# ---- Insert tests + options ----
for q in questions:
    test = Test(module_id=module3.id, question=q["question"], coins=10)
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

print("✅ Module 3 (Crop Insurance Claims), with video and 10 test questions inserted successfully!")
