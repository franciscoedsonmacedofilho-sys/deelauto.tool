"""
Shared Mobility Parking & Impact Tool
--------------------------------------
Helps policymakers estimate how much parking space a new housing
development needs to set aside for shared ("carsharing") vehicles, and the
resulting impact on required parking and on emissions if carsharing is
implemented as planned.

This app is a Streamlit port of a policy-support Excel model. All
calculations live in engine.py and are unit-tested against cached values
from the source workbook (see validate.py) -- see the "Methodology" tab
for details and known quirks inherited from the source file.

Layout: every input lives on the left ribbon (sidebar); the main screen is
just two views -- "Results" (one page you scroll through: carsharing
potential, parking impact, emissions impact) and "Methodology & sources".
A Word report for the currently-selected location can be exported from the
top of the Results view.
"""
from __future__ import annotations

import copy
from dataclasses import replace
from pathlib import Path

import pandas as pd
import streamlit as st

from engine import (
    ReferenceData, ProjectInputs, Category, POLLUTANTS, KNOWN_QUIRKS,
    load_reference_data, pc4_level_default, has_pt_in_1km, categories_from_constants,
    weighted_household_size, share_single_person_households, social_housing_share,
    private_parking_spots_per_house, run_model, scenario_comparison,
)
import brand
from i18n import T, KNOWN_QUIRKS_NL
from report import build_report_docx

st.set_page_config(page_title="Shared Mobility Parking & Impact Tool", layout="wide", page_icon="🚗")
st.markdown(brand.CSS, unsafe_allow_html=True)

if "lang" not in st.session_state:
    st.session_state.lang = "en"
lang_choice = st.sidebar.radio(T(st.session_state.lang, "lang_label"), ["English", "Nederlands"],
                                horizontal=True,
                                index=0 if st.session_state.lang == "en" else 1, key="lang_radio")
st.session_state.lang = "en" if lang_choice == "English" else "nl"
lang = st.session_state.lang


@st.cache_resource
def get_reference_data() -> ReferenceData:
    return load_reference_data()


ref = get_reference_data()
pc4_info = ref.pc4_info
projects = ref.projects


# =======================================================================
# SIDEBAR -- every input lives here
# =======================================================================
st.sidebar.markdown(brand.sidebar_title(T(lang, "sidebar_title")), unsafe_allow_html=True)

CUSTOM_LABEL = T(lang, "custom_project")

# Projects the user has saved this session (name + the handful of fields the
# "Load an example development" list itself prefills) sit alongside the
# built-in examples, so saving and reloading a custom project reuses the
# exact same mechanism as loading one of the shipped examples below.
if "saved_projects" not in st.session_state:
    st.session_state.saved_projects = []
all_projects = (pd.concat([projects, pd.DataFrame(st.session_state.saved_projects)], ignore_index=True)
                if st.session_state.saved_projects else projects)

# A freshly-saved project is selected on the *next* rerun (see the Save
# button below) -- setting the selectbox's own session-state key directly
# from the button handler isn't allowed once that widget has already been
# instantiated this run, so we stage the name here, before it's created.
if "_pending_project_select" in st.session_state:
    st.session_state["project_select"] = st.session_state.pop("_pending_project_select")

project_names = [CUSTOM_LABEL] + all_projects["Name"].tolist()
st.sidebar.markdown(f'<div class="rebel-location-tag">{T(lang, "start_here")}</div>'
                     '<div class="rebel-location-marker"></div>',
                     unsafe_allow_html=True)
selected_name = st.sidebar.selectbox(T(lang, "load_example"), project_names,
                                      key="project_select")

if "loaded_project" not in st.session_state:
    st.session_state.loaded_project = None
if st.session_state.loaded_project != selected_name:
    st.session_state.loaded_project = selected_name
    st.session_state.nonce = st.session_state.get("nonce", 0) + 1
nonce = st.session_state.nonce

if selected_name != CUSTOM_LABEL:
    prow = all_projects[all_projects.Name == selected_name].iloc[0]
    default_pc4 = int(prow.PC4) if pd.notna(prow.PC4) else 3029
    default_city = str(pc4_info.loc[pc4_info.PC4 == default_pc4, "City"].iloc[0]) if (pc4_info.PC4 == default_pc4).any() else "Rotterdam"
    default_houses = float(prow.num_houses) if pd.notna(prow.num_houses) else 1000.0
    default_buy = float(prow.perc_buy) if pd.notna(prow.perc_buy) else 0.5
else:
    prow = None
    default_pc4 = 3029
    default_city = "Rotterdam"
    default_houses = 1000.0
    default_buy = 0.5

cities = sorted(pc4_info["City"].dropna().unique().tolist())

# Save the current location + development characteristics as a named project
# -- it's added to the "Load an example development" list above, exactly
# like one of the built-in examples, so picking it later reloads these same
# fields the same way. Placed right under "Start here" so it's easy to find;
# it reads the location/houses/buy-share widgets' own live values (already
# in session state from the previous run, under this same nonce) since those
# widgets aren't (re)created until the sections below.
with st.sidebar.container():
    save_name = st.text_input(T(lang, "save_as_label"), key="save_project_name",
                               placeholder=T(lang, "save_as_placeholder"))
    if st.button(T(lang, "save_button"), use_container_width=True):
        clean_name = save_name.strip()
        if not clean_name:
            st.warning(T(lang, "save_warn_noname"))
        else:
            current_pc4 = st.session_state.get(f"pc4_{nonce}", default_pc4)
            current_houses = st.session_state.get(f"houses_{nonce}", default_houses)
            current_buy = st.session_state.get(f"buy_{nonce}", default_buy)
            existing = [p for p in st.session_state.saved_projects if p["Name"] == clean_name]
            record = {"Name": clean_name, "PC4": current_pc4, "num_houses": current_houses,
                      "perc_buy": current_buy}
            if existing:
                existing[0].update(record)
            else:
                st.session_state.saved_projects.append(record)
            st.session_state["_pending_project_select"] = clean_name
            st.rerun()


def default_for(col, level_choice):
    return pc4_level_default(pc4_info, col, level_choice, pc4, city)


# These selectboxes' *values* ("PC4 level" / "City level" / ...) are matched
# by exact string in engine.py, so the options themselves stay in English --
# only the on-screen label is translated, via format_func.
_LEVEL_KEY = {"PC4 level": "opt_pc4_level", "City level": "opt_city_level",
              "Country level": "opt_country_level", "Benchmark": "opt_benchmark"}
level_fmt = lambda v: T(lang, _LEVEL_KEY[v])

with st.sidebar.expander(T(lang, "sec0_title"), expanded=True):
    city = st.selectbox(T(lang, "city_label"), cities,
                         index=cities.index(default_city) if default_city in cities else 0,
                         key=f"city_{nonce}")
    pc4_options = sorted(pc4_info.loc[pc4_info.City == city, "PC4"].dropna().unique().astype(int).tolist())
    pc4_default_idx = pc4_options.index(default_pc4) if default_pc4 in pc4_options else 0
    pc4 = st.selectbox(T(lang, "pc4_label"), pc4_options, index=pc4_default_idx, key=f"pc4_{nonce}")
    shared_car_usage_level = st.selectbox(
        T(lang, "usage_level_label"),
        ["PC4 level", "City level", "Country level", "Benchmark"],
        index=0, key=f"level_{nonce}", format_func=level_fmt,
        help=T(lang, "usage_level_help"))
    parking_category = st.radio(T(lang, "parking_cat_label"),
                                 ["A", "B", "C"], horizontal=True, key=f"parkcat_{nonce}")

with st.sidebar.expander(T(lang, "sec1_title"), expanded=True):
    num_houses = st.number_input(T(lang, "num_houses_label"), min_value=1.0, value=float(default_houses),
                                  step=10.0, key=f"houses_{nonce}")
    default_hh_size_level = st.selectbox(T(lang, "hhsize_basis_label"),
                                          ["PC4 level", "City level", "Country level"],
                                          key=f"hhsize_level_{nonce}", format_func=level_fmt)
    hh_size_area_default = default_for("hh_size", default_hh_size_level)
    avg_household_size_input = st.number_input(
        T(lang, "hhsize_label"), min_value=0.1, value=round(hh_size_area_default, 3), step=0.05,
        key=f"hhsize_val_{nonce}")
    pct_buy = st.number_input(T(lang, "pct_buy_label"), min_value=0.0, max_value=1.0,
                               value=float(default_buy), step=0.05, key=f"buy_{nonce}")
    avg_cars_per_hh_default = default_for("cars_per_hh", "PC4 level")
    avg_cars_per_household = st.number_input(T(lang, "cars_per_hh_label"),
                                               min_value=0.0, value=round(avg_cars_per_hh_default, 3), step=0.05,
                                               key=f"carshh_{nonce}")

# The remaining sections have a data dependency that runs opposite to the
# order we want them displayed in: "City-level parking policy" (a power-user
# section we want pushed to the bottom) computes default_cats, which "Unit
# mix" needs, which in turn "Parking characteristics" needs. We reserve the
# visual slots up front in display order, then fill them below in dependency
# order -- each block still renders in its reserved slot regardless of when
# its content is written, so the two orders can differ.
slot_unit_mix = st.sidebar.container()
slot_parking_char = st.sidebar.container()
slot_sociodemo = st.sidebar.container()
slot_city_policy = st.sidebar.container()

COL_CATEGORY = T(lang, "col_category")
COL_GFA_LOWER = T(lang, "col_gfa_lower")
COL_GFA_UPPER = T(lang, "col_gfa_upper")
COL_RATIO_A = T(lang, "col_ratio_a")
COL_RATIO_B = T(lang, "col_ratio_b")
COL_RATIO_C = T(lang, "col_ratio_c")
COL_SOCIAL = T(lang, "col_social_housing")
COL_SHARE = T(lang, "col_share_of_houses")
COL_PARKING_RATIO = T(lang, "col_parking_ratio", cat=parking_category)

with slot_city_policy, st.expander(T(lang, "sec5_title"), expanded=False):
    st.markdown(brand.advanced_header(T(lang, "advanced_inputs_title"), T(lang, "sec5_caption")),
                unsafe_allow_html=True)
    base_cats = categories_from_constants(ref.constants)
    policy_rows = []
    for c in base_cats:
        if not c.in_use:
            continue
        policy_rows.append({
            COL_CATEGORY: c.label, COL_GFA_LOWER: c.lower, COL_GFA_UPPER: c.upper,
            COL_RATIO_A: c.A, COL_RATIO_B: c.B, COL_RATIO_C: c.C,
        })
    policy_df = pd.DataFrame(policy_rows)
    policy_edited = st.data_editor(
        policy_df, key=f"citypolicy_{nonce}", hide_index=True, use_container_width=True,
        disabled=[COL_CATEGORY],
        column_config={
            COL_GFA_LOWER: st.column_config.NumberColumn(step=1.0, format="%.0f"),
            COL_GFA_UPPER: st.column_config.NumberColumn(step=1.0, format="%.0f"),
            COL_RATIO_A: st.column_config.NumberColumn(step=0.05, format="%.2f"),
            COL_RATIO_B: st.column_config.NumberColumn(step=0.05, format="%.2f"),
            COL_RATIO_C: st.column_config.NumberColumn(step=0.05, format="%.2f"),
        },
    )
    visitor_share_default = st.number_input(
        T(lang, "visitor_default_label"), min_value=0.0, max_value=1.0,
        value=float(ref.constants["city_parking_policy_default"]["share_visitor_parking_pct_of_private"]),
        step=0.05, key=f"cityvisitor_{nonce}")

    edited_by_label = {row[COL_CATEGORY]: row for row in policy_edited.to_dict("records")}
    default_cats = []
    for c in base_cats:
        if c.label in edited_by_label:
            row = edited_by_label[c.label]
            lower = float(row[COL_GFA_LOWER]) if pd.notna(row[COL_GFA_LOWER]) else None
            upper = float(row[COL_GFA_UPPER]) if pd.notna(row[COL_GFA_UPPER]) else None
            rA = float(row[COL_RATIO_A]) if pd.notna(row[COL_RATIO_A]) else None
            rB = float(row[COL_RATIO_B]) if pd.notna(row[COL_RATIO_B]) else None
            rC = float(row[COL_RATIO_C]) if pd.notna(row[COL_RATIO_C]) else None
            default_cats.append(Category(c.label, c.social_housing, lower, upper, rA, rB, rC))
        else:
            default_cats.append(copy.deepcopy(c))
    for cat, share in zip(default_cats, ref.constants["default_house_mix_shares"]):
        cat.share = share

with slot_unit_mix, st.expander(T(lang, "sec2_title"), expanded=False):
    st.caption(T(lang, "sec2_caption"))
    cat_rows = []
    for c in default_cats:
        cat_rows.append({
            COL_CATEGORY: c.label, COL_SOCIAL: c.social_housing,
            COL_GFA_LOWER: c.lower, COL_GFA_UPPER: c.upper,
            COL_SHARE: c.share,
            COL_PARKING_RATIO: c.parking_ratio(parking_category),
        })
    cat_df = pd.DataFrame(cat_rows)
    edited = st.data_editor(
        cat_df, key=f"catedit_{nonce}", hide_index=True, use_container_width=True,
        disabled=[COL_CATEGORY, COL_SOCIAL, COL_GFA_LOWER, COL_GFA_UPPER, COL_PARKING_RATIO],
        column_config={COL_SHARE: st.column_config.NumberColumn(min_value=0.0, max_value=1.0, step=0.01, format="%.2f")},
    )
    share_sum = edited[COL_SHARE].sum()
    if abs(share_sum - 1.0) > 0.02:
        st.warning(T(lang, "shares_warning", pct=f"{share_sum:.0%}"))

    categories = copy.deepcopy(default_cats)
    for cat, share in zip(categories, edited[COL_SHARE].tolist()):
        cat.share = float(share) if pd.notna(share) else 0.0

    computed_hh_size = weighted_household_size(categories, ref.country)
    hh_size_source = st.radio(T(lang, "hhsize_source_label"),
                               ["Use area default", "Compute from unit mix above"],
                               key=f"hhsize_src_{nonce}",
                               format_func=lambda v: T(lang, "opt_area_default" if v == "Use area default"
                                                        else "opt_compute_mix"))
    avg_household_size = avg_household_size_input if hh_size_source == "Use area default" else computed_hh_size
    st.caption(T(lang, "hhsize_selected_caption", val=avg_household_size))

    single_hh_share = share_single_person_households(categories, ref.country)
    social_share = social_housing_share(categories)
    st.caption(T(lang, "single_social_caption", single=single_hh_share, social=social_share))

with slot_parking_char, st.expander(T(lang, "sec3_title"), expanded=False):
    share_public_default = default_for("perc_public_parking", "PC4 level")
    share_public_parking = st.number_input(T(lang, "share_public_label"), min_value=0.0, max_value=1.0,
                                             value=round(share_public_default, 3), step=0.05, key=f"pubpark_{nonce}")
    share_paid_default = default_for("perc_paid_public_parking", "PC4 level")
    share_paid_public_parking = st.number_input(T(lang, "share_paid_label"), min_value=0.0,
                                                  max_value=1.0, value=round(share_paid_default, 3), step=0.05,
                                                  key=f"paidpark_{nonce}")
    share_visitor_parking = st.number_input(T(lang, "share_visitor_label"), min_value=0.0,
                                              max_value=1.0, value=round(visitor_share_default, 3), step=0.05,
                                              key=f"visitor_{nonce}")

    computed_private_ratio = private_parking_spots_per_house(categories, parking_category)
    st.caption(T(lang, "private_ratio_caption", cat=parking_category, val=computed_private_ratio))
    private_parking_spots_per_house_val = st.number_input(
        T(lang, "private_ratio_label"),
        min_value=0.0, value=round(computed_private_ratio, 3), step=0.01, key=f"privratio_{nonce}")

with slot_sociodemo, st.expander(T(lang, "sec4_title"), expanded=False):
    pct_2545_default = default_for("perc_pop_25to45yr", "PC4 level")
    pct_25_45 = st.number_input(T(lang, "pct2545_label"), min_value=0.0, max_value=1.0,
                                 value=round(pct_2545_default, 3), step=0.01, key=f"pct2545_{nonce}")
    pct_hi_default = default_for("perc_high_inc_hh", "PC4 level") / 100
    pct_high_income = st.number_input(T(lang, "pct_hi_label"), min_value=0.0, max_value=1.0,
                                       value=round(pct_hi_default, 3), step=0.01, key=f"pcthi_{nonce}")
    addr_density_default = default_for("address_density", "PC4 level")
    address_density = st.number_input(T(lang, "addr_density_label"), min_value=0.0,
                                       value=round(addr_density_default, 1), step=10.0, key=f"addrdens_{nonce}")
    pt_default = has_pt_in_1km(pc4_info, "PC4 level", pc4, city)
    has_pt = st.checkbox(T(lang, "has_pt_label"), value=pt_default, key=f"haspt_{nonce}")
    st.caption(T(lang, "single_hh_caption", val=single_hh_share))
    share_single_hh = st.number_input(T(lang, "single_hh_label"), min_value=0.0, max_value=1.0,
                                       value=round(single_hh_share, 3), step=0.01, key=f"singlehh_{nonce}")

with st.sidebar.expander(T(lang, "sec6_title"), expanded=False):
    st.markdown(brand.advanced_header(T(lang, "advanced_inputs_title"), T(lang, "sec6_caption")),
                unsafe_allow_html=True)
    cdef = ref.country
    share_18plus_with_license = st.number_input(
        T(lang, "license_label"), min_value=0.0, max_value=1.0,
        value=float(cdef["share_18plus_with_license"]), step=0.01, key="c_license")
    avg_parking_space_size_m2 = st.number_input(
        T(lang, "spot_size_label"), min_value=1.0,
        value=float(cdef["avg_parking_space_size_m2"]), step=0.5, key="c_spot_m2")
    share_train_travel = st.number_input(
        T(lang, "train_share_label"), min_value=0.0, max_value=1.0,
        value=float(cdef["share_train_travel"]), step=0.01, format="%.4f", key="c_train_share")
    avg_passengers_per_bus = st.number_input(
        T(lang, "bus_pax_label"), min_value=0.1,
        value=float(cdef["avg_passengers_per_bus"]), step=0.5, key="c_bus_pax")
    avg_yearly_travel_distance_km = st.number_input(
        T(lang, "travel_km_label"), min_value=0.0,
        value=float(cdef["avg_yearly_travel_distance_km"]), step=10.0, key="c_travel_km")
    avg_yearly_travel_hours = st.number_input(
        T(lang, "travel_hrs_label"), min_value=0.0,
        value=float(cdef["avg_yearly_travel_hours"]), step=1.0, key="c_travel_hrs")
    eu_ets_co2_price = st.number_input(
        T(lang, "co2_price_label"), min_value=0.0,
        value=float(cdef["eu_ets_co2_price_eur_per_tonne"]), step=1.0, key="c_co2_price")
    tree_co2_absorption = st.number_input(
        T(lang, "tree_abs_label"), min_value=0.1,
        value=float(cdef["tree_co2_absorption_kg_per_year"]), step=0.5, key="c_tree")
    construction_cost_per_spot = st.number_input(
        T(lang, "constr_cost_label"), min_value=0.0,
        value=float(cdef.get("construction_cost_per_parking_spot_eur", 30000.0)), step=500.0, key="c_constr_cost")
    st.markdown(T(lang, "hh_size_by_type_header"))
    hh_size_social_medium_rent = st.number_input(
        T(lang, "hh_social_label"), min_value=0.1,
        value=float(cdef["hh_size_social_medium_rent"]), step=0.1, key="c_hh_social")
    hh_size_free_up_to_30m2 = st.number_input(
        T(lang, "hh_30_label"), min_value=0.1,
        value=float(cdef["hh_size_free_up_to_30m2"]), step=0.1, key="c_hh_30")
    hh_size_free_30_to_60m2 = st.number_input(
        T(lang, "hh_60_label"), min_value=0.1,
        value=float(cdef["hh_size_free_30_to_60m2"]), step=0.1, key="c_hh_60")
    hh_size_free_above_60m2 = st.number_input(
        T(lang, "hh_above60_label"), min_value=0.1,
        value=float(cdef["hh_size_free_above_60m2"]), step=0.1, key="c_hh_above60")

country_overrides = {
    "share_18plus_with_license": share_18plus_with_license,
    "avg_parking_space_size_m2": avg_parking_space_size_m2,
    "share_train_travel": share_train_travel,
    "avg_passengers_per_bus": avg_passengers_per_bus,
    "avg_yearly_travel_distance_km": avg_yearly_travel_distance_km,
    "avg_yearly_travel_hours": avg_yearly_travel_hours,
    "eu_ets_co2_price_eur_per_tonne": eu_ets_co2_price,
    "tree_co2_absorption_kg_per_year": tree_co2_absorption,
    "construction_cost_per_parking_spot_eur": construction_cost_per_spot,
    "hh_size_social_medium_rent": hh_size_social_medium_rent,
    "hh_size_free_up_to_30m2": hh_size_free_up_to_30m2,
    "hh_size_free_30_to_60m2": hh_size_free_30_to_60m2,
    "hh_size_free_above_60m2": hh_size_free_above_60m2,
}
new_country = dict(ref.country)
new_country.update(country_overrides)
new_constants = dict(ref.constants)
new_constants["country_assumptions"] = new_country
ref = replace(ref, constants=new_constants)

inputs = ProjectInputs(
    project_name=selected_name, pc4=int(pc4), city=city,
    num_houses=num_houses, avg_household_size=avg_household_size,
    avg_cars_per_household=avg_cars_per_household, pct_buy=pct_buy,
    parking_category=parking_category, shared_car_usage_level=shared_car_usage_level,
    share_public_parking=share_public_parking, share_paid_public_parking=share_paid_public_parking,
    private_parking_spots_per_house=private_parking_spots_per_house_val,
    share_visitor_parking=share_visitor_parking, pct_25_45=pct_25_45, pct_high_income=pct_high_income,
    address_density=address_density, has_pt_in_1km=has_pt, categories=categories,
    share_single_hh=share_single_hh,
)
results = run_model(ref, inputs)

location_label = f"{inputs.city} (PC4 {inputs.pc4})"
project_label = selected_name if selected_name != CUSTOM_LABEL else T(lang, "custom_project_label")

brand.hero(
    T(lang, "hero_title"),
    T(lang, "hero_subtitle"),
    crumb=T(lang, "crumb", project=project_label, location=location_label),
    image_path=str(Path(__file__).parent / "assets" / "hero_car.jpg"),
    tag=T(lang, "hero_tag"),
)

tab_results, tab_method = st.tabs([T(lang, "tab_results"), T(lang, "tab_method")])

# =======================================================================
# RESULTS -- one page: carsharing potential + parking impact + emissions
# =======================================================================
with tab_results:
    top_l, top_r = st.columns([4, 1])
    with top_l:
        st.subheader(f"{project_label} — {location_label}")
    with top_r:
        docx_bytes = build_report_docx(ref, inputs, results)
        st.download_button(
            T(lang, "export_button"),
            data=docx_bytes,
            file_name=f"AVR_report_{inputs.city}_{inputs.pc4}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )

    # ---- 1. Carsharing potential ----
    brand.eyebrow(T(lang, "eyebrow_demand"))
    st.subheader(T(lang, "carsharing_potential"))
    st.caption(T(lang, "carsharing_potential_caption"))

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(brand.stat_card(T(lang, "card_residents"), f"{results.residents:,.0f}",
                                     T(lang, "card_residents_sub"),
                                     icon="🏘️", value_size="2.5rem"), unsafe_allow_html=True)
    with c2:
        st.markdown(brand.stat_card(T(lang, "card_active_users"),
                                     f"{results.active_share_min * 100:.1f}–{results.active_share_max * 100:.1f}%",
                                     icon="🧑‍🤝‍🧑", value_size="2.5rem"), unsafe_allow_html=True)
    with c3:
        st.markdown(brand.stat_card(T(lang, "card_active_users_n"),
                                     f"{results.active_users_min:,.0f}–{results.active_users_max:,.0f}",
                                     icon="👥", value_size="2.5rem"), unsafe_allow_html=True)
    with c4:
        st.markdown(brand.stat_card(T(lang, "card_deelautos_needed"),
                                     f"{results.additional_shared_cars_min:,.1f}–{results.additional_shared_cars_max:,.1f}",
                                     icon="🚗", value_size="2.5rem"), unsafe_allow_html=True)
    with c5:
        st.markdown(brand.stat_card(T(lang, "card_deelautos_per100"),
                                     f"{results.shared_cars_per_100hh_min:,.2f}–{results.shared_cars_per_100hh_max:,.2f}",
                                     icon="📊", value_size="2.5rem"), unsafe_allow_html=True)

    with st.expander(T(lang, "show_full_detail")):
        detail = pd.DataFrame({
            T(lang, "col_metric"): [
                T(lang, "metric_relevant_residents"), T(lang, "metric_active_share"), T(lang, "metric_active_users_n"),
                T(lang, "metric_untapped_demand"), T(lang, "metric_additional_shared"), T(lang, "metric_shared_per_1000"),
                T(lang, "metric_avr"), T(lang, "metric_cars_saved_gross"), T(lang, "metric_cars_saved_net"),
            ],
            T(lang, "col_min"): [results.relevant_residents, results.active_share_min, results.active_users_min,
                    results.untapped_demand_min_hours, results.additional_shared_cars_min, results.shared_cars_per_1000_min,
                    results.avr_min, results.cars_saved_gross_min, results.cars_saved_net_min],
            T(lang, "col_max"): [results.relevant_residents, results.active_share_max, results.active_users_max,
                    results.untapped_demand_max_hours, results.additional_shared_cars_max, results.shared_cars_per_1000_max,
                    results.avr_max, results.cars_saved_gross_max, results.cars_saved_net_max],
        })
        st.dataframe(detail, hide_index=True, use_container_width=True)

    brand.remark(T(lang, "remark_prediction_interval"))

    scenarios = scenario_comparison(ref, inputs, results)

    st.markdown(f"###### {T(lang, 'scenarios_demand_title')}")
    st.caption(T(lang, "scenarios_demand_caption"))
    st.markdown(
        brand.scenario_cards(
            [s.name for s in scenarios], [s.shared_cars_min for s in scenarios],
            [s.shared_cars_max for s in scenarios], value_fmt="{:.1f}",
            descriptions=[s.description for s in scenarios],
        ),
        unsafe_allow_html=True,
    )

    st.divider()

    # ---- 2. Parking space impact ----
    brand.eyebrow(T(lang, "eyebrow_supply"))
    st.subheader(T(lang, "parking_space_impact"))
    st.caption(T(lang, "parking_space_impact_caption"))

    m2_before_free = results.num_parking_spots * ref.country["avg_parking_space_size_m2"]
    freed_m2_low = m2_before_free - results.parking_space_needed_max_m2
    freed_m2_high = m2_before_free - results.parking_space_needed_min_m2

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(brand.stat_card(T(lang, "card_parking_norm"), f"{results.num_parking_spots:,.0f}",
                                     T(lang, "card_parking_norm_sub"), icon="🅿️"), unsafe_allow_html=True)
    with c2:
        st.markdown(brand.stat_card(T(lang, "card_parking_needed"),
                                     f"{results.parking_spots_after_min:,.0f}–{results.parking_spots_after_max:,.0f}",
                                     T(lang, "card_parking_needed_sub"), icon="🅿️"), unsafe_allow_html=True)
    with c3:
        st.markdown(brand.stat_card(T(lang, "card_space_freed"),
                                     f"{freed_m2_low:,.0f}–{freed_m2_high:,.0f} m²",
                                     T(lang, "card_space_freed_sub", lo=results.discount_min, hi=results.discount_max),
                                     icon="📐"),
                    unsafe_allow_html=True)

    st.write("")
    m3, m4, m5 = st.columns(3)
    with m3:
        st.markdown(brand.stat_card(T(lang, "card_cars_saved"),
                                     f"{results.cars_saved_net_min:,.1f} – {results.cars_saved_net_max:,.1f}",
                                     T(lang, "card_cars_saved_sub"), icon="🔻", value_size="2.5rem"), unsafe_allow_html=True)
    with m4:
        avr_val = (f"{results.avr_min:.1f}" if abs(results.avr_min - results.avr_max) < 0.05
                   else f"{results.avr_min:.1f} – {results.avr_max:.1f}")
        st.markdown(brand.stat_card(T(lang, "card_avr"), avr_val,
                                     T(lang, "card_avr_sub"), icon="🔄", value_size="2.5rem"),
                    unsafe_allow_html=True)
    with m5:
        # Same as the source Excel's "Savings (EUR) min/max": net parking
        # spots saved x a flat construction cost per spot (editable under
        # Country-level assumptions).
        constr_cost = ref.country["construction_cost_per_parking_spot_eur"]
        constr_savings_min = results.cars_saved_net_min * constr_cost
        constr_savings_max = results.cars_saved_net_max * constr_cost
        st.markdown(brand.stat_card(T(lang, "card_constr_savings"),
                                     f"€{constr_savings_min:,.0f} – €{constr_savings_max:,.0f}",
                                     T(lang, "card_constr_savings_sub",
                                       lo=results.cars_saved_net_min, hi=results.cars_saved_net_max,
                                       cost=constr_cost),
                                     icon="🏗️", value_size="2.5rem"),
                    unsafe_allow_html=True)

    st.markdown(f"###### {T(lang, 'scenarios_parking_title')}")
    st.caption(T(lang, "scenarios_parking_caption"))
    st.markdown(
        brand.scenario_cards(
            [s.name for s in scenarios], [abs(s.discount_max) * 100 for s in scenarios],
            [abs(s.discount_min) * 100 for s in scenarios], value_fmt="{:.1f}", unit="%",
            descriptions=[s.description for s in scenarios],
        ),
        unsafe_allow_html=True,
    )

    brand.remark(T(lang, "remark_parking_gap"))

    st.divider()

    # ---- 3. Emissions impact ----
    brand.eyebrow(T(lang, "eyebrow_environment"))
    st.subheader(T(lang, "emissions_impact"))
    st.caption(T(lang, "emissions_impact_caption"))

    co2 = results.emissions["CO2"]
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(brand.stat_card(T(lang, "card_co2_impact"), f"{co2['total_min']:,.0f} to {co2['total_max']:,.0f}",
                                     T(lang, "card_co2_impact_sub"), icon="🌍"), unsafe_allow_html=True)
    with c2:
        st.markdown(brand.stat_card(T(lang, "card_ets_value"),
                                     f"€{results.co2_cost_eur_min:,.0f} to €{results.co2_cost_eur_max:,.0f}",
                                     T(lang, "card_ets_value_sub"), icon="💶"), unsafe_allow_html=True)
    with c3:
        st.markdown(brand.stat_card(T(lang, "card_trees"),
                                     f"{results.trees_min:,.0f} to {results.trees_max:,.0f}",
                                     T(lang, "card_trees_sub"), icon="🌳"), unsafe_allow_html=True)
    st.write("")

    st.markdown(f"###### {T(lang, 'emissions_table_title')}")
    st.caption(T(lang, "emissions_table_caption"))

    price = ref.country["eu_ets_co2_price_eur_per_tonne"]
    tree_abs = ref.country["tree_co2_absorption_kg_per_year"]

    COL_ABS_MIN = T(lang, "col_absolute_min")
    COL_ABS_MAX = T(lang, "col_absolute_max")
    COL_A_MIN = T(lang, "col_a_min")
    COL_A_MAX = T(lang, "col_a_max")
    COL_B_MIN = T(lang, "col_b_min")
    COL_B_MAX = T(lang, "col_b_max")
    COL_TOTAL_MIN = T(lang, "col_total_min")
    COL_TOTAL_MAX = T(lang, "col_total_max")

    def _emissions_row(label, min_val, max_val, a_min, a_max, b_min, b_max, t_min, t_max):
        return {
            "": label,
            COL_ABS_MIN: min_val, COL_ABS_MAX: max_val,
            COL_A_MIN: a_min, COL_A_MAX: a_max,
            COL_B_MIN: b_min, COL_B_MAX: b_max,
            COL_TOTAL_MIN: t_min, COL_TOTAL_MAX: t_max,
        }

    rows = []
    for p in POLLUTANTS:
        e = results.emissions[p]
        rows.append(_emissions_row(
            T(lang, "row_total_pollutant", p=p),
            e["absolute_min"], e["absolute_max"], e["impact_a_min"], e["impact_a_max"],
            e["impact_b_min"], e["impact_b_max"], e["total_min"], e["total_max"],
        ))

    co2 = results.emissions["CO2"]
    rows.append(_emissions_row(
        T(lang, "row_ets_cost"),
        co2["absolute_min"] * price / 1000, co2["absolute_max"] * price / 1000,
        co2["impact_a_min"] * price / 1000, co2["impact_a_max"] * price / 1000,
        co2["impact_b_min"] * price / 1000, co2["impact_b_max"] * price / 1000,
        results.co2_cost_eur_min, results.co2_cost_eur_max,
    ))
    rows.append(_emissions_row(
        T(lang, "row_trees_required"),
        co2["absolute_min"] / tree_abs, co2["absolute_max"] / tree_abs,
        co2["impact_a_min"] / tree_abs, co2["impact_a_max"] / tree_abs,
        co2["impact_b_min"] / tree_abs, co2["impact_b_max"] / tree_abs,
        results.trees_min, results.trees_max,
    ))

    emissions_df = pd.DataFrame(rows).set_index("")
    emissions_fmt = emissions_df.map(lambda v: f"{v:,.1f}")
    st.markdown(brand.data_table(emissions_fmt), unsafe_allow_html=True)

    brand.remark(T(lang, "remark_pollutants"))

# =======================================================================
# METHODOLOGY TAB
# =======================================================================
with tab_method:
    brand.eyebrow(T(lang, "method_eyebrow"))
    st.subheader(T(lang, "method_title"))
    st.markdown(T(lang, "method_body"))
    st.subheader(T(lang, "method_quirks_title"))
    st.caption(T(lang, "method_quirks_caption"))
    for q in (KNOWN_QUIRKS if lang == "en" else KNOWN_QUIRKS_NL):
        st.markdown(f"- {q}")

    st.subheader(T(lang, "method_validation_title"))
    st.markdown(T(lang, "method_validation_body"))

st.markdown(brand.footer(T(lang, "footer_powered_by")), unsafe_allow_html=True)
