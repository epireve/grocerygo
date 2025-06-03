from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("profile/", views.profile_view, name="profile"),
    # Address management
    path("address/add/", views.add_address_view, name="add_address"),
    path(
        "address/<int:address_id>/edit/", views.edit_address_view, name="edit_address"
    ),
    path(
        "address/<int:address_id>/delete/",
        views.delete_address_view,
        name="delete_address",
    ),
    path(
        "address/<int:address_id>/set-default/",
        views.set_default_address_view,
        name="set_default_address",
    ),
    # Order management
    path("order-history/", views.order_history_view, name="order_history"),
    path("order/<int:order_id>/", views.order_detail_view, name="order_detail"),
    path("order/<int:order_id>/cancel/", views.cancel_order_view, name="cancel_order"),
    # Password reset URLs
    path(
        "password-reset/",
        views.CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        views.CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        views.CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
