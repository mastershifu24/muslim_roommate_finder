# Study Guide: Views (views.py) - Complete Code Analysis

## 🎯 Views Deep Dive

Views are the heart of your Django application. They handle HTTP requests, process data, and return responses. This guide covers all the views in your Muslim Roommate Finder app.

---

## 📋 Imports and Setup

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile, Room, Message
from .forms import ProfileForm, ContactForm, RoomForm, UserRegistrationForm
```

### **Key Imports Explained:**

1. **`render`**: Renders templates with context
2. **`redirect`**: Redirects to another URL
3. **`get_object_or_404`**: Gets object or returns 404 error
4. **`messages`**: Flash messages for user feedback
5. **`Q`**: Complex database queries
6. **`login_required`**: Decorator to protect views
7. **`login, authenticate, logout`**: Authentication functions

---

## 🏠 Home View

**Purpose:** Main page showing all profiles and rooms with search/filter functionality.

```python
def home(request):
    # Get search parameters from URL
    search_query = request.GET.get('search', '')
    city_filter = request.GET.get('city', '')
    neighborhood_filter = request.GET.get('neighborhood', '')
    gender_filter = request.GET.get('gender', '')
    preference_filter = request.GET.get('preference', '')
    age_min = request.GET.get('age_min', '')
    age_max = request.GET.get('age_max', '')
    charleston_only = request.GET.get('charleston_only', '')
    
    # Start with all profiles
    profiles = Profile.objects.all()
    
    # Apply search filter
    if search_query:
        profiles = profiles.filter(
            Q(name__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(neighborhood__icontains=search_query) |
            Q(bio__icontains=search_query)
        )
    
    # Apply city and location filter
    if city_filter:
        profiles = profiles.filter(city__icontains=city_filter)
    if neighborhood_filter:
        profiles = profiles.filter(neighborhood__icontains=neighborhood_filter)

    # Charleston area filter
    if charleston_only:
        charleston_areas = ['Downtown', 'West Ashley', 'Mount Pleasant', 'James Island', 'Charleston County']
        profiles = profiles.filter(city__iregex=r'(' + '|'.join(charleston_areas) + ')')
    
    # Apply gender filter
    if gender_filter:
        profiles = profiles.filter(gender=gender_filter)

    # Apply age filters
    if age_min:
        profiles = profiles.filter(age__gte=age_min)
    if age_max:
        profiles = profiles.filter(age__lte=age_max)
    
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
        elif preference_filter == 'offering_room':
            profiles = profiles.filter(is_looking_for_room=False)
    
    # Get unique cities and neighborhoods for dropdowns
    cities = Profile.objects.values_list('city', flat=True).distinct().order_by('city')
    neighborhoods = Profile.objects.values_list('neighborhood', flat=True).distinct().order_by('neighborhood')
    
    # Get available rooms from Room model
    available_rooms = Room.objects.all()

    # Apply filters to available rooms
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
    
    # Create context dictionary
    context = {
        'profiles': profiles,
        'available_rooms': available_rooms,
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
        "rooms_count": available_rooms.count(),
    }
    
    return render(request, 'home.html', context)
```

### **Key Concepts:**

1. **GET Parameters:** Extract search/filter parameters from URL
2. **Q Objects:** Complex queries with OR conditions
3. **Filter Chaining:** Apply multiple filters to queryset
4. **Context Dictionary:** Pass data to template
5. **Count Queries:** Get counts for display

---

## 👤 Profile Detail View

**Purpose:** Show detailed information about a specific profile with similar profiles.

```python
def profile_detail(request, profile_id):
    # Get the profile or show 404
    profile = get_object_or_404(Profile, id=profile_id)
    
    # Get similar profiles with location matching
    similar_profiles = Profile.objects.exclude(id=profile.id)
    similar_profiles_list = []
    
    # First, try to find profiles in same neighborhood
    if profile.neighborhood:
        similar_neighborhood = similar_profiles.filter(
            city=profile.city,
            neighborhood=profile.neighborhood
        )[:2]
        similar_profiles_list.extend(similar_neighborhood)

    # Then, find profiles in same city
    if len(similar_profiles_list) < 3:
        similar_city = similar_profiles.filter(city=profile.city).exclude(
            id__in=[p.id for p in similar_profiles_list]
        )[:3-len(similar_profiles_list)]
        similar_profiles_list.extend(similar_city)
    
    # If still need more, expand to Charleston metro area
    if len(similar_profiles_list) < 3 and profile.is_charleston_area():
        charleston_cities = ['charleston', 'mount pleasant', 'west ashley']
        similar_metro = similar_profiles.filter(
            city__iregex=r'(' + '|'.join(charleston_cities) + ')'
        ).exclude(
            id__in=[p.id for p in similar_profiles_list]
        )[:3-len(similar_profiles_list)]
        similar_profiles_list.extend(similar_metro)
    
    similar_profiles = similar_profiles_list
    context = {
        'profile': profile,
        'similar_profiles': similar_profiles,
    }
    
    return render(request, 'profile_detail.html', context)
```

### **Key Concepts:**

1. **get_object_or_404:** Safe way to get objects
2. **Similar Profiles Algorithm:** Location-based matching
3. **Exclude:** Remove current profile from results
4. **List Comprehension:** Get IDs for exclusion
5. **Regex Filtering:** Pattern matching for cities

---

## 🏠 Room Detail View

**Purpose:** Show detailed information about a specific room.

```python
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    context = {
        'room': room,
    }
    return render(request, 'room_detail.html', context)
```

### **Key Concepts:**

1. **Simple View:** Sometimes less is more
2. **Context:** Pass single object to template
3. **Template Rendering:** Let template handle display logic

---

## 📞 Contact Profile View

**Purpose:** Handle contact requests between users.

```python
def contact_profile(request, profile_id):
    # Get the profile being contacted
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
```

### **Key Concepts:**

1. **POST vs GET:** Different handling for form submission
2. **Form Validation:** Check if form data is valid
3. **commit=False:** Create object without saving
4. **Messages Framework:** User feedback
5. **Redirect:** Send user to another page

---

## 🗑️ Delete Profile View

**Purpose:** Delete a profile with confirmation.

```python
def delete_profile(request, profile_id):
    # Get the profile to delete
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
```

### **Key Concepts:**

1. **Confirmation Pattern:** GET shows form, POST performs action
2. **Store Data:** Keep profile name before deletion
3. **Delete Method:** Remove from database
4. **Success Feedback:** Inform user of success

---

## ✏️ Edit Profile View

**Purpose:** Edit an existing profile.

```python
def edit_profile(request, profile_id):
    # Get the profile to edit
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
```

### **Key Concepts:**

1. **instance Parameter:** Pre-fill form with existing data
2. **Update vs Create:** Same form, different behavior
3. **Context Flag:** Template can show different UI
4. **Redirect to Detail:** Show updated profile

---

## ➕ Create Profile View

**Purpose:** Create a new profile (requires login).

```python
@login_required
def create_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user  # Associate with current user
            profile.save()
            messages.success(request, 'Profile created successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm()
    
    return render(request, 'create_profile.html', {'form': form})
```

### **Key Concepts:**

1. **@login_required:** Protect view from anonymous users
2. **commit=False:** Create object without saving
3. **User Association:** Link profile to current user
4. **Redirect to Home:** Show all profiles after creation

---

## 🏠 Create Room View

**Purpose:** Create a new room listing (requires login).

```python
@login_required
def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.user = request.user  # Associate with current user
            room.save()
            messages.success(request, 'Room listing created successfully!')
            return redirect('room_detail', room_id=room.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RoomForm()
    return render(request, 'create_room.html', {'form': form})
```

### **Key Concepts:**

1. **Similar Pattern:** Same as create_profile
2. **User Association:** Link room to current user
3. **Redirect to Detail:** Show the created room

---

## 📝 Register View

**Purpose:** User registration and account creation.

```python
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Create the user
            login(request, user)  # Log them in automatically
            messages.success(request, 'Account created successfully! Welcome to Muslim Roommate Finder!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})
```

### **Key Concepts:**

1. **User Creation:** Save new user to database
2. **Auto Login:** Log user in after registration
3. **Welcome Message:** Friendly user feedback
4. **Redirect to Home:** Start using the app

---

## 🔐 Login View

**Purpose:** User authentication.

```python
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})
```

### **Key Concepts:**

1. **Authentication Form:** Django's built-in login form
2. **authenticate():** Verify credentials
3. **login():** Create user session
4. **cleaned_data:** Safe form data
5. **Error Handling:** Invalid credentials

---

## 🚪 Logout View

**Purpose:** User logout.

```python
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')
```

### **Key Concepts:**

1. **logout():** End user session
2. **Simple View:** Minimal logic needed
3. **Feedback:** Inform user of logout

---

## 📊 Dashboard View

**Purpose:** User's personal dashboard (requires login).

```python
@login_required
def dashboard(request):
    user_rooms = Room.objects.filter(user=request.user)[:5]  # Limit to 5
    user_profiles = Profile.objects.filter(user=request.user)[:5]  # Limit to 5
    
    return render(request, 'dashboard.html', {
        'rooms': user_rooms,
        'profiles': user_profiles
    })
```

### **Key Concepts:**

1. **User-Specific Data:** Filter by current user
2. **Limit Results:** Show only recent items
3. **Protected View:** Only for logged-in users

---

## 📋 My Listings View

**Purpose:** Show all user's listings (requires login).

```python
@login_required
def my_listings(request):
    user_rooms = Room.objects.filter(user=request.user)
    user_profiles = Profile.objects.filter(user=request.user)
    
    return render(request, 'my_listings.html', {
        'rooms': user_rooms,
        'profiles': user_profiles
    })
```

### **Key Concepts:**

1. **Complete List:** Show all user's content
2. **User Filtering:** Only show current user's data
3. **Management Interface:** User can manage their content

---

## 🔍 Advanced Search View

**Purpose:** Advanced room search with multiple filters.

```python
def advanced_search(request):
    # Get all filter parameters
    min_rent = request.GET.get('min_rent', '')
    max_rent = request.GET.get('max_rent', '')
    available_date = request.GET.get('available', '')
    room_type = request.GET.get('room_type', '')

    rooms = Room.objects.all()

    # Apply filters
    if min_rent:
        rooms = rooms.filter(rent__gte=min_rent)
    if max_rent:
        rooms = rooms.filter(rent__lte=max_rent)
    if available_date:
        rooms = rooms.filter(available_from__lte=available_date)
    if room_type:
        rooms = rooms.filter(room_type=room_type)

    # Get unique values for dropdowns
    cities = Room.objects.values_list('city', flat=True).distinct().order_by('city')
    rent_ranges = [
        ('0-500', 'Under $500'),
        ('500-1000', '$500 - $1000'),
        ('1000-1500', '$1,000 - $1,500'),
        ('1500+', 'Over $1,500'),
    ]

    return render(request, 'advanced_search.html', {
        'rooms': rooms,
        'cities': cities,
        'rent_ranges': rent_ranges,
        'filters': request.GET
    })
```

### **Key Concepts:**

1. **Multiple Filters:** Combine different search criteria
2. **Range Queries:** Min/max values
3. **Date Filtering:** Available from date
4. **Dropdown Data:** Predefined options
5. **Filter Preservation:** Keep current filters in context

---

## 💬 Send Message View

**Purpose:** Send messages between users (requires login).

```python
@login_required
def send_message(request, room_id=None):
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        subject = request.POST.get('subject')
        content = request.POST.get('content')

        recipient = User.objects.get(id=recipient_id)
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
```

### **Key Concepts:**

1. **Optional Parameters:** room_id can be None
2. **Message Creation:** Create new message object
3. **User Lookup:** Get recipient by ID
4. **Success Feedback:** Confirm message sent

---

## 📥 Inbox View

**Purpose:** Show user's messages (requires login).

```python
@login_required
def inbox(request):
    received_messages = Message.objects.filter(recipient=request.user)
    sent_messages = Message.objects.filter(sender=request.user)

    return render(request, 'inbox.html', {
        'received_messages': received_messages,
        'sent_messages': sent_messages
    })
```

### **Key Concepts:**

1. **Separate Lists:** Received vs sent messages
2. **User Filtering:** Only show user's messages
3. **Message Management:** View and manage communications

---

## 🎯 Key Learning Points

### **1. View Patterns:**
- **List Views:** Show multiple objects
- **Detail Views:** Show single object
- **Create Views:** Add new objects
- **Update Views:** Modify existing objects
- **Delete Views:** Remove objects
- **Form Views:** Handle form submissions

### **2. HTTP Methods:**
- **GET:** Retrieve data, show forms
- **POST:** Submit data, process forms

### **3. Authentication:**
- **@login_required:** Protect views
- **User Association:** Link content to users
- **Session Management:** Login/logout

### **4. Database Queries:**
- **Filter:** Narrow down results
- **Q Objects:** Complex queries
- **Exclude:** Remove specific items
- **Order By:** Sort results
- **Limit:** Restrict number of results

### **5. User Experience:**
- **Messages:** Provide feedback
- **Redirects:** Guide user flow
- **Error Handling:** Graceful failures
- **Context:** Pass data to templates

---

## 🧪 Practice Questions

1. **How would you add pagination to the home view?**
   - Answer: Use `Paginator` class and `page` parameter

2. **How would you add sorting to room listings?**
   - Answer: Add `order_by` parameter and apply to queryset

3. **How would you implement search history?**
   - Answer: Store searches in session or database

4. **How would you add caching to expensive queries?**
   - Answer: Use `cache.get()` and `cache.set()`

5. **How would you implement AJAX for real-time search?**
   - Answer: Return JSON response instead of rendering template

---

## 🚀 Next Steps

1. **Study the patterns** in different view types
2. **Practice writing views** for new features
3. **Learn about class-based views** for more complex logic
4. **Explore Django REST Framework** for API views
5. **Understand middleware** and how it affects views
