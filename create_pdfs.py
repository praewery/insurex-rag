import requests
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

BASE_URL = "https://www.insurex.co.th/api/v1"
HEADERS = {"User-Agent": "Mozilla/5.0"}
FONT_PATH = "/Users/ppraew/Library/Fonts/THSarabunNew.ttf"

PRODUCT_GROUPS = {
    "01_health": {
        "title": "ประกันสุขภาพ InsureX",
        "paths": ["easy-e-health", "e-health-deduct", "health-mini",
                  "kumruksamaojaiextra", "kumtalodchepplus", "Primacare", "healthforkids"]
    },
    "02_life": {
        "title": "ประกันคุ้มครองชีวิต InsureX",
        "paths": ["term", "termtele", "Wholelife90_20", "Wholelife99/99",
                  "kumcheveExtra", "kuncheva"]
    },
    "03_accident": {
        "title": "ประกันอุบัติเหตุ InsureX",
        "paths": ["PA_plus"]
    },
    "04_critical_illness": {
        "title": "ประกันโรคร้ายแรง InsureX",
        "paths": ["ciplus", "Cancer", "ci50"]
    },
    "05_savings": {
        "title": "ประกันสะสมทรัพย์และบำนาญ InsureX",
        "paths": ["saving189", "saving/aomsook", "kumkasein", "khumbumnan"]
    }
}


def clean_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fetch_product(path):
    try:
        url = f"{BASE_URL}/products?path={path}"
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list):
                for p in data:
                    if p.get('path') == path:
                        return p
                return None
            return data

    except Exception as e:
        print(f"  Error fetching {path}: {e}")
    return None


def product_to_text(p):
    lines = []
    lines.append(f"ชื่อผลิตภัณฑ์: {p.get('name', '')}")
    lines.append(f"ประเภท: {p.get('type', '')}")

    short = clean_html(p.get('shortDescrition', ''))
    if short:
        lines.append(f"คุณสมบัติเด่น: {short}")

    for item in p.get('highlightItems', []):
        title = clean_html(item.get('title', ''))
        text = clean_html(item.get('text', ''))
        if title or text:
            lines.append(f"  - {title}: {text}")

    desc = clean_html(p.get('description', ''))
    if desc:
        lines.append(f"รายละเอียด: {desc}")

    cond = clean_html(p.get('condition', ''))
    if cond:
        lines.append(f"เงื่อนไข: {cond}")

    faq = clean_html(p.get('frequencyQuestions', ''))
    if faq:
        lines.append(f"คำถามที่พบบ่อย: {faq}")

    return '\n'.join(lines)


def create_pdf(filename, title, products_text):
    pdfmetrics.registerFont(TTFont('THSarabun', FONT_PATH))

    doc = SimpleDocTemplate(
        f"data/pdfs/{filename}.pdf",
        pagesize=A4,
        rightMargin=20*mm, leftMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'],
                                  fontSize=18, spaceAfter=12, fontName='THSarabun')
    product_style = ParagraphStyle('Product', parent=styles['Heading2'],
                                    fontSize=14, spaceBefore=12, spaceAfter=6, fontName='THSarabun')
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
                                 fontSize=12, leading=18, spaceAfter=4, fontName='THSarabun')

    story = []
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 6*mm))

    for text in products_text:
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            safe = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            if line.startswith('ชื่อผลิตภัณฑ์:'):
                story.append(Paragraph(safe, product_style))
            else:
                story.append(Paragraph(safe, body_style))
        story.append(Spacer(1, 4*mm))

    doc.build(story)
    print(f"  Created: data/pdfs/{filename}.pdf")


if __name__ == "__main__":
    for filename, group in PRODUCT_GROUPS.items():
        print(f"\nProcessing: {group['title']}")
        products_text = []
        for path in group['paths']:
            print(f"  Fetching: {path}")
            product = fetch_product(path)
            if product:
                text = product_to_text(product)
                products_text.append(text)
                print(f"  OK: {product.get('name', path)}")
            else:
                print(f"  Skipped: {path}")
        if products_text:
            create_pdf(filename, group['title'], products_text)

    print("\nDone! Check data/pdfs/")