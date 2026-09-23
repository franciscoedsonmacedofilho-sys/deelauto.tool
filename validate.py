"""Validate engine.py against cached values from the source Excel workbook
for the 'Rotterdam - Merwedevierhavens M4H' example project."""
from engine import (load_reference_data, run_model, ProjectInputs, categories_from_constants)

ref = load_reference_data()
categories = categories_from_constants(ref.constants)  # default shares match the example exactly

inp = ProjectInputs(
    project_name="Rotterdam - Merwedevierhavens M4H",
    pc4=3029,
    city="Rotterdam",
    num_houses=3750,
    avg_household_size=1.84,
    avg_cars_per_household=0.5,
    pct_buy=0.5,
    parking_category="A",
    shared_car_usage_level="PC4 level",
    share_public_parking=0.578556263269639,
    share_paid_public_parking=0.435217177092804,
    private_parking_spots_per_house=0.45,
    share_visitor_parking=0.2,
    pct_25_45=0.170710571923743,
    pct_high_income=0.061,
    address_density=3481,
    has_pt_in_1km=True,
    categories=categories,
)

r = run_model(ref, inp)

expected = {
    "num_parking_spots": 2025,
    "residents": 6900,
    "relevant_residents": 4140,
    "active_share_min": 0.0207973734786793,
    "active_share_max": 0.0474707990988022,
    "active_users_min": 86.1011262017322,
    "active_users_max": 196.529108269041,
    "untapped_demand_min_hours": 651.978067605011,
    "untapped_demand_max_hours": 1488.16483465239,
    "additional_shared_cars_min": 3.81506235037293,
    "additional_shared_cars_max": 8.70802549031582,
    "avr_min": 4.08690320218076,
    "avr_max": 6.89881534701943,
    "cars_saved_gross_min": 15.5917905362584,
    "cars_saved_gross_max": 60.0750598948271,
    "cars_saved_net_min": 11.7767281858855,
    "cars_saved_net_max": 51.3670344045113,
    "parking_spots_after_min": 1973.63296559549,
    "parking_spots_after_max": 2013.22327181411,
    "discount_min": -0.00581566823994351,
    "discount_max": -0.0253664367429686,
    "parking_space_needed_min_m2": 29604.4944839323,
    "parking_space_needed_max_m2": 30198.3490772117,
}

got = {
    "num_parking_spots": r.num_parking_spots,
    "residents": r.residents,
    "relevant_residents": r.relevant_residents,
    "active_share_min": r.active_share_min,
    "active_share_max": r.active_share_max,
    "active_users_min": r.active_users_min,
    "active_users_max": r.active_users_max,
    "untapped_demand_min_hours": r.untapped_demand_min_hours,
    "untapped_demand_max_hours": r.untapped_demand_max_hours,
    "additional_shared_cars_min": r.additional_shared_cars_min,
    "additional_shared_cars_max": r.additional_shared_cars_max,
    "avr_min": r.avr_min,
    "avr_max": r.avr_max,
    "cars_saved_gross_min": r.cars_saved_gross_min,
    "cars_saved_gross_max": r.cars_saved_gross_max,
    "cars_saved_net_min": r.cars_saved_net_min,
    "cars_saved_net_max": r.cars_saved_net_max,
    "parking_spots_after_min": r.parking_spots_after_min,
    "parking_spots_after_max": r.parking_spots_after_max,
    "discount_min": r.discount_min,
    "discount_max": r.discount_max,
    "parking_space_needed_min_m2": r.parking_space_needed_min_m2,
    "parking_space_needed_max_m2": r.parking_space_needed_max_m2,
}

print(f"{'metric':35s} {'expected':>18s} {'got':>18s} {'match':>7s}")
all_ok = True
for k, exp_v in expected.items():
    got_v = got[k]
    ok = abs(exp_v - got_v) < max(1e-6, abs(exp_v) * 1e-3)
    all_ok &= ok
    print(f"{k:35s} {exp_v:18.6f} {got_v:18.6f} {'OK' if ok else 'MISMATCH'}")

print()
print("Emissions (CO row) expected: min A=-77.66 B=-179.18 total=-256.84 | max A=-177.26 B=-408.98 total=-586.25")
co = r.emissions["CO"]
print(f"got: impact_a_min={co['impact_a_min']:.4f} impact_b_min={co['impact_b_min']:.4f} total_min={co['total_min']:.4f}")
print(f"got: impact_a_max={co['impact_a_max']:.4f} impact_b_max={co['impact_b_max']:.4f} total_max={co['total_max']:.4f}")
print(f"got: absolute_min(S20)={r.emissions['CO']['absolute_min']:.4f} expected 11.4365114033578")
print(f"got: absolute_max(T20)={r.emissions['CO']['absolute_max']:.4f} expected 26.1042739736593")

print()
print("ALL OK" if all_ok else "SOME MISMATCHES ABOVE")
