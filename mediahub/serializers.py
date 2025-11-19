# mediahub/serializers.py
from rest_framework import serializers
from .models import GalleryItem

# --- Image validation policy ---
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_UPLOAD_MB = 10  # adjust as needed

# --- Tag derivation policy ---
DEFAULT_TAG = "general"
TAG_RULES = {
    "kitchen": "kitchen",
    "bathroom": "bathroom",
    "bath": "bathroom",
    "tile": "tiling",
    "floor": "flooring",
    "shop": "shopfitting",
    "fitout": "shopfitting",
    "carpentry": "carpentry",
    "paint": "painting",
    "plaster": "plastering",
    "plumb": "plumbing",
    "ceiling": "ceiling",
    "reno": "renovation",
    "refurb": "renovation",
}


def derive_tags_from_text(text: str) -> list[str]:
    """Return sorted, unique tags based on TAG_RULES; guarantee at least DEFAULT_TAG."""
    lowered = (text or "").lower()
    tags = {rule_tag for key, rule_tag in TAG_RULES.items() if key in lowered}
    return sorted(tags or {DEFAULT_TAG})


class GalleryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryItem
        fields = ["id", "title", "image", "caption",
                  "tags", "is_active", "created_at"]
        read_only_fields = ["created_at"]

    # --- Field-level validation for the image ---
    def validate_image(self, file):
        """
        Ensure the uploaded file is a supported image and within size limits.
        Works for multipart uploads where InMemoryUploadedFile/TemporaryUploadedFile
        exposes .content_type and .size.
        """
        if file is None:
            # Allow creating/updating metadata without changing image (PATCH)
            return file

        content_type = getattr(file, "content_type", None)
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise serializers.ValidationError(
                "Only JPEG/PNG/WEBP images are allowed.")

        size_bytes = getattr(file, "size", 0)
        if size_bytes and size_bytes > MAX_UPLOAD_MB * 1024 * 1024:
            raise serializers.ValidationError(
                f"Max file size is {MAX_UPLOAD_MB} MB.")

        return file

    # --- Object-level validation for tags ---
    def validate(self, attrs):
        """
        Guarantee that 'tags' is present and non-empty:
        - If incoming 'tags' is empty/missing, derive from title or filename.
        - Normalize to lowercase unique list for consistent filtering.
        """
        incoming_tags = attrs.get("tags")
        title = attrs.get("title") or ""
        filename = getattr(attrs.get("image"), "name", "") or ""

        if not incoming_tags:
            base_text = title or filename
            attrs["tags"] = derive_tags_from_text(base_text)
        else:
            normalized = sorted({(t or "").strip().lower()
                                for t in incoming_tags if (t or "").strip()})
            attrs["tags"] = normalized or [DEFAULT_TAG]

        return attrs
