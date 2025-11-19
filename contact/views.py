
from rest_framework import generics
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage
from .serializers import ContactMessageSerializer


class ContactMessageCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        if getattr(settings, 'CONTACT_NOTIFY_EMAIL', None):
            try:
                send_mail(
                    subject=f"[ARConstruction] Contact: {instance.subject or instance.name}",
                    message=(
                        f"From: {instance.name} (" f"{instance.email}, {instance.phone})" f"{instance.message}"
                    ),
                    from_email=getattr(
                        settings, 'DEFAULT_FROM_EMAIL', instance.email),
                    recipient_list=[settings.CONTACT_NOTIFY_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass
