from django.db import models


class Quote(models.Model):
    # Who’s enquiring
    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)

    # What they want
    # free text or normalize later
    service = models.CharField(max_length=120, blank=True)
    # optional details from the form
    description = models.TextField(blank=True)
    source_page = models.CharField(
        max_length=200, blank=True)  # e.g., "/services/kitchen"

    # Commercial tracking
    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("contracted", "Contracted"),  # you have a signed deal/PO
        ("won", "Converted / Won"),    # job completed / firmed
        ("lost", "Lost"),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="new")
    estimated_value = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    contracted_value = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    # e.g., "budget", "scope", etc.
    close_reason = models.CharField(max_length=200, blank=True)

    # Ops metadata
    # optional simple assignment
    assigned_to = models.CharField(max_length=120, blank=True)
    tags = models.JSONField(default=list, blank=True)

    # Notes / timeline
    notes = models.TextField(blank=True)  # single field for quick notes
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional attachment (client brief, images) – local storage under <root>/gallery/ or /quotes/
    attachment = models.FileField(upload_to="quotes/", blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} [{self.status}]"
