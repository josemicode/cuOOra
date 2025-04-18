from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from home.views import home, socials, questions_list_view, topics

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('users/', include('users.urls'), name='users'),
    path('socials/', socials, name='socials'),
    path("questions/", questions_list_view, name = "questions_list"),
    path("topics/", topics, name = "topics")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
