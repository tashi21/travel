from django.db.models.signals import post_save
from django.dispatch import receiver
import numpy as np
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.


class Hotel(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    address = models.CharField(max_length=100)
    longitude = models.FloatField()
    latitude = models.FloatField()
    smoking_rooms = models.BooleanField(default=False)
    pool = models.BooleanField(default=False)
    gym = models.BooleanField(default=False)
    room_service = models.BooleanField(default=False)
    spa = models.BooleanField(default=False)
    breakfast = models.BooleanField(default=False)
    free_wifi = models.BooleanField(default=False)
    dry_cleaning = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def average_rating(self):
        all_ratings = list(map(lambda x: x.rating, self.review_set.all()))
        if all_ratings:
            return round(np.mean(all_ratings))
        else:
            0

    def get_absolute_url(self):
        """Returns the url to access a particular instance of the model."""
        return f"/hotels/{self.id}"

    def __str__(self):
        return self.name


class Photo(models.Model):
    url = models.CharField(max_length=400)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    rating = models.IntegerField(
        default=3,
        validators=[MinValueValidator(0), MaxValueValidator(5)])
    review = models.TextField(default="Great", null=True)


class Booking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    start = models.DateField()
    end = models.DateField()
    guests = models.IntegerField()
    total = models.IntegerField()
    payment = models.CharField(max_length=100)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)

    class Meta:
        ordering = ["start"]


class Profile(models.Model):
    """
    User profile model.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=10, blank=True)
    profile_pic = models.ImageField(
        upload_to="profile_pics/", blank=True, null=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance=None, created=False, **kwargs):
    """
    Create a profile for the user when user is created.
    """
    if created:
        Profile.objects.create(user=instance)
