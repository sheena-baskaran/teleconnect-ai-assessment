import re
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, Preformatted, ListFlowable, ListItem
)
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.lib.colors import HexColor
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

# ── Colour palette (forest green / gold / slate) ─────────────────────────────
BLUE_DARK  = HexColor("#1C3530")   # header bar, H1, table header
BLUE_MID   = HexColor("#2D6A4F")   # H2
BLUE_LIGHT = HexColor("#52796F")   # H3, accent rule
GREY_DARK  = HexColor("#3D4F4A")   # H4
GREY_MID   = HexColor("#5E706A")   # footer / caption
GREY_LIGHT = HexColor("#EEF2F0")   # alt table rows
GREY_LINE  = HexColor("#BCC9C3")   # grid lines
GOLD       = HexColor("#C59B31")   # accent lines
WHITE      = colors.white
BLACK      = HexColor("#1E2820")   # body text
CODE_BG    = HexColor("#F3F6F4")
BT         = chr(96)               # backtick — avoids encoding corruption in tooling


# ── Page template with header / footer ───────────────────────────────────────
class TeleConnectDoc(BaseDocTemplate):
    def __init__(self, filename, doc_title="", **kw):
        self.doc_title = doc_title
        BaseDocTemplate.__init__(self, filename, **kw)
        W, H = A4
        frame = Frame(
            1.8*cm, 2.5*cm, W - 3.6*cm, H - 4.8*cm,
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="main"
        )
        self.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=self._chrome)])

    def _chrome(self, canvas, doc):
        W, H = A4
        canvas.saveState()
        canvas.setFillColor(BLUE_DARK)
        canvas.rect(0, H - 1.8*cm, W, 1.8*cm, fill=1, stroke=0)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.setFillColor(WHITE)
        canvas.drawString(1.8*cm, H - 1.1*cm, "TeleConnect AI Platform")
        canvas.setFont("Helvetica", 9)
        tw = canvas.stringWidth(self.doc_title, "Helvetica", 9)
        canvas.drawString(W - 1.8*cm - tw, H - 1.1*cm, self.doc_title)
        canvas.setStrokeColor(GOLD)
        canvas.setLineWidth(2.5)
        canvas.line(0, H - 1.85*cm, W, H - 1.85*cm)
        canvas.setFillColor(GREY_LIGHT)
        canvas.rect(0, 0, W, 1.8*cm, fill=1, stroke=0)
        canvas.setStrokeColor(GREY_LINE)
        canvas.setLineWidth(0.5)
        canvas.line(0, 1.8*cm, W, 1.8*cm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GREY_MID)
        canvas.drawString(1.8*cm, 0.65*cm, "Confidential -- Internal Use Only | June 2026")
        ps = "Page %d" % doc.page
        pw = canvas.stringWidth(ps, "Helvetica", 8)
        canvas.drawString(W - 1.8*cm - pw, 0.65*cm, ps)
        canvas.restoreState()


# ── Architecture diagram (replaces ASCII art in technical_design.md) ──────────
def make_arch_diagram():
    """Draw the on-prem system architecture as a proper vector diagram."""

    FG   = HexColor("#1C3530")
    G2   = HexColor("#2D6A4F")
    G3   = HexColor("#52796F")

    W = 17.4 * cm
    H = 19.8 * cm
    d = Drawing(W, H)

    # ── outer cluster border ──────────────────────────────────────────────────
    d.add(Rect(0.1*cm, 0.1*cm, W - 0.2*cm, H - 0.2*cm,
               rx=7, ry=7,
               fillColor=HexColor("#F4F8F5"),
               strokeColor=FG, strokeWidth=1.8))

    # cluster title bar
    d.add(Rect(0.1*cm, H - 1.35*cm, W - 0.2*cm, 1.25*cm,
               rx=7, ry=7,
               fillColor=FG, strokeColor=None))
    d.add(Rect(0.1*cm, H - 1.35*cm, W - 0.2*cm, 0.6*cm,
               fillColor=FG, strokeColor=None))          # flatten bottom
    d.add(String(W / 2, H - 0.78*cm,
                 "ON-PREMISE CLUSTER   |   AIR-GAPPED   |   No External Network Access",
                 fontSize=8.5, fontName="Helvetica-Bold",
                 fillColor=WHITE, textAnchor="middle"))

    # ── zone backgrounds ──────────────────────────────────────────────────────
    # Data plane  (y: 8.4 to 18.1)
    d.add(Rect(0.25*cm, 8.4*cm, W - 0.5*cm, 9.7*cm,
               rx=5, ry=5,
               fillColor=HexColor("#EDF4F0"),
               strokeColor=G2, strokeWidth=0.7))
    d.add(String(0.75*cm, 17.8*cm, "DATA PLANE",
                 fontSize=7, fontName="Helvetica-Bold",
                 fillColor=G2, textAnchor="start"))

    # Observability (y: 4.0 to 8.0)
    d.add(Rect(0.25*cm, 4.0*cm, W - 0.5*cm, 4.0*cm,
               rx=5, ry=5,
               fillColor=HexColor("#EDF1F8"),
               strokeColor=HexColor("#4A6C9E"), strokeWidth=0.7))
    d.add(String(0.75*cm, 7.7*cm, "OBSERVABILITY PLANE",
                 fontSize=7, fontName="Helvetica-Bold",
                 fillColor=HexColor("#2C4A7A"), textAnchor="start"))

    # Batch / offline (y: 0.25 to 3.6)
    d.add(Rect(0.25*cm, 0.25*cm, W - 0.5*cm, 3.55*cm,
               rx=5, ry=5,
               fillColor=HexColor("#F8F2E8"),
               strokeColor=HexColor("#8B6914"), strokeWidth=0.7))
    d.add(String(0.75*cm, 3.55*cm, "BATCH / OFFLINE PROCESSES",
                 fontSize=7, fontName="Helvetica-Bold",
                 fillColor=HexColor("#6B4A1C"), textAnchor="start"))

    # ── component box helper ──────────────────────────────────────────────────
    def box(x, y, w, h, title, sub1="", sub2="", hdr_col=None, stroke_col=None):
        hc = hdr_col or G2
        sc = stroke_col or G2
        hh = 0.72   # header strip height

        d.add(Rect(x*cm, y*cm, w*cm, h*cm,
                   rx=5, ry=5,
                   fillColor=WHITE, strokeColor=sc, strokeWidth=1.4))
        d.add(Rect(x*cm, (y + h - hh)*cm, w*cm, hh*cm,
                   rx=5, ry=5,
                   fillColor=hc, strokeColor=None))
        d.add(Rect(x*cm, (y + h - hh)*cm, w*cm, hh * 0.45*cm,
                   fillColor=hc, strokeColor=None))         # flatten bottom half
        d.add(String((x + w/2)*cm, (y + h - hh/2 - 0.07)*cm, title,
                     fontSize=8, fontName="Helvetica-Bold",
                     fillColor=WHITE, textAnchor="middle"))
        mid_y = y + (h - hh) * 0.52
        if sub1:
            d.add(String((x + w/2)*cm, (mid_y + 0.22)*cm, sub1,
                         fontSize=6.8, fontName="Helvetica",
                         fillColor=G3, textAnchor="middle"))
        if sub2:
            d.add(String((x + w/2)*cm, (mid_y - 0.25)*cm, sub2,
                         fontSize=6.8, fontName="Helvetica",
                         fillColor=G3, textAnchor="middle"))

    # ── arrow helper ─────────────────────────────────────────────────────────
    def arrow(x1, y1, x2, y2, label=""):
        """Straight arrow with arrowhead at (x2, y2)."""
        d.add(Line(x1*cm, y1*cm, x2*cm, y2*cm,
                   strokeColor=FG, strokeWidth=1.2))
        dx = x2 - x1; dy = y2 - y1
        L = (dx**2 + dy**2) ** 0.5
        if L < 0.01:
            return
        ux, uy = dx/L, dy/L
        px, py = -uy, ux
        s = 0.22
        pts = [x2*cm, y2*cm,
               (x2 - s*ux + s*0.5*px)*cm, (y2 - s*uy + s*0.5*py)*cm,
               (x2 - s*ux - s*0.5*px)*cm, (y2 - s*uy - s*0.5*py)*cm]
        d.add(Polygon(pts, fillColor=FG, strokeColor=None))
        if label:
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2 + 0.2
            d.add(String(mx*cm, my*cm, label,
                         fontSize=6, fontName="Helvetica-Oblique",
                         fillColor=HexColor("#52796F"), textAnchor="middle"))

    # ── data plane components ─────────────────────────────────────────────────
    #   Rep UI
    box(0.5,  14.8, 2.6, 2.3,
        "Rep UI",
        "Retention Reps",
        "API / CLI Client")

    #   Agent Service (centre-piece, dark header)
    box(5.0,  13.3, 4.4, 4.0,
        "Agent Service",
        "agent.py  +  tools.py",
        "FastAPI  |  Session Mgmt",
        hdr_col=FG, stroke_col=FG)

    #   vLLM Server (purple header to distinguish)
    box(11.8, 12.8, 5.0, 4.7,
        "vLLM Inference Server",
        "Mistral 7B Instruct v0.3",
        "INT4 GPTQ  |  2x NVIDIA T4 GPU",
        hdr_col=HexColor("#3D2060"), stroke_col=HexColor("#3D2060"))

    #   Churn Model Service
    box(5.0,  9.0,  4.4, 2.8,
        "Churn Model Service",
        "FastAPI  |  model.joblib",
        "GradientBoosting + Preprocessing")

    # ── arrows ────────────────────────────────────────────────────────────────
    # Rep UI  →  Agent Service
    arrow(3.1, 15.95, 5.0, 15.3, "query")

    # Agent Service  →  vLLM
    arrow(9.4, 15.3, 11.8, 15.15, "chat completion")

    # Agent Service  →  Churn Model (downward)
    arrow(7.2, 13.3, 7.2, 11.8, "predict()")

    # ── observability boxes ───────────────────────────────────────────────────
    obs = [
        ("Prometheus",  "metrics scrape",   HexColor("#E8F0FD"), HexColor("#1A56B0")),
        ("Grafana",     "dashboards",        HexColor("#FFF3E0"), HexColor("#B84000")),
        ("Loki",        "log aggregation",   HexColor("#E8F5E9"), HexColor("#256029")),
        ("MLflow",      "model versioning",  HexColor("#FCE4EC"), HexColor("#8B1A2A")),
        ("PostgreSQL",  "interaction log",   HexColor("#EDE7F6"), HexColor("#512DA8")),
    ]
    n_obs = len(obs)
    gap_o = 0.28
    w_obs = (17.4 - 0.45 - (n_obs - 1) * gap_o - 0.45) / n_obs
    for idx, (title, sub, bg, sc) in enumerate(obs):
        ox = 0.45 + idx * (w_obs + gap_o)
        oy, oh = 4.45, 2.85
        d.add(Rect(ox*cm, oy*cm, w_obs*cm, oh*cm,
                   rx=4, ry=4, fillColor=bg, strokeColor=sc, strokeWidth=1.2))
        hh = 0.65
        d.add(Rect(ox*cm, (oy + oh - hh)*cm, w_obs*cm, hh*cm,
                   rx=4, ry=4, fillColor=sc, strokeColor=None))
        d.add(Rect(ox*cm, (oy + oh - hh)*cm, w_obs*cm, hh*0.45*cm,
                   fillColor=sc, strokeColor=None))
        d.add(String((ox + w_obs/2)*cm, (oy + oh - hh/2 - 0.06)*cm, title,
                     fontSize=7.5, fontName="Helvetica-Bold",
                     fillColor=WHITE, textAnchor="middle"))
        d.add(String((ox + w_obs/2)*cm, (oy + oh/2 - 0.22)*cm, sub,
                     fontSize=6.5, fontName="Helvetica",
                     fillColor=sc, textAnchor="middle"))

    # ── batch boxes ───────────────────────────────────────────────────────────
    bat = [
        ("Eval Runner",      "nightly  |  local LLM judge"),
        ("Model Retraining", "on drift trigger / quarterly"),
        ("Model Registry",   "NFS  |  joblib + SHA-256 hash"),
    ]
    n_bat = len(bat)
    gap_b = 0.35
    w_bat = (17.4 - 0.45 - (n_bat - 1) * gap_b - 0.45) / n_bat
    sc_b  = HexColor("#7A5C20")
    bg_b  = HexColor("#FBF5E6")
    for idx, (title, sub) in enumerate(bat):
        bx = 0.45 + idx * (w_bat + gap_b)
        by, bh = 0.55, 2.55
        d.add(Rect(bx*cm, by*cm, w_bat*cm, bh*cm,
                   rx=4, ry=4, fillColor=bg_b, strokeColor=sc_b, strokeWidth=1.2))
        hh = 0.65
        d.add(Rect(bx*cm, (by + bh - hh)*cm, w_bat*cm, hh*cm,
                   rx=4, ry=4, fillColor=sc_b, strokeColor=None))
        d.add(Rect(bx*cm, (by + bh - hh)*cm, w_bat*cm, hh*0.45*cm,
                   fillColor=sc_b, strokeColor=None))
        d.add(String((bx + w_bat/2)*cm, (by + bh - hh/2 - 0.06)*cm, title,
                     fontSize=7.5, fontName="Helvetica-Bold",
                     fillColor=WHITE, textAnchor="middle"))
        d.add(String((bx + w_bat/2)*cm, (by + bh/2 - 0.2)*cm, sub,
                     fontSize=6.5, fontName="Helvetica",
                     fillColor=sc_b, textAnchor="middle"))

    return d


# ── Paragraph styles ─────────────────────────────────────────────────────────
def build_styles():
    s = {}
    s["h1"]     = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=20, leading=26,
                    textColor=BLUE_DARK, spaceBefore=18, spaceAfter=8)
    s["h2"]     = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=14, leading=18,
                    textColor=BLUE_MID, spaceBefore=16, spaceAfter=6)
    s["h3"]     = ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=12, leading=16,
                    textColor=BLUE_LIGHT, spaceBefore=12, spaceAfter=4)
    s["h4"]     = ParagraphStyle("h4", fontName="Helvetica-Bold", fontSize=10, leading=14,
                    textColor=GREY_DARK, spaceBefore=8, spaceAfter=2)
    s["body"]   = ParagraphStyle("body", fontName="Helvetica", fontSize=10, leading=15,
                    textColor=BLACK, spaceBefore=3, spaceAfter=3, alignment=TA_JUSTIFY)
    s["bullet"] = ParagraphStyle("bullet", fontName="Helvetica", fontSize=10, leading=14,
                    textColor=BLACK, leftIndent=14, spaceBefore=2, spaceAfter=2)
    s["th"]     = ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=9, leading=12,
                    textColor=WHITE, alignment=TA_LEFT)
    s["td"]     = ParagraphStyle("td", fontName="Helvetica", fontSize=9, leading=13,
                    textColor=BLACK, alignment=TA_LEFT)
    return s


def safe(t):
    return t.encode("ascii", "ignore").decode()


def inline(text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    bt = BT
    text = re.sub(bt + "([^" + bt + "]+)" + bt,
                  r'<font name="Courier" size="8" color="#2C3E50">\1</font>', text)
    text = safe(text)
    text = re.sub(r'\bCritical\b', '<font color="#C0392B"><b>Critical</b></font>', text)
    text = re.sub(r'\bHigh\b',     '<font color="#D35400"><b>High</b></font>',     text)
    text = re.sub(r'\bMedium\b',   '<font color="#B7950B"><b>Medium</b></font>',   text)
    text = re.sub(r'\bLow\b',      '<font color="#1E8449"><b>Low</b></font>',      text)
    return text


def parse_table(lines):
    rows = []
    for line in lines:
        if re.match(r"^\s*\|[-:| ]+\|\s*$", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)
    return rows


_WIDE = {
    "why", "reason", "recommendation", "description", "purpose", "issue",
    "mitigation", "action", "detail", "deliverable", "acceptance", "criteria",
    "constraint", "what", "fix", "matter", "benefit", "risk", "notes",
    "context", "problem", "impact", "responsibility", "approach", "result",
    "need", "needed",
}
_NARROW = {
    "#", "no", "id", "severity", "file", "effort", "weight", "week",
    "duration", "likelihood", "priority", "type", "layer", "gpu", "ram",
    "resource", "tool", "phase", "tier", "allocation", "owners", "owner",
    "latency", "size", "count", "rate", "score", "kb", "check",
}
TOTAL_W = 17.4 * cm


def smart_col_widths(headers):
    def _w(h):
        words = set(re.split(r"\W+", h.lower()))
        if words & _NARROW or h.lower().strip() in _NARROW:
            return 0.7
        if words & _WIDE or any(kw in h.lower() for kw in _WIDE):
            return 3.5
        return 1.5
    ws = [_w(h) for h in headers]
    total = sum(ws)
    return [TOTAL_W * w / total for w in ws]


def make_table(rows, styles):
    if not rows:
        return Spacer(1, 0.1*cm)
    n = max(len(r) for r in rows)
    headers = rows[0]
    fs = 9 if n <= 3 else 8.5
    th_st = ParagraphStyle("_th", fontName="Helvetica-Bold", fontSize=fs,
                           leading=fs+3, textColor=WHITE, alignment=TA_LEFT)
    td_st = ParagraphStyle("_td", fontName="Helvetica", fontSize=fs,
                           leading=fs+4, textColor=BLACK, alignment=TA_LEFT)
    cw  = smart_col_widths(headers)
    pad = 5 if n >= 5 else 7
    pr  = []
    for r_i, row in enumerate(rows):
        while len(row) < n:
            row.append("")
        st = th_st if r_i == 0 else td_st
        pr.append([Paragraph(inline(c), st) for c in row])
    tbl = Table(pr, colWidths=cw, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  BLUE_DARK),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, GREY_LIGHT]),
        ("GRID",          (0,0), (-1,-1), 0.4, GREY_LINE),
        ("LINEBELOW",     (0,0), (-1,0),  2.0, GOLD),
        ("TOPPADDING",    (0,0), (-1,-1), pad),
        ("BOTTOMPADDING", (0,0), (-1,-1), pad),
        ("LEFTPADDING",   (0,0), (-1,-1), pad+1),
        ("RIGHTPADDING",  (0,0), (-1,-1), pad+1),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]))
    return tbl


def make_code(lines):
    st = ParagraphStyle("cb",
        fontName="Courier", fontSize=7.5, leading=11,
        backColor=CODE_BG, leftIndent=8, rightIndent=8,
        spaceBefore=6, spaceAfter=6,
        borderColor=BLUE_LIGHT, borderWidth=1, borderPadding=6)
    return Preformatted(safe("\n".join(lines)), st)


# ── Markdown → story ─────────────────────────────────────────────────────────
def md_to_story(md_text, styles):
    story   = []
    lines   = md_text.split("\n")
    i       = 0
    pending = []
    next_codeblock_is_diagram = False   # set when H3 mentions "System Diagram"

    def flush():
        if not pending:
            return
        items = [ListItem(Paragraph(inline(t), styles["bullet"]),
                          leftIndent=18, bulletColor=BLUE_LIGHT)
                 for t in pending]
        story.append(ListFlowable(items, bulletType="bullet",
                                   leftIndent=0, spaceBefore=2, spaceAfter=4))
        pending.clear()

    bt3 = BT * 3

    while i < len(lines):
        raw  = lines[i]
        line = raw.strip()

        # Code fence
        if line.startswith(bt3):
            flush()
            i += 1
            cl = []
            while i < len(lines) and not lines[i].strip().startswith(bt3):
                cl.append(lines[i])
                i += 1
            i += 1
            if next_codeblock_is_diagram:
                # Replace ASCII art with real vector diagram
                story.append(Spacer(1, 0.4*cm))
                story.append(make_arch_diagram())
                story.append(Spacer(1, 0.4*cm))
                next_codeblock_is_diagram = False
            elif cl:
                story.append(make_code(cl))
            continue

        # Table
        if line.startswith("|"):
            flush()
            tl = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tl.append(lines[i])
                i += 1
            rows = parse_table(tl)
            if rows:
                story.append(Spacer(1, 0.2*cm))
                story.append(make_table(rows, styles))
                story.append(Spacer(1, 0.25*cm))
            continue

        # H1
        if re.match(r"^# [^#]", line):
            flush()
            story.append(Spacer(1, 0.4*cm))
            story.append(Paragraph(inline(line[2:].strip()), styles["h1"]))
            story.append(HRFlowable(width="100%", thickness=2.5,
                                     color=BLUE_DARK, spaceAfter=8))
            i += 1; continue

        # H2
        if re.match(r"^## [^#]", line):
            flush()
            story.append(KeepTogether([
                Spacer(1, 0.3*cm),
                Paragraph(inline(line[3:].strip()), styles["h2"]),
                HRFlowable(width="100%", thickness=1.5, color=GOLD, spaceAfter=4),
            ]))
            i += 1; continue

        # H3  — detect diagram section
        if re.match(r"^### [^#]", line):
            flush()
            heading_text = line[4:].strip()
            if "Diagram" in heading_text or "High-Level" in heading_text:
                next_codeblock_is_diagram = True
            story.append(KeepTogether([
                Spacer(1, 0.2*cm),
                Paragraph(inline(heading_text), styles["h3"]),
            ]))
            i += 1; continue

        # H4
        if re.match(r"^#### ", line):
            flush()
            story.append(Paragraph(inline(line[5:].strip()), styles["h4"]))
            i += 1; continue

        # HR
        if re.match(r"^---+$", line) or re.match(r"^\*\*\*+$", line):
            flush()
            story.append(HRFlowable(width="100%", thickness=0.5,
                                     color=GREY_LINE, spaceAfter=4))
            i += 1; continue

        # Bullets / numbered list
        if re.match(r"^[-*+] ", line) or re.match(r"^\d+\. ", line):
            pending.append(re.sub(r"^[-*+] |^\d+\.\s+", "", line))
            i += 1; continue

        # Blank line
        if not line:
            flush()
            story.append(Spacer(1, 0.08*cm))
            i += 1; continue

        # Paragraph
        flush()
        try:
            story.append(Paragraph(inline(line), styles["body"]))
        except Exception:
            s = safe(line)
            if s:
                story.append(Paragraph(s, styles["body"]))
        i += 1

    flush()
    return story


# ── Converter ─────────────────────────────────────────────────────────────────
def convert(md_path, pdf_path, doc_title):
    styles = build_styles()
    doc = TeleConnectDoc(
        str(pdf_path), doc_title=doc_title,
        pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=2.8*cm,  bottomMargin=2.5*cm,
    )
    doc.build(md_to_story(md_path.read_text(encoding="utf-8"), styles))
    print("  OK  %s  (%d KB)" % (pdf_path.name, pdf_path.stat().st_size // 1024))


BASE = Path(r"c:\Users\sheen\Downloads\review_codebase")
FILES = [
    ("code_review.md",       "code_review.pdf",       "Code Review -- Part 1"),
    ("technical_design.md",  "technical_design.pdf",  "Technical Design -- Part 2"),
    ("stakeholder_brief.md", "stakeholder_brief.pdf", "Stakeholder Brief -- Part 2"),
]

print("Building professional PDFs...")
for mn, pn, title in FILES:
    try:
        convert(BASE / mn, BASE / pn, title)
    except Exception as e:
        import traceback; traceback.print_exc()
        print("  ERR %s: %s" % (mn, e))
print("Done.")
