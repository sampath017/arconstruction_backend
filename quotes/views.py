from io import BytesIO
from django.http import HttpResponse
from rest_framework import viewsets, permissions, decorators, response, status, parsers
from django.db.models import Count, Sum
import pandas as pd
from .models import Quote
from .serializers import QuoteSerializer
from .filters import QuoteFilter


class IsAdminOrCreateOnly(permissions.BasePermission):
    """Anyone can POST (create enquiry). Other methods require staff."""

    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        return bool(request.user and request.user.is_staff)


class QuoteViewSet(viewsets.ModelViewSet):
    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer
    permission_classes = [IsAdminOrCreateOnly]
    filterset_class = QuoteFilter
    search_fields = ["full_name", "email",
                     "phone", "service", "description", "notes"]
    ordering_fields = ["created_at", "updated_at",
                       "estimated_value", "contracted_value"]
    parser_classes = [parsers.JSONParser, parsers.FormParser,
                      parsers.MultiPartParser]  # allow attachment uploads

    def get_queryset(self):
        qs = super().get_queryset()
        # Public readers should not read; but admins (staff) can list.
        if self.request.user and self.request.user.is_staff:
            return qs
        if self.request.method.lower() == "get":
            return Quote.objects.none()  # block listing to anonymous
        return qs

    @decorators.action(detail=False, methods=["get"], permission_classes=[permissions.IsAdminUser])
    def dashboard(self, request):
        """
        Quick KPIs:
        - total, by status
        - sum estimated_value, sum contracted_value
        - last 7/30 days counts
        """
        qs = self.filter_queryset(self.get_queryset())
        kpi = {
            "total": qs.count(),
            "by_status": dict(qs.values_list("status").annotate(c=Count("id"))),
            "sum_estimated": qs.aggregate(s=Sum("estimated_value"))["s"] or 0,
            "sum_contracted": qs.aggregate(s=Sum("contracted_value"))["s"] or 0,
        }
        return response.Response(kpi)

    @decorators.action(detail=False, methods=["get"], permission_classes=[permissions.IsAdminUser])
    def export_excel(self, request):
        """
        Exports filtered queryset to a styled Excel (XLSX).
        """
        qs = self.filter_queryset(self.get_queryset()).order_by("-created_at")
        rows = list(qs.values(
            "id", "created_at", "full_name", "email", "phone",
            "service", "description", "status", "estimated_value", "contracted_value",
            "assigned_to", "tags", "source_page", "notes", "updated_at"
        ))
        df = pd.DataFrame(rows)

        # Create Excel in-memory
        with BytesIO() as bio:
            with pd.ExcelWriter(bio, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Enquiries")
                ws = writer.book["Enquiries"]
                # Freeze header & adjust column widths
                ws.freeze_panes = "A2"
                for col in ws.columns:
                    max_len = max(
                        (len(str(c.value)) if c.value is not None else 0 for c in col), default=10)
                    ws.column_dimensions[col[0].column_letter].width = min(
                        max_len + 2, 60)
            data = bio.getvalue()

        resp = HttpResponse(
            data,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        resp["Content-Disposition"] = 'attachment; filename="arconstruction-enquiries.xlsx"'
        return resp

    @decorators.action(detail=False, methods=["get"], permission_classes=[permissions.IsAdminUser])
    def export_pdf(self, request):
        """
        Minimal PDF export (summary table) using reportlab.
        """
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        qs = self.filter_queryset(self.get_queryset()).order_by(
            "-created_at")[:200]  # cap for brevity
        rows = [["ID", "Created", "Name", "Email", "Phone",
                 "Service", "Status", "Est.", "Contracted"]]
        for q in qs:
            rows.append([
                q.id, q.created_at.strftime(
                    "%Y-%m-%d"), q.full_name, q.email, q.phone,
                q.service, q.status, str(q.estimated_value or ""), str(
                    q.contracted_value or "")
            ])

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(
            A4), title="ARConstruction Enquiries")
        styles = getSampleStyleSheet()
        elements = [
            Paragraph("AR Construction – Enquiries Export", styles["Title"]),
            Spacer(1, 12)
        ]
        table = Table(rows, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e78")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.whitesmoke, colors.lightgrey]),
        ]))
        elements.append(table)
        doc.build(elements)

        pdf = buffer.getvalue()
        buffer.close()

        resp = HttpResponse(pdf, content_type="application/pdf")
        resp["Content-Disposition"] = 'attachment; filename="arconstruction-enquiries.pdf"'
        return resp
