from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable
)


def generate_pdf(topic, post):

    post = str(post)

    if not post.strip():
        raise ValueError("Cannot create PDF from an empty post.")

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=55,
        leftMargin=55,
        topMargin=55,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=20,
        leading=26,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0A66C2"),
        spaceAfter=15
    )

    topic_style = ParagraphStyle(
        "TopicStyle",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#555555"),
        spaceAfter=18
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["BodyText"],
        fontSize=11,
        leading=17,
        spaceAfter=10
    )

    story = [
        Paragraph("LinkedIn Post", title_style),

        Paragraph(
            f"<b>Topic:</b> {escape(topic)}",
            topic_style
        ),

        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#0A66C2")
        ),

        Spacer(1, 20)
    ]

    # Add each post line to the PDF
    for line in post.splitlines():

        if line.strip():

            story.append(
                Paragraph(
                    escape(line),
                    body_style
                )
            )

        else:
            story.append(Spacer(1, 8))

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()