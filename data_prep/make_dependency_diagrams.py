# Team name:        The Equal SQLs
# Student numbers:  4351723, 4354243, 4359047, 4358074, 4335167
# File name:        make_dependency_diagrams.py
#
# make_dependency_diagrams.py - dependency diagrams for the normalisation section
# Requires reportlab. Output: dep_crew.pdf, dep_cast.pdf, dep_schedule.pdf
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white

FD = "/usr/share/fonts/truetype/liberation/"
try:
    pdfmetrics.registerFont(TTFont("R", FD + "LiberationSerif-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("B", FD + "LiberationSerif-Bold.ttf"))
    R, B = "R", "B"
except Exception:
    R, B = "Times-Roman", "Times-Bold"

INK = HexColor("#111111")
COLORS = [HexColor("#b3261e"), HexColor("#1f5fa8"), HexColor("#2e7d32")]
W, M, GAP, BH = 468, 2, 4, 30


def diagram(name, attrs, full, below):
    """attrs: [(label, is_key)], full: indexes that depend on the whole key,
    below: [(determinant index, [dependent indexes], label, level)]"""
    n = len(attrs)
    bw = (W - 2 * M - GAP * (n - 1)) / n
    top = 30 if full else 6
    levels = max((b[3] for b in below), default=-1) + 1
    H = top + BH + 14 + levels * 26 + 4
    c = canvas.Canvas(name + ".pdf", pagesize=(W, H))
    Y = lambda y: H - y
    cx = lambda i: M + i * (bw + GAP) + bw / 2

    def arrow(x, y_from, y_to, color):
        c.setStrokeColor(color); c.setFillColor(color); c.setLineWidth(1)
        c.line(x, Y(y_from), x, Y(y_to))
        d = 4.5 if y_to > y_from else -4.5
        p = c.beginPath(); p.moveTo(x, Y(y_to)); p.lineTo(x - 2.6, Y(y_to - d)); p.lineTo(x + 2.6, Y(y_to - d)); p.close()
        c.drawPath(p, fill=1)

    keys = [i for i, a in enumerate(attrs) if a[1]]
    if full:                                   # arrows above: dependency on the whole key
        ya = top - 16
        c.setStrokeColor(INK); c.setLineWidth(1)
        c.line(cx(min(keys)), Y(ya), cx(max(full)), Y(ya))
        for k in keys:
            c.line(cx(k), Y(top), cx(k), Y(ya))
        for i in full:
            arrow(cx(i), ya, top, INK)
        c.setFont(R, 7.5); c.setFillColor(INK)
        c.drawString(cx(max(keys)) + 6, Y(ya - 3), "Full dependency on the primary key")

    for i, (label, is_key) in enumerate(attrs):   # attribute boxes
        x = M + i * (bw + GAP)
        c.setStrokeColor(INK); c.setLineWidth(0.9)
        c.setFillColor(HexColor("#e6edf5") if is_key else white)
        c.rect(x, Y(top + BH), bw, BH, fill=1)
        lines = label.split("|")
        c.setFillColor(INK); c.setFont(B if is_key else R, 8)
        for j, t in enumerate(lines):
            ty = top + BH / 2 + 3 + (j - (len(lines) - 1) / 2) * 9
            c.drawCentredString(x + bw / 2, Y(ty), t)
            if is_key:
                tw = pdfmetrics.stringWidth(t, B, 8)
                c.setLineWidth(0.6); c.line(x + bw / 2 - tw / 2, Y(ty + 1.5), x + bw / 2 + tw / 2, Y(ty + 1.5))

    for n_dep, (det, deps, label, level) in enumerate(below):   # arrows below
        color = COLORS[n_dep % len(COLORS)]
        yl = top + BH + 14 + level * 26
        off = (level - (levels - 1) / 2) * 7 if det in keys and len(keys) > 1 else 0
        c.setStrokeColor(color); c.setLineWidth(1)
        c.line(cx(det) + off, Y(top + BH), cx(det) + off, Y(yl))
        c.line(cx(det) + off, Y(yl), cx(max(deps)), Y(yl))
        for i in deps:
            arrow(cx(i), yl, top + BH, color)
        c.setFont(R, 7.5); c.setFillColor(color)
        lx = cx(det) + off if len(keys) == 1 else cx(min(deps))   # keep labels clear of other lines
        if lx + 4 + pdfmetrics.stringWidth(label, R, 7.5) > W:
            c.drawRightString(cx(max(deps)) - 4, Y(yl + 9), label)
        else:
            c.drawString(lx + 4, Y(yl + 9), label)
    c.showPage(); c.save()


K, A = True, False
diagram("dep_crew",
        [("FilmID", K), ("Crew|MemberID", K), ("RoleID", K), ("Title", A), ("Release|Year", A),
         ("Runtime|Minutes", A), ("First|Name", A), ("Last|Name", A), ("Contact|Email", A), ("Role|Name", A)],
        [],
        [(0, [3, 4, 5], "Partial dependency", 0), (1, [6, 7, 8], "Partial dependency", 1),
         (2, [9], "Partial dependency", 2)])
diagram("dep_cast",
        [("FilmID", K), ("ActorID", K), ("Character|Name", A), ("Title", A), ("Release|Year", A),
         ("Runtime|Minutes", A), ("First|Name", A), ("Last|Name", A), ("Birth|Year", A)],
        [2],
        [(0, [3, 4, 5], "Partial dependency", 0), (1, [6, 7, 8], "Partial dependency", 1)])
diagram("dep_schedule",
        [("Schedule|ID", K), ("Filming|Date", A), ("Start|Time", A), ("End|Time", A), ("FilmID", A),
         ("Title", A), ("Location|ID", A), ("Location|Name", A), ("Address", A), ("City", A)],
        [1, 2, 3, 4, 6],
        [(4, [5], "Transitive dependency", 0), (6, [7, 8, 9], "Transitive dependency", 0)])
