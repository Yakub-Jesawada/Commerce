from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newlisting", views.newlisting, name="newlisting"),
    path("categories", views.categories, name="categories"),
    path("item/<int:id>", views.listingitem, name="listingitem"),
    path("addToWatchlist", views.addToWatchlist, name="addToWatchlist"),
    path("deleteFromWatchlist", views.deleteFromWatchlist, name="deleteFromWatchlist"),
    path("displayWatchlist", views.displayWatchlist, name="displayWatchlist"),
    path("closeListing", views.closeListing, name="closeListing"),
    path("login", auth_views.LoginView.as_view()),
    path("wonBids", views.wonBids, name="wonBids"),
    path("addCommment/<int:id>", views.addCommment, name="addCommment"),

]
