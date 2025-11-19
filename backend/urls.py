
from quotes.views import QuoteViewSet
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from core.views import SiteInfoViewSet, StaticPageViewSet
from services.views import ServiceViewSet
from mediahub.views import GalleryViewSet
from blog.views import PostViewSet
from contact.views import ContactMessageCreateView

router = DefaultRouter()
router.register(r'site', SiteInfoViewSet, basename='site-info')
router.register(r'pages', StaticPageViewSet, basename='pages')
router.register(r'services', ServiceViewSet, basename='services')
router.register(r'gallery', GalleryViewSet, basename='gallery')
router.register(r'blog', PostViewSet, basename='blog')
router.register(r"quotes", QuoteViewSet, basename="quotes")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/contact-messages/', ContactMessageCreateView.as_view(),
         name='contact-messages'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
