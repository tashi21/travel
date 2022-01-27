from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import RatingForm, searchForm, BookingForm, ProfileForm, PasswordForm
from .models import Hotel, Review, Booking, Profile
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

# Create your views here.


def priceRange(price):
    diff = 1000
    h = Hotel.objects.all()
    h = h.filter(price__gt=price-diff)
    h = h.filter(price__lt=price+diff)
    return h[:4]


def searchFunctionality(smoking_rooms, pool, free_wifi, gym, spa, dry_cleaning, room_service, breakfast):
    x = Hotel.objects.all()
    x = x.filter(smoking_rooms=True) if smoking_rooms == True else x
    x = x.filter(pool=True) if pool == True else x
    x = x.filter(free_wifi=True) if free_wifi else x
    x = x.filter(gym=True) if gym else x
    x = x.filter(spa=True) if spa else x
    x = x.filter(dry_cleaning=True) if dry_cleaning else x
    x = x.filter(room_service=True) if room_service else x
    x = x.filter(breakfast=True) if breakfast else x
    return x


def homeView(request):
    context = {}
    return render(request, "home.html", context)


def bookingsView(request):
    bookings = Booking.objects.filter(user=request.user)
    context = {
        "bookings": bookings,
    }
    return render(request, "bookings.html", context)


def details_view(request, my_id):
    if request.method == "POST":
        form = RatingForm(request.POST or None)
        booking = BookingForm(request.POST or None)
        print(booking.errors)
        if booking.is_valid():
            user = request.user
            start = booking.cleaned_data["start"]
            end = booking.cleaned_data["end"]
            guests = booking.cleaned_data["guests"]
            payment = booking.cleaned_data["payment"]
            hotel = Hotel.objects.get(id=my_id)
            total = int(guests) * hotel.price
            book = Booking(
                start=start, end=end, guests=guests, payment=payment, total=total, hotel=hotel, user=user)
            book.save()
            return redirect("bookings")

        if form.is_valid():
            body = {
                "name": form.cleaned_data["name"],
                "rating": form.cleaned_data["rating"],
                "review": form.cleaned_data["review"]
            }
            rev = Review(rating=body["rating"], hotel=Hotel.objects.get(
                id=my_id), review=body["review"], user=request.user)
            rev.save()
            return redirect(f"/hotels/{my_id}")

    form = RatingForm()
    booking = BookingForm()
    h = Hotel.objects.get(id=my_id)
    similar = priceRange(h.price)
    photos = h.photo_set.all()
    reviews = h.review_set.all()
    photo_urls = [photo.url for photo in photos]
    facilities = [(h.smoking_rooms, "Smoking Rooms"), (h.pool, "Pool"), (h.gym, "Gymnasium"), (h.room_service, "Room Service"),
                  (h.spa, "Spa"), (h.breakfast, "Breakfast Included"), (h.free_wifi, "Free Wifi"), (h.dry_cleaning, "Dry Cleaning Service Offered")]
    context = {
        "reviews": reviews,
        "form": form,
        "object": h,
        "urls": photo_urls,
        "facilities": facilities,
        "recommendations": similar,
        "booking": booking
    }
    return render(request, "details.html", context)


def hotel_search_view(request):
    x = Hotel.objects.all()

    if request.method == "GET":
        form = searchForm(request.GET)
        # if the form is valid
        if form.is_valid():
            x = searchFunctionality(form.cleaned_data["smoking_rooms"], form.cleaned_data["pool"], form.cleaned_data["free_wifi"], form.cleaned_data["gym"],
                                    form.cleaned_data["spa"], form.cleaned_data["dry_cleaning"], form.cleaned_data["room_service"], form.cleaned_data["breakfast"])

            if form.cleaned_data["price_lower"] != None:
                x = x.filter(price__gt=form.cleaned_data["price_lower"])

            if form.cleaned_data["price_upper"] != None:
                x = x.filter(price__lt=form.cleaned_data["price_upper"])

            if form.cleaned_data["neighbourhood"] != None:
                x = x.filter(
                    address__icontains=form.cleaned_data["neighbourhood"])

            # if the rating field isn't filled
            if form.cleaned_data["rating"] != None:
                y = []
                # search every hotel and check if it has that rating. after this we get a list y with hotels of that rating
                for hotel in x:
                    # if the hotel has an average rating of what is asked
                    if hotel.review_set.all():
                        if hotel.average_rating() == form.cleaned_data["rating"]:
                            y.append(hotel)
                # x needs to be put into the context
                x = y

        context = {
            "hotels": x,
            "form": form
        }
        return render(request, "search.html", context)


class AboutView(TemplateView):
    """The About Page"""
    template_name = "about.html"


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Profile view.
    """
    template_name = "profile.html"

    def get(self, *args, **kwargs):
        """Get profile view."""
        user = self.request.user
        reviews = user.review_set.all()
        profile_form = ProfileForm()
        password_form = PasswordForm()
        profile = Profile.objects.get(user=self.request.user)
        return render(self.request, "profile.html", {"profile_form": profile_form, "password_form": password_form, "user": self.request.user, "profile": profile, "reviews": reviews})

    def post(self, *args, **kwargs):
        """Update profile view."""
        profile_form = ProfileForm(
            self.request.POST or None, self.request.FILES)
        password_form = PasswordForm(self.request.POST or None)
        user = self.request.user
        profile = Profile.objects.get(user=user)
        if profile_form.is_valid():
            print(profile_form.cleaned_data)
            user.first_name = profile_form.cleaned_data["first_name"]
            user.last_name = profile_form.cleaned_data["last_name"]
            try:
                testuser = get_user_model().objects.get(
                    username=profile_form.cleaned_data["username"])
                if testuser != user:
                    messages.warning(self.request, "Username already exists")
                    return redirect("core:profile")
            except ObjectDoesNotExist:
                user.username = profile_form.cleaned_data["username"]
            try:
                testuser = get_user_model().objects.get(
                    username=profile_form.cleaned_data["email"])
                if testuser != user:
                    messages.warning(self.request, "Email already exists")
                    return redirect("core:profile")
            except ObjectDoesNotExist:
                user.email = profile_form.cleaned_data["email"]
            profile.phone_number = profile_form.cleaned_data["phone_number"]
            if profile_form.cleaned_data["profile_pic"]:
                profile.profile_pic = profile_form.cleaned_data["profile_pic"]
            user.save()
            profile.save()
            messages.success(self.request, "Profile updated successfully")

        if password_form.is_valid():
            if password_form.cleaned_data["password1"] == "" and password_form.cleaned_data["password2"] == "" and password_form.cleaned_data["password_old"] == "":
                return redirect("profile")
            old_password = password_form.cleaned_data["password_old"]
            correct = user.check_password(old_password)
            if correct:
                try:
                    validate_password(
                        password_form.cleaned_data["password1"])
                except ValidationError:
                    messages.warning(
                        self.request, "Password does not pass validation checks.")
                    return redirect("profile")
                else:
                    if password_form.cleaned_data["password1"] == password_form.cleaned_data["password2"]:
                        user.set_password(
                            password_form.cleaned_data["password1"])
                        user.save()
                        messages.success(
                            self.request, "Password updated successfully!")
                    else:
                        messages.warning(
                            self.request, "Passwords do not match.")
                        return redirect("profile")
            else:
                messages.warning(self.request, "Old password is incorrect.")
        return redirect("profile")
