from datetime import timedelta
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone

from .models import Appointment, Service, Pet

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
        .select_related("species")
        .order_by("-created_at")[:5]
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
    # Дублируем три виджета
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
        .select_related("species")
        .order_by("-created_at")[:5]
    )
    total_appointments = Appointment.objects.count()

    # Сам поиск питомцев
    q = request.GET.get("q", "").strip()
    if q:
        pets = (
            Pet.objects
            .filter(
                Q(name__icontains=q) |
                Q(owner__first_name__icontains=q) |
                Q(owner__last_name__icontains=q)
            )
            .select_related("species", "owner")
            .order_by("name")
        )
    else:
        pets = Pet.objects.none()

    return render(request, "vetclinic/pet_search.html", {
        "query": q,
        "pets": pets,
        # контекст для виджетов
        "upcoming": upcoming,
        "popular": popular,
        "newest": newest,
        "total_appointments": total_appointments,
    })
