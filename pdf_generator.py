from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_with_same_design(improved_sections, original_filename):
    pdf_filename = f"improved_{original_filename}.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    for section, content in improved_sections.items():
        # Add section title
        story.append(Paragraph(section, styles['Heading1']))
        story.append(Spacer(1, 12))
        
        # Add section content
        story.append(Paragraph(content, styles['BodyText']))
        story.append(Spacer(1, 24))

    doc.build(story)
    return pdf_filename
