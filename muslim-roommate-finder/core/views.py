from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Profile
from .forms import ProfileForm, ContactForm

def home(request):
    # Get search parameters from URL (e.g., ?city=NewYork&gender=M)
    search_query = request.GET.get('search', '')  # Get 'search' parameter, default to empty string
    city_filter = request.GET.get('city', '')  # Get 'city' parameter
    neighborhood_filter = request.GET.get('neighborhood', '')  # Get 'neighborhood' parameter
    gender_filter = request.GET.get('gender', '')  # Get 'gender' parameter
    preference_filter = request.GET.get('preference', '')  # Get 'preference' parameter
    age_min = request.GET.get('age_min', '') # Get 'age_min' parameter
    age_max = request.GET.get('age_max', '') # Get 'age_max' parameter
    charleston_only = request.GET.get('charleston_only', '') # Get 'charleston_only' paramete
    
    # Start with all profiles, optimize with select_related if needed later
    profiles = Profile.objects.all()
    
    # Apply search filter (searches name, city, neighborhood, and bio)
    if search_query:
        profiles = profiles.filter(
            Q(name__icontains=search_query) |  # Search in name (case-insensitive)
            Q(city__icontains=search_query) |  # Search in city
            Q(neighborhood__icontains=search_query) | # Search in neighborhood
            Q(bio__icontains=search_query)     # Search in bio
        )
    
    # Apply city and location filter
    if city_filter:
        profiles = profiles.filter(city__icontains=city_filter)
    if neighborhood_filter:
        profiles = profiles.filter(neighborhood__icontains=neighborhood_filter)

    #Charleston area filter
    if charleston_only:
        charleston_areas = ['Downtown', 'West Ashley', 'Mount Pleasant', 'James Island', 'Charleston County']
        profiles = profiles.filter(city__iregex=r'(' + '|'.join(charleston_areas) + ')')
    
    # Apply gender filter
    if gender_filter:
        profiles = profiles.filter(gender=gender_filter)

    if age_min:
        profiles = profiles.filter(age__gte=age_min)
    if age_max:
        profiles = profiles.filter(age__lte=age_max)
    else:
        raise ValueError("Age range must be specified")
    
    # Apply preference filter
    if preference_filter:
        if preference_filter == 'halal_kitchen':
            profiles = profiles.filter(halal_kitchen=True)
        elif preference_filter == 'prayer_friendly':
            profiles = profiles.filter(prayer_friendly=True)
        elif preference_filter == 'guests_allowed':
            profiles = profiles.filter(guests_allowed=True)
        elif preference_filter == 'looking_for_room':
            profiles = profiles.filter(is_looking_for_room=True)
    
    # Get unique cities and neighborhoods for dropdowns
    cities = Profile.objects.values_list('city', flat=True).distinct().order_by('city')
    neighborhoods = Profile.objects.values_list('neighborhood', flat=True).distinct().order_by('neighborhood')
    
    # Create context dictionary to send to template
    context = {
        'profiles': profiles,
        'cities': cities,
        'neighborhoods': neighborhoods,
        'search_query': search_query,
        'city_filter': city_filter,
        "neighborhood_filter": neighborhood_filter,
        'gender_filter': gender_filter,
        'preference_filter': preference_filter,
        'age_min': age_min,
        'age_max': age_max,
        'charleston_only': charleston_only,
        "profile_count": profiles.count(),
    }
    
    return render(request, 'home.html', context)

def profile_detail(request, profile_id):
    """
    Display detailed information about a specific profile.
    
    Args:
        request: The HTTP request object
        profile_id: The ID of the profile to display (from URL)
    
    Returns:
        Rendered template with profile details
    """
    # get_object_or_404 tries to find the profile, if not found, shows 404 page
    profile = get_object_or_404(Profile, id=profile_id)
    
    # Get similar profiles with better location matching
    similar_profiles = Profile.objects.exclude(id=profile.id)
    if profile.neighborhood:
        similar_neighborhood = similar_profiles.filter(
            city=profile.city,
            neighborhood=profile.neighborhood
        )[:2]
        similar_profiles = list(similar_neighborhood)
    else:
        similar_profiles_list = []

    #then same city
    if len(similar_profiles_list) < 3:
        similar_city = similar_profiles.filter(city=profile.city).exclude(
            id__in=[p.id for p in similar_profiles_list]
        )[:3-len(similar_profiles_list)]
        similar_profiles_list.extend(similar_city)
    #if still need more, and it's charleston area, expand to Charleston metro
    if len(similar_profiles_list) < 3 and profile.is_charleston_area():
        charleston_cities = ['charleston', 'mount pleasant', 'west ashley']
        similar_metro = similar_profiles.filter(
            city__iregex=r'(' + '|'.join(charleston_cities) + ')'
        ).exclude(
            id_in=[p.id for p in similar_profiles_list]
        )[:3-len(similar_profiles_list)]
        similar_profiles_list.extend(similar_metro)
    similar_profiles = similar_profiles_list
    context = {
        'profile': profile,
        'similar_profiles': similar_profiles,
    }
    
    return render(request, 'profile_detail.html', context)

def contact_profile(request, profile_id):
    """
    Handle contact requests to profile owners.
    
    This view allows users to send messages to profile owners while
    maintaining privacy and tracking contact history.
    
    Args:
        request: The HTTP request object
        profile_id: The ID of the profile being contacted (from URL)
    
    Returns:
        Either contact form or redirect to profile detail
    """
    # Get the profile being contacted, or show 404 if not found
    profile = get_object_or_404(Profile, id=profile_id)
    
    if request.method == 'POST':
        # User submitted the contact form
        form = ContactForm(request.POST)
        if form.is_valid():
            # Create the contact but don't save yet
            contact = form.save(commit=False)
            # Associate the contact with the specific profile
            contact.profile = profile
            # Save the contact to the database
            contact.save()
            
            # Show success message
            messages.success(
                request, 
                f'Your message has been sent to {profile.name}! They will receive your contact information.'
            )
            
            # Redirect back to the profile detail page
            return redirect('profile_detail', profile_id=profile.id)
        else:
            # Form has errors, show them to the user
            messages.error(request, 'Please correct the errors below.')
    else:
        # GET request - show empty contact form
        form = ContactForm()
    
    # Create context for the template
    context = {
        'form': form,
        'profile': profile,
    }
    
    return render(request, 'contact_profile.html', context)

def delete_profile(request, profile_id):
    """
    Delete a profile with confirmation.
    
    This view handles two scenarios:
    1. GET request: Shows confirmation page
    2. POST request: Actually deletes the profile
    
    Args:
        request: The HTTP request object
        profile_id: The ID of the profile to delete (from URL)
    
    Returns:
        Either confirmation page or redirect to home
    """
    # Get the profile to delete, or show 404 if not found
    profile = get_object_or_404(Profile, id=profile_id)
    
    if request.method == 'POST':
        # User confirmed deletion - actually delete the profile
        profile_name = profile.name  # Store name for success message
        profile.delete()  # This removes the profile from the database
        
        # Show success message
        messages.success(request, f'Profile "{profile_name}" has been deleted successfully.')
        
        # Redirect to home page
        return redirect('home')
    
    # GET request - show confirmation page
    context = {
        'profile': profile,
    }
    
    return render(request, 'delete_profile.html', context)

def edit_profile(request, profile_id):
    """
    Edit an existing profile.
    
    Args:
        request: The HTTP request object
        profile_id: The ID of the profile to edit (from URL)
    
    Returns:
        Rendered template with edit form
    """
    # Get the profile to edit, or show 404 if not found
    profile = get_object_or_404(Profile, id=profile_id)
    
    if request.method == 'POST':
        # Create form with submitted data AND the existing profile instance
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()  # This updates the existing profile instead of creating new one
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_detail', profile_id=profile.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Create form with existing profile data (pre-fills all fields)
        form = ProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
        'is_editing': True,  # Flag to show different title/button text
    }
    
    return render(request, 'edit_profile.html', context)

def create_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile created successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm()
    
    return render(request, 'create_profile.html', {'form': form})
