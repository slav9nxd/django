from datetime import timedelta
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

from .models import Appointment, Service, Pet
from .forms import PetForm, ServiceForm


# ---------- Главная и поиск ----------
def index(request):
    now = timezone.now()

    upcoming = (
        Appointment.objects
        .filter(start_time__gte=now, start_time__lte=now + timedelta(days=7))
        .select_related("pet", "vet__user")
        .order_by("start_time")[:5]
    )

    popular = (
        Service.objects
        .filter(appointments__start_time__gte=now - timedelta(days=30))
        .annotate(times=Count("appointments"))
        .order_by("-times")[:5]
    )

    newest = (
    Pet.objects
    .filter(id__range=(1, 5))      
    .select_related("species")
    .order_by("id")               
    )


    total_appointments = Appointment.objects.count()

    return render(request, "vetclinic/index.html", {
        "upcoming": upcoming,
        "popular": popular,
        "newest": newest,
        "total_appointments": total_appointments,
    })


def pet_search(request):
    now = timezone.now()

    upcoming = Appointment.objects.filter(
        start_time__gte=now, start_time__lte=now + timedelta(days=7)
    ).select_related("pet", "vet__user").order_by("start_time")[:5]

    popular = Service.objects.filter(
        appointments__start_time__gte=now - timedelta(days=30)
    ).annotate(times=Count("appointments")).order_by("-times")[:5]

    newest = Pet.objects.select_related("species").order_by("-created_at")[:5]
    total_appointments = Appointment.objects.count()

    q = request.GET.get("q", "").strip()
    if q:
        pets = Pet.objects.filter(
            Q(name__icontains=q) |
            Q(owner__first_name__icontains=q) |
            Q(owner__last_name__icontains=q)
        ).select_related("species", "owner").order_by("name")
    else:
        pets = Pet.objects.none()

    return render(request, "vetclinic/pet_search.html", {
        "query": q,
        "pets": pets,
        "upcoming": upcoming,
        "popular": popular,
        "newest": newest,
        "total_appointments": total_appointments,
    })


# ---------- Услуги ----------
class ServiceListView(ListView):
    model = Service
    template_name = "vetclinic/service_list.html"
    context_object_name = "services"


class ServiceDetailView(DetailView):
    model = Service
    template_name = "vetclinic/service_detail.html"
    context_object_name = "service"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["last_appointments"] = (
            Appointment.objects
            .select_related("pet", "clinic", "vet__user")
            .filter(service=self.object)
            .order_by("-start_time")[:10]
        )
        return ctx


class ServiceCreateView(CreateView):
    model = Service
    form_class = ServiceForm
    template_name = "vetclinic/service_form.html"
    success_url = reverse_lazy("vetclinic:service_list")


class ServiceUpdateView(UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = "vetclinic/service_form.html"
    success_url = reverse_lazy("vetclinic:service_list")


class ServiceDeleteView(DeleteView):
    model = Service
    template_name = "vetclinic/service_confirm_delete.html"
    success_url = reverse_lazy("vetclinic:service_list")


# ---------- Питомцы ----------
class PetListView(ListView):
    model = Pet
    template_name = "vetclinic/pet_list.html"
    context_object_name = "pets"


class PetDetailView(DetailView):
    model = Pet
    template_name = "vetclinic/pet_detail.html"
    context_object_name = "pet"


class PetCreateView(CreateView):
    model = Pet
    form_class = PetForm
    template_name = "vetclinic/pet_form.html"
    success_url = reverse_lazy("vetclinic:pet_list")


class PetUpdateView(UpdateView):
    model = Pet
    form_class = PetForm
    template_name = "vetclinic/pet_form.html"
    success_url = reverse_lazy("vetclinic:pet_list")


class PetDeleteView(DeleteView):
    model = Pet
    template_name = "vetclinic/pet_confirm_delete.html"
    success_url = reverse_lazy("vetclinic:pet_list")


# ---------- Приёмы (простой список для ссылки) ----------
class AppointmentListView(ListView):
    model = Appointment
    template_name = "vetclinic/appointment_list.html"
    context_object_name = "appointments"
    paginate_by = 20
    ordering = "-start_time"
