from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class RatingDistributionChart(Flowable):
    def __init__(self, distribution: dict[str, int]) -> None:
        super().__init__()
        self.distribution = distribution
        self.width = 6.4 * inch
        self.height = 1.8 * inch

    def draw(self) -> None:
        canvas = self.canv
        max_count = max(self.distribution.values(), default=0) or 1
        chart_left = 0.55 * inch
        chart_bottom = 0.35 * inch
        chart_height = 1.05 * inch
        chart_width = 5.3 * inch
        category_count = max(len(self.distribution), 1)
        slot_width = chart_width / category_count
        bar_width = min(0.55 * inch, slot_width * 0.65)
        canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
        canvas.line(chart_left, chart_bottom, chart_left + chart_width, chart_bottom)
        ratings = sorted(self.distribution.items(), key=lambda item: float(item[0]))
        for index, (rating, count) in enumerate(ratings):
            bar_height = chart_height * count / max_count
            x = chart_left + index * slot_width + (slot_width - bar_width) / 2
            canvas.setFillColor(colors.HexColor("#0EA5E9"))
            canvas.roundRect(x, chart_bottom, bar_width, bar_height, 3, fill=1, stroke=0)
            canvas.setFillColor(colors.HexColor("#334155"))
            canvas.setFont("Helvetica", 7)
            canvas.drawCentredString(x + bar_width / 2, chart_bottom - 0.16 * inch, f"{float(rating):g} star")
            canvas.drawCentredString(x + bar_width / 2, chart_bottom + bar_height + 0.08 * inch, str(count))


def create_product_report(product: dict, analysis: dict) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title=f"Product investigation — {product['name']}",
        author="ReviewShield AI",
    )
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#0F172A"),
            alignment=TA_LEFT,
            fontSize=20,
            leading=24,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#0369A1"),
            fontSize=12,
            leading=15,
            spaceBefore=12,
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallNote",
            parent=styles["BodyText"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#475569"),
        )
    )

    def footer(canvas, document) -> None:
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
        canvas.line(0.7 * inch, 0.5 * inch, 7.8 * inch, 0.5 * inch)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.drawString(0.7 * inch, 0.34 * inch, "ReviewShield AI · Heuristic investigation report")
        canvas.drawRightString(7.8 * inch, 0.34 * inch, f"Page {document.page}")
        canvas.restoreState()

    story: list[Flowable] = [
        Paragraph("Product Investigation Report", styles["ReportTitle"]),
        Paragraph(escape(product["name"]), styles["Heading1"]),
        Paragraph(
            f"Product ID: {escape(product['product_id'])} &nbsp; | &nbsp; "
            f"Category: {escape(product.get('category') or 'General')} &nbsp; | &nbsp; "
            f"Seller: {escape(product.get('seller') or 'Not provided')}",
            styles["BodyText"],
        ),
        Spacer(1, 12),
    ]

    if analysis["risk_score"] is None:
        score_text = "Not estimable — no stored review data"
    else:
        score_text = f"Risk {analysis['risk_score']:.1f}/100 · Trust {analysis['trust_score']:.1f}/100"
    score_table = Table(
        [
            ["Product risk assessment", score_text],
            ["Reviews", str(analysis["review_count"])],
            [
                "Prediction coverage",
                f"{analysis['prediction_coverage']:.1f}% "
                f"({analysis['predicted_review_count']} of {analysis['review_count']})",
            ],
            [
                "Suspicious among scored reviews",
                (
                    f"{analysis['suspicious_percentage']:.1f}% "
                    f"({analysis['suspicious_review_count']} of {analysis['predicted_review_count']})"
                    if analysis["suspicious_percentage"] is not None
                    else "Unavailable — no stored predictions"
                ),
            ],
            ["Campaign candidates", str(analysis["campaign_count"])],
            [
                "Campaign-involved reviews",
                (
                    f"{analysis['campaign_involvement_percentage']:.1f}% "
                    f"({analysis['campaign_review_count']} of {analysis['review_count']})"
                    if analysis["campaign_involvement_percentage"] is not None
                    else "Unavailable"
                ),
            ],
        ],
        colWidths=[2.6 * inch, 4.1 * inch],
    )
    score_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E0F2FE")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#334155")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend(
        [
            Paragraph("Investigation summary", styles["SectionHeading"]),
            score_table,
            Paragraph("Rating distribution", styles["SectionHeading"]),
            RatingDistributionChart(analysis["rating_distribution"]),
            Paragraph("Risk indicators and supporting evidence", styles["SectionHeading"]),
        ]
    )
    if analysis["indicators"]:
        indicator_rows: list[list[str | Paragraph]] = [
            ["Indicator", "Observed value", "Risk", "Weight", "Interpretation"]
        ]
        for indicator in analysis["indicators"]:
            value = indicator["value"]
            observed = "Not available" if value is None else f"{value:.1f}%"
            indicator_rows.append(
                [
                    Paragraph(escape(indicator["label"]), styles["SmallNote"]),
                    observed,
                    f"{indicator['risk_score']:.1f}/100" if indicator["risk_score"] is not None else "N/A",
                    f"{indicator['weight']:.1f}%",
                    Paragraph(escape(indicator["explanation"]), styles["SmallNote"]),
                ]
            )
        indicator_table = Table(
            indicator_rows,
            colWidths=[1.05 * inch, 0.8 * inch, 0.65 * inch, 0.6 * inch, 3.6 * inch],
            repeatRows=1,
        )
        indicator_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 8),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(indicator_table)
    else:
        story.append(Paragraph("No review evidence is available for this product.", styles["BodyText"]))
    story.extend(
        [
            Spacer(1, 10),
            Paragraph(escape(analysis["score_explanation"]), styles["SmallNote"]),
            Paragraph(
                "Risk and trust scores are estimates derived from available stored data. They are not proof that "
                "reviews or reviewers are fraudulent. Missing prediction coverage is disclosed and is not treated "
                "as genuine activity.",
                styles["SmallNote"],
            ),
        ]
    )
    document.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()
