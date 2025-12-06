from datetime import date, timedelta
from math import log
from collections import defaultdict

def load_batch_data(db, batch, DailyRecord, WeightSampling, HarvestForm):
    daily_records = (
        db.query(DailyRecord)
        .filter(DailyRecord.batch_id == batch.id)
        .order_by(DailyRecord.date)
        .all()
    )

    weight_samples = (
        db.query(WeightSampling)
        .filter(WeightSampling.batch_id == batch.id)
        .order_by(WeightSampling.date)
        .all()
    )

    harvests = (
        db.query(HarvestForm)
        .filter(HarvestForm.batch_id == batch.id)
        .order_by(HarvestForm.date)
        .all()
    )

    return daily_records, weight_samples, harvests


def index_by_date(daily_records, weight_samples, harvests):
    daily_map = defaultdict(lambda: {"feed_kg": 0.0, "mortality": 0})
    sample_map = {}
    harvest_map = defaultdict(lambda: {"harvest_count": 0})

    # Daily log
    for d in daily_records:
        key = d.date
        daily_map[key]["feed_kg"] += float(d.feed_quantity or 0)
        daily_map[key]["mortality"] += int(d.mortality or 0)

    # ABW sampling
    for w in weight_samples:
        key = w.date
        if w.total_weight and w.fish_numbers:
            abw = (w.total_weight * 1000.0) / max(1, w.fish_numbers)
            sample_map[key] = abw

    # Harvest log
    for h in harvests:
        key = h.date
        harvest_map[key]["harvest_count"] += int(h.quantity_harvest or 0)

    return daily_map, sample_map, harvest_map


def compute_daily_kpis(batch, daily_map, sample_map, harvest_map):
    all_dates = sorted(daily_map.keys() | sample_map.keys() | harvest_map.keys())
    if not all_dates:
        return []

    start_date = min(all_dates)
    end_date = max(all_dates)

    population = int(batch.number_of_fishes or 0)
    abw_current = float(batch.average_body_weight or 0.0)

    accumulated_feed_kg = 0.0
    accumulated_growth_kg = 0.0

    prev_abw = abw_current
    rows = []
    current = start_date

    while current <= end_date:
        feed_kg = daily_map[current]["feed_kg"]
        mortality_no = daily_map[current]["mortality"]
        harvest_no = harvest_map[current]["harvest_count"]

        population_start = population
        population_end = max(0, population_start - mortality_no - harvest_no)

        abw_start = prev_abw
        abw_end = sample_map[current] if current in sample_map else abw_start

        # Growth
        try:
            sgr_percent = ((log(abw_end) - log(abw_start)) / 1) * 100.0 if abw_end > abw_start else 0
        except ValueError:
            sgr_percent = 0

        adg = abw_end - abw_start

        biomass_start_kg = (population_start * abw_start) / 1000.0
        biomass_end_kg = (population_end * abw_end) / 1000.0

        growth_kg = biomass_end_kg - biomass_start_kg

        accumulated_feed_kg += feed_kg
        accumulated_growth_kg += growth_kg

        fcr = (feed_kg / growth_kg) if growth_kg > 0 else None
        accumulated_fcr = (accumulated_feed_kg / accumulated_growth_kg) if accumulated_growth_kg > 0 else None

        mortality_percent = (mortality_no / population_start) * 100 if population_start > 0 else 0

        rows.append({
            "date": str(current),
            "month": current.month,
            "month_name": current.strftime("%B"),
            "batch_id": batch.batch_id,

            "population_start": population_start,
            "population_end": population_end,
            "recorded_mortality_no": mortality_no,
            "recorded_mortality_percent": mortality_percent,
            "harvest_no": harvest_no,

            "abw_start_g": abw_start,
            "abw_end_g": abw_end,
            "growth_rate_g_per_day": adg,
            "SGR_percent": sgr_percent,
            "ADG_g": adg,

            "biomass_start_kg": biomass_start_kg,
            "biomass_end_kg": biomass_end_kg,
            "growth_kg": growth_kg,
            "accumulated_growth_kg": accumulated_growth_kg,

            "feed_recorded_kg": feed_kg,
            "accumulated_feed_kg": accumulated_feed_kg,
            "FCR": fcr,
            "accumulated_FCR": accumulated_fcr
        })

        population = population_end
        prev_abw = abw_end
        current += timedelta(days=1)

    return rows
