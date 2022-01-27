from django.contrib import admin

from core.models import Hotel, Photo, Review, Booking, Profile
# Register your models here.

admin.site.register(Hotel)
admin.site.register(Photo)
admin.site.register(Review)
admin.site.register(Booking)
admin.site.register(Profile)
