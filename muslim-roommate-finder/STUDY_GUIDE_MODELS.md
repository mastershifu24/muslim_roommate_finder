# Study Guide: Models (models.py) - Complete Code Analysis

## 🗄️ Database Models Deep Dive

This guide covers all the models in your Muslim Roommate Finder app. Each model represents a table in your database.

---

## 📋 Profile Model

**Purpose:** Stores user profile information for roommate matching.

```python
class Profile(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    city = models.CharField(max_length=100)
    neighborhood = models.CharField(max_length=100, blank=True, help_text="Downtown, West Ashley, Mount Pleasant")
    is_looking_for_room = models.BooleanField(default=True)
    bio = models.TextField(blank=True)
    contact_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    # Lifestyle preferences
    halal_kitchen = models.BooleanField(default=True)
    prayer_friendly = models.BooleanField(default=True)
    guests_allowed = models.BooleanField(default=False)
```

### **Key Concepts:**

1. **OneToOneField with User:** Each profile belongs to exactly one user
2. **Choices for Gender:** Dropdown with predefined options
3. **Auto Fields:** `created_at` and `updated_at` are automatically managed
4. **Slug Field:** URL-friendly version of the name for SEO

### **Meta Configuration:**
```python
class Meta:
    ordering = ["-created_at"]  # Newest profiles first
    indexes = [
        models.Index(fields=['city', 'neighborhood']),
        models.Index(fields=['age']),
        models.Index(fields=['gender']),
        # ... more indexes for performance
    ]
```

### **Custom Methods:**
```python
def get_absolute_url(self):
    return reverse("profile_detail", args=[self.id])

def get_location_display(self):
    if self.neighborhood and self.city:
        return f"{self.neighborhood}, {self.city}"
    elif self.city:
        return self.city
    return "Unknown"

def is_charleston_area(self):
    charleston_areas = ['Downtown', 'West Ashley', 'Mount Pleasant', 'James Island', 'Charleston County']
    return self.city.lower() in charleston_areas

def save(self, *args, **kwargs):
    if not self.slug and self.name and self.city:
        self.slug = slugify(f"{self.name}-{self.city}")
    super().save(*args, **kwargs)
```

---

## 🏠 Room Model

**Purpose:** Stores room listings posted by users.

```python
class Room(models.Model):
    owner = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.SET_NULL, related_name='rooms')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    city = models.CharField(max_length=100)
    neighborhood = models.CharField(max_length=100, blank=True, help_text="Downtown, West Ashley, Mount Pleasant")
    rent = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    available_from = models.DateField(null=True, blank=True)
    
    # Lifestyle preferences
    halal_kitchen = models.BooleanField(default=True)
    prayer_friendly = models.BooleanField(default=True)
    guests_allowed = models.BooleanField(default=False)
    
    contact_email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    
    # Additional features
    room_type = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True, blank=True)
    private_bathroom = models.BooleanField(default=False)
    furnished = models.BooleanField(default=False)
    utilities_included = models.BooleanField(default=False)
```

### **Key Concepts:**

1. **ForeignKey to Profile:** Room can belong to a profile (optional)
2. **ForeignKey to User:** Room can belong to a user (optional)
3. **DecimalField for Rent:** Precise decimal storage for money
4. **DateField for Availability:** When the room becomes available

### **Custom Methods:**
```python
def save(self, *args, **kwargs):
    if not self.contact_email and self.owner:
        self.contact_email = self.owner.contact_email
    if not self.slug and self.title and self.city:
        self.slug = slugify(f"{self.title}-{self.city}")
    super().save(*args, **kwargs)

def get_absolute_url(self):
    return reverse("room_detail", args=[self.id])
```

---

## 📞 Contact Model

**Purpose:** Stores messages between users.

```python
class Contact(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='contacts_received')
    sender_name = models.CharField(max_length=100, verbose_name='Your name')
    sender_email = models.EmailField(verbose_name='Your email')
    message = models.TextField(verbose_name='Your message')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Contact date')
    is_read = models.BooleanField(default=False, verbose_name='Has been read')
```

### **Key Concepts:**

1. **ForeignKey to Profile:** Which profile is being contacted
2. **Sender Information:** Name and email of person sending message
3. **Read Status:** Track if the message has been read
4. **Verbose Names:** Human-readable field names for admin

### **Custom Methods:**
```python
def get_short_message(self):
    if len(self.message) <= 50:
        return self.message
    return self.message[:50] + "..."
```

---

## 🖼️ RoomImage Model

**Purpose:** Stores images for room listings.

```python
def room_image_path(instance, filename):
    return f'room_images/{instance.room_id}/{filename}'

class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=room_image_path)
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
```

### **Key Concepts:**

1. **Custom Upload Path:** Images organized by room ID
2. **Primary Image:** Flag to mark the main image
3. **Caption:** Optional description for the image

---

## 💬 Message Model

**Purpose:** Internal messaging system between users.

```python
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
```

### **Key Concepts:**

1. **Sender/Recipient:** Both are User objects
2. **Optional Room Reference:** Message can be about a specific room
3. **Read Status:** Track if message has been read

---

## ⭐ RoomReview Model

**Purpose:** User reviews and ratings for rooms.

```python
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
```

### **Key Concepts:**

1. **Rating Choices:** Predefined rating options
2. **Unique Together:** Prevents multiple reviews from same user
3. **Related Name:** Access reviews via `room.reviews.all()`

---

## 📅 RoomAvailability Model

**Purpose:** Track when rooms are available/unavailable.

```python
class RoomAvailability(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='availability')
    start_date = models.DateField()
    end_date = models.DateField()
    is_available = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
```

---

## 🏷️ Amenity & RoomAmenity Models

**Purpose:** Manage room amenities and features.

```python
class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)

class RoomAmenity(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='amenities')
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)
    included = models.BooleanField(default=True)

    class Meta:
        unique_together = ['room', 'amenity']
```

### **Key Concepts:**

1. **Many-to-Many Relationship:** Rooms can have many amenities, amenities can be in many rooms
2. **Junction Table:** RoomAmenity connects rooms and amenities
3. **Included Flag:** Whether the amenity is included in rent

---

## 🔍 RoomType Model

**Purpose:** Categorize different types of rooms.

```python
class RoomType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
```

---

## ✅ RoomVerification Model

**Purpose:** Admin verification of room listings.

```python
class RoomVerification(models.Model):
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    room = models.OneToOneField(Room, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
```

---

## ❤️ RoomFavorite Model

**Purpose:** Allow users to favorite rooms.

```python
class RoomFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'room']  # Prevent duplicate favorites
```

---

## 🎯 Key Learning Points

### **1. Field Types:**
- `CharField`: Short text
- `TextField`: Long text
- `IntegerField`: Whole numbers
- `DecimalField`: Precise decimal numbers
- `BooleanField`: True/False
- `DateField`: Date only
- `DateTimeField`: Date and time
- `EmailField`: Email validation
- `SlugField`: URL-friendly text
- `ImageField`: Image uploads

### **2. Relationships:**
- `OneToOneField`: One-to-one relationship
- `ForeignKey`: One-to-many relationship
- `ManyToManyField`: Many-to-many relationship

### **3. Field Options:**
- `max_length`: Maximum characters
- `blank=True`: Can be empty in forms
- `null=True`: Can be NULL in database
- `default`: Default value
- `choices`: Predefined options
- `help_text`: Help text for forms
- `verbose_name`: Human-readable name

### **4. Meta Options:**
- `ordering`: Default ordering
- `indexes`: Database indexes for performance
- `unique_together`: Unique combinations
- `verbose_name`: Human-readable model name

### **5. Custom Methods:**
- `__str__`: String representation
- `save`: Custom save logic
- `get_absolute_url`: URL for the object

---

## 🧪 Practice Questions

1. **What happens if you delete a User who has a Profile?**
   - Answer: The Profile is also deleted (CASCADE)

2. **How would you find all rooms in Charleston?**
   - Answer: `Room.objects.filter(city='Charleston')`

3. **How would you find all reviews for a specific room?**
   - Answer: `room.reviews.all()` (using related_name)

4. **What's the difference between `blank=True` and `null=True`?**
   - Answer: `blank=True` affects forms, `null=True` affects database

5. **How would you prevent duplicate favorites?**
   - Answer: Use `unique_together = ['user', 'room']` in Meta

---

## 🚀 Next Steps

1. **Study the relationships** between models
2. **Practice writing queries** using the Django shell
3. **Understand the Meta options** and their effects
4. **Learn about migrations** and how they work
5. **Explore the admin interface** to see how models are displayed
