# Shared Mobility Parking & Impact Tool

A Streamlit port of a policy-support Excel model ("AVR - excel tool - mockup - v3")
built to help municipalities:

1. size how much parking a new housing development needs to set aside for shared
   ("carsharing") vehicles, and
2. estimate the resulting parking-space and emissions impact if carsharing is
   implemented as planned.

## Running it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (usually http://localhost:8501).

## Project layout

- `app.py` — the Streamlit UI (3 tabs: project setup, carsharing & parking impact,
  emissions impact, plus a methodology tab).
- `engine.py` — the calculation engine, a pure-Python/pandas port of the Excel
  formulas. No Streamlit dependency, so it can be tested standalone.
- `validate.py` — checks `engine.py`'s output against cached values from the
  source workbook for the "Rotterdam - Merwedevierhavens M4H" example project.
  Run `python validate.py` — it should print `ALL OK`.
- `reference/` — data extracted from the source workbook:
  - `constants.json` — country-level assumptions, the beta-regression
    coefficients for the active-user model, vehicle/bus/train emission factors,
    and the default city parking-policy table.
  - `existing_areas_benchmark.csv` — per-postcode-area carsharing usage
    statistics (hours driven, AVR, fuel mix, etc.) used to compute PC4/city/
    country/benchmark-level carsharing metrics.
  - `pc4_info.csv` — per-postcode-area socio-demographic statistics used as
    defaults for the project-setup inputs.
  - `city_diesel_share.csv` — per-city diesel-bus-share, used in the emissions
    calculation.
  - `projects.csv` — the 25 example developments from the source workbook,
    used to populate the project picker.

## What's faithfully replicated vs. simplified

The calculation logic (sections 1–8 of the source "New development overview"
sheet, the beta-regression active-user model, the carsharing-statistics
percentile engine, and the emissions model) is ported formula-for-formula and
validated against the source workbook's cached values — see `validate.py`.

A few things were simplified for usability rather than replicated 1:1:

- **Overrides.** The source sheet has an explicit "override enabled" switch and
  separate default/override columns per field. This app instead shows every
  input pre-filled with its computed default and directly editable — functionally
  equivalent, but friendlier for a policymaker who isn't an Excel power-user.
- **City parking-policy table.** In the source file this is a single, manually
  maintained table (not looked up per city). This app keeps it that way — it's
  shown as an editable reference in the unit-mix table (parking ratio column)
  keyed off the chosen parking category (A/B/C). If different cities' policies
  need to be swapped in, that table is the place to extend it.

## Known quirks inherited from the source workbook

While porting the formulas cell-by-cell, a few apparent inconsistencies in the
source model were found. They are replicated exactly (not "fixed"), since the
brief was to match the Excel tool's exact calculation mechanism — but they're
worth checking with whoever maintains the source file. See `KNOWN_QUIRKS` in
`engine.py` (also shown in the app's "Methodology & sources" tab):

1. The regression input labelled `perc_pop_25to45yr` is actually wired to the
   PC4 column for 45-65 year-olds, not 25-45.
2. The "Petrol cars" and "Diesel cars" emission-factor rows appear to pull
   from swapped rows in the source PBL_emission factors table.
3. In the modal-shift-to-public-transport emissions term, the own-car figure
   is converted to kg but the PT-alternative figure isn't, so the latter
   contributes negligibly to the result.
4. The active-user prediction interval's width uses `Z * confidence_level`
   rather than the adjacent "error multiplier" input that looks like it's
   meant for that purpose — the error multiplier is effectively unused.

## Next steps / ideas for v2

- Wire up the 4 pre-built "Scenario analysis" comparisons from the source
  workbook (Baseline / City 75th percentile / Country 95th percentile / fixed
  1:20 & 1:4 ratios) as a side-by-side comparison view.
- Add a city-specific parking-policy library instead of one shared table.
- Add a map view (postcode-area picker) instead of a dropdown.
- Export a one-page PDF/summary for a given project.
