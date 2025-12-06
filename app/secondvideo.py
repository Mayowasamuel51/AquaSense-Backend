from app.database import SessionLocal, engine
from app.models import Base, Module, Video, Test, Option

# ✅ Create tables
Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ---- Insert Module 2 ----
module2 = Module(
    title="Introduction to Insurance Products",
    description="Learn the basics of insurance, including products, risk categories, and business applications.",
    total_coins=100,  # 10 questions * 10 coins
    completion_bonus_coins=30
)
db.add(module2)
db.commit()
db.refresh(module2)

# ---- Insert Video ----
video2 = Video(
    module_id=module2.id,
    title="Insurance Products Overview",
    description="Learn about insurance as a promise, its categories, and practical applications.",
    video_url="https://res.cloudinary.com/dicz9c7kk/video/upload/v1758573884/mypromosphere/videos/vzzsgyxey5anum4y7g4f.mp4",
    thumbnail_url="https://res.cloudinary.com/dicz9c7kk/image/upload/v1758574333/mypromosphere/ads/pyx2shkjqstbzciqd4qo.png",
    coins=70,  # give more since it’s more advanced
    duration_in_seconds=750  # ~12.5 mins
)
db.add(video2)
db.commit()

# ---- Questions + Options ----
insurance_questions = [
    {
        "question": "What is the insurance product defined as in the video?",
        "options": ["A financial asset", "A promise", "A physical good", "A legal document"],
        "correct": 2
    },
    {
        "question": "What are the three main categories into which the insurance industry groups risks?",
        "options": ["Auto, Home, and Business", "Life, Health, and Liability", "Property & Casualty, Life, and Health", "Personal, Commercial, and Specialty"],
        "correct": 3
    },
    {
        "question": "According to the video, what does 'casualty insurance' (otherwise known as liability) cover?",
        "options": ["Damage to your own property", "Your responsibilities for harm to others", "Financial loss due to business interruption", "The maximum cost of a claim"],
        "correct": 2
    },
    {
        "question": "Which of the following is an example of a 'property' risk?",
        "options": ["A claim against you for causing a car accident", "Your responsibility to pay for damage to another person's car", "The damage to your own car from an accident", "A claim from a professional for errors and omissions"],
        "correct": 3
    },
    {
        "question": "Why do insurers usually set a limit on casualty insurance?",
        "options": ["To manage the unknowable range of outcomes for liability", "Because the value of property is fixed", "To comply with government regulations", "To encourage people to buy more insurance"],
        "correct": 1
    },
    {
        "question": "In personal insurance, what are the two largest categories?",
        "options": ["Home and Condominium", "Owners and Renters", "Home and Motor (or Auto)", "Pet and Travel"],
        "correct": 3
    },
    {
        "question": "Which of the following would be covered by a commercial policy?",
        "options": ["Home insurance", "Motor (Auto) insurance for a personal car", "Workers' compensation for employees", "A personal travel policy"],
        "correct": 3
    },
    {
        "question": "What type of commercial insurance covers a business's failure to deliver or damages caused by their service?",
        "options": ["Product liability", "Professional liability", "Workers' compensation", "Business interruption"],
        "correct": 2
    },
    {
        "question": "What is a standard Business Owner's Policy (BOP) in the US designed for?",
        "options": ["High-value, industry-specific risks", "A combination of personal and commercial risks", "Basic risks for small businesses", "Umbrella coverage for all businesses"],
        "correct": 3
    },
    {
        "question": "What is a key difference in the timeline of claims between property and liability risks?",
        "options": ["Property claims take years to be resolved, while liability claims are immediate.", "Property claims are usually known immediately, while liability claims may take longer to play out.", "Both property and liability claims always take a long time to be resolved.", "There is no difference in the timeline of claims."],
        "correct": 2
    },
]

# ---- Insert tests + options ----
for q in insurance_questions:
    test = Test(module_id=module2.id, question=q["question"], coins=10)
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

print("✅ Module 2 (Insurance), with 1 video and 10 test questions inserted successfully!")















