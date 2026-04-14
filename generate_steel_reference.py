#!/usr/bin/env python3
"""
Steel Detailing Quick Reference — Excel Generator
Generates steel_detailing_reference.xlsx for shop/drafting use.
"""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

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

# ── Tab builders ─────────────────────────────────────────────────────────────
def build_shapes(wb):
    ws = wb["Shapes"]
    ws.sheet_properties.tabColor = TAB_COLORS["Shapes"]
    ws.freeze_panes = "A3"

    row = banner(ws, 1, "W-SHAPES  (Wide Flange)  —  AISC", 8)
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


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    wb = Workbook()
    wb.active.title = "Shapes"
    for name in ["Plate","Pipe","Materials","Handrail","Pipe Supports","Platforms"]:
        wb.create_sheet(name)

    build_shapes(wb)
    build_plate(wb)
    build_pipe(wb)
    build_materials(wb)
    build_handrail(wb)
    build_pipe_supports(wb)
    build_platforms(wb)

    out = "steel_detailing_reference.xlsx"
    wb.save(out)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
