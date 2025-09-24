from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile, Room, Message
from .forms import ProfileForm, ContactForm, RoomForm, UserRegistrationForm
from .models import RoomType, Amenity


def home(request):
    """
    Home page showing profiles and room listings with search and filters.
    Supports filtering by city, neighborhood, gender, preferences, age range, and Charleston area.
    """
    search_query = request.GET.get('search', '')
    city_filter = request.GET.get('city', '')
    neighborhood_filter = request.GET.get('neighborhood', '')
    gender_filter = request.GET.get('gender', '')
    preference_filter = request.GET.get('preference', '')
    age_min = request.GET.get('age_min', '')
    age_max = request.GET.get('age_max', '')
    charleston_only = request.GET.get('charleston_only', '')

    # Filter Profiles
    profiles = Profile.objects.all()

    if search_query:
        profiles = profiles.filter(
            Q(name__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(neighborhood__icontains=search_query) |
            Q(bio__icontains=search_query)
        )

    if city_filter:
        profiles = profiles.filter(city__icontains=city_filter)
    if neighborhood_filter:
        profiles = profiles.filter(neighborhood__icontains=neighborhood_filter)
    if charleston_only:
        charleston_areas = ['Downtown', 'West Ashley', 'Mount Pleasant', 'James Island', 'Charleston County']
        profiles = profiles.filter(city__iregex=r'(' + '|'.join(charleston_areas) + ')')
    if gender_filter:
        profiles = profiles.filter(gender=gender_filter)
    if age_min:
        profiles = profiles.filter(age__gte=age_min)
    if age_max:
        profiles = profiles.filter(age__lte=age_max)
    if preference_filter:
        # Map preference filters to Profile fields
        pref_map = {
            'halal_kitchen': 'halal_kitchen',
            'prayer_friendly': 'prayer_friendly',
            'guests_allowed': 'guests_allowed',
            'looking_for_room': 'is_looking_for_room',
            'offering_room': 'is_looking_for_room'
        }
        field = pref_map.get(preference_filter)
        if field:
            value = True if preference_filter != 'offering_room' else False
            profiles = profiles.filter(**{field: value})

    # Filter Rooms
    available_rooms = Room.objects.filter(is_active=True)
    if search_query:
        available_rooms = available_rooms.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(neighborhood__icontains=search_query)
        )
    if city_filter:
        available_rooms = available_rooms.filter(city__icontains=city_filter)
    if neighborhood_filter:
        available_rooms = available_rooms.filter(neighborhood__icontains=neighborhood_filter)
    if charleston_only:
        charleston_areas = ['Downtown', 'West Ashley', 'Mount Pleasant', 'James Island', 'Charleston County']
        available_rooms = available_rooms.filter(city__iregex=r'(' + '|'.join(charleston_areas) + ')')
    if preference_filter in ['halal_kitchen', 'prayer_friendly', 'guests_allowed']:
        available_rooms = available_rooms.filter(**{preference_filter: True})

    # Unique cities and neighborhoods for filter dropdowns
    cities = Profile.objects.values_list('city', flat=True).distinct().order_by('city')
    neighborhoods = Profile.objects.values_list('neighborhood', flat=True).distinct().order_by('neighborhood')

    context = {
        'profiles': profiles,
        'available_rooms': available_rooms,
        'cities': cities,
        'neighborhoods': neighborhoods,
        'search_query': search_query,
        'city_filter': city_filter,
        'neighborhood_filter': neighborhood_filter,
        'gender_filter': gender_filter,
        'preference_filter': preference_filter,
        'age_min': age_min,
        'age_max': age_max,
        'charleston_only': charleston_only,
        'profile_count': profiles.count(),
        'rooms_count': available_rooms.count(),
    }

    return render(request, 'home.html', context)


def profile_detail(request, profile_id):
    """
    Display a single profile with similar profile suggestions.
    """
    profile = get_object_or_404(Profile, id=profile_id)

    # Similar profiles: same neighborhood -> same city -> Charleston metro
    similar_profiles_list = []
    similar_profiles = Profile.objects.exclude(id=profile.id)

    if profile.neighborhood:
        neighborhood_matches = similar_profiles.filter(
            city=profile.city,
            neighborhood=profile.neighborhood
        )[:2]
        similar_profiles_list.extend(neighborhood_matches)

    if len(similar_profiles_list) < 3:
        city_matches = similar_profiles.filter(city=profile.city).exclude(
            id__in=[p.id for p in similar_profiles_list]
        )[:3-len(similar_profiles_list)]
        similar_profiles_list.extend(city_matches)

    if len(similar_profiles_list) < 3 and profile.is_charleston_area():
        charleston_cities = ['charleston', 'mount pleasant', 'west ashley']
        metro_matches = similar_profiles.filter(
            city__iregex=r'(' + '|'.join(charleston_cities) + ')'
        ).exclude(id__in=[p.id for p in similar_profiles_list])[:3-len(similar_profiles_list)]
        similar_profiles_list.extend(metro_matches)

    context = {
        'profile': profile,
        'similar_profiles': similar_profiles_list,
    }

    return render(request, 'profile_detail.html', context)


def room_detail(request, room_id):
    """
    Display a single room listing.
    """
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'room_detail.html', {'room': room})


def contact_profile(request, profile_id):
    """
    Contact a profile owner via form submission.
    """
    profile = get_object_or_404(Profile, id=profile_id)

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.profile = profile
            contact.save()
            messages.success(request, f'Your message has been sent to {profile.name}!')
            return redirect('profile_detail', profile_id=profile.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()

    return render(request, 'contact_profile.html', {'form': form, 'profile': profile})


@login_required
def create_profile(request):
    """
    Create a new profile or update existing one to prevent duplicates.
    """
    try:
        profile = Profile.objects.get(user=request.user)
        is_new = False
    except Profile.DoesNotExist:
        profile = None
        is_new = True

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            msg = 'Profile created successfully!' if is_new else 'Profile updated successfully!'
            messages.success(request, msg)
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'create_profile.html', {'form': form})


@login_required
def edit_profile(request, profile_id):
    """
    Edit an existing profile.
    """
    profile = get_object_or_404(Profile, id=profile_id)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_detail', profile_id=profile.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'edit_profile.html', {'form': form, 'profile': profile, 'is_editing': True})


@login_required
def delete_profile(request, profile_id):
    """
    Delete a profile with confirmation.
    """
    profile = get_object_or_404(Profile, id=profile_id)

    if request.method == 'POST':
        profile_name = profile.name
        profile.delete()
        messages.success(request, f'Profile "{profile_name}" has been deleted successfully.')
        return redirect('home')

    return render(request, 'delete_profile.html', {'profile': profile})


@login_required
def create_room(request):
    """
    Create a room listing associated with the current user's profile.
    """
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        # Ensure querysets are populated server-side
        form.fields['room_type'].queryset = RoomType.objects.order_by('name')
        form.fields['amenities'].queryset = Amenity.objects.order_by('name')
        if form.is_valid():
            room = form.save(commit=False)
            room.user = request.user.profile
            room.save()
            messages.success(request, 'Room listing created successfully!')
            return redirect('room_detail', room_id=room.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RoomForm()
        # Ensure querysets are populated server-side
        form.fields['room_type'].queryset = RoomType.objects.order_by('name')
        form.fields['amenities'].queryset = Amenity.objects.order_by('name')
    return render(request, 'create_room.html', {'form': form})


def register(request):
    """
    Register a new user and log them in immediately.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    """
    User login view using Django AuthenticationForm.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def user_logout(request):
    """
    Logout the current user.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard(request):
    """
    User dashboard showing their profile and recent room listings.
    """
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return redirect('create_profile')

    user_rooms = profile.rooms.all()[:5]

    return render(request, 'dashboard.html', {
        'rooms': user_rooms,
        'profiles': [profile],
    })


@login_required
def my_listings(request):
    """
    Show all room listings of the logged-in user.
    """
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return redirect('create_profile')

    user_rooms = Room.objects.filter(user=profile)
    return render(request, 'my_listings.html', {'rooms': user_rooms})


def advanced_search(request):
    """
    Advanced room search by rent, availability date, and room type.
    """
    min_rent = request.GET.get('min_rent', '')
    max_rent = request.GET.get('max_rent', '')
    available_date = request.GET.get('available', '')
    room_type = request.GET.get('room_type', '')
    amenities = request.GET.getlist('amenities')

    rooms = Room.objects.filter(is_active=True)

    if min_rent:
        rooms = rooms.filter(price__gte=min_rent)
    if max_rent:
        rooms = rooms.filter(price__lte=max_rent)
    if available_date:
        rooms = rooms.filter(available_from__lte=available_date)
    if room_type:
        rooms = rooms.filter(room_type=room_type)
    if amenities:
        rooms = rooms.filter(amenities__id__in=amenities).distinct()

    cities = Room.objects.values_list('city', flat=True).distinct().order_by('city')
    rent_ranges = [
        ('0-500', 'Under $500'),
        ('500-1000', '$500 - $1000'),
        ('1000-1500', '$1,000 - $1,500'),
        ('1500+', 'Over $1,500'),
    ]
    all_amenities = Amenity.objects.all().order_by('name')

    return render(request, 'advanced_search.html', {
        'rooms': rooms,
        'cities': cities,
        'rent_ranges': rent_ranges,
        'filters': request.GET,
        'amenities': all_amenities,
        'room_type_list': room_type_list,
    })


@login_required
def send_message(request, room_id=None):
    """
    Send a message to a user, optionally tied to a room.
    """
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        subject = request.POST.get('subject')
        content = request.POST.get('content')

        recipient = get_object_or_404(User, id=recipient_id)
        room = Room.objects.get(id=room_id) if room_id else None

        Message.objects.create(
            sender=request.user,
            recipient=recipient,
            room=room,
            subject=subject,
            content=content
        )

        messages.success(request, 'Message sent successfully!')
        return redirect('inbox')

    room = Room.objects.get(id=room_id) if room_id else None
    return render(request, 'send_message.html', {'room': room})


@login_required
def inbox(request):
    """
    Inbox showing received and sent messages.
    """
    received_messages = Message.objects.filter(recipient=request.user)
    sent_messages = Message.objects.filter(sender=request.user)

    return render(request, 'inbox.html', {
        'received_messages': received_messages,
        'sent_messages': sent_messages
    })
