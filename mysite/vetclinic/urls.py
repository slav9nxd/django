from django.urls import path
from . import views

app_name = "vetclinic"

urlpatterns = [
    # Главная
    path("", views.index, name="home"),

    # ---------- Услуги ----------
    path("services/",               views.ServiceListView.as_view(),   name="service_list"),
    path("services/add/",           views.ServiceCreateView.as_view(), name="service_add"),
    path("services/<int:pk>/",      views.ServiceDetailView.as_view(), name="service_detail"),
    path("services/<int:pk>/edit/", views.ServiceUpdateView.as_view(), name="service_edit"),
    path("services/<int:pk>/delete/", views.ServiceDeleteView.as_view(), name="service_delete"),

    # ---------- Питомцы ----------
    path("pets/",               views.PetListView.as_view(),   name="pet_list"),
    path("pets/add/",           views.PetCreateView.as_view(), name="pet_add"),
    path("pets/<int:pk>/",      views.PetDetailView.as_view(), name="pet_detail"),
    path("pets/<int:pk>/edit/", views.PetUpdateView.as_view(), name="pet_edit"),
    path("pets/<int:pk>/delete/", views.PetDeleteView.as_view(), name="pet_delete"),
    path("pets/search/", views.pet_search, name="pet_search"),

    # ---------- Приёмы ----------
    # пока выводим тот же index-шаблон, чтобы ссылка существовала
    path("appointments/", views.AppointmentListView.as_view(), name="appointment_list"),
]
