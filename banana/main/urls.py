from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_request, name="logout"),
    path("login/", views.login_request, name="login"),
    path("about/", views.about_us, name="about"),
    path("profile/", views.profile, name="profile"),
    path("landing/", views.landing_page, name="landing"),
    path("portals/<slug:slug>/", views.portal_about, name="slug"),
    path("data/", views.preview_data, name="data"),
    path("comment/", views.comment, name="comment"),
    path("comments/", views.comments, name="comments"),
    path("gmd/", views.get_more_data, name="gmd"),
]