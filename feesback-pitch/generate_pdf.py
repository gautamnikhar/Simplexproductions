#!/usr/bin/env python3
"""
Feesback Pitch Deck — PDF Generator
Personal Branding Services for Shilen Arrow, Founder of Feesback
Color Scheme: Blue (#1B3A5C) + Beige (#F5E6D0)
Font: Montserrat (with Helvetica fallback)
"""

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import os
import glob

# ── Page Setup ──────────────────────────────────────────────────────────────
W, H = landscape((13.333 * inch, 7.5 * inch))

# ── Colors ──────────────────────────────────────────────────────────────────
BLUE_DARK   = HexColor("#1B3A5C")
BLUE_MED    = HexColor("#2C5F8A")
BLUE_LIGHT  = HexColor("#4A90C4")
BEIGE       = HexColor("#F5E6D0")
BEIGE_LIGHT = HexColor("#FAF3EB")
GOLD        = HexColor("#C9A962")
GRAY        = HexColor("#6B6B6B")
DARK_TEXT   = HexColor("#1A1A1A")
BEIGE_BUILD = HexColor("#D4C5AD")

# ── Font Registration ──────────────────────────────────────────────────────
# Try to find and register Montserrat; fallback to Helvetica
FONT = "Helvetica"
FONT_B = "Helvetica-Bold"

script_dir = os.path.dirname(os.path.abspath(__file__))
montserrat_regular = os.path.join(script_dir, "Montserrat-Regular.ttf")
montserrat_bold = os.path.join(script_dir, "Montserrat-Bold.ttf")

if not os.path.exists(montserrat_regular) or not os.path.exists(montserrat_bold):
    montserrat_regular = None
    montserrat_bold = None

if montserrat_regular and montserrat_bold:
    try:
        pdfmetrics.registerFont(TTFont("Montserrat", montserrat_regular))
        pdfmetrics.registerFont(TTFont("Montserrat-Bold", montserrat_bold))
        FONT = "Montserrat"
        FONT_B = "Montserrat-Bold"
        print(f"✅ Montserrat fonts loaded")
    except Exception as e:
        print(f"⚠️  Montserrat registration failed ({e}), using Helvetica")
else:
    print("⚠️  Montserrat not found on system, using Helvetica. Install Montserrat for exact styling.")

# ── Helper Functions ────────────────────────────────────────────────────────

def rect(c, x, y, w, h, fill_color, stroke=False):
    """Draw a filled rectangle. (x, y) is bottom-left in reportlab coords."""
    c.setFillColor(fill_color)
    if stroke:
        c.setStrokeColor(fill_color)
    else:
        c.setStrokeColor(fill_color)
    c.rect(x, y, w, h, fill=1, stroke=0)


def rounded_rect(c, x, y, w, h, fill_color, radius=10):
    c.setFillColor(fill_color)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=0)


def circle(c, cx, cy, r, fill_color):
    c.setFillColor(fill_color)
    c.circle(cx, cy, r, fill=1, stroke=0)


def text(c, x, y, txt, size=18, color=white, bold=False, font=None):
    """Draw text at position. y is baseline."""
    f = font or (FONT_B if bold else FONT)
    c.setFont(f, size)
    c.setFillColor(color)
    c.drawString(x, y, txt)


def text_center(c, x, y, txt, size=18, color=white, bold=False, width=None):
    f = FONT_B if bold else FONT
    c.setFont(f, size)
    c.setFillColor(color)
    tw = c.stringWidth(txt, f, size)
    if width:
        c.drawString(x + (width - tw) / 2, y, txt)
    else:
        c.drawString(x - tw / 2, y, txt)


def text_right(c, x, y, txt, size=18, color=white, bold=False):
    f = FONT_B if bold else FONT
    c.setFont(f, size)
    c.setFillColor(color)
    c.drawRightString(x, y, txt)


def wrapped_text(c, x, y, txt, size, color, bold, max_width, line_height=None):
    """Simple word-wrap text. Returns final y position."""
    f = FONT_B if bold else FONT
    c.setFont(f, size)
    c.setFillColor(color)
    lh = line_height or size * 1.35
    words = txt.split()
    lines = []
    current = ""
    for w in words:
        test = current + " " + w if current else w
        if c.stringWidth(test, f, size) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    for line in lines:
        c.drawString(x, y, line)
        y -= lh
    return y


def multiline_text(c, x, y, txt, size, color, bold, line_height=None):
    """Draw text with explicit newlines."""
    f = FONT_B if bold else FONT
    c.setFont(f, size)
    c.setFillColor(color)
    lh = line_height or size * 1.4
    for line in txt.split("\n"):
        c.drawString(x, y, line)
        y -= lh
    return y


def multiline_center(c, x, y, txt, size, color, bold, width, line_height=None):
    f = FONT_B if bold else FONT
    c.setFont(f, size)
    c.setFillColor(color)
    lh = line_height or size * 1.4
    for line in txt.split("\n"):
        tw = c.stringWidth(line, f, size)
        c.drawString(x + (width - tw) / 2, y, line)
        y -= lh
    return y


def dots_grid(c, x, y, cols, rows, spacing, color, radius=2):
    for r in range(rows):
        for col in range(cols):
            circle(c, x + col * spacing, y - r * spacing, radius, color)


def draw_buildings(c, base_x, base_y):
    """Draw abstract building skyline."""
    # Building 1
    rect(c, base_x, base_y, 1.0 * inch, 3.0 * inch, BLUE_MED)
    for row in range(5):
        rect(c, base_x + 0.15 * inch, base_y + 2.6 * inch - row * 0.5 * inch,
             0.2 * inch, 0.25 * inch, BEIGE_LIGHT)
        rect(c, base_x + 0.55 * inch, base_y + 2.6 * inch - row * 0.5 * inch,
             0.2 * inch, 0.25 * inch, BEIGE_LIGHT)
    # Building 2
    rect(c, base_x + 1.3 * inch, base_y, 1.2 * inch, 2.3 * inch, BLUE_LIGHT)
    for row in range(4):
        rect(c, base_x + 1.5 * inch, base_y + 1.8 * inch - row * 0.45 * inch,
             0.2 * inch, 0.2 * inch, white)
        rect(c, base_x + 1.9 * inch, base_y + 1.8 * inch - row * 0.45 * inch,
             0.2 * inch, 0.2 * inch, white)
    # Building 3
    rect(c, base_x + 2.8 * inch, base_y, 0.8 * inch, 2.7 * inch, BEIGE_BUILD)
    for row in range(4):
        rect(c, base_x + 2.95 * inch, base_y + 2.3 * inch - row * 0.55 * inch,
             0.15 * inch, 0.25 * inch, BLUE_DARK)


# ── Convert coords: slide inches (top-left origin) → PDF points (bottom-left) ──
def Y(slide_y_inches):
    """Convert top-origin y (inches) to bottom-origin y (points)."""
    return H - slide_y_inches * inch


# ══════════════════════════════════════════════════════════════════════════════
# CREATE PDF
# ══════════════════════════════════════════════════════════════════════════════

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "Feesback_Personal_Branding_Pitch_Deck.pdf")
c = canvas.Canvas(output_path, pagesize=(W, H))
c.setTitle("Feesback — Personal Branding Proposal for Shilen Arrow")
c.setAuthor("Personal Branding Agency")
c.setSubject("Marketing Services Pitch Deck")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — COVER
# ══════════════════════════════════════════════════════════════════════════════

# Background
rect(c, 0, 0, W, H, BLUE_DARK)
# Left beige panel
rect(c, 0, 0, 5.5 * inch, H, BEIGE)
# Gold vertical divider
rect(c, 5.2 * inch, 0, 0.08 * inch, H, GOLD)
# Decorative dots
dots_grid(c, 0.5 * inch, H - 0.5 * inch, 5, 5, 0.35 * inch, BLUE_LIGHT, 3)

# Beige panel text
text(c, 0.8 * inch, Y(2.2), "PERSONAL BRANDING", 14, BLUE_MED, bold=True)
text(c, 0.8 * inch, Y(3.1), "PROPOSAL", 42, BLUE_DARK, bold=True)
rect(c, 0.8 * inch, Y(3.5), 1.5 * inch, 3, GOLD)
text(c, 0.8 * inch, Y(3.9), "for", 16, GRAY)
text(c, 0.8 * inch, Y(4.6), "SHILEN ARROW", 36, BLUE_DARK, bold=True)
text(c, 0.8 * inch, Y(5.25), "Founder — Feesback", 16, BLUE_MED)

# Right panel
text(c, 6.2 * inch, Y(1.75), "FEESBACK", 16, BEIGE, bold=True)
rect(c, 6.2 * inch, Y(2.2), 1.0 * inch, 2, GOLD)

# Buildings
draw_buildings(c, 7.0 * inch, 0.8 * inch)

# Connection nodes
for (cx, cy) in [(6.5, 3.8), (6.8, 2.5), (6.1, 3.1)]:
    circle(c, cx * inch, Y(cy), 0.15 * inch, GOLD)

# Bottom gold bar
rect(c, 0, 0, W, 0.65 * inch, GOLD)
text_center(c, 0, 0.22 * inch,
            "Elevating Real Estate Leadership Through Strategic Personal Branding",
            14, BLUE_DARK, bold=True, width=W)

c.showPage()


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — WHO WE ARE
# ══════════════════════════════════════════════════════════════════════════════

rect(c, 0, 0, W, H, BEIGE_LIGHT)
rect(c, 0, H - 0.12 * inch, W, 0.12 * inch, BLUE_DARK)
rect(c, 0, H - 0.16 * inch, W, 0.04 * inch, GOLD)

text(c, 0.8 * inch, Y(0.85), "WHO WE ARE", 12, BLUE_LIGHT, bold=True)
text(c, 0.8 * inch, Y(1.4), "Your Strategic Branding Partner", 36, BLUE_DARK, bold=True)
rect(c, 0.8 * inch, Y(1.9), 2.0 * inch, 3, GOLD)

wrapped_text(c, 0.8 * inch, Y(2.5), (
    "We are a boutique personal branding agency specializing in building "
    "powerful, authentic brands for founders and executives in the tech "
    "and real estate space."
), 15, DARK_TEXT, False, 6.0 * inch)

wrapped_text(c, 0.8 * inch, Y(3.5), (
    "Our mission is to transform Shilen Arrow's expertise and vision "
    "into a magnetic personal brand that attracts top agents, buyers, "
    "and industry partnerships to Feesback."
), 15, DARK_TEXT, False, 6.0 * inch)

# Right side cards
card_items = [
    ("01", "Strategic Positioning", "Defining your unique narrative in prop-tech"),
    ("02", "Content Architecture", "LinkedIn, video, thought leadership pillars"),
    ("03", "Visual Identity", "Cohesive brand aesthetics across platforms"),
    ("04", "Community Building", "Engaged audience of agents & buyers"),
]
for idx, (num, title, desc) in enumerate(card_items):
    cy = Y(2.5 + idx * 1.15)
    rounded_rect(c, 8.0 * inch, cy - 0.3 * inch, 4.8 * inch, 0.95 * inch, white)
    circle(c, 8.5 * inch, cy + 0.15 * inch, 0.25 * inch, BLUE_DARK)
    text_center(c, 8.5 * inch, cy + 0.08 * inch, num, 15, white, bold=True)
    text(c, 9.0 * inch, cy + 0.3 * inch, title, 15, BLUE_DARK, bold=True)
    text(c, 9.0 * inch, cy - 0.05 * inch, desc, 11, GRAY)

dots_grid(c, 0.5 * inch, Y(5.8), 8, 3, 0.3 * inch, BLUE_LIGHT, 2.5)

c.showPage()


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — WHY PERSONAL BRANDING
# ══════════════════════════════════════════════════════════════════════════════

rect(c, 0, 0, W, H, BLUE_DARK)
rect(c, 0, 0, 0.12 * inch, H, GOLD)

text(c, 0.8 * inch, Y(0.85), "THE OPPORTUNITY", 12, GOLD, bold=True)
text(c, 0.8 * inch, Y(1.5), "Why Personal Branding Matters for Shilen Arrow", 32, white, bold=True)
rect(c, 0.8 * inch, Y(1.9), 2.5 * inch, 3, GOLD)

stats = [
    ("82%", "of consumers trust a\ncompany more when its\nfounder is active on\nsocial media"),
    ("77%", "of buyers research\nthe company founder\nbefore making a\npurchase decision"),
    ("3.5×", "more engagement\nwhen content comes\nfrom a personal\nbrand vs company"),
    ("64%", "of real estate leads\ncome from referrals\ndriven by personal\nreputation"),
]

for i, (number, label) in enumerate(stats):
    x = (0.8 + i * 3.1) * inch
    rounded_rect(c, x, Y(4.9), 2.8 * inch, 2.4 * inch, BLUE_MED)
    text(c, x + 0.3 * inch, Y(2.8), number, 42, GOLD, bold=True)
    multiline_text(c, x + 0.3 * inch, Y(3.6), label, 12, BEIGE_LIGHT, False)

# Bottom insight
rounded_rect(c, 0.8 * inch, Y(6.9), 11.7 * inch, 1.4 * inch, BEIGE)
text(c, 1.2 * inch, Y(5.75), "THE INSIGHT", 12, BLUE_DARK, bold=True)
wrapped_text(c, 1.2 * inch, Y(6.15),
    "Feesback connects real estate agents with customers — but trust starts with WHO is behind the platform. "
    "Shilen Arrow's personal brand becomes the trust signal that drives platform adoption by agents and buyers alike.",
    13, BLUE_DARK, False, 10.5 * inch)

c.showPage()


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — SCOPE OF WORK
# ══════════════════════════════════════════════════════════════════════════════

rect(c, 0, 0, W, H, BEIGE_LIGHT)
rect(c, 0, H - 0.12 * inch, W, 0.12 * inch, BLUE_DARK)
rect(c, 0, H - 0.16 * inch, W, 0.04 * inch, GOLD)

text(c, 0.8 * inch, Y(0.85), "SCOPE OF WORK", 12, BLUE_LIGHT, bold=True)
text(c, 0.8 * inch, Y(1.4), "What We'll Build Together", 36, BLUE_DARK, bold=True)
rect(c, 0.8 * inch, Y(1.85), 2.0 * inch, 3, GOLD)

columns = [
    ("BRAND FOUNDATION", BLUE_DARK, [
        "Brand audit & competitor analysis",
        "Personal brand positioning statement",
        "Tone of voice & messaging guide",
        "Bio & headline optimization",
        "Visual brand direction",
    ]),
    ("CONTENT STRATEGY", BLUE_MED, [
        "Content pillar development",
        "Monthly content calendar",
        "LinkedIn optimization & strategy",
        "Thought leadership articles",
        "Video content direction",
    ]),
    ("GROWTH & VISIBILITY", BLUE_LIGHT, [
        "Engagement strategy playbook",
        "PR & media outreach plan",
        "Speaking opportunity sourcing",
        "Network expansion strategy",
        "Monthly analytics & reporting",
    ]),
]

for i, (title, strip_color, items) in enumerate(columns):
    x = (0.8 + i * 4.1) * inch
    # White card
    rounded_rect(c, x, Y(7.1), 3.8 * inch, 4.65 * inch, white)
    # Colored header strip
    rect(c, x, Y(2.85), 3.8 * inch, 0.5 * inch, strip_color)
    # Number badge
    circle(c, x + 0.35 * inch, Y(2.6), 0.18 * inch, GOLD)
    text_center(c, x + 0.35 * inch, Y(2.66), str(i + 1), 14, BLUE_DARK, bold=True)
    # Title
    text(c, x + 0.7 * inch, Y(2.68), title, 13, white, bold=True)
    # Items
    for j, item in enumerate(items):
        iy = Y(3.3 + j * 0.65)
        circle(c, x + 0.35 * inch, iy + 0.04 * inch, 0.12 * inch, BEIGE)
        text_center(c, x + 0.35 * inch, iy - 0.03 * inch, "✓", 10, BLUE_DARK, bold=True)
        text(c, x + 0.6 * inch, iy, item, 12, DARK_TEXT)

c.showPage()


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — CONTENT PILLARS
# ══════════════════════════════════════════════════════════════════════════════

rect(c, 0, 0, W, H, BLUE_DARK)
rect(c, 0, 0, 0.12 * inch, H, GOLD)

text(c, 0.8 * inch, Y(0.75), "CONTENT PILLARS", 12, GOLD, bold=True)
text(c, 0.8 * inch, Y(1.35), "Shilen Arrow's Brand Narrative", 34, white, bold=True)
rect(c, 0.8 * inch, Y(1.75), 2.5 * inch, 3, GOLD)
wrapped_text(c, 0.8 * inch, Y(2.1),
    "Five strategic content pillars to establish authority and build trust in the real estate tech space.",
    14, BEIGE, False, 10 * inch)

pillars = [
    ("VISIONARY\nFOUNDER", "The future of real estate\ntech and how Feesback\nis shaping it", "▲"),
    ("INDUSTRY\nINSIDER", "Market trends, data insights,\nand what agents & buyers\nreally need", "◆"),
    ("BUILDER'S\nJOURNEY", "Behind-the-scenes of\ngrowing Feesback — wins,\nchallenges, lessons", "■"),
    ("COMMUNITY\nCHAMPION", "Spotlighting agents, success\nstories, and the people\nwho make real estate human", "●"),
    ("THOUGHT\nLEADER", "Bold takes on prop-tech,\ncustomer experience, and\nthe agent economy", "★"),
]

for i, (title, desc, icon) in enumerate(pillars):
    x = (0.5 + i * 2.5) * inch
    # Card
    rounded_rect(c, x, Y(7.0), 2.3 * inch, 4.1 * inch, BLUE_MED)
    # Gold top accent
    rect(c, x, Y(2.98), 2.3 * inch, 0.06 * inch, GOLD)
    # Icon circle
    circle(c, x + 1.15 * inch, Y(3.5), 0.35 * inch, BEIGE)
    text_center(c, x + 1.15 * inch, Y(3.58), icon, 22, BLUE_DARK, bold=True)
    # Title
    multiline_center(c, x + 0.1 * inch, Y(4.2), title, 14, white, True, 2.1 * inch)
    # Separator
    rect(c, x + 0.6 * inch, Y(5.05), 1.1 * inch, 2, GOLD)
    # Desc
    multiline_center(c, x + 0.1 * inch, Y(5.3), desc, 10, BEIGE_LIGHT, False, 2.1 * inch)

c.showPage()


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — 90-DAY ROADMAP
# ══════════════════════════════════════════════════════════════════════════════

rect(c, 0, 0, W, H, BEIGE_LIGHT)
rect(c, 0, H - 0.12 * inch, W, 0.12 * inch, BLUE_DARK)
rect(c, 0, H - 0.16 * inch, W, 0.04 * inch, GOLD)

text(c, 0.8 * inch, Y(0.85), "ROADMAP", 12, BLUE_LIGHT, bold=True)
text(c, 0.8 * inch, Y(1.4), "90-Day Brand Launch Plan", 36, BLUE_DARK, bold=True)
rect(c, 0.8 * inch, Y(1.85), 2.0 * inch, 3, GOLD)

# Timeline line
rect(c, 1.5 * inch, Y(3.35), 10.5 * inch, 0.04 * inch, BLUE_DARK)

phases = [
    ("MONTH 1", "Foundation", "Brand audit\nPositioning\nVisual identity\nProfile optimization\nContent pillar setup"),
    ("MONTH 2", "Activation", "Content calendar launch\nLinkedIn strategy go-live\nFirst thought pieces\nEngagement campaign\nVideo content kickoff"),
    ("MONTH 3", "Amplification", "PR outreach begins\nSpeaking pitches sent\nCommunity engagement\nPerformance review\nStrategy refinement"),
]

for i, (month, phase, details) in enumerate(phases):
    x = (1.5 + i * 3.9) * inch
    cx = x + 1.6 * inch
    # Timeline node
    circle(c, cx, Y(3.32), 0.2 * inch, BLUE_DARK)
    text_center(c, cx, Y(3.4), str(i + 1), 14, white, bold=True)
    # Labels above
    text_center(c, cx, Y(2.4), month, 11, BLUE_LIGHT, bold=True)
    text_center(c, cx, Y(2.85), phase, 20, BLUE_DARK, bold=True)
    # Card below
    rounded_rect(c, x + 0.1 * inch, Y(6.9), 3.0 * inch, 2.9 * inch, white)
    multiline_text(c, x + 0.3 * inch, Y(4.15), details, 12, DARK_TEXT, False)

c.showPage()


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — PRICING
# ══════════════════════════════════════════════════════════════════════════════

rect(c, 0, 0, W, H, BLUE_DARK)
rect(c, 0, 0, 0.12 * inch, H, GOLD)

text(c, 0.8 * inch, Y(0.75), "INVESTMENT", 12, GOLD, bold=True)
text(c, 0.8 * inch, Y(1.35), "Choose Your Growth Plan", 36, white, bold=True)
rect(c, 0.8 * inch, Y(1.75), 2.5 * inch, 3, GOLD)
wrapped_text(c, 0.8 * inch, Y(2.1),
    "Two tailored packages designed for maximum brand impact and ROI.",
    14, BEIGE, False, 10 * inch)

# ── Essential Package ($1,200) ──
x1 = 1.5 * inch
rounded_rect(c, x1, Y(7.1), 5.0 * inch, 4.4 * inch, BLUE_MED)
# Beige header area
rect(c, x1, Y(3.8), 5.0 * inch, 1.1 * inch, BEIGE)
text(c, x1 + 0.4 * inch, Y(2.95), "ESSENTIAL", 14, BLUE_DARK, bold=True)
text(c, x1 + 0.4 * inch, Y(3.55), "$1,200", 38, BLUE_DARK, bold=True)
text(c, x1 + 2.8 * inch, Y(3.45), "/ month", 13, GRAY)

essential_items = [
    "Brand audit & positioning",
    "Profile optimization (LinkedIn)",
    "Content pillar strategy",
    "8 content pieces / month",
    "Monthly content calendar",
    "Basic analytics report",
    "Email support",
]
for j, item in enumerate(essential_items):
    iy = Y(4.15 + j * 0.4)
    text(c, x1 + 0.4 * inch, iy, "→  " + item, 12, white)

# ── Premium Package ($1,500) — HIGHLIGHTED ──
x2 = 7.0 * inch
# Gold glow border
rounded_rect(c, x2 - 0.05 * inch, Y(7.25), 5.1 * inch, 4.75 * inch, GOLD)
rounded_rect(c, x2, Y(7.2), 5.0 * inch, 4.65 * inch, white)

# Recommended badge
rounded_rect(c, x2 + 1.2 * inch, Y(2.55), 2.5 * inch, 0.35 * inch, GOLD)
text_center(c, x2 + 2.45 * inch, Y(2.45), "★  RECOMMENDED", 10, BLUE_DARK, bold=True)

text(c, x2 + 0.4 * inch, Y(2.9), "PREMIUM", 14, BLUE_DARK, bold=True)
text(c, x2 + 0.4 * inch, Y(3.55), "$1,500", 38, BLUE_DARK, bold=True)
text(c, x2 + 2.8 * inch, Y(3.45), "/ month", 13, GRAY)

premium_items = [
    ("Everything in Essential, plus:", True),
    ("12 content pieces / month", False),
    ("Video content strategy & scripts", False),
    ("Thought leadership ghostwriting", False),
    ("PR & media outreach", False),
    ("Speaking opportunity sourcing", False),
    ("Weekly strategy calls", False),
    ("Priority support", False),
]
for j, (item, is_bold) in enumerate(premium_items):
    iy = Y(4.15 + j * 0.4)
    text(c, x2 + 0.4 * inch, iy, "→  " + item, 12, BLUE_DARK, bold=is_bold)

c.showPage()


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — WHY CHOOSE US
# ══════════════════════════════════════════════════════════════════════════════

rect(c, 0, 0, W, H, BEIGE_LIGHT)
rect(c, 0, H - 0.12 * inch, W, 0.12 * inch, BLUE_DARK)
rect(c, 0, H - 0.16 * inch, W, 0.04 * inch, GOLD)

text(c, 0.8 * inch, Y(0.85), "WHY CHOOSE US", 12, BLUE_LIGHT, bold=True)
text(c, 0.8 * inch, Y(1.4), "What Sets Us Apart", 36, BLUE_DARK, bold=True)
rect(c, 0.8 * inch, Y(1.85), 2.0 * inch, 3, GOLD)

diff_items = [
    ("Real Estate Focus", "We understand the real estate and prop-tech landscape inside out. "
     "Your brand strategy won't be generic — it'll speak directly to agents and home buyers."),
    ("Founder-First Approach", "We don't build company brands. We build people brands. "
     "Everything is crafted around Shilen's unique voice, story, and vision."),
    ("Data-Driven Creative", "Every piece of content is backed by engagement data and audience "
     "insights. We optimize what works and pivot fast on what doesn't."),
    ("Full-Service Execution", "Strategy is just the start. We create, publish, engage, and report — "
     "so Shilen can focus on building Feesback while we build the brand."),
]

for i, (title, desc) in enumerate(diff_items):
    row = i // 2
    col = i % 2
    x = (0.8 + col * 6.2) * inch
    y_top = (2.3 + row * 2.4)
    # Card
    rounded_rect(c, x, Y(y_top + 2.0), 5.8 * inch, 2.0 * inch, white)
    # Gold left accent
    rect(c, x, Y(y_top + 2.0), 0.06 * inch, 2.0 * inch, GOLD)
    # Number circle
    circle(c, x + 0.5 * inch, Y(y_top + 0.55), 0.22 * inch, BLUE_DARK)
    text_center(c, x + 0.5 * inch, Y(y_top + 0.62), str(i + 1), 16, white, bold=True)
    # Title
    text(c, x + 1.0 * inch, Y(y_top + 0.55), title, 17, BLUE_DARK, bold=True)
    # Description
    wrapped_text(c, x + 1.0 * inch, Y(y_top + 1.05), desc, 12, GRAY, False, 4.5 * inch)

c.showPage()


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — PROJECTED OUTCOMES
# ══════════════════════════════════════════════════════════════════════════════

rect(c, 0, 0, W, H, BLUE_DARK)
rect(c, 0, 0, 0.12 * inch, H, GOLD)

text(c, 0.8 * inch, Y(0.75), "PROJECTED OUTCOMES", 12, GOLD, bold=True)
text(c, 0.8 * inch, Y(1.35), "What Success Looks Like", 34, white, bold=True)
rect(c, 0.8 * inch, Y(1.75), 2.5 * inch, 3, GOLD)

kpis = [
    ("5,000+", "LinkedIn\nFollowers", "Targeted growth in\n90 days"),
    ("3×", "Engagement\nRate", "Above industry\naverage"),
    ("15+", "Media\nMentions", "PR & thought\nleadership hits"),
    ("50%", "Inbound\nGrowth", "More organic leads\nto Feesback"),
]

for i, (metric, label, desc) in enumerate(kpis):
    x = (0.8 + i * 3.1) * inch
    cx = x + 1.4 * inch
    rounded_rect(c, x, Y(5.6), 2.8 * inch, 3.2 * inch, BLUE_MED)
    # Metric circle
    circle(c, cx, Y(3.3), 0.7 * inch, BEIGE)
    text_center(c, cx, Y(3.2), metric, 30, BLUE_DARK, bold=True)
    # Label
    multiline_center(c, x + 0.2 * inch, Y(4.5), label, 15, white, True, 2.4 * inch)
    # Desc
    multiline_center(c, x + 0.2 * inch, Y(5.2), desc, 11, BEIGE_LIGHT, False, 2.4 * inch)

# Bottom bar
rounded_rect(c, 0.8 * inch, Y(6.95), 11.7 * inch, 0.95 * inch, BEIGE)
wrapped_text(c, 1.2 * inch, Y(6.25),
    "We don't just promise results — we track, measure, and optimize every step. "
    "Monthly reports keep you informed and confident in the ROI of your brand investment.",
    13, BLUE_DARK, False, 10.5 * inch)

c.showPage()


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — NEXT STEPS
# ══════════════════════════════════════════════════════════════════════════════

rect(c, 0, 0, W, H, BEIGE_LIGHT)
# Header area
rect(c, 0, H - 3.0 * inch, W, 3.0 * inch, BLUE_DARK)
rect(c, 0, H - 3.06 * inch, W, 0.06 * inch, GOLD)

dots_grid(c, 10.0 * inch, H - 0.5 * inch, 6, 5, 0.3 * inch, BLUE_MED, 3)

text(c, 0.8 * inch, Y(0.75), "NEXT STEPS", 12, GOLD, bold=True)
text(c, 0.8 * inch, Y(1.35), "Let's Build Something", 38, white, bold=True)
text(c, 0.8 * inch, Y(1.95), "Extraordinary", 38, white, bold=True)

steps = [
    ("01", "Discovery Call", "Let's dive deep into Shilen's vision, goals, and brand aspirations for Feesback."),
    ("02", "Strategy Proposal", "We'll deliver a customized brand strategy and content roadmap within 5 business days."),
    ("03", "Kick-Off", "Once approved, we hit the ground running with brand foundation work in Week 1."),
]

for i, (num, title, desc) in enumerate(steps):
    x = (0.8 + i * 4.1) * inch
    rounded_rect(c, x, Y(5.6), 3.8 * inch, 1.9 * inch, white)
    rect(c, x, Y(3.76), 3.8 * inch, 0.06 * inch, GOLD)
    circle(c, x + 0.45 * inch, Y(4.2), 0.22 * inch, BLUE_DARK)
    text_center(c, x + 0.45 * inch, Y(4.28), num, 15, white, bold=True)
    text(c, x + 0.9 * inch, Y(4.22), title, 17, BLUE_DARK, bold=True)
    wrapped_text(c, x + 0.2 * inch, Y(4.75), desc, 12, GRAY, False, 3.3 * inch)

# CTA bar
rounded_rect(c, 3.5 * inch, Y(6.95), 6.3 * inch, 0.9 * inch, BLUE_DARK)
text_center(c, 3.5 * inch, Y(6.35), "Ready to elevate the Feesback brand?",
            17, white, bold=True, width=6.3 * inch)
text_center(c, 3.5 * inch, Y(6.7), "Let's schedule a call  →  [Your Email]  |  [Your Phone]",
            12, BEIGE, width=6.3 * inch)

c.showPage()


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — THANK YOU
# ══════════════════════════════════════════════════════════════════════════════

rect(c, 0, 0, W, H, BLUE_DARK)
# Left beige panel
rect(c, 0, 0, 5.5 * inch, H, BEIGE)
# Gold divider
rect(c, 5.2 * inch, 0, 0.08 * inch, H, GOLD)

# Decorative dots
dots_grid(c, 0.5 * inch, 2.0 * inch, 5, 4, 0.35 * inch, BLUE_LIGHT, 2.5)

# Buildings on left
draw_buildings(c, 1.0 * inch, 0.55 * inch)

# Right side content
text(c, 6.2 * inch, Y(2.5), "THANK YOU", 48, white, bold=True)
rect(c, 6.2 * inch, Y(3.1), 2.0 * inch, 3, GOLD)

multiline_text(c, 6.2 * inch, Y(3.5),
    "We're excited about the opportunity to build\n"
    "Shilen Arrow's personal brand and drive\n"
    "Feesback's growth through strategic branding.",
    15, BEIGE, False)

text(c, 6.2 * inch, Y(5.0), "Prepared exclusively for", 12, GRAY)
text(c, 6.2 * inch, Y(5.5), "SHILEN ARROW", 28, white, bold=True)
text(c, 6.2 * inch, Y(5.95), "Founder, Feesback", 16, GOLD)

# Bottom gold bar
rect(c, 0, 0, W, 0.5 * inch, GOLD)
text_center(c, 0, 0.18 * inch, "Confidential  |  Prepared for Feesback",
            11, BLUE_DARK, width=W)

c.showPage()


# ── Save ────────────────────────────────────────────────────────────────────
c.save()
print(f"✅ PDF saved to: {output_path}")
print(f"📊 Total pages: 11")
