from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# ---------- справочники ----------
class Role(models.Model):
    id = models.AutoField(primary_key=True, db_column="role_id")
    name = models.CharField(_("Название роли"), max_length=50, unique=True)

    class Meta:
        db_table = "roles"
        verbose_name = _("роль")
        verbose_name_plural = _("роли")

    def __str__(self):
        return self.name


class Species(models.Model):
    id = models.AutoField(primary_key=True, db_column="species_id")
    name = models.CharField(_("Вид"), max_length=50, unique=True)

    class Meta:
        db_table = "species"
        verbose_name = _("вид животного")
        verbose_name_plural = _("виды животных")

    def __str__(self):
        return self.name


class AppointmentStatus(models.Model):
    id = models.AutoField(primary_key=True, db_column="status_id")
    name = models.CharField(_("Статус"), max_length=50, unique=True)

    class Meta:
        db_table = "appointment_statuses"
        verbose_name = _("статус записи")
        verbose_name_plural = _("статусы записей")

    def __str__(self):
        return self.name


# ---------- пользователи ----------
class User(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="user_id")
    role = models.ForeignKey(
        Role,
        db_column="role_id",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("роль"),
        related_name="users",
    )
    first_name = models.CharField(_("имя"), max_length=100)
    last_name = models.CharField(_("фамилия"), max_length=100, blank=True)
    email = models.EmailField(_("e-mail"), max_length=255, unique=True, null=True, blank=True)
    phone = models.CharField(_("телефон"), max_length=20, blank=True)
    password_hash = models.TextField(_("хеш пароля"), blank=True)
    created_at = models.DateTimeField(_("создан"), default=timezone.now)
    updated_at = models.DateTimeField(_("обновлён"), auto_now=True)

    class Meta:
        db_table = "users"
        verbose_name = _("пользователь")
        verbose_name_plural = _("пользователи")

    def __str__(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full or self.email or f"User #{self.pk}"


# ---------- ветеринарные клиники, врачи ----------
class Clinic(models.Model):
    id = models.AutoField(primary_key=True, db_column="clinic_id")
    name = models.CharField(_("название"), max_length=150)
    address = models.TextField(_("адрес"), blank=True)
    phone = models.CharField(_("телефон"), max_length=20, blank=True)
    description = models.TextField(_("описание"), blank=True)
    timetable = models.JSONField(_("расписание"), null=True, blank=True)
    created_at = models.DateTimeField(_("создан"), default=timezone.now)
    updated_at = models.DateTimeField(_("обновлён"), auto_now=True)

    class Meta:
        db_table = "clinics"
        verbose_name = _("клиника")
        verbose_name_plural = _("клиники")

    def __str__(self):
        return self.name


class Service(models.Model):
    id = models.AutoField(primary_key=True, db_column="service_id")
    name = models.CharField(_("название"), max_length=150)
    description = models.TextField(_("описание"), blank=True)
    base_price = models.DecimalField(_("базовая цена"), max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(_("длительность, мин"), null=True, blank=True)
    created_at = models.DateTimeField(_("создан"), default=timezone.now)
    updated_at = models.DateTimeField(_("обновлён"), auto_now=True)

    class Meta:
        db_table = "services"
        verbose_name = _("услуга")
        verbose_name_plural = _("услуги")

    def __str__(self):
        return self.name


class Vet(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="vet_id")
    user = models.ForeignKey(
        User,
        db_column="user_id",
        on_delete=models.CASCADE,
        related_name="veterinary_profiles",
        verbose_name=_("пользователь"),
    )
    clinic = models.ForeignKey(
        Clinic,
        db_column="clinic_id",
        on_delete=models.SET_NULL,
        null=True,
        related_name="vets",
        verbose_name=_("клиника"),
    )
    specialization = models.CharField(_("специализация"), max_length=150, blank=True)
    bio = models.TextField(_("биография"), blank=True)
    photo = models.ImageField(
        _("фото"), upload_to="vets/", blank=True, null=True, db_column="photo_path"
    )
    services = models.ManyToManyField(
        Service,
        through="VetService",
        related_name="vets",
        verbose_name=_("оказываемые услуги"),
    )
    created_at = models.DateTimeField(_("создан"), default=timezone.now)
    updated_at = models.DateTimeField(_("обновлён"), auto_now=True)

    class Meta:
        db_table = "vets"
        verbose_name = _("ветеринар")
        verbose_name_plural = _("ветеринары")

    def __str__(self):
        return f"{self.full_name} ({self.specialization})" if self.specialization else self.full_name

    # для list_display
    @property
    def full_name(self):
        return str(self.user)


class VetService(models.Model):
    vet = models.ForeignKey(
        Vet, db_column="vet_id", on_delete=models.CASCADE, verbose_name=_("ветеринар")
    )
    service = models.ForeignKey(
        Service, db_column="service_id", on_delete=models.CASCADE, verbose_name=_("услуга")
    )

    class Meta:
        db_table = "vet_services"
        unique_together = ("vet", "service")
        verbose_name = _("услуга ветеринара")
        verbose_name_plural = _("услуги ветеринара")

    def __str__(self):
        return f"{self.vet} → {self.service}"


# ---------- питомцы ----------
class Pet(models.Model):
    GENDERS = [("M", _("М")), ("F", _("Ж"))]

    id = models.BigAutoField(primary_key=True, db_column="pet_id")
    owner = models.ForeignKey(
        User,
        db_column="user_id",
        on_delete=models.CASCADE,
        related_name="pets",
        verbose_name=_("владелец"),
    )
    species = models.ForeignKey(
        Species,
        db_column="species_id",
        on_delete=models.SET_NULL,
        null=True,
        related_name="pets",
        verbose_name=_("вид"),
    )
    name = models.CharField(_("кличка"), max_length=100)
    breed = models.CharField(_("порода"), max_length=100, blank=True)
    gender = models.CharField(_("пол"), max_length=1, choices=GENDERS)
    date_of_birth = models.DateField(_("дата рождения"), null=True, blank=True)
    weight_kg = models.DecimalField(
        _("вес (кг)"), max_digits=5, decimal_places=2, null=True, blank=True
    )
    photo = models.ImageField(
        _("фото"), upload_to="pets/", blank=True, null=True, db_column="photo_path"
    )
    created_at = models.DateTimeField(_("создан"), default=timezone.now)
    updated_at = models.DateTimeField(_("обновлён"), auto_now=True)

    class Meta:
        db_table = "pets"
        verbose_name = _("питомец")
        verbose_name_plural = _("питомцы")

    def __str__(self):
        return self.name

    # вспомогательный метод для админки
    @property
    def age_years(self):
        if not self.date_of_birth:
            return "—"
        return (timezone.now().date() - self.date_of_birth).days // 365
    age_years.fget.short_description = _("возраст, лет")


# ---------- записи ----------
class Appointment(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="appointment_id")
    pet = models.ForeignKey(
        Pet, db_column="pet_id", on_delete=models.CASCADE, related_name="appointments", verbose_name=_("питомец")
    )
    clinic = models.ForeignKey(
        Clinic,
        db_column="clinic_id",
        on_delete=models.SET_NULL,
        null=True,
        related_name="appointments",
        verbose_name=_("клиника"),
    )
    service = models.ForeignKey(
        Service,
        db_column="service_id",
        on_delete=models.SET_NULL,
        null=True,
        related_name="appointments",
        verbose_name=_("услуга"),
    )
    vet = models.ForeignKey(
        Vet,
        db_column="vet_id",
        on_delete=models.SET_NULL,
        null=True,
        related_name="appointments",
        verbose_name=_("ветеринар"),
    )
    start_time = models.DateTimeField(_("начало"))
    end_time = models.DateTimeField(_("конец"), null=True, blank=True)
    status = models.ForeignKey(
        AppointmentStatus,
        db_column="status_id",
        on_delete=models.SET_NULL,
        null=True,
        related_name="appointments",
        verbose_name=_("статус"),
    )
    notes = models.TextField(_("заметки"), blank=True)
    created_at = models.DateTimeField(_("создан"), default=timezone.now)
    updated_at = models.DateTimeField(_("обновлён"), auto_now=True)
    created_by_user = models.ForeignKey(
        User,
        db_column="created_by_user_id",
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
        verbose_name=_("создал"),
    )
    updated_by_user = models.ForeignKey(
        User,
        db_column="updated_by_user_id",
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
        verbose_name=_("обновил"),
    )

    class Meta:
        db_table = "appointments"
        verbose_name = _("запись")
        verbose_name_plural = _("записи")

    def __str__(self):
        return f"{self.pet} • {self.start_time:%d.%m %H:%M}"

    @property
    def duration(self):
        if self.end_time:
            return (self.end_time - self.start_time).seconds // 60
        return None
    duration.fget.short_description = _("длительность, мин")
