from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from ..database import get_db
from syncsehemas import BatchIn
from ..models import (
    User, Batch, Unit, UnitRecord, DailyRecord,
    WeightSampling, HarvestForm, Grade, GradingAndSorting,
    Income, Stocking, Feed, Labour, Medication, Maintenance, Logistics, OperationalExpense
)
from ..dep.security import get_current_user

router = APIRouter(prefix="/batches", tags=["Batch"])

@router.post("/", status_code=201)
def upsert_batch(payload: BatchIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Create or update a batch with nested unit records and all children.
    Ensures parent-child relationships are inserted correctly.
    """
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    batch_id = payload.batchId or str(uuid4())

    # --- UPSERT Batch ---
    batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
    if batch:
        batch.batch_name = payload.batchName
        batch.fishtype = payload.fishtype
        batch.number_of_fishes = payload.numberoffishes
        batch.average_body_weight = payload.averagebodyweight
        batch.age_at_stock = payload.ageAtStock
        batch.is_completed = payload.isCompleted or 0
        batch.is_synced = payload.isSynced or 0
        batch.updated_at = payload.updatedAt or datetime.utcnow()
    else:
        batch = Batch(
            batch_id=batch_id,
            farmer_id=user.id,
            batch_name=payload.batchName,
            fishtype=payload.fishtype,
            number_of_fishes=payload.numberoffishes,
            average_body_weight=payload.averagebodyweight,
            age_at_stock=payload.ageAtStock,
            is_completed=payload.isCompleted or 0,
            is_synced=payload.isSynced or 0,
            created_at=payload.createdAt or datetime.utcnow(),
            updated_at=payload.updatedAt or datetime.utcnow(),
        )
        db.add(batch)
    db.flush()  # Ensure batch.id is available

    # --- UPSERT Units & Records ---
    for r in payload.records or []:
        # --- Unit ---
        unit = db.query(Unit).filter(Unit.id == r.unitId).first()
        if not unit and r.unit:
            u = r.unit
            unit = Unit(
                id=u.id or str(uuid4()),
                farmer_id=user.id,
                unit_name=u.unitName or "unknown",
                unit_type=u.unitType,
                unit_dimension=u.unitDimension,
                unit_capacity=u.unitCapacity,
                fishes=u.fishes,
                image_file=u.imageFile,
                image_url=u.imageUrl,
                unitcategory=getattr(u, "unitcategory", None),
                is_active=u.isActive or 0,
                is_synced=u.isSynced or 0,
                created_at=u.createdAt or datetime.utcnow(),
                updated_at=u.updatedAt or datetime.utcnow(),
            )
            db.add(unit)
            db.flush()
        elif not unit:
            raise HTTPException(status_code=400, detail=f"Unit {r.unitId} not found and unit payload not provided")

        # --- UnitRecord ---
        rec = db.query(UnitRecord).filter(UnitRecord.id == r.id).first()
        if rec:
            rec.stocknumber = r.stocknumber
            rec.movedfishes = r.movedfishes
            rec.mortality = r.mortality
            rec.fishleft = r.fishleft
            rec.incomingfish = r.incomingfish
            rec.fishtype = r.fishtype
            rec.stockedon = r.stockedon
            rec.totalfishcost = r.totalfishcost
            rec.is_synced = r.isSynced or 0
            rec.updated_at = r.updatedAt or datetime.utcnow()
        else:
            rec = UnitRecord(
                id=r.id or str(uuid4()),
                farmer_id=user.id,
                batch_id=batch.id,
                unit_id=unit.id,
                stocknumber=r.stocknumber,
                movedfishes=r.movedfishes,
                mortality=r.mortality,
                fishleft=r.fishleft,
                incomingfish=r.incomingfish,
                fishtype=r.fishtype,
                stockedon=r.stockedon,
                totalfishcost=r.totalfishcost,
                is_synced=r.isSynced or 0,
                created_at=r.createdAt or datetime.utcnow(),
                updated_at=r.updatedAt or datetime.utcnow(),
            )
            db.add(rec)
        db.flush()

        # --- DailyRecords ---
        for d in r.dailyRecords or []:
            dr = db.query(DailyRecord).filter(DailyRecord.id == d.id).first()
            if dr:
                dr.date = d.date
                dr.feed_name = d.feedName
                dr.feed_size = d.feedSize
                dr.feed_quantity = d.feedQuantity
                dr.mortality = d.mortality
                dr.coins = d.coins
                dr.is_synced = d.isSynced or 0
                dr.updated_at = d.updatedAt or datetime.utcnow()
            else:
                dr = DailyRecord(
                    id=d.id or str(uuid4()),
                    record_id=rec.id,
                    farmer_id=user.id,
                    batch_id=batch.id,
                    unit_id=unit.id,
                    date=d.date,
                    feed_name=d.feedName,
                    feed_size=d.feedSize,
                    feed_quantity=d.feedQuantity,
                    mortality=d.mortality,
                    coins=d.coins,
                    is_synced=d.isSynced or 0,
                    created_at=d.createdAt or datetime.utcnow(),
                    updated_at=d.updatedAt or datetime.utcnow(),
                )
                db.add(dr)

        # --- WeightSamplings ---
        for w in r.weightSamplings or []:
            ws = db.query(WeightSampling).filter(WeightSampling.id == w.id).first()
            if ws:
                ws.fish_numbers = w.fishNumbers
                ws.total_weight = w.totalWeight
                ws.completed = w.completed
                ws.is_synced = w.isSynced or 0
                ws.updated_at = w.updatedAt or datetime.utcnow()
            else:
                ws = WeightSampling(
                    id=w.id or str(uuid4()),
                    record_id=rec.id,
                    farmer_id=user.id,
                    batch_id=batch.id,
                    unit_id=unit.id,
                    sample_name=w.sampleName,
                    date=w.date,
                    fish_numbers=w.fishNumbers,
                    total_weight=w.totalWeight,
                    completed=w.completed,
                    is_synced=w.isSynced or 0,
                    created_at=w.createdAt or datetime.utcnow(),
                    updated_at=w.updatedAt or datetime.utcnow(),
                )
                db.add(ws)

        # --- Grading & Grades ---
        for g in r.gradingAndSortings or []:
            grading = db.query(GradingAndSorting).filter(GradingAndSorting.id == g.id).first()
            grading_id = g.id or str(uuid4())
            if grading:
                grading.fish_numbers = g.fishNumbers
                grading.total_weight = g.totalWeight
                grading.completed = g.completed
                grading.is_synced = g.isSynced or 0
                grading.updated_at = g.updatedAt or datetime.utcnow()
            else:
                grading = GradingAndSorting(
                    id=grading_id,
                    record_id=rec.id,
                    farmer_id=user.id,
                    batch_id=batch.id,
                    unit_id=unit.id,
                    grade_with=g.gradeWith,
                    sample_name=g.sampleName,
                    date=g.date,
                    grading_pond_number=str(g.gradingPondNumber or ""),  # always string
                    fish_numbers=g.fishNumbers,
                    total_weight=g.totalWeight,
                    completed=g.completed,
                    is_synced=g.isSynced or 0,
                    created_at=g.createdAt or datetime.utcnow(),
                    updated_at=g.updatedAt or datetime.utcnow(),
                )
                db.add(grading)
                db.flush()  # make grading_id available

            for gr in g.grades or []:
                grade = db.query(Grade).filter(Grade.id == gr.id).first()
                if grade:
                    grade.average_fish_weight = gr.averageFishWeight
                    grade.fish_transferred = gr.fishTransferred
                    grade.is_synced = gr.isSynced or 0
                    grade.updated_at = gr.updatedAt or datetime.utcnow()
                else:
                    grade = Grade(
                        id=gr.id or str(uuid4()),
                        sorting_id=grading.id,  # <-- use actual DB parent ID
                        destination_batch_id=gr.destinationBatchId,
                        destination_batch_name=gr.destinationBatchName,
                        destination_unit_id=gr.destinationUnitId,
                        destination_unit_name=gr.destinationUnitName,
                        average_fish_weight=gr.averageFishWeight,
                        fish_transferred=gr.fishTransferred,
                        sample_name=gr.sampleName,
                        record_id=rec.id,
                        batch_id=batch.id,
                        is_synced=gr.isSynced or 0,
                        created_at=gr.createdAt or datetime.utcnow(),
                        updated_at=gr.updatedAt or datetime.utcnow(),
                    )
                    db.add(grade)

        # --- Harvests ---
        for h in r.harvests or []:
            hv = db.query(HarvestForm).filter(HarvestForm.id == h.id).first()
            if hv:
                hv.quantity_harvest = h.quantityHarvest
                hv.total_weight = h.totalWeight
                hv.price_per_kg = h.pricePerKg
                hv.total_sales = h.totalSales
                hv.is_synced = h.isSynced or 0
                hv.updated_at = h.updatedAt or datetime.utcnow()
            else:
                hv = HarvestForm(
                    id=h.id or str(uuid4()),
                    record_id=rec.id,
                    farmer_id=user.id,
                    batch_id=batch.id,
                    unit_id=unit.id,
                    date=h.date,
                    sales_invoice_number=h.salesInvoiceNumber,
                    quantity_harvest=h.quantityHarvest,
                    total_weight=h.totalWeight,
                    price_per_kg=h.pricePerKg,
                    total_sales=h.totalSales,
                    is_synced=h.isSynced or 0,
                    created_at=h.createdAt or datetime.utcnow(),
                    updated_at=h.updatedAt or datetime.utcnow(),
                )
                db.add(hv)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving batch: {str(e)}")

    return {"detail": "Batch created/updated", "batchId": batch.batch_id}


# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from uuid import uuid4
# from datetime import datetime
# from typing import List
#
# from ..database import get_db
# from syncsehemas import BatchIn
# # from ..models import (
# #     User, Batch, Unit, UnitRecord, DailyRecord,
# #     WeightSampling, HarvestForm, Grade, GradingAndSorting
# # )
# from ..models import (
#     User, Batch, Unit, UnitRecord, DailyRecord,
#     WeightSampling, HarvestForm, Grade, GradingAndSorting,
#     Income, Stocking, Feed, Labour, Medication, Maintenance, Logistics, OperationalExpense
# )
# from ..dep.security import get_current_user
#
# router = APIRouter(prefix="/batches", tags=["Batch"])
#
# @router.post("/", status_code=201)
# def upsert_batch(payload: BatchIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
#     """
#     Create or update a batch with nested unit records and all children.
#     Farmer is always the authenticated user.
#     """
#     # Validate current user
#     db_user = db.query(User).filter(User.id == user.id).first()
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     batch_id = payload.batchId or str(uuid4())
#
#     # --- UPSERT Batch ---
#     batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
#     if batch:
#         # update existing
#         batch.batch_name = payload.batchName
#         batch.fishtype = payload.fishtype
#         batch.number_of_fishes = payload.numberoffishes
#         batch.average_body_weight = payload.averagebodyweight
#         batch.age_at_stock = payload.ageAtStock
#         batch.is_completed = payload.isCompleted or 0
#         batch.is_synced = payload.isSynced or 0
#         batch.updated_at = payload.updatedAt or datetime.utcnow()
#     else:
#         batch = Batch(
#             batch_id=batch_id,
#             farmer_id=user.id,
#             batch_name=payload.batchName,
#             fishtype=payload.fishtype,
#             number_of_fishes=payload.numberoffishes,
#             average_body_weight=payload.averagebodyweight,
#             age_at_stock=payload.ageAtStock,
#             is_completed=payload.isCompleted or 0,
#             is_synced=payload.isSynced or 0,
#             created_at=payload.createdAt or datetime.utcnow(),
#             updated_at=payload.updatedAt or datetime.utcnow(),
#         )
#         db.add(batch)
#     db.flush()  # Ensure batch.id is available
#
#     # --- UPSERT Units and UnitRecords ---
#     for r in payload.records or []:
#         # Unit UPSERT
#         unit = db.query(Unit).filter(Unit.id == r.unitId).first()
#         if not unit and r.unit:
#             u = r.unit
#             unit = Unit(
#                 id=u.id,
#                 farmer_id=user.id,
#                 unit_name=u.unitName or "unknown",
#                 unit_type=u.unitType,
#                 unit_dimension=u.unitDimension,
#                 unit_capacity=u.unitCapacity,
#                 fishes=u.fishes,
#                 image_file=u.imageFile,
#                 image_url=u.imageUrl,
#                 unitcategory=getattr(u, "unitcategory", None),
#                 is_active=u.isActive or 0,
#                 is_synced=u.isSynced or 0,
#                 created_at=u.createdAt or datetime.utcnow(),
#                 updated_at=u.updatedAt or datetime.utcnow(),
#             )
#             db.add(unit)
#             db.flush()
#             # --- FINANCE / EXPENSES UPSERT ---
#             # Make sure payload has r.finance (per syncschemas.FinanceIn)
#             fin = getattr(r, "finance", None) or {}
#
#             # Income
#             for inc in fin.get("income", []) if isinstance(fin, dict) else (fin.income or []):
#                 # support both dict (raw payload) and pydantic model
#                 inc_id = getattr(inc, "id", inc.get("id") if isinstance(inc, dict) else None)
#                 income = db.query(Income).filter(Income.id == inc_id).first()
#                 if income:
#                     income.income_type = getattr(inc, "incomeType", getattr(inc, "income_type", None)) or getattr(inc,
#                                                                                                                   "income_type",
#                                                                                                                   None)
#                     income.amount_earned = getattr(inc, "amountEarned", getattr(inc, "amount_earned", None))
#                     income.amount = getattr(inc, "amount", None) or getattr(inc, "amount", None)
#                     income.quantity_sold = getattr(inc, "quantitySold", getattr(inc, "quantity_sold", None))
#                     income.payment_method = getattr(inc, "paymentMethod", getattr(inc, "payment_method", None))
#                     income.income_date = getattr(inc, "date", None)
#                     income.is_synced = getattr(inc, "isSynced", getattr(inc, "is_synced", 0)) or 0
#                     income.updated_at = getattr(inc, "updatedAt", None) or datetime.utcnow()
#                 else:
#                     income = Income(
#                         id=inc_id or str(uuid4()),
#                         farmer_id=user.id,
#                         pond_id=r.unitId,
#                         batch_id=batch.batch_id,
#                         income_type=getattr(inc, "incomeType", getattr(inc, "income_type", None)),
#                         amount_earned=getattr(inc, "amountEarned", getattr(inc, "amount_earned", None)),
#                         amount=getattr(inc, "amount", None),
#                         quantity_sold=getattr(inc, "quantitySold", getattr(inc, "quantity_sold", None)),
#                         payment_method=getattr(inc, "paymentMethod", getattr(inc, "payment_method", None)),
#                         income_date=getattr(inc, "date", None),
#                         is_synced=getattr(inc, "isSynced", 0) or 0,
#                         created_at=getattr(inc, "createdAt", None) or datetime.utcnow(),
#                         updated_at=getattr(inc, "updatedAt", None) or datetime.utcnow(),
#                     )
#                     db.add(income)
#
#             # Stocking
#             for s in fin.get("stocking", []) if isinstance(fin, dict) else (fin.stocking or []):
#                 s_id = getattr(s, "id", s.get("id") if isinstance(s, dict) else None)
#                 stocking = db.query(Stocking).filter(Stocking.id == s_id).first()
#                 if stocking:
#                     stocking.fish_type = getattr(s, "fishType", getattr(s, "fish_type", None))
#                     stocking.quantity_purchased = getattr(s, "quantityPurchased",
#                                                           getattr(s, "quantity_purchased", None))
#                     stocking.total_amount = getattr(s, "totalAmount", getattr(s, "total_amount", None))
#                     stocking.date = getattr(s, "date", None)
#                     stocking.is_synced = getattr(s, "isSynced", 0) or 0
#                     stocking.updated_at = getattr(s, "updatedAt", None) or datetime.utcnow()
#                 else:
#                     stocking = Stocking(
#                         id=s_id or str(uuid4()),
#                         farmer_id=user.id,
#                         pond_id=r.unitId,
#                         batch_id=batch.batch_id,
#                         fish_type=getattr(s, "fishType", getattr(s, "fish_type", None)),
#                         quantity_purchased=getattr(s, "quantityPurchased", getattr(s, "quantity_purchased", None)),
#                         total_amount=getattr(s, "totalAmount", getattr(s, "total_amount", None)),
#                         date=getattr(s, "date", None),
#                         is_synced=getattr(s, "isSynced", 0) or 0,
#                         created_at=getattr(s, "createdAt", None) or datetime.utcnow(),
#                         updated_at=getattr(s, "updatedAt", None) or datetime.utcnow(),
#                     )
#                     db.add(stocking)
#
#             # Feed expenses
#             for f in fin.get("feed", []) if isinstance(fin, dict) else (fin.feed or []):
#                 f_id = getattr(f, "id", f.get("id") if isinstance(f, dict) else None)
#                 feed = db.query(Feed).filter(Feed.id == f_id).first()
#                 if feed:
#                     feed.feed_name = getattr(f, "feedName", getattr(f, "feed_name", None))
#                     feed.feed_size = getattr(f, "feedSize", getattr(f, "feed_size", None))
#                     feed.quantity = getattr(f, "quantity", None)
#                     feed.cost_per_unit = getattr(f, "costPerUnit", getattr(f, "cost_per_unit", None))
#                     feed.total_amount = getattr(f, "totalAmount", getattr(f, "total_amount", None))
#                     feed.date = getattr(f, "date", None)
#                     feed.is_synced = getattr(f, "isSynced", 0) or 0
#                     feed.updated_at = getattr(f, "updatedAt", None) or datetime.utcnow()
#                 else:
#                     feed = Feed(
#                         id=f_id or str(uuid4()),
#                         farmer_id=user.id,
#                         pond_id=r.unitId,
#                         batch_id=batch.batch_id,
#                         feed_name=getattr(f, "feedName", getattr(f, "feed_name", None)),
#                         feed_form=getattr(f, "feedForm", getattr(f, "feed_form", None)),
#                         feed_size=getattr(f, "feedSize", getattr(f, "feed_size", None)),
#                         quantity=getattr(f, "quantity", None),
#                         unit=getattr(f, "unit", None),
#                         cost_per_unit=getattr(f, "costPerUnit", getattr(f, "cost_per_unit", None)),
#                         total_amount=getattr(f, "totalAmount", getattr(f, "total_amount", None)),
#                         date=getattr(f, "date", None),
#                         is_synced=getattr(f, "isSynced", 0) or 0,
#                         created_at=getattr(f, "createdAt", None) or datetime.utcnow(),
#                         updated_at=getattr(f, "updatedAt", None) or datetime.utcnow(),
#                     )
#                     db.add(feed)
#
#             # Labour
#             for l in fin.get("labour", []) if isinstance(fin, dict) else (fin.labour or []):
#                 l_id = getattr(l, "id", l.get("id") if isinstance(l, dict) else None)
#                 labour = db.query(Labour).filter(Labour.id == l_id).first()
#                 if labour:
#                     labour.labour_type = getattr(l, "labourType", getattr(l, "labour_type", None))
#                     labour.number_of_workers = getattr(l, "numberOfWorkers", getattr(l, "number_of_workers", None))
#                     labour.total_amount = getattr(l, "totalAmount", getattr(l, "total_amount", None))
#                     labour.date = getattr(l, "date", None)
#                     labour.payment_method = getattr(l, "paymentMethod", getattr(l, "payment_method", None))
#                     labour.notes = getattr(l, "notes", None)
#                     labour.is_synced = getattr(l, "isSynced", 0) or 0
#                     labour.updated_at = getattr(l, "updatedAt", None) or datetime.utcnow()
#                 else:
#                     labour = Labour(
#                         id=l_id or str(uuid4()),
#                         farmer_id=user.id,
#                         pond_id=r.unitId,
#                         batch_id=batch.batch_id,
#                         labour_type=getattr(l, "labourType", getattr(l, "labour_type", None)),
#                         number_of_workers=getattr(l, "numberOfWorkers", getattr(l, "number_of_workers", None)),
#                         total_amount=getattr(l, "totalAmount", getattr(l, "total_amount", None)),
#                         date=getattr(l, "date", None),
#                         payment_method=getattr(l, "paymentMethod", getattr(l, "payment_method", None)),
#                         notes=getattr(l, "notes", None),
#                         is_synced=getattr(l, "isSynced", 0) or 0,
#                         created_at=getattr(l, "createdAt", None) or datetime.utcnow(),
#                         updated_at=getattr(l, "updatedAt", None) or datetime.utcnow(),
#                     )
#                     db.add(labour)
#
#             # Medication
#             for m in fin.get("medication", []) if isinstance(fin, dict) else (fin.medication or []):
#                 m_id = getattr(m, "id", m.get("id") if isinstance(m, dict) else None)
#                 med = db.query(Medication).filter(Medication.id == m_id).first()
#                 if med:
#                     med.medication_name = getattr(m, "medicationName", getattr(m, "medication_name", None))
#                     med.quantity = getattr(m, "quantity", None)
#                     med.total_cost = getattr(m, "totalCost", getattr(m, "total_cost", None))
#                     med.date_paid = getattr(m, "datePaid", getattr(m, "date_paid", None))
#                     med.payment_method = getattr(m, "paymentMethod", getattr(m, "payment_method", None))
#                     med.notes = getattr(m, "notes", None)
#                     med.is_synced = getattr(m, "isSynced", 0) or 0
#                     med.updated_at = getattr(m, "updatedAt", None) or datetime.utcnow()
#                 else:
#                     med = Medication(
#                         id=m_id or str(uuid4()),
#                         farmer_id=user.id,
#                         pond_id=r.unitId,
#                         batch_id=batch.batch_id,
#                         medication_name=getattr(m, "medicationName", getattr(m, "medication_name", None)),
#                         quantity=getattr(m, "quantity", None),
#                         total_cost=getattr(m, "totalCost", getattr(m, "total_cost", None)),
#                         date_paid=getattr(m, "datePaid", getattr(m, "date_paid", None)),
#                         payment_method=getattr(m, "paymentMethod", getattr(m, "payment_method", None)),
#                         notes=getattr(m, "notes", None),
#                         is_synced=getattr(m, "isSynced", 0) or 0,
#                         created_at=getattr(m, "createdAt", None) or datetime.utcnow(),
#                         updated_at=getattr(m, "updatedAt", None) or datetime.utcnow(),
#                     )
#                     db.add(med)
#
#             # Maintenance
#             for mt in fin.get("maintenance", []) if isinstance(fin, dict) else (fin.maintenance or []):
#                 mt_id = getattr(mt, "id", mt.get("id") if isinstance(mt, dict) else None)
#                 maint = db.query(Maintenance).filter(Maintenance.id == mt_id).first()
#                 if maint:
#                     maint.activity_type = getattr(mt, "activityType", getattr(mt, "activity_type", None))
#                     maint.total_cost = getattr(mt, "totalCost", getattr(mt, "total_cost", None))
#                     maint.date_paid = getattr(mt, "datePaid", getattr(mt, "date_paid", None))
#                     maint.payment_method = getattr(mt, "paymentMethod", getattr(mt, "payment_method", None))
#                     maint.notes = getattr(mt, "notes", None)
#                     maint.is_synced = getattr(mt, "isSynced", 0) or 0
#                     maint.updated_at = getattr(mt, "updatedAt", None) or datetime.utcnow()
#                 else:
#                     maint = Maintenance(
#                         id=mt_id or str(uuid4()),
#                         farmer_id=user.id,
#                         pond_id=r.unitId,
#                         batch_id=batch.batch_id,
#                         activity_type=getattr(mt, "activityType", getattr(mt, "activity_type", None)),
#                         total_cost=getattr(mt, "totalCost", getattr(mt, "total_cost", None)),
#                         date_paid=getattr(mt, "datePaid", getattr(mt, "date_paid", None)),
#                         payment_method=getattr(mt, "paymentMethod", getattr(mt, "payment_method", None)),
#                         notes=getattr(mt, "notes", None),
#                         is_synced=getattr(mt, "isSynced", 0) or 0,
#                         created_at=getattr(mt, "createdAt", None) or datetime.utcnow(),
#                         updated_at=getattr(mt, "updatedAt", None) or datetime.utcnow(),
#                     )
#                     db.add(maint)
#
#             # Logistics
#             for lg in fin.get("logistics", []) if isinstance(fin, dict) else (fin.logistics or []):
#                 lg_id = getattr(lg, "id", lg.get("id") if isinstance(lg, dict) else None)
#                 log = db.query(Logistics).filter(Logistics.id == lg_id).first()
#                 if log:
#                     log.activity_type = getattr(lg, "activityType", getattr(lg, "activity_type", None))
#                     log.total_cost = getattr(lg, "totalCost", getattr(lg, "total_cost", None))
#                     log.date_paid = getattr(lg, "datePaid", getattr(lg, "date_paid", None))
#                     log.payment_method = getattr(lg, "paymentMethod", getattr(lg, "payment_method", None))
#                     log.notes = getattr(lg, "notes", None)
#                     log.is_synced = getattr(lg, "isSynced", 0) or 0
#                     log.updated_at = getattr(lg, "updatedAt", None) or datetime.utcnow()
#                 else:
#                     log = Logistics(
#                         id=lg_id or str(uuid4()),
#                         farmer_id=user.id,
#                         pond_id=r.unitId,
#                         batch_id=batch.batch_id,
#                         activity_type=getattr(lg, "activityType", getattr(lg, "activity_type", None)),
#                         total_cost=getattr(lg, "totalCost", getattr(lg, "total_cost", None)),
#                         date_paid=getattr(lg, "datePaid", getattr(lg, "date_paid", None)),
#                         payment_method=getattr(lg, "paymentMethod", getattr(lg, "payment_method", None)),
#                         notes=getattr(lg, "notes", None),
#                         is_synced=getattr(lg, "isSynced", 0) or 0,
#                         created_at=getattr(lg, "createdAt", None) or datetime.utcnow(),
#                         updated_at=getattr(lg, "updatedAt", None) or datetime.utcnow(),
#                     )
#                     db.add(log)
#
#             # Operational Expenses
#             for oe in fin.get("operationalExpenses", []) if isinstance(fin, dict) else (fin.operationalExpenses or []):
#                 oe_id = getattr(oe, "id", oe.get("id") if isinstance(oe, dict) else None)
#                 op = db.query(OperationalExpense).filter(OperationalExpense.id == oe_id).first()
#                 if op:
#                     op.expense_name = getattr(oe, "expenseName", getattr(oe, "expense_name", None))
#                     op.total_cost = getattr(oe, "totalCost", getattr(oe, "total_cost", None))
#                     op.date_paid = getattr(oe, "datePaid", getattr(oe, "date_paid", None))
#                     op.payment_method = getattr(oe, "paymentMethod", getattr(oe, "payment_method", None))
#                     op.notes = getattr(oe, "notes", None)
#                     op.is_synced = getattr(oe, "isSynced", 0) or 0
#                     op.updated_at = getattr(oe, "updatedAt", None) or datetime.utcnow()
#                 else:
#                     op = OperationalExpense(
#                         id=oe_id or str(uuid4()),
#                         farmer_id=user.id,
#                         pond_id=r.unitId,
#                         batch_id=batch.batch_id,
#                         expense_name=getattr(oe, "expenseName", getattr(oe, "expense_name", None)),
#                         total_cost=getattr(oe, "totalCost", getattr(oe, "total_cost", None)),
#                         date_paid=getattr(oe, "datePaid", getattr(oe, "date_paid", None)),
#                         payment_method=getattr(oe, "paymentMethod", getattr(oe, "payment_method", None)),
#                         notes=getattr(oe, "notes", None),
#                         is_synced=getattr(oe, "isSynced", 0) or 0,
#                         created_at=getattr(oe, "createdAt", None) or datetime.utcnow(),
#                         updated_at=getattr(oe, "updatedAt", None) or datetime.utcnow(),
#                     )
#                     db.add(op)
#
#         elif not unit:
#             raise HTTPException(status_code=400, detail=f"Unit {r.unitId} not found and unit payload not provided")
#
#         # UnitRecord UPSERT
#         rec = db.query(UnitRecord).filter(UnitRecord.id == r.id).first()
#         if rec:
#             # update
#             rec.stocknumber = r.stocknumber
#             rec.movedfishes = r.movedfishes
#             rec.mortality = r.mortality
#             rec.fishleft = r.fishleft
#             rec.incomingfish = r.incomingfish
#             rec.fishtype = r.fishtype
#             rec.stockedon = r.stockedon
#             rec.totalfishcost = r.totalfishcost
#             rec.is_synced = r.isSynced or 0
#             rec.updated_at = r.updatedAt or datetime.utcnow()
#         else:
#             rec = UnitRecord(
#                 id=r.id or str(uuid4()),
#                 farmer_id=user.id,
#                 batch_id=batch.id,
#                 unit_id=r.unitId,
#                 stocknumber=r.stocknumber,
#                 movedfishes=r.movedfishes,
#                 mortality=r.mortality,
#                 fishleft=r.fishleft,
#                 incomingfish=r.incomingfish,
#                 fishtype=r.fishtype,
#                 stockedon=r.stockedon,
#                 totalfishcost=r.totalfishcost,
#                 is_synced=r.isSynced or 0,
#                 created_at=r.createdAt or datetime.utcnow(),
#                 updated_at=r.updatedAt or datetime.utcnow(),
#             )
#             db.add(rec)
#         db.flush()
#
#         # --- DailyRecords UPSERT ---
#         for d in r.dailyRecords or []:
#             dr = db.query(DailyRecord).filter(DailyRecord.id == d.id).first()
#             if dr:
#                 dr.date = d.date
#                 dr.feed_name = d.feedName
#                 dr.feed_size = d.feedSize
#                 dr.feed_quantity = d.feedQuantity
#                 dr.mortality = d.mortality
#                 dr.coins = d.coins
#                 dr.is_synced = d.isSynced or 0
#                 dr.updated_at = d.updatedAt or datetime.utcnow()
#             else:
#                 dr = DailyRecord(
#                     id=d.id or str(uuid4()),
#                     record_id=rec.id,
#                     farmer_id=user.id,
#                     batch_id=batch.id,
#                     unit_id=d.unitId,
#                     date=d.date,
#                     feed_name=d.feedName,
#                     feed_size=d.feedSize,
#                     feed_quantity=d.feedQuantity,
#                     mortality=d.mortality,
#                     coins=d.coins,
#                     is_synced=d.isSynced or 0,
#                     created_at=d.createdAt or datetime.utcnow(),
#                     updated_at=d.updatedAt or datetime.utcnow(),
#                 )
#                 db.add(dr)
#
#         # --- WeightSamplings UPSERT ---
#         for w in r.weightSamplings or []:
#             ws = db.query(WeightSampling).filter(WeightSampling.id == w.id).first()
#             if ws:
#                 ws.fish_numbers = w.fishNumbers
#                 ws.total_weight = w.totalWeight
#                 ws.completed = w.completed
#                 ws.is_synced = w.isSynced or 0
#                 ws.updated_at = w.updatedAt or datetime.utcnow()
#             else:
#                 ws = WeightSampling(
#                     id=w.id or str(uuid4()),
#                     record_id=rec.id,
#                     farmer_id=user.id,
#                     batch_id=batch.id,
#                     unit_id=w.unitId,
#                     sample_name=w.sampleName,
#                     date=w.date,
#                     fish_numbers=w.fishNumbers,
#                     total_weight=w.totalWeight,
#                     completed=w.completed,
#                     is_synced=w.isSynced or 0,
#                     created_at=w.createdAt or datetime.utcnow(),
#                     updated_at=w.updatedAt or datetime.utcnow(),
#                 )
#                 db.add(ws)
#
#         # --- Grading & Sortings UPSERT ---
#         for g in r.gradingAndSortings or []:
#             grading = db.query(GradingAndSorting).filter(GradingAndSorting.id == g.id).first()
#             if grading:
#                 grading.fish_numbers = g.fishNumbers
#                 grading.total_weight = g.totalWeight
#                 grading.completed = g.completed
#                 grading.is_synced = g.isSynced or 0
#                 grading.updated_at = g.updatedAt or datetime.utcnow()
#             else:
#                 grading = GradingAndSorting(
#                     id=g.id or str(uuid4()),
#                     record_id=rec.id,
#                     farmer_id=user.id,
#                     batch_id=batch.id,
#                     unit_id=g.unitId,
#                     grade_with=g.gradeWith,
#                     sample_name=g.sampleName,
#                     date=g.date,
#                     grading_pond_number=g.gradingPondNumber,
#                     fish_numbers=g.fishNumbers,
#                     total_weight=g.totalWeight,
#                     completed=g.completed,
#                     is_synced=g.isSynced or 0,
#                     created_at=g.createdAt or datetime.utcnow(),
#                     updated_at=g.updatedAt or datetime.utcnow(),
#                 )
#                 db.add(grading)
#                 db.flush()
#
#             # Grades
#             for gr in g.grades or []:
#                 grade = db.query(Grade).filter(Grade.id == gr.id).first()
#                 if grade:
#                     grade.average_fish_weight = gr.averageFishWeight
#                     grade.fish_transferred = gr.fishTransferred
#                     grade.is_synced = gr.isSynced or 0
#                     grade.updated_at = gr.updatedAt or datetime.utcnow()
#                 else:
#                     grade = Grade(
#                         id=gr.id or str(uuid4()),
#                         sorting_id=grading.id,
#                         destination_batch_id=gr.destinationBatchId,
#                         destination_batch_name=gr.destinationBatchName,
#                         destination_unit_id=gr.destinationUnitId,
#                         destination_unit_name=gr.destinationUnitName,
#                         average_fish_weight=gr.averageFishWeight,
#                         fish_transferred=gr.fishTransferred,
#                         sample_name=gr.sampleName,
#                         record_id=rec.id,
#                         batch_id=batch.id,
#                         is_synced=gr.isSynced or 0,
#                         created_at=gr.createdAt or datetime.utcnow(),
#                         updated_at=gr.updatedAt or datetime.utcnow(),
#                     )
#                     db.add(grade)
#
#         # --- Harvests UPSERT ---
#         for h in r.harvests or []:
#             hv = db.query(HarvestForm).filter(HarvestForm.id == h.id).first()
#             if hv:
#                 hv.quantity_harvest = h.quantityHarvest
#                 hv.total_weight = h.totalWeight
#                 hv.price_per_kg = h.pricePerKg
#                 hv.total_sales = h.totalSales
#                 hv.is_synced = h.isSynced or 0
#                 hv.updated_at = h.updatedAt or datetime.utcnow()
#             else:
#                 hv = HarvestForm(
#                     id=h.id or str(uuid4()),
#                     record_id=rec.id,
#                     farmer_id=user.id,
#                     batch_id=batch.id,
#                     unit_id=h.unitId,
#                     date=h.date,
#                     sales_invoice_number=h.salesInvoiceNumber,
#                     quantity_harvest=h.quantityHarvest,
#                     total_weight=h.totalWeight,
#                     price_per_kg=h.pricePerKg,
#                     total_sales=h.totalSales,
#                     is_synced=h.isSynced or 0,
#                     created_at=h.createdAt or datetime.utcnow(),
#                     updated_at=h.updatedAt or datetime.utcnow(),
#                 )
#                 db.add(hv)
#
#     try:
#         db.commit()
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Error saving batch: {str(e)}")
#
#     return {"detail": "Batch created/updated", "batchId": batch.batch_id}



# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from uuid import uuid4
# from datetime import datetime
# from typing import List
#
# from ..database import get_db
# from syncsehemas import BatchIn
# from ..models import (
#     User, Batch, Unit, UnitRecord, DailyRecord,
#     WeightSampling, HarvestForm, Grade, GradingAndSorting
# )
# from ..dep.security import get_current_user
#
# router = APIRouter(prefix="/batches", tags=["Batch"])
#
#
# @router.post("/", status_code=201)
# def create_batch(
#     payload: BatchIn,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user)
# ):
#     """
#     Create a batch with nested unit records and all children.
#     Farmer is always the authenticated user.
#     """
#     # Validate current user
#     db_user = db.query(User).filter(User.id == user.id).first()
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     # Auto-generate batchId if not provided
#     batch_id = payload.batchId or str(uuid4())
#
#     # Create Batch
#     batch = Batch(
#         batch_id=batch_id,
#         farmer_id=user.id,
#         batch_name=payload.batchName,
#         fishtype=payload.fishtype,
#         number_of_fishes=payload.numberoffishes,
#         average_body_weight=payload.averagebodyweight,
#         age_at_stock=payload.ageAtStock,
#         is_completed=payload.isCompleted or 0,
#         is_synced=payload.isSynced or 0,
#         created_at=payload.createdAt or datetime.utcnow(),
#         updated_at=payload.updatedAt or datetime.utcnow(),
#     )
#     db.add(batch)
#     db.flush()  # Ensure batch_id is available
#
#     # Insert UnitRecords and nested children
#     for r in payload.records or []:
#         # Ensure Unit exists
#         unit = db.query(Unit).filter(Unit.id == r.unitId).first()
#         if not unit:
#             if r.unit:
#                 u = r.unit  # UnitIn instance
#                 unit = Unit(
#                     id=u.id,
#                     farmer_id=u.farmerId or user.id,
#                     unit_name=u.unitName or "unknown",
#                     unit_type=u.unitType,
#                     unit_dimension=u.unitDimension,
#                     unit_capacity=u.unitCapacity,
#                     fishes=u.fishes,
#                     image_file=u.imageFile,
#                     image_url=u.imageUrl,
#                     unitcategory=getattr(u, "unitcategory", None),
#                     is_active=u.isActive or 0,
#                     is_synced=u.isSynced or 0,
#                     created_at=u.createdAt or datetime.utcnow(),
#                     updated_at=u.updatedAt or datetime.utcnow(),
#                 )
#                 db.add(unit)
#                 db.flush()
#             else:
#                 raise HTTPException(status_code=400, detail=f"Unit {r.unitId} not found and unit payload not provided")
#
#         # UnitRecord
#         # rec = UnitRecord(
#         #     id=r.id or str(uuid4()),
#         #     farmer_id=user.id,
#         #     batch_id=batch.batch_id,
#         #     unit_id=r.unitId,
#         #     stocknumber=r.stocknumber,
#         #     movedfishes=r.movedfishes,
#         #     mortality=r.mortality,
#         #     fishleft=r.fishleft,
#         #     incomingfish=r.incomingfish,
#         #     fishtype=r.fishtype,
#         #     stockedon=r.stockedon,
#         #     totalfishcost=r.totalfishcost,
#         #     is_synced=r.isSynced or 0,
#         #     created_at=r.createdAt or datetime.utcnow(),
#         #     updated_at=r.updatedAt or datetime.utcnow(),
#         # )
#         rec = UnitRecord(
#             id=r.id or str(uuid4()),
#             farmer_id=user.id,
#             batch_id=batch.id,  # <-- must be the PK that matches unit_records FK
#             unit_id=r.unitId,
#             stocknumber=r.stocknumber,
#             movedfishes=r.movedfishes,
#             mortality=r.mortality,
#             fishleft=r.fishleft,
#             incomingfish=r.incomingfish,
#             fishtype=r.fishtype,
#             stockedon=r.stockedon,
#             totalfishcost=r.totalfishcost,
#             is_synced=r.isSynced or 0,
#             created_at=r.createdAt or datetime.utcnow(),
#             updated_at=r.updatedAt or datetime.utcnow(),
#         )
#
#         db.add(rec)
#         db.flush()
#
#         # DailyRecords
#         for d in r.dailyRecords or []:
#             dr = DailyRecord(
#                 id=d.id or str(uuid4()),
#                 record_id=rec.id,
#                 farmer_id=user.id,
#                 # batch_id=
#                 # ,
#                 batch_id=batch.id,
#
#                 unit_id=d.unitId,
#                 date=d.date,
#                 feed_name=d.feedName,
#                 feed_size=d.feedSize,
#                 feed_quantity=d.feedQuantity,
#                 mortality=d.mortality,
#                 coins=d.coins,
#                 is_synced=d.isSynced or 0,
#                 created_at=d.createdAt or datetime.utcnow(),
#                 updated_at=d.updatedAt or datetime.utcnow(),
#             )
#             db.add(dr)
#
#         # WeightSamplings
#         for w in r.weightSamplings or []:
#             ws = WeightSampling(
#                 id=w.id or str(uuid4()),
#                 record_id=rec.id,
#                 farmer_id=user.id,
#                 batch_id=batch.id,
#
#                 # batch_id=batch.batch_id,
#                 unit_id=w.unitId,
#                 sample_name=w.sampleName,
#                 date=w.date,
#                 fish_numbers=w.fishNumbers,
#                 total_weight=w.totalWeight,
#                 completed=w.completed,
#                 is_synced=w.isSynced or 0,
#                 created_at=w.createdAt or datetime.utcnow(),
#                 updated_at=w.updatedAt or datetime.utcnow(),
#             )
#             db.add(ws)
#
#         # Grading & Sortings + Grades
#         for g in r.gradingAndSortings or []:
#             grading = GradingAndSorting(
#                 id=g.id or str(uuid4()),
#                 record_id=rec.id,
#                 farmer_id=user.id,
#                 batch_id=batch.id,
#
#                 # batch_id=batch.batch_id,
#                 unit_id=g.unitId,
#                 grade_with=g.gradeWith,
#                 sample_name=g.sampleName,
#                 date=g.date,
#                 grading_pond_number=g.gradingPondNumber,
#                 fish_numbers=g.fishNumbers,
#                 total_weight=g.totalWeight,
#                 completed=g.completed,
#                 is_synced=g.isSynced or 0,
#                 created_at=g.createdAt or datetime.utcnow(),
#                 updated_at=g.updatedAt or datetime.utcnow(),
#             )
#             db.add(grading)
#             db.flush()
#
#             for gr in g.grades or []:
#                 grade = Grade(
#                     id=gr.id or str(uuid4()),
#                     sorting_id=grading.id,
#                     destination_batch_id=gr.destinationBatchId,
#                     destination_batch_name=gr.destinationBatchName,
#                     destination_unit_id=gr.destinationUnitId,
#                     destination_unit_name=gr.destinationUnitName,
#                     average_fish_weight=gr.averageFishWeight,
#                     fish_transferred=gr.fishTransferred,
#                     sample_name=gr.sampleName,
#                     record_id=rec.id,
#                     batch_id=batch.id,
#
#                     # batch_id=batch.batch_id,
#                     is_synced=gr.isSynced or 0,
#                     created_at=gr.createdAt or datetime.utcnow(),
#                     updated_at=gr.updatedAt or datetime.utcnow(),
#                 )
#                 db.add(grade)
#
#         # Harvests
#         for h in r.harvests or []:
#             hv = HarvestForm(
#                 id=h.id or str(uuid4()),
#                 record_id=rec.id,
#                 farmer_id=user.id,
#                 batch_id=batch.id,
#
#                 # batch_id=batch.batch_id,
#                 unit_id=h.unitId,
#                 date=h.date,
#                 sales_invoice_number=h.salesInvoiceNumber,
#                 quantity_harvest=h.quantityHarvest,
#                 total_weight=h.totalWeight,
#                 price_per_kg=h.pricePerKg,
#                 total_sales=h.totalSales,
#                 is_synced=h.isSynced or 0,
#                 created_at=h.createdAt or datetime.utcnow(),
#                 updated_at=h.updatedAt or datetime.utcnow(),
#             )
#             db.add(hv)
#
#     # Commit once
#     try:
#         db.commit()
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Error saving batch: {str(e)}")
#
#     return {"detail": "Batch created", "batchId": batch.batch_id}
#
#
# # from fastapi import APIRouter, Depends, HTTPException
# # from sqlalchemy.orm import Session
# # from uuid import uuid4
# # from datetime import datetime
# # from typing import List
# #
# # from ..database import get_db
# # from syncsehemas import BatchIn
# # from ..models import (
# #     User, Batch, Unit, UnitRecord, DailyRecord,
# #     WeightSampling, HarvestForm, Grade, GradingAndSorting
# # )
# # from ..dep.security import get_current_user
# #
# # router = APIRouter(prefix="/batches", tags=["Batch"])
# #
# #
# # @router.post("/", status_code=201)
# # def create_batch(payload: BatchIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
# #     """
# #     Create a batch with nested unit records and all children.
# #     Farmer is always the authenticated user.
# #     """
# #     # Validate current user
# #     db_user = db.query(User).filter(User.id == user.id).first()
# #     if not db_user:
# #         raise HTTPException(status_code=404, detail="User not found")
# #
# #     # Auto-generate batchId if not provided
# #     batch_id = payload.batchId or str(uuid4())
# #
# #     # Create Batch
# #     batch = Batch(
# #         batch_id=batch_id,
# #         farmer_id=user.id,
# #         batch_name=payload.batchName,
# #         fishtype=payload.fishtype,
# #         number_of_fishes=payload.numberoffishes,
# #         average_body_weight=payload.averagebodyweight,
# #         age_at_stock=payload.ageAtStock,
# #         is_completed=payload.isCompleted or 0,
# #         is_synced=payload.isSynced or 0,
# #         created_at=payload.createdAt or datetime.utcnow(),
# #         updated_at=payload.updatedAt or datetime.utcnow(),
# #     )
# #     db.add(batch)
# #     db.flush()  # Ensure batch_id is available
# #
# #     # Insert UnitRecords and nested children
# #     for r in payload.records or []:
# #         # Ensure Unit exists
# #         unit = db.query(Unit).filter(Unit.id == r.unitId).first()
# #         if not unit:
# #             if r.unit:
# #                 unit = Unit(
# #                     id=r.unit.get("id"),
# #                     farmer_id=r.unit.get("farmerId", user.id),
# #                     unit_name=r.unit.get("unitName", "unknown"),
# #                     unit_type=r.unit.get("unitType"),
# #                     unit_dimension=r.unit.get("unitDimension"),
# #                     unit_capacity=r.unit.get("unitCapacity"),
# #                     fishes=r.unit.get("fishes"),
# #                     image_file=r.unit.get("imageFile"),
# #                     image_url=r.unit.get("imageUrl"),
# #                     unitcategory=r.unit.get("unitcategory"),
# #                     is_active=r.unit.get("isActive", 0),
# #                     is_synced=r.unit.get("isSynced", 0),
# #                     created_at=r.unit.get("createdAt", datetime.utcnow()),
# #                     updated_at=r.unit.get("updatedAt", datetime.utcnow()),
# #                 )
# #                 db.add(unit)
# #                 db.flush()
# #             else:
# #                 raise HTTPException(status_code=400, detail=f"Unit {r.unitId} not found and unit payload not provided")
# #
# #         # UnitRecord
# #         rec = UnitRecord(
# #             id=r.id or str(uuid4()),
# #             farmer_id=user.id,
# #             batch_id=batch.batch_id,
# #             unit_id=r.unitId,
# #             stocknumber=r.stocknumber,
# #             movedfishes=r.movedfishes,
# #             mortality=r.mortality,
# #             fishleft=r.fishleft,
# #             incomingfish=r.incomingfish,
# #             fishtype=r.fishtype,
# #             stockedon=r.stockedon,
# #             totalfishcost=r.totalfishcost,
# #             is_synced=r.isSynced or 0,
# #             created_at=r.createdAt or datetime.utcnow(),
# #             updated_at=r.updatedAt or datetime.utcnow(),
# #         )
# #         db.add(rec)
# #         db.flush()
# #
# #         # DailyRecords
# #         for d in r.dailyRecords or []:
# #             dr = DailyRecord(
# #                 id=d.id or str(uuid4()),
# #                 record_id=rec.id,
# #                 farmer_id=user.id,
# #                 batch_id=batch.batch_id,
# #                 unit_id=d.unitId,
# #                 date=d.date,
# #                 feed_name=d.feedName,
# #                 feed_size=d.feedSize,
# #                 feed_quantity=d.feedQuantity,
# #                 mortality=d.mortality,
# #                 coins=d.coins,
# #                 is_synced=d.isSynced or 0,
# #                 created_at=d.createdAt or datetime.utcnow(),
# #                 updated_at=d.updatedAt or datetime.utcnow(),
# #             )
# #             db.add(dr)
# #
# #         # WeightSamplings
# #         for w in r.weightSamplings or []:
# #             ws = WeightSampling(
# #                 id=w.id or str(uuid4()),
# #                 record_id=rec.id,
# #                 farmer_id=user.id,
# #                 batch_id=batch.batch_id,
# #                 unit_id=w.unitId,
# #                 sample_name=w.sampleName,
# #                 date=w.date,
# #                 fish_numbers=w.fishNumbers,
# #                 total_weight=w.totalWeight,
# #                 completed=w.completed,
# #                 is_synced=w.isSynced or 0,
# #                 created_at=w.createdAt or datetime.utcnow(),
# #                 updated_at=w.updatedAt or datetime.utcnow(),
# #             )
# #             db.add(ws)
# #
# #         # Grading & Sortings + Grades
# #         for g in r.gradingAndSortings or []:
# #             grading = GradingAndSorting(
# #                 id=g.id or str(uuid4()),
# #                 record_id=rec.id,
# #                 farmer_id=user.id,
# #                 batch_id=batch.batch_id,
# #                 unit_id=g.unitId,
# #                 grade_with=g.gradeWith,
# #                 sample_name=g.sampleName,
# #                 date=g.date,
# #                 grading_pond_number=g.gradingPondNumber,
# #                 fish_numbers=g.fishNumbers,
# #                 total_weight=g.totalWeight,
# #                 completed=g.completed,
# #                 is_synced=g.isSynced or 0,
# #                 created_at=g.createdAt or datetime.utcnow(),
# #                 updated_at=g.updatedAt or datetime.utcnow(),
# #             )
# #             db.add(grading)
# #             db.flush()
# #
# #             for gr in g.grades or []:
# #                 grade = Grade(
# #                     id=gr.id or str(uuid4()),
# #                     sorting_id=grading.id,
# #                     destination_batch_id=gr.destinationBatchId,
# #                     destination_batch_name=gr.destinationBatchName,
# #                     destination_unit_id=gr.destinationUnitId,
# #                     destination_unit_name=gr.destinationUnitName,
# #                     average_fish_weight=gr.averageFishWeight,
# #                     fish_transferred=gr.fishTransferred,
# #                     sample_name=gr.sampleName,
# #                     record_id=rec.id,
# #                     batch_id=batch.batch_id,
# #                     is_synced=gr.isSynced or 0,
# #                     created_at=gr.createdAt or datetime.utcnow(),
# #                     updated_at=gr.updatedAt or datetime.utcnow(),
# #                 )
# #                 db.add(grade)
# #
# #         # Harvests
# #         for h in r.harvests or []:
# #             hv = HarvestForm(
# #                 id=h.id or str(uuid4()),
# #                 record_id=rec.id,
# #                 farmer_id=user.id,
# #                 batch_id=batch.batch_id,
# #                 unit_id=h.unitId,
# #                 date=h.date,
# #                 sales_invoice_number=h.salesInvoiceNumber,
# #                 quantity_harvest=h.quantityHarvest,
# #                 total_weight=h.totalWeight,
# #                 price_per_kg=h.pricePerKg,
# #                 total_sales=h.totalSales,
# #                 is_synced=h.isSynced or 0,
# #                 created_at=h.createdAt or datetime.utcnow(),
# #                 updated_at=h.updatedAt or datetime.utcnow(),
# #             )
# #             db.add(hv)
# #
# #     # Commit once
# #     try:
# #         db.commit()
# #     except Exception as e:
# #         db.rollback()
# #         raise HTTPException(status_code=500, detail=f"Error saving batch: {str(e)}")
# #
# #     return {"detail": "Batch created", "batchId": batch.batch_id}
