#!/usr/bin/env python3
"""
Steel Detailing Quick Reference — Excel Generator
Generates steel_detailing_reference.xlsx for shop/drafting use.
"""

import io
import math

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.drawing.image import Image as XLImage
from openpyxl.worksheet.hyperlink import Hyperlink as XLHyperlink

# ── Style constants ──────────────────────────────────────────────────────────
HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
BANNER_FILL = PatternFill("solid", fgColor="2E74B5")
ALT_FILL    = PatternFill("solid", fgColor="D9E1F2")
WHITE_FILL  = PatternFill("solid", fgColor="FFFFFF")
INPUT_FILL  = PatternFill("solid", fgColor="FFF2CC")
OUT_FILL    = PatternFill("solid", fgColor="E2EFDA")

HEADER_FONT = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
BANNER_FONT = Font(name="Calibri", bold=True, color="FFFFFF", size=12)
BODY_FONT   = Font(name="Calibri", size=10)
LABEL_FONT  = Font(name="Calibri", bold=True, size=10)
NOTE_FONT   = Font(name="Calibri", italic=True, color="595959", size=9)
OUT_FONT    = Font(name="Calibri", bold=True, size=10, color="375623")

THIN = Side(style="thin", color="AAAAAA")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT   = Alignment(horizontal="left",   vertical="center", wrap_text=True)
RIGHT  = Alignment(horizontal="right",  vertical="center")

TAB_COLORS = {
    "Shapes":        "1F4E79",
    "Plate":         "375623",
    "Pipe":          "7030A0",
    "Materials":     "843C0C",
    "Handrail":      "538135",
    "Pipe Supports": "C55A11",
    "Platforms":     "2E74B5",
}

# ── Helper functions ─────────────────────────────────────────────────────────
def banner(ws, row, text, span):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=span)
    c = ws.cell(row=row, column=1, value=text)
    c.fill = BANNER_FILL
    c.font = BANNER_FONT
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[row].height = 22
    # "← Dashboard" back button on the first banner of every non-Dashboard tab
    if row == 1 and ws.title != "Dashboard":
        btn_col = span + 2
        btn = ws.cell(row=1, column=btn_col)
        btn.value = "\u2190 Dashboard"
        _ilink(btn, "Dashboard")
        btn.fill = PatternFill("solid", fgColor="595959")
        btn.font = Font(name="Calibri", bold=True, color="FFFFFF", size=10)
        btn.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[get_column_letter(btn_col)].width = 15
    return row + 1

def headers(ws, row, labels):
    for i, t in enumerate(labels, start=1):
        c = ws.cell(row=row, column=i, value=t)
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.alignment = CENTER
        c.border = BORDER
    ws.row_dimensions[row].height = 28
    return row + 1

def data_rows(ws, start_row, rows, center_cols=None):
    center_cols = center_cols or set()
    for i, r in enumerate(rows):
        rn = start_row + i
        fill = ALT_FILL if i % 2 == 0 else WHITE_FILL
        for j, v in enumerate(r, start=1):
            c = ws.cell(row=rn, column=j, value=v)
            c.fill = fill
            c.font = BODY_FONT
            c.border = BORDER
            c.alignment = CENTER if j in center_cols else LEFT
    return start_row + len(rows)

def input_cell(ws, row, col, value):
    c = ws.cell(row=row, column=col, value=value)
    c.fill = INPUT_FILL
    c.font = Font(name="Calibri", bold=True, size=11)
    c.border = Border(
        left=Side(style="medium", color="BF8F00"),
        right=Side(style="medium", color="BF8F00"),
        top=Side(style="medium", color="BF8F00"),
        bottom=Side(style="medium", color="BF8F00"),
    )
    c.alignment = CENTER
    return c

def output_cell(ws, row, col, formula, fmt="0.00"):
    c = ws.cell(row=row, column=col, value=formula)
    c.fill = OUT_FILL
    c.font = OUT_FONT
    c.border = Border(
        left=Side(style="medium", color="375623"),
        right=Side(style="medium", color="375623"),
        top=Side(style="medium", color="375623"),
        bottom=Side(style="medium", color="375623"),
    )
    c.alignment = CENTER
    c.number_format = fmt
    return c

def label_cell(ws, row, col, text):
    c = ws.cell(row=row, column=col, value=text)
    c.font = LABEL_FONT
    c.alignment = RIGHT
    return c

def set_widths(ws, widths):
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

def add_dropdown(ws, cell_range, choices):
    formula = '"' + ",".join(choices) + '"'
    dv = DataValidation(type="list", formula1=formula, allow_blank=True, showDropDown=False)
    ws.add_data_validation(dv)
    dv.add(cell_range)

def _ilink(cell, sheet_name, cell_addr="A1"):
    """Attach an internal (same-workbook) hyperlink to a cell.
    Uses Hyperlink(location=...) so Excel writes it without an external relationship."""
    loc = f"'{sheet_name}'!{cell_addr}" if " " in sheet_name else f"{sheet_name}!{cell_addr}"
    cell.hyperlink = XLHyperlink(ref=cell.coordinate, location=loc)

# ── AISC W-Shapes ────────────────────────────────────────────────────────────
# (Designation, d, bf, tw, tf, Wt lb/ft, Area in²)
W_SHAPES = [
    ("W4x13",  4.16,  4.060, 0.280, 0.345, 13.0,  3.83),
    ("W5x16",  5.01,  5.000, 0.240, 0.360, 16.0,  4.71),
    ("W6x9",   5.90,  3.940, 0.170, 0.215,  9.0,  2.68),
    ("W6x15",  5.99,  5.990, 0.230, 0.260, 15.0,  4.43),
    ("W6x20",  6.20,  6.020, 0.260, 0.365, 20.0,  5.87),
    ("W8x10",  7.89,  3.940, 0.170, 0.205, 10.0,  2.96),
    ("W8x18",  8.14,  5.250, 0.230, 0.330, 18.0,  5.26),
    ("W8x24",  7.93,  6.495, 0.245, 0.400, 24.0,  7.08),
    ("W8x31",  8.00,  7.995, 0.285, 0.435, 31.0,  9.13),
    ("W10x22", 10.17, 5.750, 0.240, 0.360, 22.0,  6.49),
    ("W10x33",  9.73, 7.960, 0.290, 0.435, 33.0,  9.71),
    ("W10x49", 10.00,10.000, 0.340, 0.560, 49.0, 14.4),
    ("W12x16", 11.99, 3.990, 0.220, 0.265, 16.0,  4.71),
    ("W12x26", 12.22, 6.490, 0.230, 0.380, 26.0,  7.65),
    ("W12x40", 11.94, 8.010, 0.295, 0.515, 40.0, 11.8),
    ("W12x53", 12.06, 9.995, 0.345, 0.575, 53.0, 15.6),
    ("W12x72", 12.25,12.040, 0.430, 0.670, 72.0, 21.1),
    ("W12x96", 12.71,12.160, 0.550, 0.900, 96.0, 28.2),
    ("W14x22", 13.74, 5.000, 0.230, 0.335, 22.0,  6.49),
    ("W14x38", 14.10, 6.770, 0.310, 0.515, 38.0, 11.2),
    ("W14x53", 13.92, 8.060, 0.370, 0.660, 53.0, 15.6),
    ("W16x26", 15.69, 5.500, 0.250, 0.345, 26.0,  7.68),
    ("W16x36", 15.86, 6.985, 0.295, 0.430, 36.0, 10.6),
    ("W18x35", 17.70, 6.000, 0.300, 0.425, 35.0, 10.3),
    ("W18x46", 18.06, 6.060, 0.360, 0.605, 46.0, 13.5),
    ("W21x44", 20.66, 6.500, 0.350, 0.530, 44.0, 13.0),
    ("W21x57", 21.06, 6.555, 0.405, 0.650, 57.0, 16.7),
    ("W21x68", 21.13, 8.270, 0.430, 0.685, 68.0, 20.0),
    ("W24x55", 23.57, 7.005, 0.395, 0.505, 55.0, 16.2),
    ("W24x76", 23.92, 8.990, 0.440, 0.680, 76.0, 22.4),
    ("W24x94", 24.31, 9.065, 0.515, 0.875, 94.0, 27.7),
    ("W27x84", 26.71, 9.960, 0.460, 0.640, 84.0, 24.8),
    ("W27x94", 26.92,10.010, 0.490, 0.745, 94.0, 27.7),
    ("W30x90", 29.53,10.400, 0.470, 0.610, 90.0, 26.3),
    ("W30x108",29.83,10.475, 0.545, 0.760,108.0, 31.7),
    ("W33x118",32.86,11.480, 0.550, 0.740,118.0, 34.7),
    ("W33x141",33.30,11.535, 0.605, 0.960,141.0, 41.6),
    ("W36x135",35.55,11.950, 0.600, 0.790,135.0, 39.7),
    ("W36x160",36.01,12.000, 0.650, 1.020,160.0, 47.0),
]

C_SHAPES = [
    ("C3x4.1",    3.00, 1.410, 0.170, 0.273,  4.1,  1.21),
    ("C4x5.4",    4.00, 1.580, 0.184, 0.296,  5.4,  1.59),
    ("C5x6.7",    5.00, 1.750, 0.190, 0.320,  6.7,  1.97),
    ("C6x8.2",    6.00, 1.920, 0.200, 0.343,  8.2,  2.40),
    ("C6x10.5",   6.00, 2.034, 0.314, 0.343, 10.5,  3.09),
    ("C7x9.8",    7.00, 2.090, 0.210, 0.366,  9.8,  2.87),
    ("C8x11.5",   8.00, 2.260, 0.220, 0.390, 11.5,  3.38),
    ("C8x13.75",  8.00, 2.343, 0.303, 0.390, 13.75, 4.04),
    ("C9x15",     9.00, 2.485, 0.285, 0.413, 15.0,  4.41),
    ("C10x15.3", 10.00, 2.600, 0.240, 0.436, 15.3,  4.49),
    ("C10x20",   10.00, 2.739, 0.379, 0.436, 20.0,  5.88),
    ("C12x20.7", 12.00, 2.942, 0.282, 0.501, 20.7,  6.09),
    ("C12x25",   12.00, 3.047, 0.387, 0.501, 25.0,  7.35),
    ("C15x33.9", 15.00, 3.400, 0.400, 0.650, 33.9,  9.96),
    ("C15x50",   15.00, 3.716, 0.716, 0.650, 50.0, 14.7),
]

# (Designation, Leg A, Leg B, Thickness, Wt lb/ft, Area in²)
ANGLES = [
    ("L2x2x1/4",    2.0, 2.0, 0.250,  3.19, 0.938),
    ("L2x2x3/8",    2.0, 2.0, 0.375,  4.70, 1.36),
    ("L2.5x2.5x1/4",2.5, 2.5, 0.250,  4.10, 1.19),
    ("L3x3x3/16",   3.0, 3.0, 0.1875, 3.71, 1.09),
    ("L3x3x1/4",    3.0, 3.0, 0.250,  4.90, 1.44),
    ("L3x3x3/8",    3.0, 3.0, 0.375,  7.20, 2.11),
    ("L3x3x1/2",    3.0, 3.0, 0.500,  9.40, 2.75),
    ("L4x4x1/4",    4.0, 4.0, 0.250,  6.60, 1.94),
    ("L4x4x3/8",    4.0, 4.0, 0.375,  9.80, 2.86),
    ("L4x4x1/2",    4.0, 4.0, 0.500, 12.80, 3.75),
    ("L5x5x3/8",    5.0, 5.0, 0.375, 12.30, 3.61),
    ("L5x5x1/2",    5.0, 5.0, 0.500, 16.20, 4.75),
    ("L6x6x3/8",    6.0, 6.0, 0.375, 14.90, 4.36),
    ("L6x6x1/2",    6.0, 6.0, 0.500, 19.60, 5.75),
    ("L3x2x1/4",    3.0, 2.0, 0.250,  3.92, 1.15),
    ("L4x3x1/4",    4.0, 3.0, 0.250,  5.80, 1.69),
    ("L4x3x3/8",    4.0, 3.0, 0.375,  8.50, 2.48),
    ("L5x3x1/4",    5.0, 3.0, 0.250,  6.60, 1.94),
    ("L6x4x3/8",    6.0, 4.0, 0.375, 12.30, 3.61),
    ("L6x4x1/2",    6.0, 4.0, 0.500, 16.20, 4.75),
]

# (Designation, H, B, Wall t, Wt lb/ft, Area in²)
HSS_SHAPES = [
    ("HSS2x2x3/16",  2.0, 2.0, 0.174,  4.32,  1.27),
    ("HSS2x2x1/4",   2.0, 2.0, 0.233,  5.41,  1.59),
    ("HSS3x3x3/16",  3.0, 3.0, 0.174,  6.87,  2.02),
    ("HSS3x3x1/4",   3.0, 3.0, 0.233,  8.81,  2.59),
    ("HSS4x4x1/4",   4.0, 4.0, 0.233, 12.20,  3.59),
    ("HSS4x4x3/8",   4.0, 4.0, 0.349, 17.30,  5.08),
    ("HSS4x4x1/2",   4.0, 4.0, 0.465, 22.40,  6.59),
    ("HSS5x5x1/4",   5.0, 5.0, 0.233, 15.60,  4.59),
    ("HSS5x5x3/8",   5.0, 5.0, 0.349, 22.40,  6.58),
    ("HSS6x6x1/4",   6.0, 6.0, 0.233, 19.00,  5.59),
    ("HSS6x6x3/8",   6.0, 6.0, 0.349, 27.50,  8.08),
    ("HSS6x6x1/2",   6.0, 6.0, 0.465, 35.10, 10.30),
    ("HSS8x8x3/8",   8.0, 8.0, 0.349, 37.70, 11.10),
    ("HSS8x8x1/2",   8.0, 8.0, 0.465, 48.90, 14.40),
    ("HSS4x2x3/16",  4.0, 2.0, 0.174,  5.59,  1.64),
    ("HSS4x3x1/4",   4.0, 3.0, 0.233, 10.50,  3.09),
    ("HSS6x4x1/4",   6.0, 4.0, 0.233, 15.60,  4.59),
    ("HSS6x4x3/8",   6.0, 4.0, 0.349, 22.40,  6.59),
    ("HSS8x4x3/8",   8.0, 4.0, 0.349, 27.50,  8.08),
    ("HSS8x6x3/8",   8.0, 6.0, 0.349, 32.60,  9.59),
]

# (NPS, OD, SCH40 wall, SCH40 ID, SCH40 wt, SCH80 wall, SCH80 ID, SCH80 wt, Material, Notes)
PIPE_DATA = [
    ("1/2",   0.840, 0.109, 0.622,  0.85, 0.147, 0.546,  1.09, "A53-B / A106-B", ""),
    ("3/4",   1.050, 0.113, 0.824,  1.13, 0.154, 0.742,  1.47, "A53-B / A106-B", ""),
    ("1",     1.315, 0.133, 1.049,  1.68, 0.179, 0.957,  2.17, "A53-B / A106-B", ""),
    ("1-1/4", 1.660, 0.140, 1.380,  2.27, 0.191, 1.278,  3.00, "A53-B / A106-B", ""),
    ("1-1/2", 1.900, 0.145, 1.610,  2.72, 0.200, 1.500,  3.63, "A53-B / A106-B", "Common handrail"),
    ("2",     2.375, 0.154, 2.067,  3.65, 0.218, 1.939,  5.02, "A53-B / A106-B", "Common support"),
    ("2-1/2", 2.875, 0.203, 2.469,  5.79, 0.276, 2.323,  7.66, "A53-B / A106-B", ""),
    ("3",     3.500, 0.216, 3.068,  7.58, 0.300, 2.900, 10.25, "A53-B / A106-B", ""),
    ("3-1/2", 4.000, 0.226, 3.548,  9.11, 0.318, 3.364, 12.50, "A53-B / A106-B", ""),
    ("4",     4.500, 0.237, 4.026, 10.79, 0.337, 3.826, 14.98, "A53-B / A106-B", ""),
    ("5",     5.563, 0.258, 5.047, 14.62, 0.375, 4.813, 20.78, "A53-B / A106-B", ""),
    ("6",     6.625, 0.280, 6.065, 18.97, 0.432, 5.761, 28.57, "A53-B / A106-B", ""),
    ("8",     8.625, 0.322, 7.981, 28.55, 0.500, 7.625, 43.39, "A53-B / A106-B", ""),
    ("10",   10.750, 0.365,10.020, 40.48, 0.500, 9.750, 54.74, "A53-B / A106-B", ""),
    ("12",   12.750, 0.406,11.938, 53.52, 0.500,11.750, 65.42, "A53-B / A106-B", ""),
]

# (Fraction, Decimal, Wt/sq ft, Stock sizes)
PLATE_THK = [
    ("3/16",  0.1875,  7.65,  "48x96, 60x120"),
    ("1/4",   0.250,  10.20,  "48x96, 60x120, 72x120"),
    ("5/16",  0.3125, 12.75,  "48x96, 60x120"),
    ("3/8",   0.375,  15.30,  "48x96, 60x120, 72x120"),
    ("1/2",   0.500,  20.40,  "48x96, 60x120, 72x144"),
    ("5/8",   0.625,  25.50,  "48x96, 60x120"),
    ("3/4",   0.750,  30.60,  "48x96, 60x120, 72x120"),
    ("1",     1.000,  40.80,  "48x96, 60x120"),
    ("1-1/4", 1.250,  51.00,  "48x96, 60x120"),
    ("1-1/2", 1.500,  61.20,  "48x96, 60x120"),
    ("2",     2.000,  81.60,  "48x96, 60x96"),
]

# (Size, Width in, Thickness in, Wt lb/ft)
FLAT_BARS = [
    ("1 x 1/4",      1.0, 0.250,  0.85),
    ("1 x 3/8",      1.0, 0.375,  1.28),
    ("1 x 1/2",      1.0, 0.500,  1.70),
    ("1-1/2 x 1/4",  1.5, 0.250,  1.28),
    ("1-1/2 x 3/8",  1.5, 0.375,  1.91),
    ("1-1/2 x 1/2",  1.5, 0.500,  2.55),
    ("2 x 1/4",      2.0, 0.250,  1.70),
    ("2 x 3/8",      2.0, 0.375,  2.55),
    ("2 x 1/2",      2.0, 0.500,  3.40),
    ("2 x 3/4",      2.0, 0.750,  5.10),
    ("2-1/2 x 1/4",  2.5, 0.250,  2.13),
    ("2-1/2 x 3/8",  2.5, 0.375,  3.19),
    ("2-1/2 x 1/2",  2.5, 0.500,  4.25),
    ("3 x 1/4",      3.0, 0.250,  2.55),
    ("3 x 3/8",      3.0, 0.375,  3.83),
    ("3 x 1/2",      3.0, 0.500,  5.10),
    ("3 x 3/4",      3.0, 0.750,  7.65),
    ("4 x 1/4",      4.0, 0.250,  3.40),
    ("4 x 3/8",      4.0, 0.375,  5.10),
    ("4 x 1/2",      4.0, 0.500,  6.80),
    ("4 x 3/4",      4.0, 0.750, 10.20),
    ("4 x 1",        4.0, 1.000, 13.60),
    ("6 x 1/2",      6.0, 0.500, 10.20),
    ("6 x 3/4",      6.0, 0.750, 15.30),
    ("6 x 1",        6.0, 1.000, 20.40),
]

# (Grade, Fy, Fu, Typical Use, Weldability, Notes)
MATERIALS = [
    ("A36",       "36",   "58-80", "Plates, angles, channels, misc steel",  "Good",  "E70xx; most common general grade"),
    ("A572 Gr50", "50",   "65",    "W-shapes, beams, columns",              "Good",  "E70xx; higher strength than A36"),
    ("A992",      "50+",  "65",    "W-shapes (modern standard)",            "Good",  "Max Fy/Fu = 0.85; preferred for W-shapes"),
    ("A500 Gr B", "46",   "58",    "HSS rectangular/square",                "Good",  "E70xx; check heat properties"),
    ("A500 Gr C", "50",   "62",    "HSS rectangular/square",                "Good",  "Higher strength HSS option"),
    ("A53-B",     "35",   "60",    "Structural pipe",                        "Fair",  "Preheat for heavy walls; E7018"),
    ("A106-B",    "35",   "60",    "High-temp service pipe",                 "Fair",  "Common in O&G process piping; E7018"),
    ("A108",      "Var.", "Var.",  "Bolts, studs, shafting",                "N/A",   "Not for primary structural welding"),
]

# (Electrode, Min Tensile ksi, Process, Use, Notes)
ELECTRODES = [
    ("E7018",   "70", "SMAW (Stick)", "Primary structural; low hydrogen",   "Preferred for A53/A106 pipe"),
    ("E70XX",   "70", "SMAW (Stick)", "General structural fillet/groove",    "Matches A36/A572/A992"),
    ("E6010",   "62", "SMAW (Stick)", "Root pass, field welding",            "DC+; burns through rust/scale"),
    ("E6013",   "62", "SMAW (Stick)", "Light fab, sheet metal",              "AC or DC; easy for beginners"),
    ("ER70S-6", "70", "GMAW (MIG)",   "Shop fillet welds, general fab",      "CO2 or 75/25 Ar/CO2 gas"),
    ("E71T-1",  "70", "FCAW",         "High-production fillet welds",        "CO2 shielding; fast deposition"),
]

# (Item, Value, Reference)
HANDRAIL_SPECS = [
    ("Top Rail Height",       '42" nominal (min 42")',   "OSHA 1910.29"),
    ("Mid Rail Height",       '21" (midpoint)',          "Required when opening > 19\""),
    ("Toeboard Height",       '3-1/2" min',              "Prevents tools/objects from rolling off"),
    ("Max Post Spacing",      "8'-0\" typical",          "Check project spec"),
    ("Top Rail Min Strength", "200 lbs",                  "OSHA load requirement"),
    ("Mid Rail Min Strength", "150 lbs",                  "OSHA load requirement"),
    ("Gate Opening Clear",    "22\" min",                 "Self-closing at stair openings"),
]

# (Component, Mat'l Opt 1, Mat'l Opt 2, Typical Size, Notes)
HANDRAIL_COMPONENTS = [
    ("Top Rail",      "Pipe",      "Angle",    "1-1/2\" SCH 40 / L1.5x1.5x3/16", "1.5\" pipe OD = 1.900\""),
    ("Mid Rail",      "Pipe",      "Angle",    "1-1/2\" SCH 40 / L1.5x1.5x3/16", "Same as top rail"),
    ("Post",          "Pipe",      "Sq. Tube", "1-1/2\" SCH 40 / HSS2x2x3/16",   "Weld to base plate"),
    ("Base Plate",    "A36 Plate", "",         "4\"x4\"x3/8\" typical",           "2x 1/2\" dia anchor bolts"),
    ("Kickplate",     "Flat Bar",  "Plate",    "1/4\" x 4\" Flat Bar",            "Tack both edges"),
    ("Return End",    "Pipe",      "",         "180° return, same size",          "Or cap plate w/ nosing"),
    ("Gate Post",     "Sq. Tube",  "",         "HSS2x2x1/4",                      "Heavier to handle gate load"),
]

# (Type, Description, Pipe Range, Base Plate, Material, Notes)
PIPE_SUPPORTS = [
    ("Dummy Leg / Shoe",  "Welded to pipe; sits on structure",       "2\"-24\"", "6x6x1/2 min",  "A36",      "Most common O&G support"),
    ("Guide",             "Allows axial travel; restricts lateral",  "2\"-24\"", "6x8x1/2",      "A36",      "Gap = OD + 1/2\" typ"),
    ("Anchor (Fixed)",    "Fully fixed — all loads/moments",         "2\"-16\"", "10x10x3/4",    "A36",      "Gussets usually required"),
    ("Rod Hanger",        "Threaded rod from above",                  "1/2\"-12\"","N/A",          "A307/A36", "Check engagement length"),
    ("U-Bolt",            "Bolted clamp; wraps pipe",                "1\"-12\"", "N/A",           "A36/SS",   "Order by pipe NPS"),
    ("Pipe Clamp",        "Bolted clamshell; MSS SP-58",             "1/2\"-36\"","N/A",          "A36/SS",   "Type 1/4/24/36 common"),
    ("Spring Hanger",     "Variable/constant-effort spring",         "Per mfr",  "N/A",           "Mfr std",  "Specify load, travel"),
    ("Saddle",            "Supports insulated pipe from below",      "2\"-24\"", "Per design",    "A36",      "Insulation insert required"),
    ("Trunnion",          "Large pipe; pin-mounted to structure",    "12\"-48\"","Heavy plate",  "A36",      "Requires stress analysis"),
]

# (NPS, OD, Shoe Height, BP W, BP L, BP T, Stiffener)
SHOE_SIZING = [
    ("2",   2.375,  "6\"",   "5\"",  "6\"",  "3/8\"", "No"),
    ("3",   3.500,  "6\"",   "6\"",  "7\"",  "3/8\"", "No"),
    ("4",   4.500,  "6\"",   "7\"",  "8\"",  "3/8\"", "No"),
    ("6",   6.625,  "6\"",   "8\"", "10\"",  "1/2\"", "Consult"),
    ("8",   8.625,  "8\"",  "10\"", "12\"",  "1/2\"", "Yes"),
    ("10", 10.750,  "8\"",  "12\"", "14\"",  "1/2\"", "Yes"),
    ("12", 12.750,  "8\"",  "12\"", "14\"",  "3/4\"", "Yes"),
    ("14", 14.000, "10\"",  "14\"", "16\"",  "3/4\"", "Yes"),
    ("16", 16.000, "10\"",  "16\"", "18\"",  "3/4\"", "Yes"),
]

# (Type, Designation, Bar Size, Panel Sizes, Wt psf, Notes)
GRATING = [
    ("Bar Grating (welded)", "19-W-4",    "1-3/16\" x 3/16\"", "24\"/36\"/48\" wide, up to 20'", 11.0, "Most common O&G spec"),
    ("Bar Grating (welded)", "15-W-4",    "15/16\" x 3/16\"",  "24\"/36\"/48\" wide",             9.0, "Lighter applications"),
    ("Bar Grating (swaged)", "19-W-4",    "1-3/16\" x 3/16\"", "24\"/36\"/48\" wide",            11.0, "No welds; cold-locked"),
    ("Checkered Plate",      "3/16\"",    "N/A",                "48x96, 60x120",                   8.25, "Verify pattern add'l wt"),
    ("Checkered Plate",      "1/4\"",     "N/A",                "48x96, 60x120",                  10.6,  ""),
    ("Checkered Plate",      "3/8\"",     "N/A",                "48x96, 60x120",                  15.6,  "Heavy traffic"),
]

# (Member, Typical Size, Material, Max Span, Notes)
PLATFORM_MEMBERS = [
    ("Floor Beam",     "W8x18 or W8x24",          "A992/A572", "12-16 ft",  "Typical for 50 psf"),
    ("Header / Rim",   "W10x22 or C10x20",        "A992/A572", "Varies",    "Perimeter support"),
    ("Knee Brace",     "L3x3x3/8 or HSS3x3x3/16", "A36/A500",  "N/A",       "45° typical"),
    ("Column",         "HSS4x4x1/4 or W6x15",     "A500/A992", "10-16 H",   "Base plate required"),
    ("Handrail Post",  "1-1/2\" SCH 40 Pipe",     "A53-B",     "8'-0\" max", "42\" above FF"),
    ("Stair Stringer", "C10x20 or C12x20.7",      "A36/A572",  "Varies",    "Slope per design"),
    ("Gusset Plate",   "3/8\" plate typical",     "A36",        "N/A",       "Size per loading"),
]

# (Item, Value, Notes)
PLATFORM_NOTES = [
    ("Design Live Load",      "50 psf typical",         "ASCE 7 minimum"),
    ("Grating Direction",     "Perp. to floor beams",   "Bearing bar across span"),
    ("Grating Fasteners",     "Saddle clips 24\" o.c.", "4 clips min per panel edge"),
    ("Drain Hole",            "1\" dia per 100 sq ft",  "At low point"),
    ("Stair Width Min",       "22\" clear",             "36\" preferred for O&G"),
    ("Tread Depth",           "11\" min",               "Nosing included"),
    ("Riser Height",          "7\" max",                "Uniform for full flight"),
    ("Nosing",                "L1.25x1.25x1/8 angle",   "Tack weld both legs"),
    ("Safety Yellow Paint",   "All leading edges",      "Kickplates, nosings"),
    ("Overhead Clearance",    "7'-0\" min",             "OSHA walkway"),
]

# ── Weld data (AWS D1.1) ─────────────────────────────────────────────────────
MIN_FILLET = [
    ("To 1/4\" incl.",       "1/8\"",  "Do not weld thinner than 1/8\""),
    ("Over 1/4\" to 1/2\"",  "3/16\"", "Most common shop minimum"),
    ("Over 1/2\" to 3/4\"",  "1/4\"",  ""),
    ("Over 3/4\"",           "5/16\"", "Minimum for heavy plate"),
]
MAX_FILLET_PASS = [
    ("Flat / Horizontal",   "5/16\"", "AWS D1.1 limit per pass"),
    ("Vertical",            "1/4\"",  ""),
    ("Overhead",            "1/4\"",  ""),
]
MAX_FILLET_EDGE = [
    ("< 1/4\" thick edge",  "= plate thickness",       "Full-thickness weld allowed"),
    (">= 1/4\" thick edge", "= plate thickness - 1/16\"","Must leave 1/16\" land"),
]
PREQUALIFIED_JOINTS = [
    ("Square Groove, no gap",  "B-L1a",  "0",       "—",   "t <= 5/16\" SMAW; <= 3/8\" SAW"),
    ("Square Groove, w/ gap",  "B-L1b",  "1/4\" max","—",  "Both sides or back-gouge"),
    ("Single-V, 60°",          "B-U1a",  "0–1/4\"", "60°", "Most common groove weld"),
    ("Single-Bevel, 45°",      "B-U2",   "0–1/8\"", "45°", "One-sided access joints"),
    ("Single-V, 45°",          "B-U1",   "0–1/8\"", "45°", ""),
    ("Double-V, 60°",          "B-U1b",  "0–1/8\"", "60°", "Both sides; balanced distortion"),
]
ELECTRODE_MATCH = [
    ("A36",     "58",  "E70xx",  "Overmatch is fine and common"),
    ("A572 Gr50","65", "E70xx",  "70 ksi filler satisfies 65 ksi base"),
    ("A992",    "65",  "E70xx",  "Same as A572 Gr50 in practice"),
    ("A500 B/C","58",  "E70xx",  "E7018 preferred for thicker walls"),
    ("A53-B",   "60",  "E70xx",  "E7018 (low hydrogen) per most WPS"),
    ("A106-B",  "60",  "E7018",  "Preheat per AWS D1.1 when t > 1\""),
]

# ── References data ───────────────────────────────────────────────────────────
REFERENCES = [
    # (Standard, Full Title, Section Used, What It Covers, Access, URL)
    ("AISC SCM 16th Ed",
     "Steel Construction Manual, 16th Edition",
     "Part 1 — Section Tables",
     "W/C/Angle/HSS/Pipe properties; connection design",
     "Free (login req.)",
     "https://www.aisc.org/steel-construction-manual-16th-ed"),

    ("AISC Table J3.3",
     "SCM Table J3.3 — Bolt Hole Sizes",
     "Bolts tab",
     "STD, OVS, SSLOT, LSLOT hole dimensions for all bolt diameters",
     "Free (login req.)",
     "https://www.aisc.org/steel-construction-manual-16th-ed"),

    ("AISC Table J3.4",
     "SCM Table J3.4 — Minimum Edge Distances",
     "Bolts tab",
     "Min edge distance from bolt center to edge of connected part",
     "Free (login req.)",
     "https://www.aisc.org/steel-construction-manual-16th-ed"),

    ("AWS D1.1",
     "Structural Welding Code — Steel",
     "Welds tab",
     "Prequalified joints, fillet weld sizes, electrode matching, preheat",
     "Purchase required",
     "https://www.aws.org/standards/details/d1-1-structural-welding-code-steel"),

    ("ASME B36.10M",
     "Welded and Seamless Wrought Steel Pipe",
     "Pipe tab",
     "Pipe OD, wall thickness, ID, weight for all NPS sizes and schedules",
     "Purchase required",
     "https://www.asme.org/codes-standards/find-codes-standards/b36-10m-welded-seamless-wrought-steel-pipe"),

    ("OSHA 1910.29",
     "Fall Protection Systems — Walking-Working Surfaces",
     "Handrail tab",
     "42\" top rail, 21\" mid rail, 200 lb strength, toeboard requirements",
     "FREE",
     "https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.29"),

    ("OSHA 1926.502",
     "Fall Protection Systems — Construction",
     "Handrail tab",
     "Construction site fall protection; same rail heights as 1910.29",
     "FREE",
     "https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.502"),

    ("ASCE 7-22",
     "Minimum Design Loads and Associated Criteria",
     "Platforms tab",
     "Live loads: 50 psf industrial platform, 40 psf maintenance only",
     "Purchase required",
     "https://www.asce.org/publications-and-news/asce-7"),

    ("ASTM A36",
     "Standard Spec for Carbon Structural Steel",
     "Materials tab",
     "Fy=36 ksi, Fu=58-80 ksi; plates, shapes, bars",
     "Purchase required",
     "https://www.astm.org/a0036_a0036m-19.html"),

    ("ASTM A572",
     "HSLA Structural Steel (Gr 42/50/55/60/65)",
     "Materials tab",
     "Gr50: Fy=50, Fu=65; W-shapes, beams, columns",
     "Purchase required",
     "https://www.astm.org/a0572_a0572m-21e01.html"),

    ("ASTM A992",
     "Structural Steel Shapes — W-Shapes",
     "Materials tab",
     "Fy=50 min, Fu=65; Fy/Fu <= 0.85; current standard for W-shapes",
     "Purchase required",
     "https://www.astm.org/a0992_a0992m-11r22.html"),

    ("ASTM A500",
     "Cold-Formed Welded/Seamless Structural Tubing",
     "Materials tab",
     "Gr B: Fy=46, Fu=58; Gr C: Fy=50, Fu=62; square/rect HSS",
     "Purchase required",
     "https://www.astm.org/a0500_a0500m-21.html"),

    ("ASTM A53",
     "Pipe, Steel, Black and Hot-Dipped",
     "Pipe & Materials tabs",
     "Gr B: Fy=35, Fu=60; ERW or seamless; structural pipe",
     "Purchase required",
     "https://www.astm.org/a0053_a0053m-22.html"),

    ("ASTM A106",
     "Seamless Carbon Steel Pipe for High-Temp Service",
     "Pipe & Materials tabs",
     "Gr B: Fy=35, Fu=60; seamless only; process/pressure piping",
     "Purchase required",
     "https://www.astm.org/a0106_a0106m-19a.html"),

    ("ASTM F3125 (A325/A490)",
     "High Strength Structural Bolts (supersedes A325/A490)",
     "Bolts tab",
     "Gr A325: Fy=92, Fu=120; Gr A490: Fy=130, Fu=150",
     "Purchase required",
     "https://www.astm.org/f3125_f3125m-21.html"),

    ("ASTM F1554",
     "Anchor Bolts, Steel, 36/55/105 ksi Yield",
     "Bolts tab",
     "Anchor rods for base plates; Gr36 is weldable",
     "Purchase required",
     "https://www.astm.org/f1554-15r20.html"),

    ("ASTM A307",
     "Carbon Steel Bolts, Studs — 60 ksi",
     "Bolts tab",
     "Low-strength; non-structural connections, anchor bolts",
     "Purchase required",
     "https://www.astm.org/a0307-14r21.html"),

    ("MSS SP-58",
     "Pipe Hangers and Supports — Materials/Design",
     "Pipe Supports tab",
     "Types 1-42 pipe clamp/support configurations",
     "Purchase required",
     "https://www.mss-hq.org/Store/ProductDetails/tabid/193/ProductID/116/Default.aspx"),
]

# (Bolt, Grade, Fy ksi, Fu ksi, Shear ksi, Tension ksi, Notes)
BOLT_GRADES = [
    ("A307",    "Low carbon", "N/A", "60",  "27.0", "45.0", "Non-structural; anchor bolts, light connections"),
    ("A325",    "Med carbon", "92", "120", "54.0", "90.0",  "Standard structural bolt; most common"),
    ("A490",    "Alloy steel","130","150", "67.5","112.5",  "High-strength; heavier connections"),
    ("F1554 Gr36","Low carbon","36",  "58", "N/A",  "N/A",  "Anchor rods; weldable"),
    ("F1554 Gr55","Med carbon","55",  "75", "N/A",  "N/A",  "Anchor rods; higher strength"),
    ("F1554 Gr105","Alloy",   "105","125", "N/A",  "N/A",  "Anchor rods; heavy equipment"),
    ("A36 Threaded","Low carbon","36","58","N/A",   "N/A",  "All-thread rod; misc bracing/hangers"),
]

# (Bolt Dia, STD Hole, OVS Hole, SSLOT W, SSLOT L, LSLOT W, LSLOT L)
HOLE_SIZES = [
    ('1/2"',  '9/16"',  '5/8"',  '9/16"',  '11/16"', '9/16"',  '1-1/4"'),
    ('5/8"',  '11/16"', '13/16"','11/16"', '7/8"',   '11/16"', '1-9/16"'),
    ('3/4"',  '13/16"', '15/16"','13/16"', '1"',     '13/16"', '1-7/8"'),
    ('7/8"',  '15/16"', '1-1/16"','15/16"','1-1/8"', '15/16"', '2-3/16"'),
    ('1"',    '1-1/16"','1-1/4"','1-1/16"','1-5/16"','1-1/16"','2-1/2"'),
    ('1-1/8"','1-3/16"','1-3/8"','1-3/16"','1-7/16"','1-3/16"','2-13/16"'),
    ('1-1/4"','1-5/16"','1-1/2"','1-5/16"','1-9/16"','1-5/16"','3-1/8"'),
]

# (Bolt Dia, Min Edge Dist (sheared), Min Edge Dist (rolled/saw), Min Spacing)
BOLT_SPACING = [
    ('1/2"',  '7/8"',  '3/4"',  '1-1/2"'),
    ('5/8"',  '1-1/8"','7/8"',  '1-7/8"'),
    ('3/4"',  '1-1/4"','1"',    '2-1/4"'),
    ('7/8"',  '1-1/2"','1-1/8"','2-5/8"'),
    ('1"',    '1-3/4"','1-1/4"','3"'),
    ('1-1/8"','2"',    '1-1/2"','3-3/8"'),
    ('1-1/4"','2-1/4"','1-5/8"','3-3/4"'),
]

# (Bolt Dia, SCH 40 Pipe thk, Plate thk range, Torque ft-lbs A325, Torque ft-lbs A490)
BOLT_TORQUE = [
    ('1/2"',  "—", "3/16\" – 1\"", "85",  "107"),
    ('5/8"',  "—", "3/16\" – 1\"", "170", "212"),
    ('3/4"',  "—", "1/4\" – 1-1/2\"", "300", "375"),
    ('7/8"',  "—", "1/4\" – 2\"", "490", "612"),
    ('1"',    "—", "1/4\" – 2\"", "730", "912"),
    ('1-1/8"',"—", "3/8\" – 2\"", "1050","1312"),
    ('1-1/4"',"—", "3/8\" – 2\"", "1460","1825"),
]

# ── Bending / bend allowance data ────────────────────────────────────────────
# K-factor: portion of thickness at neutral axis
# 0.33 = sharp bend (t/R > 1), 0.41 = air bend typical, 0.50 = radius bend
KFACTOR_TABLE = [
    ("Sharp bend  (inside R < thickness)",    "0.33", "Tightest bend; expect more springback"),
    ("Standard air bend  (R ≈ thickness)",    "0.41", "Most common shop bending"),
    ("Radius bend  (R = 2–4× thickness)",     "0.45", "Smoother; less distortion"),
    ("Large radius  (R > 4× thickness)",      "0.50", "Near-neutral axis; minimal thinning"),
]
MIN_BEND_RADIUS = [
    # (Material, Grade, Min R as multiple of t)
    ("A36 Plate",        "A36",      "1.0t",  "Across grain; 1.5t with grain"),
    ("A572 Gr50 Plate",  "A572",     "1.5t",  "Higher strength = less ductility"),
    ("A500 HSS",         "A500 B/C", "N/A",   "Do not cold bend HSS in field"),
    ("A53 Pipe",         "A53-B",    "3D min","D = pipe OD; check wall thickness"),
    ("Flat bar A36",     "A36",      "1.0t",  "Hot-roll; consult fabricator for CRS"),
]

# ── Bending diagram (matplotlib) ─────────────────────────────────────────────
def generate_bend_diagram():
    """Create a 2-panel reference diagram for the Bending Calculator tab.
    Returns a BytesIO PNG buffer, or None if matplotlib is unavailable."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Polygon as MplPoly, Rectangle, FancyArrowPatch
    except ImportError:
        return None

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.patch.set_facecolor("#EEF2F7")

    # ── Panel 1: Side view of bent plate ──────────────────────────────────
    ax1.set_aspect("equal")
    ax1.set_facecolor("#EEF2F7")
    ax1.set_xlim(-1.8, 4.2)
    ax1.set_ylim(-1.8, 4.2)
    ax1.axis("off")
    ax1.set_title("Bend Geometry (Side View)", fontweight="bold", fontsize=12,
                  color="#1F4E79", pad=8)

    Ri  = 0.5   # inside bend radius (visual units)
    t   = 0.28  # plate thickness (visual)
    Ro  = Ri + t
    Rn  = Ri + 0.41 * t   # neutral axis (K = 0.41)
    L   = 2.2   # leg length (visual)
    N   = 30    # arc resolution

    thetas = [math.radians(i * 90 / N) for i in range(N + 1)]  # 0° → 90°
    inner_arc = [(Ri * math.cos(a), Ri * math.sin(a)) for a in thetas]
    outer_arc = [(Ro * math.cos(a), Ro * math.sin(a)) for a in thetas]

    # Plate polygon (clockwise from top-left of leg1):
    # outer leg1 | inner leg1 | inner arc | inner leg2 | outer leg2 |
    # small connector | outer arc (reversed) | small connector
    poly = (
        [(-t, Ro + L), (0, Ro + L)]        # top of leg1 (outer → inner)
        + [(0, Ri)]                          # down inner leg1 to arc start
        + inner_arc[1:-1]                    # inner arc
        + [(Ri, 0), (Ri + L, 0)]            # inner leg2
        + [(Ri + L, -t), (Ro, -t), (Ro, 0)] # outer leg2 + connector
        + list(reversed(outer_arc[1:-1]))    # outer arc (0° → 90°, reversed)
        + [(0, Ro), (-t, Ro), (-t, Ro + L)] # connector + close
    )

    plate = MplPoly(poly, closed=True, facecolor="#2E74B5",
                    edgecolor="#1F4E79", linewidth=1.8, alpha=0.88, zorder=2)
    ax1.add_patch(plate)

    # Neutral axis arc (dashed gold)
    na_x = [Rn * math.cos(a) for a in thetas]
    na_y = [Rn * math.sin(a) for a in thetas]
    ax1.plot(na_x, na_y, color="#FFC000", linewidth=1.8, linestyle="--",
             zorder=3, label="Neutral axis (K·t from inside)")

    # ── Dimension annotations ──

    # Thickness "t" — horizontal arrow on top of leg1
    y_t = Ro + L - 0.4
    ax1.annotate("", xy=(-t, y_t), xytext=(0, y_t),
                 arrowprops=dict(arrowstyle="<->", color="#1F1F1F", lw=1.2), zorder=4)
    ax1.text(-t / 2, y_t + 0.06, "t", ha="center", va="bottom",
             fontsize=11, fontweight="bold", zorder=4)

    # Inside radius "R" — diagonal arrow from center to arc mid-point
    mid_a = math.radians(45)
    ax1.annotate("", xy=(Ri * math.cos(mid_a), Ri * math.sin(mid_a)), xytext=(0, 0),
                 arrowprops=dict(arrowstyle="-|>", color="#C00000", lw=1.6), zorder=4)
    ax1.text(0.05, 0.18, "R", ha="left", va="bottom", fontsize=11,
             fontweight="bold", color="#C00000", zorder=4)

    # Angle arc "A°"
    a_arc_r = 1.3
    a_arc_x = [a_arc_r * math.cos(a) for a in thetas]
    a_arc_y = [a_arc_r * math.sin(a) for a in thetas]
    ax1.plot(a_arc_x, a_arc_y, color="#595959", linewidth=1.0, linestyle=":", zorder=3)
    ax1.text(a_arc_r * math.cos(math.radians(45)) + 0.12,
             a_arc_r * math.sin(math.radians(45)) + 0.08,
             "A°", ha="left", va="bottom", fontsize=10, color="#595959", zorder=4)

    # Leg 1 length brace (right side of leg1)
    bx = 0.55
    ax1.annotate("", xy=(bx, Ri), xytext=(bx, Ri + L),
                 arrowprops=dict(arrowstyle="<->", color="#375623", lw=1.2), zorder=4)
    ax1.text(bx + 0.12, Ri + L / 2, "Leg 1", ha="left", va="center",
             fontsize=10, color="#375623", fontweight="bold", zorder=4)

    # Leg 2 length brace (below leg2)
    by = -t - 0.42
    ax1.annotate("", xy=(Ri, by), xytext=(Ri + L, by),
                 arrowprops=dict(arrowstyle="<->", color="#375623", lw=1.2), zorder=4)
    ax1.text(Ri + L / 2, by - 0.12, "Leg 2", ha="center", va="top",
             fontsize=10, color="#375623", fontweight="bold", zorder=4)

    ax1.legend(loc="upper right", fontsize=8, framealpha=0.7)

    # ── Panel 2: Flat blank layout ─────────────────────────────────────────
    ax2.set_facecolor("#EEF2F7")
    ax2.set_xlim(-0.4, 6.4)
    ax2.set_ylim(-1.4, 2.2)
    ax2.axis("off")
    ax2.set_title("Flat Blank Layout", fontweight="bold", fontsize=12,
                  color="#1F4E79", pad=8)

    leg1_w = 2.1
    ba_w   = 0.9
    leg2_w = 2.1
    total  = leg1_w + ba_w + leg2_w
    bh     = 0.55   # bar height

    ax2.add_patch(Rectangle((0, 0), leg1_w, bh, facecolor="#2E74B5",
                             edgecolor="#1F4E79", lw=1.8))
    ax2.text(leg1_w / 2, bh / 2, "Leg 1", ha="center", va="center",
             fontsize=12, fontweight="bold", color="white")

    ax2.add_patch(Rectangle((leg1_w, 0), ba_w, bh, facecolor="#FFC000",
                             edgecolor="#BF8F00", lw=1.8))
    ax2.text(leg1_w + ba_w / 2, bh / 2, "BA", ha="center", va="center",
             fontsize=11, fontweight="bold", color="#3F1F00")

    ax2.add_patch(Rectangle((leg1_w + ba_w, 0), leg2_w, bh, facecolor="#2E74B5",
                             edgecolor="#1F4E79", lw=1.8))
    ax2.text(leg1_w + ba_w + leg2_w / 2, bh / 2, "Leg 2", ha="center", va="center",
             fontsize=12, fontweight="bold", color="white")

    # "Bend Allowance" label above BA section
    ax2.text(leg1_w + ba_w / 2, bh + 0.12,
             "Bend\nAllowance\n(arc length)",
             ha="center", va="bottom", fontsize=9, color="#BF8F00",
             fontweight="bold", linespacing=1.3)

    # Blank Length brace below
    by2 = -0.35
    ax2.annotate("", xy=(0, by2), xytext=(total, by2),
                 arrowprops=dict(arrowstyle="<->", color="#595959", lw=1.6))
    ax2.text(total / 2, by2 - 0.14, "Flat Blank Length",
             ha="center", va="top", fontsize=11, fontweight="bold", color="#595959")

    # Formula note box
    ax2.text(total / 2, 1.85,
             "Blank = Leg 1  +  Leg 2  +  BA  −  2 × OSSB",
             ha="center", va="center", fontsize=10, color="#843C0C",
             fontstyle="italic",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#FCE4D6",
                       edgecolor="#843C0C", alpha=0.9))

    plt.tight_layout(pad=1.5)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf


# ── Tab builders ─────────────────────────────────────────────────────────────
def build_shapes(wb):
    ws = wb["Shapes"]
    ws.sheet_properties.tabColor = TAB_COLORS["Shapes"]
    ws.freeze_panes = "A3"   # rows 1-2 always visible (nav + spacer)

    # ── Row 1: section jump buttons + Back to Dashboard ───────────────────
    # Pre-calculate banner row for each section (content starts at row 3)
    # Each section: 1 banner + 1 header + N data rows + 1 blank gap
    w_row = 3
    c_row = w_row + 1 + 1 + len(W_SHAPES) + 1   # = 45
    a_row = c_row + 1 + 1 + len(C_SHAPES) + 1   # = 63
    h_row = a_row + 1 + 1 + len(ANGLES)  + 1    # = 86

    nav_sections = [
        (1, 2, "\u25BC  W-Shapes",  w_row, "1F4E79"),
        (3, 4, "\u25BC  C-Shapes",  c_row, "375623"),
        (5, 6, "\u25BC  Angles",    a_row, "843C0C"),
        (7, 8, "\u25BC  HSS",       h_row, "7030A0"),
    ]
    for sc, ec, label, tgt, color in nav_sections:
        ws.merge_cells(start_row=1, start_column=sc, end_row=1, end_column=ec)
        nc = ws.cell(row=1, column=sc, value=label)
        _ilink(nc, "Shapes", f"A{tgt}")
        nc.fill = PatternFill("solid", fgColor=color)
        nc.font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
        nc.alignment = Alignment(horizontal="center", vertical="center")

    btn = ws.cell(row=1, column=10)
    btn.value = "\u2190 Dashboard"
    _ilink(btn, "Dashboard")
    btn.fill = PatternFill("solid", fgColor="595959")
    btn.font = Font(name="Calibri", bold=True, color="FFFFFF", size=10)
    btn.alignment = Alignment(horizontal="center", vertical="center")
    ws.column_dimensions["J"].width = 15
    ws.row_dimensions[1].height = 26
    ws.row_dimensions[2].height = 5   # thin spacer between nav and first section

    # ── Sections ──────────────────────────────────────────────────────────
    row = w_row   # = 3
    row = banner(ws, row, "W-SHAPES  (Wide Flange)  —  AISC", 8)
    row = headers(ws, row, ["Designation","d (in)","bf (in)","tw (in)","tf (in)","Wt (lb/ft)","Area (in²)","Notes"])
    row = data_rows(ws, row, [(d,a,b,c,e,f,g,"") for (d,a,b,c,e,f,g) in W_SHAPES], center_cols={2,3,4,5,6,7})

    row += 1
    row = banner(ws, row, "C-SHAPES  (American Standard Channels)", 8)
    row = headers(ws, row, ["Designation","d (in)","bf (in)","tw (in)","tf (in)","Wt (lb/ft)","Area (in²)",""])
    row = data_rows(ws, row, [(d,a,b,c,e,f,g,"") for (d,a,b,c,e,f,g) in C_SHAPES], center_cols={2,3,4,5,6,7})

    row += 1
    row = banner(ws, row, "ANGLES  (Equal & Unequal Leg)", 8)
    row = headers(ws, row, ["Designation","Leg A (in)","Leg B (in)","Thickness (in)","Wt (lb/ft)","Area (in²)","",""])
    row = data_rows(ws, row, [(d,a,b,c,e,f,"","") for (d,a,b,c,e,f) in ANGLES], center_cols={2,3,4,5,6})

    row += 1
    row = banner(ws, row, "HSS  (Hollow Structural Sections — Square & Rectangular)", 8)
    row = headers(ws, row, ["Designation","H (in)","B (in)","Wall t (in)","Wt (lb/ft)","Area (in²)","",""])
    row = data_rows(ws, row, [(d,a,b,c,e,f,"","") for (d,a,b,c,e,f) in HSS_SHAPES], center_cols={2,3,4,5,6})

    ws.auto_filter.ref = f"A4:H{ws.max_row}"
    set_widths(ws, {"A":20,"B":11,"C":11,"D":12,"E":12,"F":12,"G":12,"H":28})


def build_plate(wb):
    ws = wb["Plate"]
    ws.sheet_properties.tabColor = TAB_COLORS["Plate"]
    ws.freeze_panes = "A3"

    row = banner(ws, 1, "PLATE THICKNESS REFERENCE  (Wt/sq ft = thickness × 40.8)", 6)
    row = headers(ws, row, ["Thickness","Decimal (in)","Wt (lb/ft²)","Common Stock (in)","",""])
    row = data_rows(ws, row, [(f,d,w,s,"","") for (f,d,w,s) in PLATE_THK], center_cols={1,2,3})

    row += 1
    row = banner(ws, row, "PLATE WEIGHT CALCULATOR  (Yellow = input, Green = result)", 6)
    label_cell(ws, row, 1, "Thickness (dec in):");  input_cell(ws, row, 2, 0.25)
    label_cell(ws, row, 3, "Length (in):");          input_cell(ws, row, 4, 48)
    label_cell(ws, row, 5, "Width (in):");           input_cell(ws, row, 6, 96)
    calc_row = row
    row += 1
    label_cell(ws, row, 1, "Weight (lbs):")
    output_cell(ws, row, 2, f"=B{calc_row}*40.8*(D{calc_row}/12)*(F{calc_row}/12)", "#,##0.00")
    note = ws.cell(row=row, column=3, value="Formula: t × 40.8 × (L/12) × (W/12)")
    note.font = NOTE_FONT

    row += 2
    row = banner(ws, row, "FLAT BAR REFERENCE  (Wt = W × T × 3.4 lb/ft/in²)", 6)
    row = headers(ws, row, ["Size (W x T)","Width (in)","Thickness (in)","Wt (lb/ft)","",""])
    row = data_rows(ws, row, [(s,w,t,wt,"","") for (s,w,t,wt) in FLAT_BARS], center_cols={1,2,3,4})

    set_widths(ws, {"A":20,"B":16,"C":16,"D":22,"E":12,"F":12})


def build_pipe(wb):
    ws = wb["Pipe"]
    ws.sheet_properties.tabColor = TAB_COLORS["Pipe"]
    ws.freeze_panes = "A3"

    row = banner(ws, 1, "PIPE SIZE & WEIGHT REFERENCE  (ASME B36.10)", 10)
    hdr_row = row
    row = headers(ws, row, [
        "NPS (in)","OD (in)",
        "SCH40 Wall","SCH40 ID","SCH40 Wt/ft",
        "SCH80 Wall","SCH80 ID","SCH80 Wt/ft",
        "Material","Notes"
    ])
    data_start = row
    row = data_rows(ws, row, PIPE_DATA, center_cols={1,2,3,4,5,6,7,8})
    data_end = row - 1

    row += 1
    row = banner(ws, row, "PIPE WEIGHT CALCULATOR  (Pick NPS + Schedule, enter length)", 10)

    label_cell(ws, row, 1, "NPS:");        nps_cell = input_cell(ws, row, 2, "2")
    label_cell(ws, row, 3, "Schedule:");   sch_cell = input_cell(ws, row, 4, "SCH 40")
    nps_row = row

    row += 1
    label_cell(ws, row, 1, "Length (ft):"); len_cell = input_cell(ws, row, 2, 10)
    len_row = row

    row += 1
    label_cell(ws, row, 1, "Wt/ft (lb/ft):")
    wt_formula = (
        f'=IF(D{nps_row}="SCH 40",'
        f'INDEX($E${data_start}:$E${data_end},MATCH(B{nps_row},$A${data_start}:$A${data_end},0)),'
        f'INDEX($H${data_start}:$H${data_end},MATCH(B{nps_row},$A${data_start}:$A${data_end},0)))'
    )
    output_cell(ws, row, 2, wt_formula, "0.000")
    wt_row = row

    row += 1
    label_cell(ws, row, 1, "Total Weight (lbs):")
    output_cell(ws, row, 2, f"=B{wt_row}*B{len_row}", "#,##0.00")

    # Dropdowns
    add_dropdown(ws, f"B{nps_row}", [p[0] for p in PIPE_DATA])
    add_dropdown(ws, f"D{nps_row}", ["SCH 40","SCH 80"])

    set_widths(ws, {"A":12,"B":12,"C":13,"D":13,"E":14,"F":13,"G":13,"H":14,"I":18,"J":24})


def build_materials(wb):
    ws = wb["Materials"]
    ws.sheet_properties.tabColor = TAB_COLORS["Materials"]
    ws.freeze_panes = "A3"

    row = banner(ws, 1, "STRUCTURAL STEEL MATERIAL GRADES  (Quick Reference)", 6)
    row = headers(ws, row, ["Grade","Fy (ksi)","Fu (ksi)","Typical Use","Weldability","Notes"])
    row = data_rows(ws, row, MATERIALS, center_cols={2,3,5})

    row += 1
    row = banner(ws, row, "WELDING ELECTRODE QUICK REFERENCE", 6)
    row = headers(ws, row, ["Electrode","Min Tensile","Process","Typical Use","Notes",""])
    row = data_rows(ws, row, [(e,t,p,u,n,"") for (e,t,p,u,n) in ELECTRODES], center_cols={1,2,3})

    row += 2
    notes = [
        "• E70xx electrodes match A36, A572, A992 (tensile ≥ 70 ksi)",
        "• Use E7018 (low hydrogen) on A53-B / A106-B pipe per most WPS",
        "• Always verify material grade from Mill Test Report (MTR)",
        "• A992 is current standard for W-shapes",
        "• A500 Gr B/C is used for HSS — verify per PO",
    ]
    for n in notes:
        c = ws.cell(row=row, column=1, value=n)
        c.font = NOTE_FONT
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
        row += 1

    set_widths(ws, {"A":14,"B":12,"C":16,"D":38,"E":14,"F":40})


def build_handrail(wb):
    ws = wb["Handrail"]
    ws.sheet_properties.tabColor = TAB_COLORS["Handrail"]
    ws.freeze_panes = "A3"

    row = banner(ws, 1, "HANDRAIL — OSHA & SHOP STANDARDS", 5)
    row = headers(ws, row, ["Item","Value / Spec","Code Reference","",""])
    row = data_rows(ws, row, [(i,v,r,"","") for (i,v,r) in HANDRAIL_SPECS])

    row += 1
    row = banner(ws, row, "COMPONENT REFERENCE", 5)
    row = headers(ws, row, ["Component","Mat'l Opt 1","Mat'l Opt 2","Typical Size","Notes"])
    row = data_rows(ws, row, HANDRAIL_COMPONENTS)

    row += 1
    row = banner(ws, row, "HANDRAIL RUN CALCULATOR  (Yellow = input, Green = result)", 5)

    label_cell(ws, row, 1, "Total Run Length (ft):")
    input_cell(ws, row, 2, 20)
    run_row = row

    row += 1
    label_cell(ws, row, 1, "Post Spacing (ft, ≤8):")
    input_cell(ws, row, 2, 6)
    sp_row = row

    row += 1
    label_cell(ws, row, 1, "Number of Posts:")
    output_cell(ws, row, 2, f"=CEILING(B{run_row}/B{sp_row},1)+1", "0")

    row += 1
    label_cell(ws, row, 1, "Top Rail Length (ft):")
    output_cell(ws, row, 2, f"=B{run_row}+2", "0.0")
    ws.cell(row=row, column=3, value="(+2 for returns)").font = NOTE_FONT

    row += 1
    label_cell(ws, row, 1, "Mid Rail Length (ft):")
    output_cell(ws, row, 2, f"=B{run_row}+2", "0.0")
    ws.cell(row=row, column=3, value="(+2 for returns)").font = NOTE_FONT

    set_widths(ws, {"A":28,"B":26,"C":18,"D":32,"E":40})


def build_pipe_supports(wb):
    ws = wb["Pipe Supports"]
    ws.sheet_properties.tabColor = TAB_COLORS["Pipe Supports"]
    ws.freeze_panes = "A3"

    row = banner(ws, 1, "PIPE SUPPORT TYPE REFERENCE  (O&G / Chemical)", 9)
    row = headers(ws, row, ["Support Type","Description","Pipe Size","Base Plate","Material","Shop Notes","","",""])
    row = data_rows(ws, row, [(t,d,p,b,m,n,"","","") for (t,d,p,b,m,n) in PIPE_SUPPORTS])

    row += 1
    row = banner(ws, row, "DUMMY LEG / SHOE SIZING GUIDE  (Typical — Verify w/ Engineer)", 9)
    row = headers(ws, row, ["Pipe NPS","Pipe OD","Shoe Ht","BP Width","BP Length","BP Thickness","Stiffener?","",""])
    row = data_rows(ws, row, [(n,o,h,w,l,t,s,"","") for (n,o,h,w,l,t,s) in SHOE_SIZING], center_cols={1,2,3,4,5,6,7})

    row += 1
    row = banner(ws, row, "SUPPORT DETAIL LOG  (Fill in as you detail — dropdown in column D)", 9)
    row = headers(ws, row, ["Tag","Line #","NPS","Support Type","Elev (ft)","Material","Base Plate","Gusset?","Notes"])
    log_start = row
    for i in range(15):
        fill = ALT_FILL if i % 2 == 0 else WHITE_FILL
        for col in range(1, 10):
            c = ws.cell(row=row, column=col, value="")
            c.fill = fill
            c.font = BODY_FONT
            c.border = BORDER
            c.alignment = CENTER if col in (3,5,8) else LEFT
        row += 1
    log_end = row - 1

    add_dropdown(ws, f"D{log_start}:D{log_end}", [s[0] for s in PIPE_SUPPORTS])
    add_dropdown(ws, f"F{log_start}:F{log_end}", [m[0] for m in MATERIALS])

    set_widths(ws, {"A":12,"B":14,"C":10,"D":22,"E":12,"F":14,"G":14,"H":10,"I":30})


def build_platforms(wb):
    ws = wb["Platforms"]
    ws.sheet_properties.tabColor = TAB_COLORS["Platforms"]
    ws.freeze_panes = "A3"

    row = banner(ws, 1, "GRATING REFERENCE", 8)
    row = headers(ws, row, ["Type","Designation","Bar Size","Panel Sizes","Wt (lb/ft²)","Notes","",""])
    row = data_rows(ws, row, [(t,d,b,p,w,n,"","") for (t,d,b,p,w,n) in GRATING], center_cols={2,5})

    row += 1
    row = banner(ws, row, "STRUCTURAL MEMBER REFERENCE", 8)
    row = headers(ws, row, ["Member","Typical Size","Material","Max Span","Notes","","",""])
    row = data_rows(ws, row, [(m,s,mat,sp,n,"","","") for (m,s,mat,sp,n) in PLATFORM_MEMBERS])

    row += 1
    row = banner(ws, row, "DESIGN NOTES & SHOP STANDARDS", 8)
    row = headers(ws, row, ["Item","Standard Value","Notes","","","","",""])
    row = data_rows(ws, row, [(i,v,n,"","","","","") for (i,v,n) in PLATFORM_NOTES])

    row += 1
    row = banner(ws, row, "PLATFORM BILL OF MATERIALS  (Fill in — Total Wt auto-calcs)", 8)
    row = headers(ws, row, ["Mark","Description","Material","Size","Length (ft)","Qty","Wt/ea (lbs)","Total Wt"])
    bom_start = row
    for i in range(20):
        fill = ALT_FILL if i % 2 == 0 else WHITE_FILL
        for col in range(1, 8):
            c = ws.cell(row=row, column=col, value="")
            c.fill = fill
            c.font = BODY_FONT
            c.border = BORDER
            c.alignment = CENTER if col in (1,5,6) else LEFT
        # Total Wt formula
        tc = ws.cell(row=row, column=8, value=f'=IF(OR(F{row}="",G{row}=""),"",F{row}*G{row})')
        tc.fill = OUT_FILL
        tc.font = OUT_FONT
        tc.border = BORDER
        tc.alignment = CENTER
        tc.number_format = "#,##0.0"
        row += 1
    bom_end = row - 1

    # Grand total row
    label_cell(ws, row, 7, "GRAND TOTAL (lbs):")
    output_cell(ws, row, 8, f"=SUM(H{bom_start}:H{bom_end})", "#,##0.0")

    add_dropdown(ws, f"C{bom_start}:C{bom_end}", [m[0] for m in MATERIALS])

    set_widths(ws, {"A":10,"B":30,"C":14,"D":20,"E":12,"F":8,"G":14,"H":14})


def build_bolts(wb):
    ws = wb["Bolts"]
    ws.sheet_properties.tabColor = "C00000"
    ws.freeze_panes = "A3"

    row = banner(ws, 1, "BOLT & ANCHOR ROD GRADES  (AISC / ASTM)", 7)
    row = headers(ws, row, ["Spec","Grade","Fy (ksi)","Fu (ksi)","Shear (ksi)","Tension (ksi)","Notes"])
    row = data_rows(ws, row, BOLT_GRADES, center_cols={3,4,5,6})

    row += 1
    row = banner(ws, row, "STANDARD HOLE SIZES  (AISC Table J3.3)", 7)
    row = headers(ws, row, ["Bolt Dia","STD Hole","OVS Hole","SSLOT Width","SSLOT Length","LSLOT Width","LSLOT Length"])
    row = data_rows(ws, row, HOLE_SIZES, center_cols={1,2,3,4,5,6,7})

    row += 1
    row = banner(ws, row, "MIN EDGE DISTANCE & BOLT SPACING  (AISC Table J3.4)", 7)
    row = headers(ws, row, ["Bolt Dia","Min Edge (sheared)","Min Edge (rolled/saw)","Min Spacing (3x dia)","","",""])
    row = data_rows(ws, row, [(d,a,b,c,"","","") for (d,a,b,c) in BOLT_SPACING], center_cols={1,2,3,4})

    row += 1
    row = banner(ws, row, "APPROXIMATE SNUG-TIGHT TORQUE  (Reference only — follow approved ITP)", 7)
    row = headers(ws, row, ["Bolt Dia","","Grip Range","A325 Torque (ft-lbs)","A490 Torque (ft-lbs)","",""])
    row = data_rows(ws, row, [(d,"",g,t1,t2,"","") for (d,_,g,t1,t2) in BOLT_TORQUE], center_cols={1,3,4,5})

    row += 2
    notes = [
        "• STD = Standard hole | OVS = Oversized | SSLOT = Short-slot | LSLOT = Long-slot",
        "• A325 and A490 are now superseded by ASTM F3125 Gr A325/A490 — same dimensions/strengths",
        "• Min spacing = 2-2/3 × bolt dia (preferred 3×); min edge = per table above",
        "• For slip-critical connections use Class A or B faying surface — see engineer",
        "• Torque values are approximate — always follow the project Inspection & Test Plan (ITP)",
        "• F1554 anchor rods: embed length = 12× dia minimum unless engineer specifies otherwise",
    ]
    for n in notes:
        c = ws.cell(row=row, column=1, value=n)
        c.font = NOTE_FONT
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)
        row += 1

    set_widths(ws, {"A":12,"B":14,"C":16,"D":18,"E":18,"F":14,"G":36})


def build_welds(wb):
    ws = wb["Welds"]
    ws.sheet_properties.tabColor = "FF6600"
    ws.freeze_panes = "A3"

    AISC_URL = "https://www.aws.org/standards/details/d1-1-structural-welding-code-steel"

    row = banner(ws, 1, "WELD REFERENCE — AWS D1.1 Structural Welding Code (Steel)", 7)
    c = ws.cell(row=1, column=1)
    c.hyperlink = AISC_URL
    c.style = "Hyperlink"
    c.font = Font(name="Calibri", bold=True, color="FFFFFF", size=12)

    row = banner(ws, row, "MIN FILLET WELD SIZE (AWS D1.1 Table 8.8)  — based on THICKER part joined", 7)
    row = headers(ws, row, ["Base Metal Thickness (thicker part)", "Min Fillet Weld Size", "Notes", "", "", "", ""])
    row = data_rows(ws, row, [(t, w, n, "", "", "", "") for (t, w, n) in MIN_FILLET], center_cols={1, 2})

    row += 1
    row = banner(ws, row, "MAX SINGLE-PASS FILLET WELD SIZE (AWS D1.1)", 7)
    row = headers(ws, row, ["Position", "Max Single-Pass Size", "Reference", "", "", "", ""])
    row = data_rows(ws, row, [(p, m, r, "", "", "", "") for (p, m, r) in MAX_FILLET_PASS], center_cols={1, 2})

    row += 1
    row = banner(ws, row, "MAX FILLET WELD SIZE ALONG EDGE", 7)
    row = headers(ws, row, ["Edge Thickness", "Max Weld Size", "Notes", "", "", "", ""])
    row = data_rows(ws, row, [(e, m, n, "", "", "", "") for (e, m, n) in MAX_FILLET_EDGE], center_cols={1, 2})

    row += 1
    row = banner(ws, row, "PREQUALIFIED JOINT DETAILS (AWS D1.1) — Reference Only", 7)
    row = headers(ws, row, ["Joint Type", "AWS Symbol", "Root Opening", "Groove Angle", "Notes", "", ""])
    row = data_rows(ws, row, [(j, s, r, g, n, "", "") for (j, s, r, g, n) in PREQUALIFIED_JOINTS], center_cols={2, 3, 4})

    row += 1
    row = banner(ws, row, "ELECTRODE — BASE METAL MATCH TABLE", 7)
    row = headers(ws, row, ["Base Metal", "Min Fu (ksi)", "Recommended Electrode", "Notes", "", "", ""])
    row = data_rows(ws, row, [(b, f, e, n, "", "", "") for (b, f, e, n) in ELECTRODE_MATCH], center_cols={2, 3})

    row += 2
    weld_notes = [
        "• Fillet weld size on drawing = LEG size (not throat). Throat = 0.707 × leg for equal-leg fillet.",
        "• Always use the THICKER part to determine minimum weld size — not the thinner.",
        "• E7018 is low-hydrogen; keep electrodes in oven or rod oven — discard if exposed > 4 hrs.",
        "• Preheat required per AWS D1.1 Table 3.2 when CEQ > 0.40 or plate t > 1.5\" A36.",
        "• WPS = Welding Procedure Specification — always weld to an approved WPS.",
        "• PQR = Procedure Qualification Record — proves the WPS works.",
        "• AWS D1.1 is the governing code for structural steel welding in most fabrication shops.",
    ]
    for n in weld_notes:
        c = ws.cell(row=row, column=1, value=n)
        c.font = NOTE_FONT
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)
        row += 1

    set_widths(ws, {"A": 30, "B": 20, "C": 18, "D": 16, "E": 40, "F": 10, "G": 10})


def build_converter(wb):
    ws = wb["Converter"]
    ws.sheet_properties.tabColor = "00B0F0"
    ws.freeze_panes = "A2"

    row = banner(ws, 1, "UNIT CONVERTER  (Enter values in YELLOW cells — results auto-calculate)", 6)

    # ── Length ──
    row = banner(ws, row, "LENGTH", 6)
    label_cell(ws, row, 1, "Inches:")
    in_cell = input_cell(ws, row, 2, 12)
    in_row = row
    label_cell(ws, row, 3, "→  Feet:");      output_cell(ws, row, 4, f"=B{in_row}/12", "0.000")
    label_cell(ws, row, 5, "→  mm:");        output_cell(ws, row, 6, f"=B{in_row}*25.4", "0.000")
    row += 1
    label_cell(ws, row, 3, "→  Meters:");   output_cell(ws, row, 4, f"=B{in_row}*0.0254", "0.0000")
    label_cell(ws, row, 5, "→  cm:");       output_cell(ws, row, 6, f"=B{in_row}*2.54", "0.000")
    row += 2

    # ── Weight / Force ──
    row = banner(ws, row, "WEIGHT / FORCE", 6)
    label_cell(ws, row, 1, "Pounds (lbs):")
    lb_cell = input_cell(ws, row, 2, 1000)
    lb_row = row
    label_cell(ws, row, 3, "→  Kilograms:"); output_cell(ws, row, 4, f"=B{lb_row}*0.453592", "0.000")
    label_cell(ws, row, 5, "→  kips:");      output_cell(ws, row, 6, f"=B{lb_row}/1000", "0.000")
    row += 1
    label_cell(ws, row, 3, "→  kN:");        output_cell(ws, row, 4, f"=B{lb_row}*0.004448", "0.000")
    label_cell(ws, row, 5, "→  Newtons:");   output_cell(ws, row, 6, f"=B{lb_row}*4.44822", "0.0")
    row += 2

    # ── Load / Pressure ──
    row = banner(ws, row, "LOAD / PRESSURE", 6)
    label_cell(ws, row, 1, "lb/sq ft (psf):")
    psf_cell = input_cell(ws, row, 2, 50)
    psf_row = row
    label_cell(ws, row, 3, "→  kPa:");  output_cell(ws, row, 4, f"=B{psf_row}*0.047880", "0.000")
    label_cell(ws, row, 5, "→  psi:");  output_cell(ws, row, 6, f"=B{psf_row}/144", "0.000")
    row += 1
    label_cell(ws, row, 3, "→  ksf:");  output_cell(ws, row, 4, f"=B{psf_row}/1000", "0.0000")
    label_cell(ws, row, 5, "→  Pa:");   output_cell(ws, row, 6, f"=B{psf_row}*47.880", "0.0")
    row += 2

    # ── Stress ──
    row = banner(ws, row, "STRESS (ksi ↔ MPa)", 6)
    label_cell(ws, row, 1, "ksi (kips/in²):")
    ksi_cell = input_cell(ws, row, 2, 36)
    ksi_row = row
    label_cell(ws, row, 3, "→  MPa:");  output_cell(ws, row, 4, f"=B{ksi_row}*6.89476", "0.00")
    label_cell(ws, row, 5, "→  psi:");  output_cell(ws, row, 6, f"=B{ksi_row}*1000", "0")
    row += 2

    # ── Temperature ──
    row = banner(ws, row, "TEMPERATURE", 6)
    label_cell(ws, row, 1, "°F:")
    f_cell = input_cell(ws, row, 2, 70)
    f_row = row
    label_cell(ws, row, 3, "→  °C:");  output_cell(ws, row, 4, f"=(B{f_row}-32)*5/9", "0.0")
    row += 2

    # ── Static reference table ──
    row = banner(ws, row, "COMMON CONVERSION FACTORS (Quick Reference)", 6)
    row = headers(ws, row, ["From", "To", "Multiply by", "", "", ""])
    static = [
        ("1 inch",    "millimeters",  "25.4"),
        ("1 foot",    "millimeters",  "304.8"),
        ("1 foot",    "meters",       "0.3048"),
        ("1 lb",      "kilograms",    "0.4536"),
        ("1 kip",     "kilonewtons",  "4.4482"),
        ("1 psf",     "kPa",          "0.04788"),
        ("1 ksi",     "MPa",          "6.8948"),
        ("1 lb/ft",   "kg/m",         "1.4882"),
        ("1 in²",     "mm²",          "645.16"),
        ("1 in³",     "mm³",          "16387.1"),
        ("1 in⁴",     "mm⁴",          "416231.0"),
    ]
    row = data_rows(ws, row, [(f, t, m, "", "", "") for (f, t, m) in static], center_cols={3})

    set_widths(ws, {"A": 20, "B": 16, "C": 20, "D": 16, "E": 16, "F": 16})


def build_references(wb):
    ws = wb["References"]
    ws.sheet_properties.tabColor = "404040"
    ws.freeze_panes = "A3"

    row = banner(ws, 1, "STANDARDS & CODE REFERENCES  — Where the data in this workbook comes from", 6)
    row = headers(ws, row, ["Standard", "Full Title", "Used In Tab", "What It Covers", "Access", "Click to Open"])

    for i, (std, title, tab, covers, access, url) in enumerate(REFERENCES):
        fill = ALT_FILL if i % 2 == 0 else WHITE_FILL
        vals = [std, title, tab, covers, access]
        for j, v in enumerate(vals, start=1):
            c = ws.cell(row=row, column=j, value=v)
            c.fill = fill
            c.font = BODY_FONT
            c.border = BORDER
            c.alignment = LEFT if j in (2, 4) else CENTER

        # Clickable link in column 6
        link_cell = ws.cell(row=row, column=6, value="Open Source")
        link_cell.hyperlink = url
        link_cell.style = "Hyperlink"
        link_cell.fill = fill
        link_cell.border = BORDER
        link_cell.alignment = CENTER
        row += 1

    row += 2
    ref_notes = [
        "• FREE = Available at no cost online (click link to open directly)",
        "• Purchase required = Paid standard; link goes to purchase/info page",
        "• AISC Steel Construction Manual is FREE to download with a free account at aisc.org — highly recommended",
        "• OSHA standards (1910 and 1926) are always free at osha.gov — bookmark these",
        "• AWS D1.1 and ASME B36.10 require purchase — your company may have copies in the office",
        "• When someone asks 'where did you get that number?' — point them to this tab and the linked source",
    ]
    for n in ref_notes:
        c = ws.cell(row=row, column=1, value=n)
        c.font = NOTE_FONT
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
        row += 1

    set_widths(ws, {"A": 18, "B": 38, "C": 16, "D": 42, "E": 16, "F": 16})


def build_bending(wb):
    ws = wb["Bending"]
    ws.sheet_properties.tabColor = "E36C09"
    ws.freeze_panes = "A2"

    row = banner(ws, 1, "BENDING CALCULATOR  —  Bend Allowance, Blank Length & Setback", 6)

    # ── Main calculator ──
    row = banner(ws, row, "INPUTS  (enter values in YELLOW cells)", 6)
    fields = [
        ("Material Thickness  t  (in):",    "B", 0.375),
        ("Inside Bend Radius  R  (in):",    "B", 0.375),
        ("Bend Angle  A  (degrees):",       "B", 90),
        ("Leg 1 Length  (in):",             "B", 6.0),
        ("Leg 2 Length  (in):",             "B", 6.0),
        ("K-Factor  (see table below):",    "B", 0.41),
    ]
    input_rows = {}
    for label, col, default in fields:
        label_cell(ws, row, 1, label)
        input_cell(ws, row, 2, default)
        input_rows[label] = row
        row += 1

    t_row  = input_rows["Material Thickness  t  (in):"]
    r_row  = input_rows["Inside Bend Radius  R  (in):"]
    a_row  = input_rows["Bend Angle  A  (degrees):"]
    l1_row = input_rows["Leg 1 Length  (in):"]
    l2_row = input_rows["Leg 2 Length  (in):"]
    k_row  = input_rows["K-Factor  (see table below):"]

    row += 1
    row = banner(ws, row, "RESULTS  (auto-calculated — do not edit green cells)", 6)

    # Bend Allowance = π × (R + K×T) × (A/180)
    label_cell(ws, row, 1, "Bend Allowance  BA  (in):")
    ba_formula = f"=PI()*(B{r_row}+B{k_row}*B{t_row})*(B{a_row}/180)"
    output_cell(ws, row, 2, ba_formula, "0.0000")
    ws.cell(row=row, column=3, value="Formula:  π × (R + K×t) × (A/180)").font = NOTE_FONT
    ba_row = row
    row += 1

    # Outside Setback = tan(A/2) × (R + T)
    label_cell(ws, row, 1, "Outside Setback  OSSB  (in):")
    ossb_formula = f"=TAN(RADIANS(B{a_row}/2))*(B{r_row}+B{t_row})"
    output_cell(ws, row, 2, ossb_formula, "0.0000")
    ws.cell(row=row, column=3, value="Formula:  tan(A/2) × (R + t)").font = NOTE_FONT
    ossb_row = row
    row += 1

    # Blank length = L1 + L2 + BA - 2×OSSB
    label_cell(ws, row, 1, "Flat Blank Length  (in):")
    blank_formula = f"=B{l1_row}+B{l2_row}+B{ba_row}-2*B{ossb_row}"
    output_cell(ws, row, 2, blank_formula, "0.0000")
    ws.cell(row=row, column=3, value="Formula:  Leg1 + Leg2 + BA − 2×OSSB").font = NOTE_FONT
    row += 1

    # Outside radius
    label_cell(ws, row, 1, "Outside Bend Radius  (in):")
    output_cell(ws, row, 2, f"=B{r_row}+B{t_row}", "0.0000")
    row += 2

    # ── K-factor table ──
    row = banner(ws, row, "K-FACTOR GUIDE", 6)
    row = headers(ws, row, ["Bend Type", "K-Factor", "Notes", "", "", ""])
    row = data_rows(ws, row, [(b, k, n, "", "", "") for (b, k, n) in KFACTOR_TABLE], center_cols={2})

    row += 1
    row = banner(ws, row, "MINIMUM BEND RADIUS BY MATERIAL", 6)
    row = headers(ws, row, ["Material", "Grade", "Min Radius", "Notes", "", ""])
    row = data_rows(ws, row, [(m, g, r, n, "", "") for (m, g, r, n) in MIN_BEND_RADIUS], center_cols={2, 3})

    row += 2
    bend_notes = [
        "• BA = Bend Allowance — the arc length consumed by the bend (added to blank, not subtracted).",
        "• OSSB = Outside Setback — distance from the apex to the start of the bend.",
        "• Blank Length = Leg1 + Leg2 + BA − 2×OSSB  (the flat length before bending).",
        "• K-factor of 0.41 works well for most A36 air-bent plate in a press brake.",
        "• Always add a test piece before running production parts — springback varies by heat.",
        "• For pipe/tube bending, use CLR (centerline radius) = inside radius + OD/2.",
        "• Reference: Machinery's Handbook / AISC Design Guide 9 / press brake manufacturer tables.",
    ]
    for n in bend_notes:
        c = ws.cell(row=row, column=1, value=n)
        c.font = NOTE_FONT
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
        row += 1

    set_widths(ws, {"A": 32, "B": 16, "C": 40, "D": 10, "E": 10, "F": 10})

    # ── Embed bend reference diagram ──────────────────────────────────────────
    row += 1
    diag_banner_row = row
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    diag_hdr = ws.cell(row=row, column=1,
                       value="BEND GEOMETRY REFERENCE DIAGRAMS  (Side view + Flat blank layout)")
    diag_hdr.fill = PatternFill("solid", fgColor="1F4E79")
    diag_hdr.font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
    diag_hdr.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[row].height = 22
    row += 1

    img_buf = generate_bend_diagram()
    if img_buf:
        try:
            img = XLImage(img_buf)
            # ~13:5 aspect ratio; fit in ~900px wide × ~346px tall
            img.width  = 900
            img.height = 346
            ws.add_image(img, f"A{row}")
            # Reserve rows for the image (approx 346px / 15pt per row ≈ 23 rows)
            for r in range(row, row + 23):
                ws.row_dimensions[r].height = 15
        except Exception:
            pass


def build_dashboard(wb):
    """First tab — navigation hub with jump links to every sheet."""
    ws = wb["Dashboard"]
    ws.sheet_properties.tabColor = "1F4E79"

    # Title
    ws.merge_cells("A1:F1")
    title = ws["A1"]
    title.value = "STEEL DETAILING QUICK REFERENCE"
    title.fill = PatternFill("solid", fgColor="1F4E79")
    title.font = Font(name="Calibri", bold=True, color="FFFFFF", size=18)
    title.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 40

    ws.merge_cells("A2:F2")
    sub = ws["A2"]
    sub.value = "Click any button below to jump directly to that section"
    sub.font = Font(name="Calibri", italic=True, color="595959", size=11)
    sub.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 20

    # Navigation buttons — (row, col, label, sheet_target, color)
    buttons = [
        (4,  1, "SHAPES",        "Shapes",        "1F4E79"),
        (4,  3, "PLATE",         "Plate",         "375623"),
        (4,  5, "PIPE",          "Pipe",          "7030A0"),
        (7,  1, "MATERIALS",     "Materials",     "843C0C"),
        (7,  3, "HANDRAIL",      "Handrail",      "538135"),
        (7,  5, "PIPE SUPPORTS", "Pipe Supports", "C55A11"),
        (10, 1, "PLATFORMS",     "Platforms",     "2E74B5"),
        (10, 3, "BOLTS",         "Bolts",         "C00000"),
        (10, 5, "WELDS",         "Welds",         "E36C09"),
        (13, 1, "BENDING CALC",  "Bending",       "E36C09"),
        (13, 3, "UNIT CONVERTER","Converter",     "00B0F0"),
        (13, 5, "REFERENCES",    "References",    "404040"),
    ]

    for (r, c, label, sheet, color) in buttons:
        # Merge 2 cols wide, 2 rows tall per button
        ws.merge_cells(start_row=r, start_column=c, end_row=r+1, end_column=c+1)
        cell = ws.cell(row=r, column=c)
        cell.value = label
        _ilink(cell, sheet)
        cell.fill = PatternFill("solid", fgColor=color)
        cell.font = Font(name="Calibri", bold=True, color="FFFFFF", size=13)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = Border(
            left=Side(style="medium", color="FFFFFF"),
            right=Side(style="medium", color="FFFFFF"),
            top=Side(style="medium", color="FFFFFF"),
            bottom=Side(style="medium", color="FFFFFF"),
        )
        ws.row_dimensions[r].height = 30
        ws.row_dimensions[r+1].height = 30

    # Quick tips section
    tip_row = 17
    ws.merge_cells(f"A{tip_row}:F{tip_row}")
    tip_hdr = ws.cell(row=tip_row, column=1, value="QUICK TIPS FOR BEGINNERS")
    tip_hdr.fill = PatternFill("solid", fgColor="D9E1F2")
    tip_hdr.font = Font(name="Calibri", bold=True, size=11, color="1F4E79")
    tip_hdr.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[tip_row].height = 20
    tip_row += 1

    tips = [
        ("Plate weight:",   "thickness (in) × 40.8 × length (ft) × width (ft) = lbs"),
        ("Pipe weight:",    "go to Pipe tab → pick NPS + schedule → enter length → done"),
        ("Weld size min:",  "go to Welds tab → min fillet size table → use thicker plate"),
        ("Bolt holes:",     "go to Bolts tab → STD hole = bolt dia + 1/16\""),
        ("Shape lookup:",   "go to Shapes tab → use the filter arrows on any column header"),
        ("Where to verify:","go to References tab → click 'Open Source' for official document"),
        ("Unit convert:",   "go to Converter tab → type your number → result auto-fills"),
        ("Blank length:",   "go to Bending tab → enter t, R, angle, legs → get flat size"),
    ]
    for label, val in tips:
        ws.merge_cells(f"A{tip_row}:A{tip_row}")
        lc = ws.cell(row=tip_row, column=1, value=label)
        lc.font = Font(name="Calibri", bold=True, size=10)
        lc.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.merge_cells(f"B{tip_row}:F{tip_row}")
        vc = ws.cell(row=tip_row, column=2, value=val)
        vc.font = Font(name="Calibri", size=10)
        vc.alignment = Alignment(horizontal="left", vertical="center")
        ws.row_dimensions[tip_row].height = 18
        tip_row += 1

    set_widths(ws, {"A": 18, "B": 18, "C": 18, "D": 18, "E": 18, "F": 18})


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    wb = Workbook()
    wb.active.title = "Dashboard"
    for name in ["Shapes","Plate","Pipe","Materials","Handrail","Pipe Supports","Platforms","Bolts","Welds","Bending","Converter","References"]:
        wb.create_sheet(name)

    build_dashboard(wb)
    build_shapes(wb)
    build_plate(wb)
    build_pipe(wb)
    build_materials(wb)
    build_handrail(wb)
    build_pipe_supports(wb)
    build_platforms(wb)
    build_bolts(wb)
    build_welds(wb)
    build_bending(wb)
    build_converter(wb)
    build_references(wb)

    out = "steel_detailing_reference.xlsx"
    wb.save(out)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
