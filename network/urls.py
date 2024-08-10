
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),
    path("profile/<str:profile>", views.profile, name="profile"),
    path("follow/<str:person>", views.follow, name="follow"),
    path("following", views.following, name="following"),
    path('edit/<int:id>', views.edit, name="edit"),
    path('like/<int:id>', views.like, name="like"),
    path('update/<int:id>', views.update_likes, name="update"),
    path('hasliked/<int:id>', views.haslike, name='hasliked')
]
