# finance_tracker/urls.py
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from finance_tracker import settings
from tracker import views as tracker_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", tracker_views.home, name="home"),
    path("admin/", admin.site.urls),
    path("signup/", tracker_views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="tracker/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("tracker.urls")),   # <- mount app at root so links are clean
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
