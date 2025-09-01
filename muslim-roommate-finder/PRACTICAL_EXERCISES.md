# Practical Exercises - Test Your Understanding

## 🎯 Exercise 1: Add a "Favorite Room" Feature

**Goal:** Add the ability for users to favorite rooms and view their favorites.

### **Step 1: Create the Model**
```python
# In models.py
from django.db import models
from django.contrib.auth.models import User

class RoomFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites') #User is a model we import directly from django.contrib.auth.models. Since Django knows what User is at this point, we can reference as a Python class.
    room = models.ForeignKey("Room", on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    #Room is a string reference. Django lets us reference models by their name instead of actual class. This is useful when we either define the model later in same file, or model is in another app.
    #Quotation marks also known as lazy reference, which means Django references it later. Also avoids import timing issues.
    #Direct class reference with no quotation marks means we already have the model imported and can use it.

    class Meta:
        unique_together = ['user', 'room']  # Prevent duplicate favorites

    def __str__(self):
        return f"{self.user.username} favorited {self.room.title}"

### **Step 2: Add the View**
# In views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import Room, RoomFavorite

@login_required
def toggle_favorite(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    favorite, created = RoomFavorite.objects.get_or_create(
        user=request.user, 
        room=room
    )
    
    if not created:
        # User already favorited, so remove it
        favorite.delete()
        messages.success(request, f'Removed {room.title} from your favorites')
    else:
        messages.success(request, f'Added {room.title} to favorites')
    
    return redirect('room_detail', room_id=room.id)

@login_required
def my_favorites(request):
    favorites = RoomFavorite.objects.filter(user=request.user).select_related("room")
    return render(request, 'my_favorites.html', {'favorites': favorites})
```

### **Step 3: Add URLs**
```python
# In urls.py
from django.urls import path
from .views import toggle_favorite, my_favorites
urlpatterns = [
path('room/<int:room_id>/favorite/', toggle_favorite, name='toggle_favorite'),
path('my-favorites/', my_favorites, name='my_favorites'),
]
```

### **Step 4: Update Templates**
```html
<!-- In room_detail.html -->
{% if user.is_authenticated %}
    <a href="{% url 'toggle_favorite' room.id %}" class="btn btn-outline-warning">
        {% if room.favorited_by.filter(user=request.user).exists %}
            ❤️ Remove from Favorites
        {% else %}
            🤍 Add to Favorites
        {% endif %}
    </a>
{% endif %}
```
<!-- In my_favorites.html -->
<h2>My Favorite Rooms</h2>

<ul>
    {% for fav in favorites %}
       <li>
         <a href="{% url 'room_detail' fav.room.id %}">{{ fav.room.title }}</a>
       </li>
    {% empty %}
      <p>You haven't favorited any rooms yet.</p>
    {% endfor %}
</ul>

## 🎯 Exercise 2: Add Room Reviews

**Goal:** Allow users to leave reviews for rooms they've stayed in.

### **Step 1: Create Review Model**
```python
# In models.py
class RoomReview(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['room', 'reviewer']  # One review per user per room
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.reviewer} for {self.room.title}"
```

### **Step 2: Create Review Form**
```python
# In forms.py
class RoomReviewForm(forms.ModelForm):
    class Meta:
        model = RoomReview
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'review_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
```

### **Step 3: Add Review View**
```python
# In views.py
@login_required
def add_review(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    # Check if user already reviewed this room
    if RoomReview.objects.filter(room=room, reviewer=request.user).exists():
        messages.error(request, 'You have already reviewed this room')
        return redirect('room_detail', room_id=room.id)
    
    if request.method == 'POST':
        form = RoomReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.room = room
            review.reviewer = request.user
            review.save()
            messages.success(request, 'Review added successfully!')
            return redirect('room_detail', room_id=room.id)
    else:
        form = RoomReviewForm()
    
    return render(request, 'add_review.html', {'form': form, 'room': room})
```

## 🎯 Exercise 3: Add Search Filters

**Goal:** Enhance the search functionality with more filters.

### **Step 1: Update the Home View**
```python
# In views.py - enhance the home view
def home(request):
    # ... existing code ...
    
    # Add new filters
    min_rent = request.GET.get('min_rent', '')
    max_rent = request.GET.get('max_rent', '')
    available_date = request.GET.get('available_date', '')
    
    # Apply rent filters to rooms
    if min_rent:
        available_rooms = available_rooms.filter(rent__gte=min_rent)
    if max_rent:
        available_rooms = available_rooms.filter(rent__lte=max_rent)
    if available_date:
        available_rooms = available_rooms.filter(available_from__lte=available_date)
    
    # Add to context
    context.update({
        'min_rent': min_rent,
        'max_rent': max_rent,
        'available_date': available_date,
    })
```

### **Step 2: Update the Template**
```html
<!-- In home.html - add to the search form -->
<div class="col-md-2">
    <label for="min_rent" class="form-label">Min Rent</label>
    <input type="number" class="form-control" id="min_rent" name="min_rent" 
           value="{{ min_rent }}" placeholder="Min rent">
</div>

<div class="col-md-2">
    <label for="max_rent" class="form-label">Max Rent</label>
    <input type="number" class="form-control" id="max_rent" name="max_rent" 
           value="{{ max_rent }}" placeholder="Max rent">
</div>

<div class="col-md-2">
    <label for="available_date" class="form-label">Available From</label>
    <input type="date" class="form-control" id="available_date" name="available_date" 
           value="{{ available_date }}">
</div>
```

## 🎯 Exercise 4: Add User Profile Pictures

**Goal:** Allow users to upload profile pictures.

### **Step 1: Update Profile Model**
```python
# In models.py
def profile_image_path(instance, filename):
    return f'profile_images/{instance.user.username}/{filename}'

class Profile(models.Model):
    # ... existing fields ...
    profile_image = models.ImageField(
        upload_to=profile_image_path, 
        blank=True, 
        null=True,
        help_text="Upload a profile picture"
    )
```

### **Step 2: Update Form**
```python
# In forms.py
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'name', 'age', 'gender', 'city', 'neighborhood', 
            'is_looking_for_room', 'bio', 'contact_email',
            'halal_kitchen', 'prayer_friendly', 'guests_allowed',
            'profile_image'  # Add this field
        ]
        widgets = {
            # ... existing widgets ...
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
```

### **Step 3: Update Template**
```html
<!-- In profile_detail.html -->
{% if profile.profile_image %}
    <img src="{{ profile.profile_image.url }}" alt="{{ profile.name }}" 
         class="img-fluid rounded" style="max-width: 200px;">
{% else %}
    <div class="bg-light rounded d-flex align-items-center justify-content-center" 
         style="width: 200px; height: 200px;">
        <i class="fas fa-user fa-3x text-muted"></i>
    </div>
{% endif %}
```

## 🎯 Exercise 5: Add Email Notifications

**Goal:** Send email notifications when someone contacts a user.

### **Step 1: Create Email Template**
```html
<!-- templates/emails/contact_notification.html -->
<!DOCTYPE html>
<html>
<head>
    <title>New Contact Request</title>
</head>
<body>
    <h2>New Contact Request</h2>
    <p>Hello {{ profile.name }},</p>
    <p>You have received a new contact request from {{ contact.sender_name }}.</p>
    
    <h3>Message:</h3>
    <p>{{ contact.message }}</p>
    
    <h3>Contact Information:</h3>
    <p>Name: {{ contact.sender_name }}</p>
    <p>Email: {{ contact.sender_email }}</p>
    
    <p>Best regards,<br>Muslim Roommate Finder</p>
</body>
</html>
```

### **Step 2: Update Contact View**
```python
# In views.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def contact_profile(request, profile_id):
    # ... existing code ...
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.profile = profile
            contact.save()
            
            # Send email notification
            subject = f'New contact request from {contact.sender_name}'
            html_message = render_to_string('emails/contact_notification.html', {
                'profile': profile,
                'contact': contact,
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email='noreply@muslimroommatefinder.com',
                recipient_list=[profile.contact_email],
                html_message=html_message,
            )
            
            messages.success(request, f'Your message has been sent to {profile.name}!')
            return redirect('profile_detail', profile_id=profile.id)
```

## 🎯 Exercise 6: Add Room Availability Calendar

**Goal:** Show when rooms are available/unavailable.

### **Step 1: Create Availability Model**
```python
# In models.py
class RoomAvailability(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='availability')
    start_date = models.DateField()
    end_date = models.DateField()
    is_available = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f"{self.room.title} - {self.start_date} to {self.end_date}"
```

### **Step 2: Add Calendar View**
```python
# In views.py
from datetime import datetime, timedelta
import calendar

def room_calendar(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    # Get current month
    today = datetime.now()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    # Create calendar
    cal = calendar.monthcalendar(year, month)
    
    # Get availability for this month
    start_of_month = datetime(year, month, 1).date()
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    availability = RoomAvailability.objects.filter(
        room=room,
        start_date__lte=end_of_month,
        end_date__gte=start_of_month
    )
    
    context = {
        'room': room,
        'calendar': cal,
        'availability': availability,
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
    }
    
    return render(request, 'room_calendar.html', context)
```

## 🧪 Debugging Exercises

### **Exercise 1: Find the Bug**
```python
def broken_view(request):
    rooms = Room.objects.all()
    for room in rooms:
        print(room.owner.name)  # What's wrong here?
    return render(request, 'rooms.html', {'rooms': rooms})
```

**Answer:** If `room.owner` is `None`, this will cause an `AttributeError`. Fix:
```python
def fixed_view(request):
    rooms = Room.objects.all()
    for room in rooms:
        if room.owner:
            print(room.owner.name)
        else:
            print("No owner")
    return render(request, 'rooms.html', {'rooms': rooms})
```

### **Exercise 2: Optimize This Query**
```python
def slow_view(request):
    profiles = Profile.objects.all()
    for profile in profiles:
        rooms = Room.objects.filter(owner=profile)
        # How can you make this faster?
```

**Answer:** Use `prefetch_related` to avoid N+1 queries:
```python
def fast_view(request):
    profiles = Profile.objects.prefetch_related('rooms')
    for profile in profiles:
        rooms = profile.rooms.all()  # This uses the prefetched data
```

## 🎯 Advanced Exercise: Build a Chat System

**Goal:** Create a real-time chat system between users.

### **Step 1: Create Message Models**
```python
# In models.py
class ChatRoom(models.Model):
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Chat between {', '.join([p.username for p in self.participants.all()])}"

class ChatMessage(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
```

### **Step 2: Create Chat Views**
```python
# In views.py
@login_required
def chat_room(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
    messages = chat_room.messages.all()
    
    if request.method == 'POST':
        content = request.POST.get('message')
        if content:
            ChatMessage.objects.create(
                chat_room=chat_room,
                sender=request.user,
                content=content
            )
        return redirect('chat_room', room_id=room_id)
    
    return render(request, 'chat_room.html', {
        'chat_room': chat_room,
        'messages': messages
    })
```

## 🎉 Challenge Yourself!

Try implementing these features on your own:

1. **Room Booking System** - Allow users to book rooms
2. **Payment Integration** - Add Stripe for deposits
3. **Room Verification** - Admin verification of room listings
4. **Advanced Search** - Elasticsearch integration
5. **Mobile App** - React Native frontend
6. **Real-time Notifications** - WebSocket integration
7. **Room Photos** - Multiple image uploads
8. **Roommate Matching Algorithm** - Compatibility scoring

## 📚 Learning Path

1. **Week 1:** Complete exercises 1-3
2. **Week 2:** Complete exercises 4-6
3. **Week 3:** Build the chat system
4. **Week 4:** Choose one advanced feature to implement

Remember: **Practice makes perfect!** Start with the simpler exercises and work your way up.
