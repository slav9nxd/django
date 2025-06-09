from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Role, Species, AppointmentStatus, User, Clinic, Service,
    Vet, VetService, Pet, Appointment, Favorite
)

class PetInline(admin.TabularInline):
    model = Pet
    extra = 0
    raw_id_fields = ("species",)
    readonly_fields = ("created_at", "updated_at")

class VetInline(admin.TabularInline):
    model = Vet
    extra = 0
    raw_id_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")

class VetServiceInline(admin.TabularInline):
    model = VetService
    extra = 1
    raw_id_fields = ("service",)

class AppointmentInline(admin.TabularInline):
    model = Appointment
    extra = 0
    raw_id_fields = ("clinic", "service", "vet", "status")
    readonly_fields = ("created_at", "updated_at")

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("id",)

@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("id",)

@admin.register(AppointmentStatus)
class AppointmentStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("id",)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "email", "role", "created_at")
    list_display_links = ("id", "first_name")
    list_filter = ("role", "created_at")
    search_fields = ("first_name", "last_name", "email", "phone")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
    inlines = (PetInline,)

@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "address_short", "created_at")
    list_display_links = ("id", "name")
    search_fields = ("name", "address")
    date_hierarchy = "created_at"
    inlines = (VetInline,)
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="адрес (60 симв.)")
    def address_short(self, obj):
        return (obj.address[:60] + "…") if obj.address and len(obj.address) > 60 else obj.address

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "base_price", "duration_minutes")
    search_fields = ("name", "description")
    list_filter = ("duration_minutes",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")

@admin.register(Vet)
class VetAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "clinic", "specialization", "services_list", "created_at")
    list_display_links = ("id", "full_name")
    list_filter = ("clinic", "specialization")
    search_fields = ("user__first_name", "user__last_name", "specialization")
    filter_horizontal = ("services",)
    raw_id_fields = ("user", "clinic")
    readonly_fields = ("created_at", "updated_at")
    inlines = (VetServiceInline, AppointmentInline)
    date_hierarchy = "created_at"

    @admin.display(description="услуги")
    def services_list(self, obj):
        names = [s.name for s in obj.services.all()[:5]]
        return ", ".join(names) + ("…" if obj.services.count() > 5 else "")

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "species", "owner", "age_years", "gender", "created_at")
    list_filter = ("species", "gender")
    search_fields = ("name", "breed", "owner__first_name", "owner__last_name")
    raw_id_fields = ("owner", "species")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    inlines = (AppointmentInline,)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "pet", "clinic", "service", "vet", "start_time", "status", "duration")
    list_filter = ("status", "clinic", "service", "vet")
    search_fields = (
        "pet__name",
        "vet__user__first_name",
        "vet__user__last_name",
        "clinic__name",
    )
    raw_id_fields = ("pet", "clinic", "service", "vet", "created_by_user", "updated_by_user")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "start_time"

    @admin.display(description="длительность, мин")
    def duration(self, obj):
        if obj.end_time:
            return (obj.end_time - obj.start_time).seconds // 60
        return None

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "pet")
    list_filter = ("user",)
    search_fields = ("user__first_name", "user__last_name", "pet__name")
    raw_id_fields = ("user", "pet")
