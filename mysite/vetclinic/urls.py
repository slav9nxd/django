from django.urls import path
from .views import index, pet_search

app_name = "vetclinic"

urlpatterns = [
    path("", index, name="home"),
    path("pets/search/", pet_search, name="pet_search"),
    # оставшиеся заглушки/списочные страницы:
    path("appointments/", index, name="appointment_list"),
    path("services/",     index, name="service_list"),
    path("pets/",         index, name="pet_list"),
]
