from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from .views import landing_page
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('', landing_page, name='landing'),
    path('chatbot/', include('chatbot.urls', namespace='chatbot')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('polls/', include('polls.urls', namespace='polls')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('marketplace/', include('marketplace.urls', namespace='marketplace')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
