"""
Minimal two-language text layer for the app (English / Dutch).

Design notes:
- TEXTS holds every user-facing string as {"en": ..., "nl": ...}, keyed by a
  short mnemonic. T(lang, key, **kwargs) looks it up and .format()s it when
  kwargs are given.
- Widget *values* that flow into engine.py (e.g. "PC4 level", "City level",
  "A"/"B"/"C") are matched there by exact English string -- see
  engine.py's pc4_level_default() and Category.parking_ratio(). Those
  internal values are never translated; only their on-screen labels are,
  via each widget's format_func. Translating the internal values would
  silently break the model's own lookups.
- The Dutch used here is intentionally plain/direct rather than very
  formal -- it doesn't need to be polished policy-Dutch, just clear.
"""

TEXTS = {
    # ---- language switcher itself ----
    "lang_label": {"en": "Language", "nl": "Taal"},
    "footer_powered_by": {"en": "Powered by:", "nl": "Mogelijk gemaakt door:"},
    "advanced_inputs_title": {"en": "Advanced inputs", "nl": "Geavanceerde invoer"},

    # ---- sidebar: header + project picker ----
    "sidebar_title": {"en": "Describe your project", "nl": "Beschrijf je project"},
    "start_here": {"en": "Start here", "nl": "Begin hier"},
    "load_example": {"en": "Load an example development, or start custom",
                      "nl": "Laad een voorbeeldproject, of begin zelf"},
    "custom_project": {"en": "— Custom project —", "nl": "— Eigen project —"},
    "save_as_label": {"en": "Save this project as", "nl": "Sla dit project op als"},
    "save_as_placeholder": {"en": "e.g. Rotterdam — Zuidplein", "nl": "bijv. Rotterdam — Zuidplein"},
    "save_button": {"en": "💾 Save project", "nl": "💾 Project opslaan"},
    "save_warn_noname": {"en": "Give the project a name first.", "nl": "Geef het project eerst een naam."},

    # ---- section 0 ----
    "sec0_title": {"en": "0 · Project location", "nl": "0 · Locatie van het project"},
    "city_label": {"en": "City", "nl": "Stad"},
    "pc4_label": {"en": "Postcode (PC4) area", "nl": "Postcodegebied (PC4)"},
    "usage_level_label": {"en": "Base carsharing-usage rates (hours driven, AVR, distance) on:",
                           "nl": "Baseer deelauto-gebruikscijfers (gereden uren, AVR, afstand) op:"},
    "usage_level_help": {"en": "Benchmark = the best-practice postcode areas defined in the source "
                                "model (NL postcodes 2516, 3534, 5616).",
                          "nl": "Benchmark = de best-practice postcodegebieden uit het bronmodel "
                                "(postcodes 2516, 3534, 5616)."},
    "opt_pc4_level": {"en": "PC4 level", "nl": "PC4-niveau"},
    "opt_city_level": {"en": "City level", "nl": "Stadsniveau"},
    "opt_country_level": {"en": "Country level", "nl": "Landelijk niveau"},
    "opt_benchmark": {"en": "Benchmark", "nl": "Benchmark"},
    "parking_cat_label": {"en": "Parking-norm category (A = most relaxed, C = strictest)",
                           "nl": "Parkeernormcategorie (A = meest soepel, C = strengst)"},

    # ---- section 1 ----
    "sec1_title": {"en": "1 · Development characteristics", "nl": "1 · Kenmerken van het project"},
    "num_houses_label": {"en": "Number of houses", "nl": "Aantal woningen"},
    "hhsize_basis_label": {"en": "Household size — basis", "nl": "Huishoudgrootte — basis"},
    "hhsize_label": {"en": "Average household size (area default, editable)",
                      "nl": "Gemiddelde huishoudgrootte (gebiedsstandaard, aanpasbaar)"},
    "pct_buy_label": {"en": "Share of homes for owner-occupation (% buy)",
                       "nl": "Aandeel koopwoningen (%)"},

    # ---- section 5: city-level parking policy ----
    "sec5_title": {"en": "5 · City-level parking policy (power users)",
                   "nl": "5 · Gemeentelijk parkeerbeleid (voor gevorderden)"},
    "sec5_caption": {"en": "GFA thresholds and A/B/C parking ratios per unit category, same as the "
                           "source Excel's 'City level assumptions' sheet. Defaults match it exactly.",
                     "nl": "Oppervlaktegrenzen en A/B/C-parkeerratio's per woningcategorie, net als "
                           "het tabblad 'City level assumptions' in de bron-Excel. De standaardwaarden "
                           "komen hier precies mee overeen."},
    "col_category": {"en": "Category", "nl": "Categorie"},
    "col_gfa_lower": {"en": "GFA lower (m2)", "nl": "Oppervlakte vanaf (m2)"},
    "col_gfa_upper": {"en": "GFA upper (m2)", "nl": "Oppervlakte tot (m2)"},
    "col_ratio_a": {"en": "Ratio A", "nl": "Ratio A"},
    "col_ratio_b": {"en": "Ratio B", "nl": "Ratio B"},
    "col_ratio_c": {"en": "Ratio C", "nl": "Ratio C"},
    "visitor_default_label": {"en": "Visitor parking, city-policy default (% of private)",
                               "nl": "Bezoekersparkeren, standaard gemeentebeleid (% van privé)"},

    # ---- section 2: unit mix ----
    "sec2_title": {"en": "2 · Unit mix", "nl": "2 · Woningmix"},
    "sec2_caption": {"en": "Drives average household size, the private-parking norm, the "
                           "social-housing share and the single-person-household share used later "
                           "in the model. Shares should sum to ~100%.",
                     "nl": "Bepaalt de gemiddelde huishoudgrootte, de privéparkeernorm, het aandeel "
                           "sociale huur en het aandeel eenpersoonshuishoudens verderop in het model. "
                           "De aandelen moeten samen ongeveer 100% zijn."},
    "col_social_housing": {"en": "Social housing", "nl": "Sociale huur"},
    "col_share_of_houses": {"en": "Share of houses", "nl": "Aandeel woningen"},
    "col_parking_ratio": {"en": "Parking ratio ({cat})", "nl": "Parkeerratio ({cat})"},
    "shares_warning": {"en": "Shares sum to {pct}, not 100%. Results still compute, but check the mix.",
                        "nl": "Aandelen tellen op tot {pct}, niet 100%. De resultaten worden nog wel "
                              "berekend, maar controleer de mix."},
    "hhsize_source_label": {"en": "Average household size", "nl": "Gemiddelde huishoudgrootte"},
    "opt_area_default": {"en": "Use area default", "nl": "Gebruik gebiedsstandaard"},
    "opt_compute_mix": {"en": "Compute from unit mix above", "nl": "Berekenen uit woningmix hierboven"},
    "hhsize_selected_caption": {"en": "Selected household size: **{val:.2f} persons/home**",
                                 "nl": "Gekozen huishoudgrootte: **{val:.2f} personen/woning**"},
    "single_social_caption": {"en": "Single-person-household share ≈ **{single:.0%}**, "
                                     "social-housing share ≈ **{social:.0%}**.",
                               "nl": "Aandeel eenpersoonshuishoudens ≈ **{single:.0%}**, "
                                     "aandeel sociale huur ≈ **{social:.0%}**."},

    # ---- section 3: parking characteristics ----
    "sec3_title": {"en": "3 · Parking characteristics", "nl": "3 · Parkeerkenmerken"},
    "cars_per_hh_label": {"en": "Average cars per household (area default, editable)",
                           "nl": "Gemiddeld aantal auto's per huishouden (gebiedsstandaard, aanpasbaar)"},
    "share_public_label": {"en": "Share of parking that is public (%)",
                            "nl": "Aandeel openbare parkeerplaatsen (%)"},
    "share_paid_label": {"en": "Share of public parking that is paid (%)",
                          "nl": "Aandeel betaald openbaar parkeren (%)"},
    "share_visitor_label": {"en": "Visitor parking (% of private parking)",
                             "nl": "Bezoekersparkeren (% van privéparkeren)"},
    "private_ratio_caption": {"en": "Computed from unit mix × category **{cat}**: "
                                     "**{val:.3f}** spots/house",
                               "nl": "Berekend uit woningmix × categorie **{cat}**: "
                                     "**{val:.3f}** plekken/woning"},
    "private_ratio_label": {"en": "Private parking spots per house (editable)",
                             "nl": "Privéparkeerplaatsen per woning (aanpasbaar)"},

    # ---- section 4: sociodemographics ----
    "sec4_title": {"en": "4 · Sociodemographics & environment", "nl": "4 · Sociodemografie & omgeving"},
    "pct2545_label": {"en": "Residents 25–45 yrs (%)", "nl": "Bewoners 25–45 jaar (%)"},
    "pct_hi_label": {"en": "High-income households (%)", "nl": "Huishoudens met hoog inkomen (%)"},
    "addr_density_label": {"en": "Address density (addresses/km²)", "nl": "Adresdichtheid (adressen/km²)"},
    "has_pt_label": {"en": "Public transport stop within 1 km", "nl": "OV-halte binnen 1 km"},
    "single_hh_caption": {"en": "Computed from the unit mix above: **{val:.0%}** of homes are "
                                 "single-person households. This feeds the carsharing-potential "
                                 "model below — override it if you have a better project-level estimate.",
                           "nl": "Berekend uit de woningmix hierboven: **{val:.0%}** van de woningen "
                                 "is een eenpersoonshuishouden. Dit voedt het deelauto-potentieelmodel "
                                 "hieronder — pas het aan als je een betere projectinschatting hebt."},
    "single_hh_label": {"en": "Share of single-person households (editable)",
                         "nl": "Aandeel eenpersoonshuishoudens (aanpasbaar)"},

    # ---- section 6: country-level assumptions ----
    "sec6_title": {"en": "6 · Country-level assumptions (power users)",
                   "nl": "6 · Landelijke aannames (voor gevorderden)"},
    "sec6_caption": {"en": "Same national constants as the source Excel's 'Country level assumptions' "
                           "sheet. Defaults match it exactly — edit only to test sensitivity.",
                     "nl": "Dezelfde landelijke constanten als het tabblad 'Country level assumptions' "
                           "in de bron-Excel. De standaardwaarden komen hier precies mee overeen — "
                           "pas ze alleen aan om de gevoeligheid te testen."},
    "license_label": {"en": "Share of residents 18+ with a driving license",
                       "nl": "Aandeel bewoners 18+ met rijbewijs"},
    "spot_size_label": {"en": "Average parking-space size (m²)", "nl": "Gemiddelde grootte parkeerplaats (m²)"},
    "train_share_label": {"en": "Share of PT travel that is by train", "nl": "Aandeel OV-reizen per trein"},
    "bus_pax_label": {"en": "Average passengers per bus", "nl": "Gemiddeld aantal passagiers per bus"},
    "travel_km_label": {"en": "Average yearly travel distance (km/person)",
                         "nl": "Gemiddelde jaarlijkse reisafstand (km/persoon)"},
    "travel_hrs_label": {"en": "Average yearly travel hours (per person)",
                          "nl": "Gemiddeld aantal reisuren per jaar (per persoon)"},
    "co2_price_label": {"en": "EU-ETS CO₂ price (€/tonne)", "nl": "EU-ETS CO₂-prijs (€/ton)"},
    "tree_abs_label": {"en": "CO₂ absorbed per tree per year (kg)", "nl": "CO₂-opname per boom per jaar (kg)"},
    "constr_cost_label": {"en": "Construction cost per parking spot (€, for savings estimate)",
                           "nl": "Bouwkosten per parkeerplaats (€, voor besparingsschatting)"},
    "hh_size_by_type_header": {"en": "**Household size by unit type** (persons/home, used where GFA isn't the driver)",
                                "nl": "**Huishoudgrootte per woningtype** (personen/woning, gebruikt "
                                      "waar oppervlakte niet bepalend is)"},
    "hh_social_label": {"en": "Social / medium-priced rent", "nl": "Sociale / middeldure huur"},
    "hh_30_label": {"en": "Free sector, up to 30 m²", "nl": "Vrije sector, tot 30 m²"},
    "hh_60_label": {"en": "Free sector, 30–60 m²", "nl": "Vrije sector, 30–60 m²"},
    "hh_above60_label": {"en": "Free sector, above 60 m²", "nl": "Vrije sector, boven 60 m²"},

    # ---- hero / tabs ----
    "hero_title": {"en": "Explore your results", "nl": "Bekijk je resultaten"},
    "hero_subtitle": {"en": "How much space should a new housing development dedicate for shared "
                             "cars — and what happens when demand is met?",
                       "nl": "Hoeveel ruimte moet een nieuwbouwproject vrijhouden voor deelauto's — "
                             "en wat gebeurt er als de vraag is opgevangen?"},
    "hero_tag": {"en": "New housing development · shared mobility tool",
                 "nl": "Nieuwbouwproject · tool voor deelmobiliteit"},
    "crumb": {"en": "Home / Tool / {project} / {location}", "nl": "Home / Tool / {project} / {location}"},
    "tab_results": {"en": "Explore your results", "nl": "Bekijk je resultaten"},
    "tab_method": {"en": "Methodology & sources", "nl": "Methodologie & bronnen"},
    "custom_project_label": {"en": "Custom project", "nl": "Eigen project"},
    "export_button": {"en": "⬇ Export report (.docx)", "nl": "⬇ Rapport exporteren (.docx)"},

    # ---- 1. carsharing potential ----
    "eyebrow_demand": {"en": "1 · Demand", "nl": "1 · Vraag"},
    "carsharing_potential": {"en": "Carsharing potential", "nl": "Potentieel voor deelauto's"},
    "carsharing_potential_caption": {"en": "Potential demand and the recommended supply of shared "
                                            "cars, from a 95% prediction interval — not a best/worst case.",
                                      "nl": "Potentiële vraag en het aanbevolen aanbod deelauto's, op "
                                            "basis van een 95%-betrouwbaarheidsinterval — geen "
                                            "beste/slechtste geval."},
    "card_residents": {"en": "Residents", "nl": "Bewoners"},
    "card_residents_sub": {"en": "from the unit mix", "nl": "op basis van de woningmix"},
    "card_active_users": {"en": "Active users", "nl": "Actieve gebruikers"},
    "card_active_users_n": {"en": "Active users (#)", "nl": "Actieve gebruikers (#)"},
    "card_deelautos_needed": {"en": "Deelauto's needed", "nl": "Deelauto's nodig"},
    "card_deelautos_per100": {"en": "Deelauto's / 100 HH", "nl": "Deelauto's / 100 huishoudens"},
    "show_full_detail": {"en": "Show full detail (all min/max carsharing-potential figures)",
                          "nl": "Toon alle details (alle min/max-cijfers voor deelautopotentieel)"},
    "col_metric": {"en": "Metric", "nl": "Kengetal"},
    "col_min": {"en": "Min", "nl": "Min"},
    "col_max": {"en": "Max", "nl": "Max"},
    "metric_relevant_residents": {"en": "Relevant residents (18+, driving-license eligible)",
                                   "nl": "Relevante bewoners (18+, rijbewijsgerechtigd)"},
    "metric_active_share": {"en": "Active-user share", "nl": "Aandeel actieve gebruikers"},
    "metric_active_users_n": {"en": "Active users (#)", "nl": "Actieve gebruikers (#)"},
    "metric_untapped_demand": {"en": "Untapped demand (hours/month)", "nl": "Onbenutte vraag (uren/maand)"},
    "metric_additional_shared": {"en": "Additional shared cars needed", "nl": "Extra deelauto's nodig"},
    "metric_shared_per_1000": {"en": "Shared cars / 1,000 residents", "nl": "Deelauto's / 1.000 bewoners"},
    "metric_avr": {"en": "Average Vehicles Replaced (AVR) per shared car",
                   "nl": "Gemiddeld aantal vervangen auto's (AVR) per deelauto"},
    "metric_cars_saved_gross": {"en": "Cars saved (gross)", "nl": "Bespaarde auto's (bruto)"},
    "metric_cars_saved_net": {"en": "Cars saved (net of shared cars)", "nl": "Bespaarde auto's (netto, na deelauto's)"},
    "remark_prediction_interval": {"en": "This is a 95% prediction interval, not a best/worst case — "
                                          "treat both ends as plausible, not extremes. Rerun once the "
                                          "unit mix and parking plan are finalised; the range narrows "
                                          "as those inputs firm up.",
                                    "nl": "Dit is een 95%-betrouwbaarheidsinterval, geen beste/slechtste "
                                          "geval — zie beide uiteinden als aannemelijk, niet als "
                                          "extremen. Herbereken zodra de woningmix en het parkeerplan "
                                          "definitief zijn; de bandbreedte wordt dan smaller."},
    "scenarios_demand_title": {"en": "Comparing scenarios — shared cars needed",
                                "nl": "Scenario's vergeleken — benodigde deelauto's"},
    "scenarios_demand_caption": {"en": "This project's own numbers (baseline) against three what-if "
                                        "benchmarks: matching the usage rate other areas in this "
                                        "city/country achieve, or a flat policy rule of thumb.",
                                  "nl": "De eigen cijfers van dit project (uitgangspunt) tegenover drie "
                                        "wat-als-scenario's: hetzelfde gebruik als andere gebieden in "
                                        "deze stad/dit land, of een simpele beleidsvuistregel."},

    # ---- 2. parking space impact ----
    "eyebrow_supply": {"en": "2 · Supply", "nl": "2 · Aanbod"},
    "parking_space_impact": {"en": "Parking space impact", "nl": "Impact op parkeerruimte"},
    "parking_space_impact_caption": {"en": "What the parking plan looks like against policy norm, and "
                                            "what carsharing frees up once it's running.",
                                      "nl": "Hoe het parkeerplan zich verhoudt tot de parkeernorm, en "
                                            "wat deelauto's opleveren zodra ze draaien."},
    "card_parking_norm": {"en": "Parking spots — policy norm", "nl": "Parkeerplaatsen — beleidsnorm"},
    "card_parking_norm_sub": {"en": "before carsharing", "nl": "vóór deelauto's"},
    "card_parking_needed": {"en": "Parking spots needed", "nl": "Benodigde parkeerplaatsen"},
    "card_parking_needed_sub": {"en": "after carsharing", "nl": "na deelauto's"},
    "card_space_freed": {"en": "Space freed up", "nl": "Vrijgekomen ruimte"},
    "card_space_freed_sub": {"en": "discount vs. norm: {lo:.1%} to {hi:.1%}",
                              "nl": "korting t.o.v. norm: {lo:.1%} tot {hi:.1%}"},
    "card_cars_saved": {"en": "Cars saved", "nl": "Bespaarde auto's"},
    "card_cars_saved_sub": {"en": "net of shared cars added", "nl": "netto, na toegevoegde deelauto's"},
    "card_avr": {"en": "Auto-vervangingsratio (AVR)", "nl": "Auto-vervangingsratio (AVR)"},
    "card_avr_sub": {"en": "parking spots freed per shared car deployed",
                      "nl": "vrijgekomen parkeerplaatsen per ingezette deelauto"},
    "card_constr_savings": {"en": "Construction savings", "nl": "Bouwbesparing"},
    "card_constr_savings_sub": {"en": "{lo:,.1f}–{hi:,.1f} spots × €{cost:,.0f}",
                                 "nl": "{lo:,.1f}–{hi:,.1f} plekken × €{cost:,.0f}"},
    "scenarios_parking_title": {"en": "Comparing scenarios — parking discount vs. policy norm",
                                 "nl": "Scenario's vergeleken — parkeerkorting t.o.v. beleidsnorm"},
    "scenarios_parking_caption": {"en": "Same four scenarios as above, read as the % of policy-norm "
                                         "parking spots no longer needed (negative values from the "
                                         "model shown here as the size of the reduction).",
                                   "nl": "Dezelfde vier scenario's als hierboven, nu als het % "
                                         "normplaatsen dat niet meer nodig is (negatieve waarden uit "
                                         "het model worden hier getoond als de omvang van de afname)."},
    "remark_parking_gap": {"en": "The gap between \"policy norm\" and \"after carsharing\" is small "
                                  "by design — carsharing trims the margin, it doesn't replace the "
                                  "norm. Read this alongside the demand range above: it's only worth "
                                  "banking these spots if the active-user range is realistic for this "
                                  "site.",
                            "nl": "Het verschil tussen \"beleidsnorm\" en \"na deelauto's\" is bewust "
                                  "klein — deelauto's knabbelen aan de marge, ze vervangen de norm "
                                  "niet. Lees dit samen met de vraagbandbreedte hierboven: reken deze "
                                  "plekken alleen mee als het aantal actieve gebruikers realistisch "
                                  "is voor deze locatie."},

    # ---- 3. emissions impact ----
    "eyebrow_environment": {"en": "3 · Environment", "nl": "3 · Milieu"},
    "emissions_impact": {"en": "Emissions impact", "nl": "Impact op uitstoot"},
    "emissions_impact_caption": {"en": "Combines (A) the effect of residents driving a shared car "
                                        "instead of their own car, and (B) the effect of former car "
                                        "owners shifting some trips to public transport.",
                                  "nl": "Combineert (A) het effect van bewoners die een deelauto "
                                        "gebruiken in plaats van hun eigen auto, en (B) het effect "
                                        "van voormalige autobezitters die deels overstappen op het OV."},
    "card_co2_impact": {"en": "CO₂ impact", "nl": "CO₂-impact"},
    "card_co2_impact_sub": {"en": "kg / year · negative = reduction", "nl": "kg / jaar · negatief = afname"},
    "card_ets_value": {"en": "EU-ETS equivalent value", "nl": "EU-ETS-equivalente waarde"},
    "card_ets_value_sub": {"en": "per year", "nl": "per jaar"},
    "card_trees": {"en": "Equivalent trees", "nl": "Equivalent aantal bomen"},
    "card_trees_sub": {"en": "absorbing this CO₂ per year", "nl": "die deze CO₂ per jaar opnemen"},
    "emissions_table_title": {"en": "8. Emission impact from carsharing", "nl": "8. Uitstootimpact van deelauto's"},
    "emissions_table_caption": {"en": "Absolute shared-fleet emission volume, the two impact channels "
                                       "that make it up, and the combined total — same structure as "
                                       "the source Excel's emissions table.",
                                 "nl": "Absoluut uitstootvolume van het deelautopark, de twee "
                                       "effecten waaruit dit is opgebouwd, en het gecombineerde "
                                       "totaal — dezelfde opzet als de emissietabel in de bron-Excel."},
    "col_absolute_min": {"en": "Absolute — Min", "nl": "Absoluut — Min"},
    "col_absolute_max": {"en": "Absolute — Max", "nl": "Absoluut — Max"},
    "col_a_min": {"en": "A) Shared vs. own car — Min", "nl": "A) Deelauto vs. eigen auto — Min"},
    "col_a_max": {"en": "A) — Max", "nl": "A) — Max"},
    "col_b_min": {"en": "B) Modal shift to PT — Min", "nl": "B) Overstap naar OV — Min"},
    "col_b_max": {"en": "B) — Max", "nl": "B) — Max"},
    "col_total_min": {"en": "Total impact (A+B) — Min", "nl": "Totale impact (A+B) — Min"},
    "col_total_max": {"en": "Total impact (A+B) — Max", "nl": "Totale impact (A+B) — Max"},
    "row_total_pollutant": {"en": "Total {p} impact per year (kg)", "nl": "Totale {p}-impact per jaar (kg)"},
    "row_ets_cost": {"en": "CO₂ EU-ETS equivalent compliance cost (EUR)",
                      "nl": "CO₂ EU-ETS-equivalente kosten (EUR)"},
    "row_trees_required": {"en": "# of trees required to absorb the CO₂ equivalent (per year)",
                            "nl": "Aantal bomen nodig om de CO₂-equivalent op te nemen (per jaar)"},
    "remark_pollutants": {"en": "All pollutants scale off the same active-user range, so the CO₂ "
                                 "figure above is a fair stand-in for reading the rest of the set at "
                                 "a glance.",
                           "nl": "Alle stoffen schalen mee met dezelfde bandbreedte actieve "
                                 "gebruikers, dus het CO₂-cijfer hierboven geeft in één oogopslag een "
                                 "goed beeld van de rest van de tabel."},

    # ---- methodology tab ----
    "method_eyebrow": {"en": "A quick intro", "nl": "Een korte introductie"},
    "method_title": {"en": "How this tool works", "nl": "Hoe deze tool werkt"},
    "method_body": {
        "en": """
This tool ports the calculation logic of a policy-support Excel model built to help
Dutch municipalities size parking for new developments and estimate the impact of
carsharing. The pipeline, section by section:

1. **Development characteristics** — number of houses, household size and car
   ownership, taken from postcode-area (PC4), city or national statistics unless overridden.
2. **Unit mix** — the share of homes in each size/tenure category drives the average
   household size, the social-housing share, and the single-person-household share.
3. **Parking characteristics** — private/public/visitor parking spots, from the
   municipal parking-norm policy (category A/B/C) applied to the unit mix.
4. **Sociodemographics & built environment** — age profile, income, address density,
   and public-transport access, from postcode-area statistics.
5. **Carsharing potential** — a beta-regression model (calibrated on existing
   carsharing areas across the Netherlands) predicts the *share of residents who
   would actively use a shared car*, as a 95% prediction interval. That share,
   combined with benchmark data on hours driven per active user and per shared car,
   gives the number of *additional shared cars* the area could support.
6. **Parking impact** — using the Average Vehicles Replaced (AVR) per shared car
   (i.e. how many private cars a single shared car typically displaces), the model
   estimates cars saved and the resulting reduction in parking spots needed — the
   **parking discount** versus the policy norm.
7. **Emissions impact** — combines (A) the tailpipe-emission difference between a
   typical shared-car fleet and a typical own-car fleet, and (B) the emissions
   effect of some trips shifting to public transport, using Dutch (PBL/CE Delft)
   emission factors.

All reference data (postcode-area statistics, regression coefficients, emission
factors) were extracted from the source workbook and ship with this tool; see
`reference/` in the project folder. Every input lives on the left-hand ribbon —
change it there and every section on the Results page updates together. Use
"⬇ Export report (.docx)" at the top of the Results page to save a Word report
for the currently-selected location.
""",
        "nl": """
Deze tool zet de rekenlogica over van een beleidsondersteunend Excel-model dat is
gebouwd om Nederlandse gemeenten te helpen bij het bepalen van parkeerruimte voor
nieuwbouwprojecten en het inschatten van de impact van deelauto's. Het proces,
onderdeel voor onderdeel:

1. **Kenmerken van het project** — aantal woningen, huishoudgrootte en autobezit,
   gehaald uit postcodegebied- (PC4), stads- of landelijke statistieken, tenzij je
   dit zelf aanpast.
2. **Woningmix** — het aandeel woningen per grootte-/eigendomscategorie bepaalt de
   gemiddelde huishoudgrootte, het aandeel sociale huur en het aandeel
   eenpersoonshuishoudens.
3. **Parkeerkenmerken** — privé-, openbare en bezoekersparkeerplaatsen, op basis van
   de gemeentelijke parkeernorm (categorie A/B/C) toegepast op de woningmix.
4. **Sociodemografie & bebouwde omgeving** — leeftijdsopbouw, inkomen, adresdichtheid
   en OV-toegankelijkheid, uit postcodegebiedstatistieken.
5. **Potentieel voor deelauto's** — een bèta-regressiemodel (gekalibreerd op
   bestaande deelautogebieden in heel Nederland) voorspelt het *aandeel bewoners
   dat actief een deelauto zou gebruiken*, als een 95%-betrouwbaarheidsinterval.
   Dat aandeel, samen met benchmarkgegevens over gereden uren per actieve
   gebruiker en per deelauto, geeft het aantal *extra deelauto's* dat het gebied
   zou kunnen dragen.
6. **Parkeerimpact** — met de gemiddelde vervangingsratio (AVR) per deelauto (hoeveel
   privéauto's één deelauto doorgaans vervangt) schat het model de bespaarde auto's
   en de bijbehorende afname in benodigde parkeerplaatsen — de **parkeerkorting**
   ten opzichte van de beleidsnorm.
7. **Uitstootimpact** — combineert (A) het verschil in uitlaatemissies tussen een
   typisch deelautopark en een typisch eigen-autopark, en (B) het uitstooteffect
   van ritten die overstappen naar het OV, met Nederlandse (PBL/CE Delft)
   emissiefactoren.

Alle brongegevens (postcodegebiedstatistieken, regressiecoëfficiënten,
emissiefactoren) zijn overgenomen uit het bronbestand en worden meegeleverd met
deze tool; zie de map `reference/` in de projectmap. Alle invoer staat op het
linkerpaneel — wijzig daar iets en elk onderdeel van de resultatenpagina werkt
dit gelijk bij. Gebruik "⬇ Rapport exporteren (.docx)" bovenaan de
resultatenpagina om een Word-rapport op te slaan voor de geselecteerde locatie.
""",
    },
    "method_quirks_title": {"en": "Known quirks inherited from the source workbook",
                             "nl": "Bekende eigenaardigheden uit het bronbestand"},
    "method_quirks_caption": {"en": "These were found while porting the formulas. They are replicated "
                                     "exactly (not 'corrected') since the brief was to match the Excel "
                                     "tool's exact calculation mechanism — but they're worth a look "
                                     "from whoever maintains the source model.",
                               "nl": "Deze zijn gevonden tijdens het overzetten van de formules. Ze "
                                     "zijn precies zo overgenomen (niet 'gecorrigeerd'), omdat de "
                                     "opdracht was om exact hetzelfde te rekenen als de Excel-tool — "
                                     "maar de beheerder van het bronmodel kan er wel eens naar kijken."},
    "method_validation_title": {"en": "Validation", "nl": "Validatie"},
    "method_validation_body": {"en": "Engine outputs were checked cell-by-cell against the cached "
                                      "values in the source workbook for the *Rotterdam – "
                                      "Merwedevierhavens M4H* example project (see `validate.py`) — "
                                      "all figures matched to within floating-point precision.",
                                "nl": "De uitkomsten van het rekenmodel zijn cel voor cel vergeleken "
                                      "met de opgeslagen waarden in het bronbestand voor het "
                                      "voorbeeldproject *Rotterdam – Merwedevierhavens M4H* (zie "
                                      "`validate.py`) — alle cijfers kwamen overeen tot op "
                                      "drijvendekomma-precisie."},
}


def T(lang: str, key: str, **kwargs) -> str:
    entry = TEXTS.get(key)
    if entry is None:
        return key
    s = entry.get(lang, entry.get("en", key))
    return s.format(**kwargs) if kwargs else s


# Dutch counterparts for engine.KNOWN_QUIRKS (kept here rather than in engine.py
# so the calculation module -- already validated cell-by-cell -- stays untouched).
# Order must match engine.KNOWN_QUIRKS exactly.
KNOWN_QUIRKS_NL = [
    "Regressie actieve gebruikers: de invoer 'perc_pop_25to45yr' is in het bronblad "
    "gekoppeld aan PC4-kolom FL ('perc_pop_45to65yr'), niet FK ('perc_pop_25to45yr'). "
    "Zo overgenomen als gebouwd; goed om te checken bij de eigenaar van het model.",
    "Emissiefactoren auto's: de rij 'Petrol cars' in het bronblad haalt gegevens uit "
    "de rij 'Diesel' van de PBL-emissiefactoren (en andersom voor 'Diesel cars'). "
    "Zo overgenomen als gebouwd.",
    "Impact B (overstap naar OV): de emissieterm voor de eigen auto wordt omgerekend "
    "naar kg (gedeeld door 1000), maar de OV-term niet — waardoor de OV-term ongeveer "
    "1000x te klein is en nauwelijks meetelt in het resultaat. Zo overgenomen als gebouwd.",
    "De brandstofmixkeuze voor eigen/deelauto's heeft een onbereikbare 'stadsniveau'-tak "
    "wanneer er geen PC4-niveaugegevens voor het gebied bestaan (die valt dan altijd "
    "terug op het landelijk gemiddelde). Gedragsmatig zo overgenomen.",
    "Betrouwbaarheidsinterval actieve gebruikers: de breedte is Z * confidence_level * SD "
    "(de Z-score van 95% keer de invoer '0,95 betrouwbaarheidsniveau', niet de "
    "ernaast staande 'foutmarge'-invoer die daarvoor bedoeld lijkt). Zo overgenomen als "
    "gebouwd; de foutmarge-invoer wordt niet gebruikt.",
]
