"""
Calculation engine for the Shared-Mobility Parking & Impact tool.

This module is a line-by-line port of the calculation logic in the source
Excel workbook "AVR - excel tool - mockup - v3.xlsb", specifically the
sheets:
    - New development overview   (the main input/output sheet)
    - Carsharing statistics      (benchmark statistics engine)
    - Model_calc_new_dev_active_users  (beta-regression prediction interval)
    - Model_calc_new_dev_emission      (emission impact calculation)
    - Country level assumptions / City level assumptions (policy constants)

It is intentionally decoupled from Streamlit so it can be unit-tested and
reused. All functions operate on plain Python / numpy / pandas objects.

A few oddities were found in the source workbook while porting it; they are
replicated exactly (not "fixed") and flagged in KNOWN_QUIRKS below, since
the brief was to match the Excel tool's exact calculation mechanism.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

REF_DIR = Path(__file__).parent / "reference"

KNOWN_QUIRKS = [
    "Active-user regression: the input labelled 'perc_pop_25to45yr' is wired in the "
    "source sheet to PC4 column FL ('perc_pop_45to65yr'), not FK ('perc_pop_25to45yr'). "
    "Replicated as built; worth confirming with the model owner.",
    "Car emission factors: the source sheet's 'Petrol cars' row pulls from the "
    "PBL_emission factors row labelled 'Diesel' (and vice-versa for 'Diesel cars'). "
    "Replicated as built.",
    "Impact B (modal shift to public transport): the own-car-emission term is scaled "
    "to kg (divided by 1000) but the public-transport-alternative term is not, so the "
    "PT term is ~1000x smaller than intended and contributes negligibly to the result. "
    "Replicated as built.",
    "Own/shared fuel-mix selector has an unreachable 'city level' branch when no "
    "PC4-level data exists for the area (it always falls back to the country average "
    "in that case). Replicated behaviourally.",
    "Active-user prediction interval: the width is Z * confidence_level * SD (95% Z-score "
    "times the 0.95 confidence-level input, not the adjacent 'error multiplier' input that "
    "looks like it's meant for this). Replicated as built; the error multiplier is unused.",
]

Z_95 = 1.959963984540054  # NORM.S.INV(0.975)


# --------------------------------------------------------------------------
# Reference data loading
# --------------------------------------------------------------------------

@dataclass
class ReferenceData:
    constants: dict
    existing_areas: pd.DataFrame
    pc4_info: pd.DataFrame
    city_diesel_share: pd.DataFrame
    projects: pd.DataFrame

    @property
    def country(self):
        return self.constants["country_assumptions"]

    @property
    def emission_factors(self):
        return self.constants["emission_factors_g_per_km"]

    @property
    def regression(self):
        return self.constants["regression_active_users"]


def load_reference_data(ref_dir: Path = REF_DIR) -> ReferenceData:
    constants = json.loads((ref_dir / "constants.json").read_text())
    existing_areas = pd.read_csv(ref_dir / "existing_areas_benchmark.csv")
    pc4_info = pd.read_csv(ref_dir / "pc4_info.csv")
    city_diesel_share = pd.read_csv(ref_dir / "city_diesel_share.csv")
    projects = pd.read_csv(ref_dir / "projects.csv")
    return ReferenceData(constants, existing_areas, pc4_info, city_diesel_share, projects)


# --------------------------------------------------------------------------
# PC4 / City / Country level lookups (section 1, 3, 4, 5 defaults)
# --------------------------------------------------------------------------

def pc4_level_default(pc4_info: pd.DataFrame, col: str, level: str, pc4: Optional[int], city: Optional[str]):
    """Replicates the IF(D='City level', MEDIAN(...), IF(D='Country level', MEDIAN(...), SUMIFS(...))) pattern."""
    if level == "City level":
        vals = pc4_info.loc[pc4_info.City == city, col].dropna()
        return float(vals.median()) if len(vals) else 0.0
    if level == "Country level":
        return float(pc4_info[col].dropna().median())
    # PC4 level (SUMIFS on a single matching PC4 == direct lookup)
    vals = pc4_info.loc[pc4_info.PC4 == pc4, col].dropna()
    return float(vals.sum()) if len(vals) else 0.0


def has_pt_in_1km(pc4_info: pd.DataFrame, level: str, pc4: Optional[int], city: Optional[str]) -> bool:
    if level == "City level":
        vals = pc4_info.loc[pc4_info.City == city, "has_pt_1km"]
        return bool(len(vals) and vals.mean() >= 0.5)
    if level == "Country level":
        return bool(pc4_info["has_pt_1km"].mean() >= 0.5)
    vals = pc4_info.loc[pc4_info.PC4 == pc4, "has_pt_1km"]
    return bool(len(vals) and (vals == 1).sum() == 1)


# --------------------------------------------------------------------------
# Carsharing statistics: the shared 4-branch "which level?" picker used for
# hours-driven-per-person, hours-driven-per-car, AVR and distance-per-car.
# --------------------------------------------------------------------------

def _percentile(series: pd.Series, q: float) -> float:
    s = series.dropna()
    if len(s) == 0:
        return 0.0
    return float(np.percentile(s.to_numpy(), q * 100))


def carsharing_metric_range(ea: pd.DataFrame, col: str, level: str, pc4: Optional[int], city: Optional[str],
                             benchmark_postcodes: list[int], positive_only: bool = True) -> tuple[float, float]:
    """Replicates the L4/M4 (and L12/M12, L49/M49, L57/M57) formula family in 'Carsharing statistics'."""
    base = ea[ea[col] > 0] if positive_only else ea
    country_p25 = _percentile(base[col], 0.25)
    country_p75 = _percentile(base[col], 0.75)

    city_rows = base[base.City == city]
    city_p25 = _percentile(city_rows[col], 0.25)
    city_p75 = _percentile(city_rows[col], 0.75)

    pc4_rows = ea.loc[ea.PC4 == pc4, col].dropna()  # SUMIFS ignores the >0 filter
    pc4_direct = float(pc4_rows.sum()) if len(pc4_rows) else 0.0

    bench_rows = base[base.PC4.isin(benchmark_postcodes)]
    bench_p25 = _percentile(bench_rows[col], 0.25)
    bench_p75 = _percentile(bench_rows[col], 0.75)

    if level == "Benchmark":
        return bench_p25, bench_p75
    if level == "PC4 level":
        if pc4_direct > city_p25:
            return pc4_direct, pc4_direct
        low = city_p25 if city_p25 != 0 else country_p25
        high = city_p75 if city_p75 != 0 else country_p75
        return low, high
    if level == "City level":
        low = city_p25 if city_p25 != 0 else country_p25
        high = city_p75 if city_p75 != 0 else country_p75
        return low, high
    return country_p25, country_p75  # Country level


FUEL_COLS_OWN = {"petrol": "own_petrol", "diesel": "own_diesel", "hybrid": "own_hybrid", "electric": "own_electric"}
FUEL_COLS_SHARED = {"petrol": "shared_petrol", "diesel": None, "hybrid": None, "electric": "shared_electric"}


def fuel_mix(ea: pd.DataFrame, fuel_cols: dict, level: str, pc4: Optional[int], city: Optional[str],
             benchmark_postcodes: list[int]) -> dict:
    """Replicates the L35:O35 / L42:O42 own/shared fuel-mix selector."""
    out = {}
    pc4_rows = ea[ea.PC4 == pc4]
    city_rows = ea[ea.City == city]
    bench_rows = ea[ea.PC4.isin(benchmark_postcodes)]
    for fuel, col in fuel_cols.items():
        if col is None:
            out[fuel] = 0.0
            continue
        country_avg = float(ea[col].mean())
        city_avg = float(city_rows[col].mean()) if len(city_rows) else 0.0
        pc4_avg = float(pc4_rows[col].mean()) if len(pc4_rows) else 0.0
        bench_avg = float(bench_rows[col].mean()) if len(bench_rows) else 0.0
        pc4_has_data = len(pc4_rows) > 0 and not math.isnan(pc4_avg)

        if level == "Benchmark":
            out[fuel] = bench_avg
        elif not pc4_has_data:
            out[fuel] = country_avg  # the "city" branch is unreachable here (see KNOWN_QUIRKS)
        elif level == "PC4 level":
            out[fuel] = pc4_avg
        elif level == "City level":
            out[fuel] = city_avg
        else:
            out[fuel] = country_avg
    return out


def city_diesel_bus_share(city_diesel_share: pd.DataFrame, city: Optional[str]) -> float:
    row = city_diesel_share[city_diesel_share.City == city]
    return float(row.diesel_share.iloc[0]) if len(row) else 0.0


# --------------------------------------------------------------------------
# Section 2/3: house-mix categories -> household size, parking ratio
# --------------------------------------------------------------------------

@dataclass
class Category:
    label: str
    social_housing: bool
    lower: Optional[float]
    upper: Optional[float]
    A: Optional[float]
    B: Optional[float]
    C: Optional[float]
    share: float = 0.0  # user input: share of the development's houses in this category

    @property
    def in_use(self) -> bool:
        return self.social_housing or (self.lower is not None or self.upper is not None)

    @property
    def avg_gfa(self) -> Optional[float]:
        vals = [v for v in (self.lower, self.upper) if v is not None]
        return sum(vals) / len(vals) if vals else None

    def household_size(self, country: dict) -> Optional[float]:
        if not self.in_use:
            return None
        if self.social_housing:
            return country["hh_size_social_medium_rent"]
        gfa = self.avg_gfa
        if gfa is None:
            return None
        if gfa <= 30:
            return country["hh_size_free_up_to_30m2"]
        if gfa <= 60:
            return country["hh_size_free_30_to_60m2"]
        return country["hh_size_free_above_60m2"]

    def parking_ratio(self, parking_category: str) -> Optional[float]:
        return {"A": self.A, "B": self.B, "C": self.C}.get(parking_category)


def categories_from_constants(constants: dict) -> list[Category]:
    cats = []
    for c in constants["city_parking_policy_default"]["categories"]:
        cats.append(Category(c["label"], c["social_housing"], c["lower"], c["upper"], c["A"], c["B"], c["C"]))
    for cat, share in zip(cats, constants["default_house_mix_shares"]):
        cat.share = share
    return cats


def weighted_household_size(categories: list[Category], country: dict) -> float:
    total = 0.0
    for c in categories:
        hh = c.household_size(country)
        if hh is not None:
            total += c.share * hh
    return total


def share_single_person_households(categories: list[Category], country: dict) -> float:
    """SUMIFS($G$29:$G$37,$F$29:$F$37,1): share of houses in categories whose imputed
    household size equals exactly 1 (used as a proxy for single-person / studio homes)."""
    total = 0.0
    for c in categories:
        hh = c.household_size(country)
        if hh is not None and hh == 1:
            total += c.share
    return total


def social_housing_share(categories: list[Category]) -> float:
    return sum(c.share for c in categories if c.social_housing)


def private_parking_spots_per_house(categories: list[Category], parking_category: str) -> float:
    total = 0.0
    for c in categories:
        ratio = c.parking_ratio(parking_category)
        if ratio is not None:
            total += c.share * ratio
    return total


# --------------------------------------------------------------------------
# Section 6: beta-regression active-user prediction interval
# --------------------------------------------------------------------------

@dataclass
class ActiveUserInputs:
    perc_dwellings_owned: float
    rental_public_housing_ratio: float
    perc_high_inc_hh: float
    cars_per_parking_spots: float
    perc_public_parking: float
    perc_paid_public_parking: float
    perc_pop_25to45yr: float  # see KNOWN_QUIRKS: actually wired to the 45-65yr column upstream
    perc_private_hh_1p: float
    has_pt_in_1km: bool
    rec_avg_cars_per_hh: float
    address_density: float


def predict_active_user_share(reg: dict, x: ActiveUserInputs) -> dict:
    terms = reg["terms"]
    values = {
        "Intercept": 1.0,
        "perc_dwellings_owned": x.perc_dwellings_owned,
        "rental_public_housing_ratio": x.rental_public_housing_ratio,
        "perc_high_inc_hh": x.perc_high_inc_hh,
        "cars_per_parking_spots": x.cars_per_parking_spots,
        "perc_public_parking": x.perc_public_parking,
        "perc_paid_public_parking": x.perc_paid_public_parking,
        "perc_pop_25to45yr": x.perc_pop_25to45yr,
        "perc_private_hh_1p": x.perc_private_hh_1p,
        "Has_PT_in_1km": 1.0 if x.has_pt_in_1km else 0.0,
        "rec_avg_cars_per_hh": x.rec_avg_cars_per_hh,
        "address_density": x.address_density,
    }
    eta = sum(terms[t]["coef"] * v for t, v in values.items())
    se_eta = math.sqrt(sum((v ** 2) * (terms[t]["se"] ** 2) for t, v in values.items()))

    mu = 1.0 / (1.0 + math.exp(-eta))
    se_mu = mu * (1 - mu) * se_eta
    phi = reg["phi"]
    beta_obs_sd = math.sqrt(mu * (1 - mu) / (phi + 1))
    total_sd = math.sqrt(se_mu ** 2 + beta_obs_sd ** 2)

    # NB: the source sheet's prediction-interval cells (B32/B33) multiply by
    # Z * confidence_level (B7*B6), not by the separate "error multiplier" (B8)
    # input that sits right next to it -- B8 is effectively unused. Replicated
    # as built rather than using the (apparently intended) error_multiplier.
    z = Z_95
    confidence_level = reg.get("confidence_level", 0.95)
    lower = max(0.0, mu - z * confidence_level * total_sd)
    upper = min(1.0, mu + z * confidence_level * total_sd)
    return {"eta": eta, "mu": mu, "se_eta": se_eta, "total_sd": total_sd, "lower": lower, "upper": upper}


# --------------------------------------------------------------------------
# Top-level project inputs & the full calculation pipeline
# --------------------------------------------------------------------------

@dataclass
class ProjectInputs:
    project_name: str
    pc4: int
    city: str
    num_houses: float
    avg_household_size: float
    avg_cars_per_household: float
    pct_buy: float
    parking_category: str  # "A" / "B" / "C"
    shared_car_usage_level: str  # "PC4 level" / "City level" / "Country level" / "Benchmark"
    share_public_parking: float
    share_paid_public_parking: float
    private_parking_spots_per_house: float
    share_visitor_parking: float
    pct_25_45: float
    pct_high_income: float
    address_density: float
    has_pt_in_1km: bool
    categories: list[Category]


@dataclass
class Results:
    inputs: ProjectInputs
    num_parking_spots: float
    num_private_spots: float
    num_public_spots: float
    num_visitor_spots: float
    num_cars: float
    residents: float
    relevant_residents: float
    active_share_min: float
    active_share_max: float
    active_users_min: float
    active_users_max: float
    untapped_demand_min_hours: float
    untapped_demand_max_hours: float
    additional_shared_cars_min: float
    additional_shared_cars_max: float
    shared_cars_per_1000_min: float
    shared_cars_per_1000_max: float
    shared_cars_per_100hh_min: float
    shared_cars_per_100hh_max: float
    avr_min: float
    avr_max: float
    cars_saved_gross_min: float
    cars_saved_gross_max: float
    cars_saved_net_min: float
    cars_saved_net_max: float
    parking_spots_after_min: float
    parking_spots_after_max: float
    discount_min: float
    discount_max: float
    parking_space_needed_min_m2: float
    parking_space_needed_max_m2: float
    emissions: dict  # pollutant -> {"absolute_min","absolute_max","impact_a_min","impact_a_max","impact_b_min","impact_b_max","total_min","total_max"}
    co2_cost_eur_min: float
    co2_cost_eur_max: float
    trees_min: float
    trees_max: float


POLLUTANTS = ["CO", "VOC", "NOx", "PM10", "NH3", "N2O", "EC", "CO2"]


def run_model(ref: ReferenceData, inp: ProjectInputs) -> Results:
    country = ref.country
    ea = ref.existing_areas
    bench_pc = country["benchmark_postcodes"]

    # ---- Section 3: parking spots -------------------------------------
    num_parking_spots = inp.private_parking_spots_per_house * inp.num_houses * (1 + inp.share_visitor_parking)
    num_private_spots = inp.private_parking_spots_per_house * inp.num_houses * (1 - inp.share_paid_public_parking)
    num_public_spots = inp.private_parking_spots_per_house * inp.num_houses - num_private_spots
    num_visitor_spots = num_parking_spots - num_public_spots - num_private_spots
    num_cars = inp.num_houses * inp.avg_cars_per_household

    # ---- Section 6: carsharing potential -------------------------------
    residents = inp.num_houses * inp.avg_household_size
    relevant_residents = residents * country["share_18plus_with_license"]

    rental_public_housing_ratio = social_housing_share(inp.categories)
    cars_per_parking_spots = (num_cars / num_parking_spots) if num_parking_spots else 100.0

    reg_inputs = ActiveUserInputs(
        perc_dwellings_owned=inp.pct_buy,
        rental_public_housing_ratio=rental_public_housing_ratio,
        perc_high_inc_hh=inp.pct_high_income,
        cars_per_parking_spots=cars_per_parking_spots,
        perc_public_parking=inp.share_public_parking,
        perc_paid_public_parking=(0.0 if inp.share_public_parking == 0 else inp.share_paid_public_parking),
        perc_pop_25to45yr=inp.pct_25_45,
        perc_private_hh_1p=share_single_person_households(inp.categories, country),
        has_pt_in_1km=inp.has_pt_in_1km,
        rec_avg_cars_per_hh=(inp.num_houses / num_cars) if num_cars else 0.0,
        address_density=inp.address_density,
    )
    pred = predict_active_user_share(ref.regression, reg_inputs)
    active_share_min, active_share_max = pred["lower"], pred["upper"]

    active_users_min = relevant_residents * active_share_min
    active_users_max = relevant_residents * active_share_max

    hrs_person_low, hrs_person_high = carsharing_metric_range(
        ea, "hours_per_person_month", inp.shared_car_usage_level, inp.pc4, inp.city, bench_pc)
    untapped_demand_min_hours = active_users_min * hrs_person_low
    untapped_demand_max_hours = active_users_max * hrs_person_high

    hrs_car_low, hrs_car_high = carsharing_metric_range(
        ea, "hours_per_car_month", inp.shared_car_usage_level, inp.pc4, inp.city, bench_pc)
    additional_shared_cars_min = untapped_demand_min_hours / hrs_car_high if hrs_car_high else 0.0
    additional_shared_cars_max = untapped_demand_max_hours / hrs_car_low if hrs_car_low else 0.0

    shared_cars_per_1000_min = additional_shared_cars_min / relevant_residents * 1000 if relevant_residents else 0.0
    shared_cars_per_1000_max = additional_shared_cars_max / relevant_residents * 1000 if relevant_residents else 0.0
    shared_cars_per_100hh_min = additional_shared_cars_min / (inp.num_houses / 100) if inp.num_houses else 0.0
    shared_cars_per_100hh_max = additional_shared_cars_max / (inp.num_houses / 100) if inp.num_houses else 0.0

    # ---- Section 7: parking impact -------------------------------------
    avr_min, avr_max = carsharing_metric_range(ea, "AVR", inp.shared_car_usage_level, inp.pc4, inp.city, bench_pc)

    cars_saved_gross_min = avr_min * additional_shared_cars_min
    cars_saved_gross_max = avr_max * additional_shared_cars_max
    cars_saved_net_min = cars_saved_gross_min - additional_shared_cars_min
    cars_saved_net_max = cars_saved_gross_max - additional_shared_cars_max

    parking_spots_before = num_parking_spots
    parking_spots_after_min = parking_spots_before - cars_saved_net_max
    parking_spots_after_max = parking_spots_before - cars_saved_net_min
    discount_min = (parking_spots_after_max / parking_spots_before - 1) if parking_spots_before else 0.0
    discount_max = (parking_spots_after_min / parking_spots_before - 1) if parking_spots_before else 0.0

    spot_size = country["avg_parking_space_size_m2"]
    parking_space_needed_min_m2 = parking_spots_after_min * spot_size
    parking_space_needed_max_m2 = parking_spots_after_max * spot_size

    # ---- Section 8: emissions --------------------------------------------
    ef = ref.emission_factors
    dist_car_low, dist_car_high = carsharing_metric_range(ea, "dist_per_car_month", inp.shared_car_usage_level,
                                                            inp.pc4, inp.city, bench_pc)
    avg_dist_per_car_month = (dist_car_low + dist_car_high) / 2

    own_mix = fuel_mix(ea, FUEL_COLS_OWN, inp.shared_car_usage_level, inp.pc4, inp.city, bench_pc)
    shared_mix = fuel_mix(ea, FUEL_COLS_SHARED, inp.shared_car_usage_level, inp.pc4, inp.city, bench_pc)

    e6 = additional_shared_cars_min * avg_dist_per_car_month   # total km/month, min shared-car fleet
    e12 = additional_shared_cars_max * avg_dist_per_car_month  # total km/month, max shared-car fleet

    avg_train_share = country["share_train_travel"]
    avg_btm_share = 1 - avg_train_share
    avg_bus_share_of_btm = float(ea["share_bus_btm"].mean())
    diesel_share_city = city_diesel_bus_share(ref.city_diesel_share, inp.city)
    avg_passengers_per_bus = country["avg_passengers_per_bus"]

    # monthly distance no longer done by the (now-shared) car -> shifted to PT
    monthly_dist_not_carsharing = country["avg_yearly_travel_distance_km"] / country["avg_yearly_travel_hours"] \
        * country["avg_yearly_travel_hours"]  # placeholder, replaced below
    # replicate: H39 = G39/F39*E39 with E39=avg yearly distance, F39=avg yearly hours,
    # G39 = avg "non-carsharing time" (existing_areas EX column average)
    avg_non_carsharing_time = float(ea["non_carsharing_time"].mean())
    monthly_dist_not_carsharing = (avg_non_carsharing_time / country["avg_yearly_travel_hours"]) * \
        country["avg_yearly_travel_distance_km"]

    emissions = {}
    co2_cost_min = co2_cost_max = trees_min = trees_max = 0.0

    for p in POLLUTANTS:
        # -- absolute emission volume of the shared-car fleet (fuel-mix weighted) --
        shared_fleet_factor = sum(shared_mix[f] * ef[f][p] for f in ["petrol", "diesel", "hybrid", "electric"])
        abs_min_g_month = shared_fleet_factor * e6
        abs_max_g_month = shared_fleet_factor * e12
        abs_min_kg_year = abs_min_g_month * 12 / 1000
        abs_max_kg_year = abs_max_g_month * 12 / 1000

        # -- Impact A: driving shared car instead of own car --
        own_factor = sum(own_mix[f] * ef[f][p] for f in ["petrol", "diesel", "hybrid", "electric"])
        delta_per_km = shared_fleet_factor - own_factor
        impact_a_min_kg = (e6 * delta_per_km) * 12 / 1000
        impact_a_max_kg = (e12 * delta_per_km) * 12 / 1000

        # -- Impact B: more public transport instead of own car --
        bus_factor = ef["bus_per_pkm"][p] / avg_passengers_per_bus
        if p == "NOx":
            train_factor = country["diesel_train_emission_per_km"]["NOx"]
        else:
            train_factor = country["diesel_train_emission_per_km"].get(p, 0.0)
        term1 = own_factor * monthly_dist_not_carsharing / 1000
        term2 = avg_btm_share * avg_bus_share_of_btm * bus_factor + avg_train_share * diesel_share_city * train_factor
        # NB: both the min and max scenarios use the *average* of AVR-min/AVR-max here
        # (Model_calc_new_dev_emission!$D$34), not the min/max AVR used elsewhere.
        # Replicated as built.
        avr_avg = (avr_min + avr_max) / 2
        impact_b_min_kg = -((term1 - term2) * avr_avg * additional_shared_cars_min)
        impact_b_max_kg = -((term1 - avg_btm_share * avg_bus_share_of_btm * bus_factor) * avr_avg * additional_shared_cars_max)

        total_min = impact_a_min_kg + impact_b_min_kg
        total_max = impact_a_max_kg + impact_b_max_kg

        emissions[p] = {
            "absolute_min": abs_min_kg_year, "absolute_max": abs_max_kg_year,
            "impact_a_min": impact_a_min_kg, "impact_a_max": impact_a_max_kg,
            "impact_b_min": impact_b_min_kg, "impact_b_max": impact_b_max_kg,
            "total_min": total_min, "total_max": total_max,
        }
        if p == "CO2":
            price = country["eu_ets_co2_price_eur_per_tonne"]
            co2_cost_min = total_min * price / 1000
            co2_cost_max = total_max * price / 1000
            tree_abs = country["tree_co2_absorption_kg_per_year"]
            trees_min = total_min / tree_abs if tree_abs else 0.0
            trees_max = total_max / tree_abs if tree_abs else 0.0

    return Results(
        inputs=inp,
        num_parking_spots=num_parking_spots, num_private_spots=num_private_spots,
        num_public_spots=num_public_spots, num_visitor_spots=num_visitor_spots, num_cars=num_cars,
        residents=residents, relevant_residents=relevant_residents,
        active_share_min=active_share_min, active_share_max=active_share_max,
        active_users_min=active_users_min, active_users_max=active_users_max,
        untapped_demand_min_hours=untapped_demand_min_hours, untapped_demand_max_hours=untapped_demand_max_hours,
        additional_shared_cars_min=additional_shared_cars_min, additional_shared_cars_max=additional_shared_cars_max,
        shared_cars_per_1000_min=shared_cars_per_1000_min, shared_cars_per_1000_max=shared_cars_per_1000_max,
        shared_cars_per_100hh_min=shared_cars_per_100hh_min, shared_cars_per_100hh_max=shared_cars_per_100hh_max,
        avr_min=avr_min, avr_max=avr_max,
        cars_saved_gross_min=cars_saved_gross_min, cars_saved_gross_max=cars_saved_gross_max,
        cars_saved_net_min=cars_saved_net_min, cars_saved_net_max=cars_saved_net_max,
        parking_spots_after_min=parking_spots_after_min, parking_spots_after_max=parking_spots_after_max,
        discount_min=discount_min, discount_max=discount_max,
        parking_space_needed_min_m2=parking_space_needed_min_m2, parking_space_needed_max_m2=parking_space_needed_max_m2,
        emissions=emissions,
        co2_cost_eur_min=co2_cost_min, co2_cost_eur_max=co2_cost_max,
        trees_min=trees_min, trees_max=trees_max,
    )


# --------------------------------------------------------------------------
# "Scenario analysis" / "Carsharing statistics" comparison chart -- ports
# the 4-scenario table at Carsharing statistics!R6:AJ9, used by the
# workbook's "Comparing scenarios" chart. This is a *separate*, simplified
# conversion path from the one in run_model() above (a single "car per
# active user" factor instead of the two-step hours-per-person /
# hours-per-car conversion) -- that's how the source workbook itself does
# it for this chart, so it's replicated as its own function rather than
# reusing run_model()'s numbers.
# --------------------------------------------------------------------------

@dataclass
class ScenarioResult:
    name: str
    description: str
    shared_cars_min: float
    shared_cars_max: float
    shared_cars_per_100hh_min: float
    shared_cars_per_100hh_max: float
    discount_min: float
    discount_max: float


def _percentile_q(series: pd.Series, q: float) -> float:
    s = series.dropna()
    return float(np.percentile(s.to_numpy(), q * 100)) if len(s) else 0.0


def scenario_comparison(ref: ReferenceData, inp: ProjectInputs, results: Results) -> list[ScenarioResult]:
    ea = ref.existing_areas
    positive_capu = ea[ea["car_per_active_user"] > 0]
    positive_avr = ea[ea["AVR"] > 0]

    pc4_capu_rows = ea.loc[ea.PC4 == inp.pc4, "car_per_active_user"].dropna()
    capu_baseline = float(pc4_capu_rows.sum()) if len(pc4_capu_rows) else 0.0
    capu_city_75 = _percentile_q(positive_capu.loc[positive_capu.City == inp.city, "car_per_active_user"], 0.75)
    capu_country_95 = _percentile_q(positive_capu["car_per_active_user"], 0.95)

    avr_city_75 = _percentile_q(positive_avr.loc[positive_avr.City == inp.city, "AVR"], 0.75)
    avr_country_95 = _percentile_q(positive_avr["AVR"], 0.95)

    au_min, au_max = results.active_users_min, results.active_users_max
    parking_before = results.num_parking_spots

    def _row(name: str, desc: str, cars_min: float, cars_max: float, avr_min_: float, avr_max_: float) -> ScenarioResult:
        gross_min = cars_min * avr_min_
        gross_max = cars_max * avr_max_
        net_min = gross_min - cars_min
        net_max = gross_max - cars_max
        after_min = parking_before - net_max
        after_max = parking_before - net_min
        discount_min = (after_max / parking_before - 1) if parking_before else 0.0
        discount_max = (after_min / parking_before - 1) if parking_before else 0.0
        per100_min = cars_min / (inp.num_houses / 100) if inp.num_houses else 0.0
        per100_max = cars_max / (inp.num_houses / 100) if inp.num_houses else 0.0
        return ScenarioResult(name, desc, cars_min, cars_max, per100_min, per100_max, discount_min, discount_max)

    scenarios = [
        _row("Baseline", "This project's own PC4-level assumptions (same as the Results page).",
             au_min * capu_baseline, au_max * capu_baseline, results.avr_min, results.avr_max),
        _row("City 75th perc.", f"If {inp.city} reached the 75th-percentile carsharing usage rate "
             "seen across its own postcode areas.",
             au_min * capu_city_75, au_max * capu_city_75, avr_city_75, avr_city_75),
        _row("Country 95th perc.", "If this project reached the 95th-percentile carsharing usage rate "
             "seen across the Netherlands.",
             au_min * capu_country_95, au_max * capu_country_95, avr_country_95, avr_country_95),
        _row("Fixed 1:20 / AVR 4", "A simple policy rule of thumb: 1 shared car per 20 households, "
             "each replacing 4 private cars.",
             inp.num_houses / 20, inp.num_houses / 20, 4.0, 4.0),
    ]
    return scenarios
