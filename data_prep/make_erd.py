# Team name:        The Equal SQLs
# Student numbers:  4351723, 4354243, 4359047, 4358074, 4335167
# File name:        make_erd.py
#
# make_erd.py - draws the Film Production Database ERD (Crow's Foot notation)
# Requires: pip install reportlab      Output: Film_Production_ERD.pdf
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white

W, H = 2000, 1414
FD = "/usr/share/fonts/truetype/dejavu/"
try:
    pdfmetrics.registerFont(TTFont("R", FD + "DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("B", FD + "DejaVuSans-Bold.ttf"))
    R, B = "R", "B"
except Exception:
    R, B = "Helvetica", "Helvetica-Bold"

INK, MUTED, LINE = HexColor("#1b2233"), HexColor("#5b6478"), HexColor("#4a5268")
HEAD, EDGE, PANEL = HexColor("#dbe6f0"), HexColor("#8e9bb3"), HexColor("#f4f6fa")

c = canvas.Canvas("Film_Production_ERD.pdf", pagesize=(W, H))
Y = lambda y: H - y

def text(x, y, s, font=R, size=22, color=INK, align="l"):
    c.setFont(font, size); c.setFillColor(color)
    {"l": c.drawString, "r": c.drawRightString, "c": c.drawCentredString}[align](x, Y(y), s)

HDR, ROW = 54, 38
def entity(x, y, w, name, rows):
    h = HDR + 10 + ROW * len(rows) + 6
    c.setStrokeColor(EDGE); c.setLineWidth(1.5); c.setFillColor(white)
    c.rect(x, Y(y + h), w, h, fill=1)
    c.setFillColor(HEAD); c.rect(x, Y(y + HDR), w, HDR, fill=1)
    text(x + 17, y + 37, name, B, 27)
    keyw = 84 if any("," in k for k, _, _ in rows) else 60
    for i, (k, n, t) in enumerate(rows):
        yy = y + HDR + 10 + ROW * i + 26
        text(x + 14, yy, k, B, 18, HexColor("#3a4358"))
        text(x + keyw, yy, n, R, 22)
        text(x + w - 14, yy, t, R, 17, MUTED, "r")
    return h

def path(pts, dashed):
    c.setStrokeColor(LINE); c.setLineWidth(2.4)
    c.setDash([9, 6] if dashed else [])
    p = c.beginPath(); p.moveTo(pts[0][0], Y(pts[0][1]))
    for px, py in pts[1:]: p.lineTo(px, Y(py))
    c.drawPath(p); c.setDash([])

def end(x, y, dx, dy, kind):
    """Symbol at an entity edge (x, y); (dx, dy) points away from the entity."""
    c.setStrokeColor(LINE); c.setLineWidth(2.4); c.setDash([])
    px, py = -dy, dx                                  # perpendicular
    def tick(d):
        c.line(x + dx*d + px*12, Y(y + dy*d + py*12), x + dx*d - px*12, Y(y + dy*d - py*12))
    if kind == "one":
        tick(14); tick(25)
    else:
        for s in (-12, 12):                           # crow's foot
            c.line(x + dx*24, Y(y + dy*24), x + px*s, Y(y + py*s))
        if kind == "one_many":
            tick(36)
        else:                                         # zero or more
            c.setFillColor(white); c.circle(x + dx*36, Y(y + dy*36), 8.5, fill=1)

# ---------------- title ----------------
text(90, 92, "FILM PRODUCTION DATABASE", B, 38)
text(90, 130, "Logical ERD  |  Crow's Foot notation  |  Nine entities and eight relationships", R, 24, MUTED)

# ---------------- entities ----------------
entity(90, 462, 366, "FILM", [("PK", "FilmID", "INT"), ("", "Title", "VARCHAR(200)"),
       ("", "ReleaseYear", "SMALLINT ?"), ("", "RuntimeMinutes", "SMALLINT ?")])
entity(90, 880, 366, "FILM_GENRE", [("PK,FK", "FilmID", "INT"), ("PK", "GenreName", "VARCHAR(30)")])
entity(768, 174, 430, "FILM_CAST", [("PK,FK", "FilmID", "INT"), ("PK,FK", "ActorID", "INT"),
       ("", "CharacterName", "VARCHAR(150)")])
entity(768, 500, 430, "FILM_CREW", [("PK,FK", "FilmID", "INT"), ("PK,FK", "CrewMemberID", "INT"),
       ("PK,FK", "RoleID", "INT")])
entity(768, 880, 430, "PRODUCTION_SCHEDULE", [("PK", "ScheduleID", "INT"), ("FK", "FilmID", "INT"),
       ("FK", "LocationID", "INT"), ("", "FilmingDate", "DATE"), ("", "StartTime", "TIME ?"),
       ("", "EndTime", "TIME ?")])
entity(1500, 152, 400, "ACTOR", [("PK", "ActorID", "INT"), ("", "FirstName", "VARCHAR(100)"),
       ("", "LastName", "VARCHAR(100) ?"), ("", "BirthYear", "SMALLINT ?")])
entity(1500, 470, 400, "CREW_MEMBER", [("PK", "CrewMemberID", "INT"), ("", "FirstName", "VARCHAR(100)"),
       ("", "LastName", "VARCHAR(100)"), ("", "ContactEmail", "VARCHAR(254) ?")])
entity(1500, 760, 400, "ROLE", [("PK", "RoleID", "INT"), ("UQ", "RoleName", "VARCHAR(100)")])
entity(1500, 960, 400, "LOCATION", [("PK", "LocationID", "INT"), ("", "LocationName", "VARCHAR(150)"),
       ("", "Address", "VARCHAR(255) ?"), ("", "City", "VARCHAR(100) ?")])

# ---------------- relationships ----------------
# strong (identifying) = solid line; weak (non-identifying) = dashed line
path([(456, 500), (600, 500), (600, 264), (768, 264)], False)        # FILM - FILM_CAST
end(456, 500, 1, 0, "one"); end(768, 264, -1, 0, "one_many"); text(640, 248, "has cast")
path([(456, 580), (768, 580)], False)                                # FILM - FILM_CREW
end(456, 580, 1, 0, "one"); end(768, 580, -1, 0, "one_many"); text(560, 562, "has crew")
path([(456, 650), (600, 650), (600, 1010), (768, 1010)], True)       # FILM - PRODUCTION_SCHEDULE
end(456, 650, 1, 0, "one"); end(768, 1010, -1, 0, "zero_many"); text(612, 1044, "has sessions")
path([(273, 684), (273, 880)], False)                                # FILM - FILM_GENRE
end(273, 684, 0, 1, "one"); end(273, 880, 0, -1, "zero_many"); text(296, 790, "classified by")
path([(1500, 264), (1198, 264)], False)                              # ACTOR - FILM_CAST
end(1500, 264, -1, 0, "one"); end(1198, 264, 1, 0, "zero_many"); text(1356, 246, "appears in", align="c")
path([(1500, 590), (1198, 590)], False)                              # CREW_MEMBER - FILM_CREW
end(1500, 590, -1, 0, "one"); end(1198, 590, 1, 0, "zero_many"); text(1356, 572, "works on", align="c")
path([(1500, 830), (1344, 830), (1344, 660), (1198, 660)], False)    # ROLE - FILM_CREW
end(1500, 830, -1, 0, "one"); end(1198, 660, 1, 0, "zero_many"); text(1362, 760, "specifies")
text(1362, 790, "role")
path([(1500, 1050), (1198, 1050)], True)                             # LOCATION - PRODUCTION_SCHEDULE
end(1500, 1050, -1, 0, "one"); end(1198, 1050, 1, 0, "zero_many"); text(1356, 1032, "hosts", align="c")

# ---------------- legend ----------------
c.setStrokeColor(EDGE); c.setLineWidth(1.5); c.setFillColor(PANEL)
c.rect(90, Y(1384), 1810, 178, fill=1)
text(110, 1238, "PARTICIPATION", B, 19, HexColor("#3a4358"))
for i, (kind, label) in enumerate([("one", "Exactly one  (1..1)"), ("one_many", "One or more  (1..*)"),
                                   ("zero_many", "Zero or more  (0..*)")]):
    yy = 1274 + 38 * i
    path([(110, yy), (190, yy)], False); end(110, yy, 1, 0, kind); text(210, yy + 8, label, R, 20)
text(560, 1238, "RELATIONSHIP STRENGTH", B, 19, HexColor("#3a4358"))
path([(560, 1274), (650, 1274)], False)
text(670, 1282, "Strong (identifying): parent PK is part of the child PK", R, 20)
path([(560, 1312), (650, 1312)], True)
text(670, 1320, "Weak (non-identifying): parent PK is only an FK in the child", R, 20)
text(560, 1358, "FILM_CAST, FILM_CREW and FILM_GENRE are weak entities.", R, 20, MUTED)
text(1330, 1238, "KEY AND NOTATION", B, 19, HexColor("#3a4358"))
text(1330, 1282, "PK = primary key      FK = foreign key", R, 20)
text(1330, 1320, "UQ = unique      ? = optional (NULL allowed)", R, 20)
text(1330, 1358, "Attributes without ? are required (NOT NULL).", R, 20, MUTED)

c.showPage(); c.save()
