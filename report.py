"""
Word (.docx) export of a project's results — one report per location, so a
policymaker can save/share the numbers without opening the tool.
"""
from __future__ import annotations

import io
from datetime import date

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor, Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from engine import POLLUTANTS, KNOWN_QUIRKS, ReferenceData, ProjectInputs, Results

NAVY = RGBColor(0x15, 0x2B, 0x4E)
CORAL = RGBColor(0xEC, 0x42, 0x3C)
GREY = RGBColor(0x5B, 0x70, 0x91)


def _shade_cell(cell, hex_color: str):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def _add_kv_table(doc, rows: list[tuple[str, str]], header: str | None = None):
    table = doc.add_table(rows=0, cols=2)
    table.style = "Light Grid Accent 1"
    table.autofit = True
    for label, value in rows:
        r = table.add_row().cells
        r[0].text = label
        r[1].text = value
        r[0].paragraphs[0].runs[0].font.size = Pt(10)
        r[1].paragraphs[0].runs[0].font.size = Pt(10)
        r[1].paragraphs[0].runs[0].bold = True
    return table


def _section_heading(doc, eyebrow: str, title: str):
    p = doc.add_paragraph()
    run = p.add_run(eyebrow.upper())
    run.font.size = Pt(9)
    run.font.color.rgb = CORAL
    run.bold = True
    h = doc.add_heading(title, level=2)
    for run in h.runs:
        run.font.color.rgb = NAVY


def _remark(doc, text: str):
    p = doc.add_paragraph()
    r = p.add_run("Remark:  ")
    r.bold = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = CORAL
    r2 = p.add_run(text)
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = GREY
    p.paragraph_format.space_after = Pt(12)


def build_report_docx(ref: ReferenceData, inputs: ProjectInputs, results: Results) -> bytes:
    doc = Document()

    # ---- base style ----
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    # ---- title page block ----
    title = doc.add_heading("Shared mobility — results report", level=0)
    for run in title.runs:
        run.font.color.rgb = CORAL

    sub = doc.add_paragraph()
    sub.add_run(
        f"{inputs.project_name if inputs.project_name != '— Custom project —' else 'Custom project'}"
    ).bold = True
    sub.runs[0].font.size = Pt(14)
    sub.runs[0].font.color.rgb = NAVY

    facts = doc.add_paragraph()
    facts.add_run(
        f"{inputs.city} · PC4 {inputs.pc4} · {inputs.num_houses:,.0f} houses · "
        f"parking category {inputs.parking_category} · generated {date.today().isoformat()}"
    ).font.color.rgb = GREY
    facts.runs[0].font.size = Pt(10)

    warn = doc.add_paragraph()
    r = warn.add_run(
        "Garbage in, garbage out. These figures come straight from the project inputs used to "
        "generate this report — there is no sanity check on the model's end. Confirm every input "
        "reflected your actual project before relying on the numbers below."
    )
    r.italic = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = GREY
    doc.add_paragraph()

    # ---- 0. project inputs recap ----
    _section_heading(doc, "0 · Inputs", "Project inputs")
    _add_kv_table(doc, [
        ("Location", f"{inputs.city} (PC4 {inputs.pc4})"),
        ("Number of houses", f"{inputs.num_houses:,.0f}"),
        ("Average household size", f"{inputs.avg_household_size:.2f} persons/home"),
        ("Average cars per household", f"{inputs.avg_cars_per_household:.2f}"),
        ("Share of homes for owner-occupation", f"{inputs.pct_buy:.0%}"),
        ("Parking policy category", inputs.parking_category),
        ("Carsharing benchmark level", inputs.shared_car_usage_level),
        ("Share of parking that is public", f"{inputs.share_public_parking:.0%}"),
        ("Share of public parking that is paid", f"{inputs.share_paid_public_parking:.0%}"),
        ("Private parking spots per house", f"{inputs.private_parking_spots_per_house:.3f}"),
        ("Visitor parking (% of private parking)", f"{inputs.share_visitor_parking:.0%}"),
        ("Residents 25–45 yrs", f"{inputs.pct_25_45:.0%}"),
        ("High-income households", f"{inputs.pct_high_income:.0%}"),
        ("Address density", f"{inputs.address_density:,.0f} / km²"),
        ("Public transport stop within 1 km", "Yes" if inputs.has_pt_in_1km else "No"),
    ])
    doc.add_paragraph()

    # ---- 1. carsharing potential ----
    _section_heading(doc, "1 · Demand", "Carsharing potential")
    doc.add_paragraph(
        "Potential demand and the recommended supply of shared cars, from a 95% prediction "
        "interval — not a best/worst case."
    ).runs[0].font.size = Pt(10)
    _add_kv_table(doc, [
        ("Residents", f"{results.residents:,.0f}"),
        ("Active users (%)", f"{results.active_share_min:.1%} – {results.active_share_max:.1%}"),
        ("Active users (#)", f"{results.active_users_min:,.0f} – {results.active_users_max:,.0f}"),
        ("Deelauto's (shared cars) needed", f"{results.additional_shared_cars_min:,.1f} – {results.additional_shared_cars_max:,.1f}"),
        ("Deelauto's per 100 households", f"{results.shared_cars_per_100hh_min:,.2f} – {results.shared_cars_per_100hh_max:,.2f}"),
    ])
    _remark(
        doc,
        "This is a 95% prediction interval, not a best/worst case — treat both ends as plausible, "
        "not extremes. Rerun once the unit mix and parking plan are finalised; the range narrows as "
        "those inputs firm up."
    )

    # ---- 2. parking space impact ----
    _section_heading(doc, "2 · Supply", "Parking space impact")
    m2_before = results.num_parking_spots * ref.country["avg_parking_space_size_m2"]
    _add_kv_table(doc, [
        ("Parking spots — policy norm", f"{results.num_parking_spots:,.0f}"),
        ("Parking spots — after carsharing", f"{results.parking_spots_after_min:,.0f} – {results.parking_spots_after_max:,.0f}"),
        ("Relative discount vs. norm", f"{results.discount_min:.1%} to {results.discount_max:.1%}"),
        ("Cars saved, net", f"{results.cars_saved_net_min:,.1f} – {results.cars_saved_net_max:,.1f}"),
        ("Average Vehicles Replaced (AVR) per shared car", f"{results.avr_min:.1f}" if abs(results.avr_min - results.avr_max) < 0.05 else f"{results.avr_min:.1f} – {results.avr_max:.1f}"),
        ("Parking space needed", f"{results.parking_space_needed_min_m2:,.0f} – {results.parking_space_needed_max_m2:,.0f} m²"),
        ("Parking space freed up", f"{m2_before - results.parking_space_needed_max_m2:,.0f} – {m2_before - results.parking_space_needed_min_m2:,.0f} m²"),
    ])
    _remark(
        doc,
        "The gap between the policy norm and the post-carsharing figure is small by design — "
        "carsharing trims the margin, it doesn't replace the norm. Read it alongside the demand "
        "range above: it's only worth banking these spots if the active-user range is realistic "
        "for this site."
    )

    # ---- 3. emissions impact ----
    _section_heading(doc, "3 · Environment", "Emissions impact")
    doc.add_paragraph(
        "Estimated yearly reduction in kg, combining (A) residents driving a shared car instead of "
        "their own car and (B) former car owners shifting some trips to public transport."
    ).runs[0].font.size = Pt(10)

    table = doc.add_table(rows=1, cols=3)
    table.style = "Light Grid Accent 1"
    hdr = table.rows[0].cells
    hdr[0].text, hdr[1].text, hdr[2].text = "Pollutant", "Min (kg/yr)", "Max (kg/yr)"
    for c in hdr:
        c.paragraphs[0].runs[0].bold = True
    for p in POLLUTANTS:
        e = results.emissions[p]
        row = table.add_row().cells
        row[0].text = p
        row[1].text = f"{e['total_min']:,.2f}"
        row[2].text = f"{e['total_max']:,.2f}"
    doc.add_paragraph()

    _add_kv_table(doc, [
        ("EU-ETS equivalent value / year", f"€{results.co2_cost_eur_min:,.0f} to €{results.co2_cost_eur_max:,.0f}"),
        ("Equivalent trees absorbing this CO₂ / year", f"{results.trees_min:,.0f} to {results.trees_max:,.0f}"),
    ])
    doc.add_paragraph()

    # ---- methodology & quirks ----
    _section_heading(doc, "Notes", "Methodology & known quirks")
    doc.add_paragraph(
        "This report is generated by a Streamlit port of a policy-support Excel model. All "
        "calculations replicate the source workbook's formulas — including the following known "
        "inconsistencies in the source file, carried over deliberately rather than 'fixed':"
    ).runs[0].font.size = Pt(9.5)
    for q in KNOWN_QUIRKS:
        b = doc.add_paragraph(style="List Bullet")
        b.add_run(q).font.size = Pt(9)

    # ---- footer ----
    footer_p = doc.add_paragraph()
    footer_p.add_run(
        "Generated by the Shared Mobility Parking & Impact Tool. Figures are estimates for policy "
        "screening, not a substitute for a detailed mobility study."
    ).font.size = Pt(8)
    footer_p.runs[0].font.color.rgb = GREY

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
