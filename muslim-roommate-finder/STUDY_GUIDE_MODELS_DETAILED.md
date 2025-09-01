# Study Guide: Models - Line-by-Line Breakdown

## 🗄️ Complete Code Explanation

This guide breaks down **every single line** of your models code, explaining the syntax, parameters, and why we use each option.

---

## 📋 Profile Model - Complete Breakdown

### **Line 1: Import Statements**
```python
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
```

**What each import does:**
- `models`: Contains all Django field types (CharField, IntegerField, etc.)
- `reverse`: Generates URLs for your models
- `slugify`: Converts text to URL-friendly format ("John Doe" → "john-doe")
- `User`: Django's built-in user model for authentication

### **Line 3: Class Definition**
```python
class Profile(models.Model):
```

**Breakdown:**
- `class Profile`: Creates a Python class named "Profile"
- `(models.Model)`: Inherits from Django's Model class
- **Why inherit?** Models.Model gives you database functionality (save, delete, query methods)

### **Line 4: Choices Definition**
```python
GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
```

**Breakdown:**
- `GENDER_CHOICES`: A Python list containing tuples
- `('M', 'Male')`: Each tuple has (database_value, human_readable_value)
- **Why use choices?** Creates a dropdown in forms, validates data

### **Line 6: One-to-One Relationship**
```python
user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
```

**Line-by-line breakdown:**
- `user`: Field name (how you'll access it in code)
- `models.OneToOneField`: Field type (creates one-to-one relationship)
OneToOneField is a class within the models 
- `User`: The model this field relates to
- `on_delete=models.CASCADE`: What happens when User is deleted
- `null=True`: Can be NULL in database
- `blank=True`: Can be empty in forms

**What each parameter means:**
- **`on_delete=models.CASCADE`**: If User is deleted, delete this Profile too
- **`null=True`**: Database can store NULL for this field
- **`blank=True`**: Form validation allows empty field

**Other on_delete options:**
- `PROTECT`: Prevent deletion if Profile exists
- `SET_NULL`: Set to NULL if User is deleted
- `SET_DEFAULT`: Set to default value if User is deleted

### **Line 7: Basic Text Field**
```python
name = models.CharField(max_length=100)
```

**Breakdown:**
- `name`: Field name
- `models.CharField`: Field type for short text
- `max_length=100`: Maximum 100 characters allowed

**Why max_length?** Database needs to know how much space to allocate

### **Line 8: Integer Field**
```python
age = models.IntegerField()
```

**Breakdown:**
- `age`: Field name
- `models.IntegerField`: Field type for whole numbers
- No parameters needed (uses default settings)

### **Line 9: Choice Field**
```python
gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
```

**Breakdown:**
- `gender`: Field name
- `models.CharField`: Text field
- `max_length=1`: Only 1 character (M or F)
- `choices=GENDER_CHOICES`: Use predefined options

**Why choices?** Creates dropdown, validates input, prevents typos

### **Line 10: Required Text Field**
```python
city = models.CharField(max_length=100)
```

**Breakdown:**
- `city`: Field name
- `models.CharField`: Text field
- `max_length=100`: Maximum 100 characters
- **No null=True or blank=True** = Required field

### **Line 11: Optional Text Field**
```python
neighborhood = models.CharField(max_length=100, blank=True, help_text="Downtown, West Ashley, Mount Pleasant")
```

**Breakdown:**
- `neighborhood`: Field name
- `models.CharField`: Text field
- `max_length=100`: Maximum 100 characters
- `blank=True`: Can be empty in forms
- `help_text="..."`: Shows as help text in forms

**Why blank=True?** Makes field optional in forms

### **Line 12: Boolean Field**
```python
is_looking_for_room = models.BooleanField(default=True)
```

**Breakdown:**
- `is_looking_for_room`: Field name
- `models.BooleanField`: True/False field
- `default=True`: Default value is True

**Why default=True?** Most users are looking for rooms

### **Line 13: Long Text Field**
```python
bio = models.TextField(blank=True)
```

**Breakdown:**
- `bio`: Field name
- `models.TextField`: Long text field (unlimited length)
- `blank=True`: Can be empty

**CharField vs TextField:**
- CharField: Short text (name, title)
- TextField: Long text (bio, description)

### **Line 14: Email Field**
```python
contact_email = models.EmailField()
```

**Breakdown:**
- `contact_email`: Field name
- `models.EmailField`: Email field with validation
- **No parameters** = Required field

**Why EmailField?** Validates email format automatically

### **Lines 15-16: Auto Timestamps**
```python
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
```

**Breakdown:**
- `created_at`: When record was created
- `updated_at`: When record was last updated
- `auto_now_add=True`: Set automatically when created
- `auto_now=True`: Updated automatically when saved

**Difference:**
- `auto_now_add`: Set once when created
- `auto_now`: Updated every time you save

### **Line 17: Slug Field**
```python
slug = models.SlugField(max_length=140, unique=True, blank=True)
```

**Breakdown:**
- `slug`: URL-friendly version of name
- `models.SlugField`: Only letters, numbers, hyphens, underscores
- `max_length=140`: Maximum 140 characters
- `unique=True`: No two profiles can have same slug
- `blank=True`: Can be empty (will be auto-generated)

**Why slug?** Creates clean URLs: `/profile/john-doe-charleston/`

### **Lines 19-22: Lifestyle Preferences**
```python
# Lifestyle
halal_kitchen = models.BooleanField(default=True)
prayer_friendly = models.BooleanField(default=True)
guests_allowed = models.BooleanField(default=False)
```

**Breakdown:**
- All BooleanField: True/False fields
- `default=True/False`: Default values
- **Why these defaults?** Most Muslims prefer halal/prayer-friendly, but guests are less common

### **Lines 24-35: Meta Class**
```python
class Meta:
    ordering = ["-created_at"]
    indexes = [
        models.Index(fields=['city', 'neighborhood']),
        models.Index(fields=['age']),
        models.Index(fields=['gender']),
        # ... more indexes
    ]
```

**Breakdown:**
- `class Meta`: Special Django class for model configuration
- `ordering = ["-created_at"]`: Default order (newest first)
- `indexes = [...]`: Database indexes for faster queries

**What each does:**
- **Ordering**: `-created_at` = newest first, `created_at` = oldest first
- **Indexes**: Makes queries faster on these fields

### **Lines 37-39: URL Method**
```python
def get_absolute_url(self):
    return reverse("profile_detail", args=[self.id])
```

**Breakdown:**
- `def get_absolute_url(self):`: Method definition
- `self`: Refers to the current Profile instance
- `reverse("profile_detail", args=[self.id])`: Generate URL for this profile
- `self.id`: The profile's database ID

**Why this method?** Django uses it to generate links automatically

### **Lines 41-46: Location Display Method**
```python
def get_location_display(self):
    if self.neighborhood and self.city:
        return f"{self.neighborhood}, {self.city}"
    elif self.city:
        return self.city
    return "Unknown"
```

**Breakdown:**
- `def get_location_display(self):`: Method definition
- `if self.neighborhood and self.city:`: Check if both exist
- `return f"{self.neighborhood}, {self.city}"`: Return formatted string
- `elif self.city:`: If only city exists
- `return "Unknown"`: Default if nothing exists

**Python concepts used:**
- **f-strings**: `f"{variable}"` for string formatting
- **Conditional logic**: if/elif/else
- **Boolean evaluation**: `self.neighborhood and self.city`

### **Lines 48-49: Age Range Method**
```python
def get_age_range(self):
    return (self.age - 2, self.age + 2)
```

**Breakdown:**
- `def get_age_range(self):`: Method definition
- `return (self.age - 2, self.age + 2)`: Return tuple
- **Why tuple?** Returns two values (min_age, max_age)

### **Lines 51-53: Charleston Check Method**
```python
def is_charleston_area(self):
    charleston_areas = ['Downtown', 'West Ashley', 'Mount Pleasant', 'James Island', 'Charleston County']
    return self.city.lower() in charleston_areas
```

**Breakdown:**
- `charleston_areas = [...]`: List of Charleston areas
- `self.city.lower()`: Convert city to lowercase
- `in charleston_areas`: Check if city is in the list
- `return`: Return True/False

**Python concepts:**
- **List**: `['item1', 'item2']`
- **String method**: `.lower()` converts to lowercase
- **In operator**: `x in list` checks membership

### **Lines 55-56: Halal Kitchen Display**
```python
def get_halal_kitchen_display(self):
    return "Halal Kitchen" if self.halal_kitchen else "Not Halal Kitchen"
```

**Breakdown:**
- **Ternary operator**: `value_if_true if condition else value_if_false`
- `self.halal_kitchen`: Boolean field value
- Returns different string based on True/False

### **Lines 58-62: Custom Save Method**
```python
def save(self, *args, **kwargs):
    if not self.slug and self.name and self.city:
        self.slug = slugify(f"{self.name}-{self.city}")
    super().save(*args, **kwargs)
```

**Breakdown:**
- `def save(self, *args, **kwargs):`: Override Django's save method
- `*args, **kwargs`: Accept any arguments (required for overriding)
- `if not self.slug and self.name and self.city:`: Check if slug is empty but name/city exist
- `self.slug = slugify(f"{self.name}-{self.city}")`: Create slug from name and city
- `super().save(*args, **kwargs)`: Call parent (Django's) save method

**Why override save?** Add custom logic before saving to database

### **Lines 64-65: String Representation**
```python
def __str__(self):
    return self.name
```

**Breakdown:**
- `def __str__(self):`: Special Python method
- `return self.name`: What to show when Profile is converted to string
- **Why this?** Shows profile name in admin interface and debugging

---

## 🏠 Room Model - Key Differences

### **Foreign Key Relationships**
```python
owner = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.SET_NULL, related_name='rooms')
user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
```

**Breakdown:**
- `models.ForeignKey`: One-to-many relationship
- `Profile/User`: The model this relates to
- `null=True, blank=True`: Optional relationships
- `on_delete=models.SET_NULL`: Set to NULL if Profile is deleted
- `on_delete=models.CASCADE`: Delete Room if User is deleted
- `related_name='rooms'`: Access via `profile.rooms.all()`

**Why different on_delete?**
- SET_NULL: Keep room even if profile is deleted
- CASCADE: Delete room if user is deleted

### **Decimal Field**
```python
rent = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
```

**Breakdown:**
- `models.DecimalField`: Precise decimal numbers (for money)
- `max_digits=8`: Total digits allowed (123456.78 = 8 digits)
- `decimal_places=2`: Decimal places (123456.78 = 2 decimal places)
- **Why DecimalField?** Avoids floating-point precision issues with money

### **Date Field**
```python
available_from = models.DateField(null=True, blank=True)
```

**Breakdown:**
- `models.DateField`: Date only (no time)
- **vs DateTimeField**: Date + time

---

## 🔗 Relationship Syntax Summary

### **One-to-One**
```python
user = models.OneToOneField(User, on_delete=models.CASCADE)
```
**Creates:** Each Profile has exactly one User, each User has exactly one Profile

### **One-to-Many (ForeignKey)**
```python
owner = models.ForeignKey(Profile, related_name='rooms')
```
**Creates:** One Profile can have many Rooms, each Room belongs to one Profile

### **Many-to-Many**
```python
amenities = models.ManyToManyField(Amenity, through='RoomAmenity')
```
**Creates:** Many Rooms can have many Amenities, many Amenities can be in many Rooms

---

## 🎯 How Django Translates to Database

### **Profile Model → Database Table**
```sql
CREATE TABLE core_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,  -- OneToOneField
    name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(1) NOT NULL,
    city VARCHAR(100) NOT NULL,
    neighborhood VARCHAR(100),
    is_looking_for_room BOOLEAN DEFAULT 1,
    bio TEXT,
    contact_email VARCHAR(254) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    slug VARCHAR(140) UNIQUE,
    halal_kitchen BOOLEAN DEFAULT 1,
    prayer_friendly BOOLEAN DEFAULT 1,
    guests_allowed BOOLEAN DEFAULT 0
);
```

**What Django does:**
- Creates table with all your fields
- Adds `id` field automatically
- Creates indexes for performance
- Handles relationships with foreign keys

---

## 💡 Key Takeaways

### **Field Types:**
- `CharField`: Short text with max_length
- `TextField`: Long text (unlimited)
- `IntegerField`: Whole numbers
- `DecimalField`: Precise decimals (money)
- `BooleanField`: True/False
- `DateField`: Date only
- `DateTimeField`: Date + time
- `EmailField`: Email with validation
- `SlugField`: URL-friendly text

### **Relationship Types:**
- `OneToOneField`: One-to-one relationship
- `ForeignKey`: One-to-many relationship
- `ManyToManyField`: Many-to-many relationship

### **Common Parameters:**
- `max_length`: Maximum characters
- `null=True`: Can be NULL in database
- `blank=True`: Can be empty in forms
- `default`: Default value
- `choices`: Predefined options
- `on_delete`: What happens when related object is deleted
- `related_name`: Custom name for reverse access

### **Why We Use Each:**
- **null=True**: Optional database field
- **blank=True**: Optional form field
- **default**: Set initial value
- **choices**: Validate input, create dropdowns
- **on_delete**: Maintain data integrity
- **related_name**: Customize reverse queries

---

## 🧪 Practice Questions

1. **What's the difference between `null=True` and `blank=True`?**
   - `null=True`: Database can store NULL
   - `blank=True`: Form validation allows empty

2. **Why use `DecimalField` for money instead of `FloatField`?**
   - Avoids floating-point precision issues

3. **What does `related_name='rooms'` do?**
   - Allows `profile.rooms.all()` instead of `profile.room_set.all()`

4. **Why override the `save()` method?**
   - Add custom logic before saving (like auto-generating slug)

5. **What's the purpose of `__str__()` method?**
   - Defines how object appears as string (admin, debugging)

---

## 🚀 Next Steps

1. **Practice creating models** with different field types
2. **Experiment with relationships** in Django shell
3. **Understand migrations** and how they work
4. **Learn about model methods** and when to use them
5. **Explore the admin interface** to see your models in action
