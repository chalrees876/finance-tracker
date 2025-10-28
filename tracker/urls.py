from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("transactions/", views.transactions, name="transactions"),
    path("categories/", views.categories, name="categories"),
    path("categories/create/", views.category_create, name="category_create"),
    path("categories/group/create/", views.category_group_create, name="category_group_create"),
    path("categories/<int:category_id>/delete/", views.category_delete, name="category_delete"),
    path("budget/allocate/", views.budget_allocate, name="budget_allocate"),
]