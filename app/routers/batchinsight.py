from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from typing import List
from ..database import get_db
from ..models import (
    User, Batch, Unit, UnitRecord, DailyRecord,
    WeightSampling, HarvestForm, Grade, GradingAndSorting, BatchInsight
)
from ..dep.security import get_current_user
router = APIRouter(prefix="/batch", tags=["Batch"])
from fastapi import HTTPException
from ..models import Batch, DailyRecord, WeightSampling, HarvestForm
from ..services.insights_service import (
    load_batch_data,
    index_by_date,
    compute_daily_kpis
)




class DailyPerformanceOut(BaseModel):
    date: str
    month: int
    month_name: str
    batch_id: str

    population_start: int
    population_end: int
    recorded_mortality_no: int
    recorded_mortality_percent: float
    harvest_no: int

    abw_start_g: float
    abw_end_g: float
    growth_rate_g_per_day: float
    SGR_percent: float
    ADG_g: float

    biomass_start_kg: float
    biomass_end_kg: float
    growth_kg: float
    accumulated_growth_kg: float

    feed_recorded_kg: float
    accumulated_feed_kg: float
    FCR: float | None
    accumulated_FCR: float | None
@router.get("/{batch_id}/performance-insights", response_model=List[DailyPerformanceOut])
def get_batch_performance_insights(
    batch_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    batch = (
        db.query(Batch)
        .filter(Batch.batch_id == batch_id)
        .first()
    )

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    daily_records, weight_samples, harvests = load_batch_data(
        db, batch, DailyRecord, WeightSampling, HarvestForm
    )

    daily_map, sample_map, harvest_map = index_by_date(
        daily_records, weight_samples, harvests
    )

    rows = compute_daily_kpis(batch, daily_map, sample_map, harvest_map)

    for row in rows:
        insight = BatchInsight(
            batch_id=row["batch_id"],
            date=row["date"],
            month=row["month"],
            month_name=row["month_name"],
            population_start=row["population_start"],
            population_end=row["population_end"],
            recorded_mortality_no=row["recorded_mortality_no"],
            recorded_mortality_percent=row["recorded_mortality_percent"],
            harvest_no=row["harvest_no"],
            abw_start_g=row["abw_start_g"],
            abw_end_g=row["abw_end_g"],
            growth_rate_g_per_day=row["growth_rate_g_per_day"],
            sgr_percent=row["SGR_percent"],
            adg_g=row["ADG_g"],
            biomass_start_kg=row["biomass_start_kg"],
            biomass_end_kg=row["biomass_end_kg"],
            growth_kg=row["growth_kg"],
            accumulated_growth_kg=row["accumulated_growth_kg"],
            feed_recorded_kg=row["feed_recorded_kg"],
            accumulated_feed_kg=row["accumulated_feed_kg"],
            fcr=row["FCR"],
            accumulated_fcr=row["accumulated_FCR"],
        )
        db.add(insight)

    db.commit()

    return rows
