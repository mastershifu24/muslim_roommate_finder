# Study Guide: URLs & Templates - Complete Code Analysis

## 🎯 URLs and Templates Deep Dive

URLs route requests to views, and templates render the HTML that users see. This guide covers the URL patterns and template structure in your Muslim Roommate Finder app.

---

## 🔗 URL Configuration (urls.py)

### **Main URL Configuration:**

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]
```

### **Core App URLs:**

```python
from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Profile routes
    path('profiles/<int:profile_id>/', views.profile_detail, name='profile_detail'),
    path('profiles/<int:profile_id>/contact/', views.contact_profile, name='contact_profile'),
    path('profiles/<int:profile_id>/delete/', views.delete_profile, name='delete_profile'),
    path('profiles/<int:profile_id>/edit/', views.edit_profile, name='edit_profile'),
    path('profiles/create/', views.create_profile, name='create_profile'),
    
    # Room routes
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('rooms/create/', views.create_room, name='create_room'),
    
    # Authentication routes
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # User dashboard routes
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-listings/', views.my_listings, name='my_listings'),
    
    # Search and messaging
    path('search/', views.advanced_search, name='advanced_search'),
    path('send-message/<int:room_id>/', views.send_message, name='send_message'),
    path('inbox/', views.inbox, name='inbox'),
]
```

### **Key Concepts:**

1. **Path Patterns:** Define URL structure and parameters
2. **View Functions:** Connect URLs to view logic
3. **Name Parameters:** Create named URLs for templates
4. **Integer Parameters:** Capture numeric IDs from URLs

---

## 🎨 Template System

### **Template Structure:**

```
templates/
├── home.html              # Main homepage
├── profile_detail.html    # Individual profile view
├── contact_profile.html   # Contact form
├── delete_profile.html    # Delete confirmation
├── edit_profile.html      # Edit profile form
├── create_profile.html    # Create profile form
├── room_detail.html       # Individual room view
├── create_room.html       # Create room form
├── register.html          # User registration
├── login.html             # User login
├── dashboard.html         # User dashboard
├── my_listings.html       # User's listings
└── base.html             # Base template (if using inheritance)
```

---

## 🏠 Home Template (home.html)

**Purpose:** Main page showing all profiles and rooms with search functionality.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Muslim Roommate Finder</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <style>
        .profile-card {
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }
        .profile-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body class="container py-4">
    <!-- Navigation Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Muslim Roommate Finder</h1>
        <div class="d-flex gap-2">
            {% if user.is_authenticated %}
                <a href="{% url 'dashboard' %}" class="btn btn-outline-primary">Dashboard</a>
                <a href="{% url 'my_listings' %}" class="btn btn-outline-secondary">My Listings</a>
                <a href="{% url 'logout' %}" class="btn btn-outline-danger">Logout</a>
            {% else %}
                <a href="{% url 'login' %}" class="btn btn-outline-primary">Login</a>
                <a href="{% url 'register' %}" class="btn btn-primary">Register</a>
            {% endif %}
            <a href="{% url 'create_room' %}" class="btn btn-success">+ List a Room</a>
            <a href="{% url 'create_profile' %}" class="btn btn-primary">+ Create Profile</a>
        </div>
    </div>

    <!-- Flash Messages -->
    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        {% endfor %}
    {% endif %}

    <!-- Quick Filter Buttons -->
    <div class="mb-3">
        <div class="btn-group" role="group">
            <a href="{% url 'home' %}" class="btn btn-outline-primary {% if not preference_filter %}active{% endif %}">
                Show All
            </a>
            <a href="?preference=offering_room" class="btn btn-outline-success {% if preference_filter == 'offering_room' %}active{% endif %}">
                🏠 Available Rooms
            </a>
            <a href="?preference=looking_for_room" class="btn btn-outline-info {% if preference_filter == 'looking_for_room' %}active{% endif %}">
                👥 Looking for Rooms
            </a>
        </div>
    </div>

    <!-- Search and Filter Form -->
    <div class="card mb-4">
        <div class="card-body">
            <form method="get" class="row g-3">
                <!-- Search Box -->
                <div class="col-md-4">
                    <label for="search" class="form-label">Search</label>
                    <input type="text" class="form-control" id="search" name="search" 
                           value="{{ search_query }}" placeholder="Search by name, city, or bio...">
                </div>
                
                <!-- City Filter -->
                <div class="col-md-2">
                    <label for="city" class="form-label">City</label>
                    <select class="form-select" id="city" name="city">
                        <option value="">All Cities</option>
                        {% for city in cities %}
                            <option value="{{ city }}" {% if city_filter == city %}selected{% endif %}>
                                {{ city }}
                            </option>
                        {% endfor %}
                    </select>
                </div>
                
                <!-- Gender Filter -->
                <div class="col-md-2">
                    <label for="gender" class="form-label">Gender</label>
                    <select class="form-select" id="gender" name="gender">
                        <option value="">All Genders</option>
                        <option value="M" {% if gender_filter == 'M' %}selected{% endif %}>Male</option>
                        <option value="F" {% if gender_filter == 'F' %}selected{% endif %}>Female</option>
                    </select>
                </div>
                
                <!-- Preference Filter -->
                <div class="col-md-2">
                    <label for="preference" class="form-label">Preference</label>
                    <select class="form-select" id="preference" name="preference">
                        <option value="">All Preferences</option>
                        <option value="halal_kitchen" {% if preference_filter == 'halal_kitchen' %}selected{% endif %}>Halal Kitchen</option>
                        <option value="prayer_friendly" {% if preference_filter == 'prayer_friendly' %}selected{% endif %}>Prayer Friendly</option>
                        <option value="guests_allowed" {% if preference_filter == 'guests_allowed' %}selected{% endif %}>Guests Allowed</option>
                        <option value="looking_for_room" {% if preference_filter == 'looking_for_room' %}selected{% endif %}>Looking for Room</option>
                        <option value="offering_room" {% if preference_filter == 'offering_room' %}selected{% endif %}>Offering Room</option>
                    </select>
                </div>
                
                <!-- Search Button -->
                <div class="col-md-2 d-flex align-items-end">
                    <button type="submit" class="btn btn-primary w-100">Search</button>
                </div>
            </form>
            
            <!-- Clear Filters Link -->
            {% if search_query or city_filter or gender_filter or preference_filter %}
                <div class="mt-3">
                    <a href="{% url 'home' %}" class="btn btn-outline-secondary btn-sm">Clear All Filters</a>
                </div>
            {% endif %}
        </div>
    </div>

    <!-- Available Rooms Section -->
    {% if available_rooms %}
        <div class="mb-4">
            <h3 class="text-success mb-3">
                🏠 Available Rooms ({{ rooms_count }})
            </h3>
            <div class="row">
                {% for room in available_rooms %}
                    <div class="col-md-4 mb-4">
                        <a href="{% url 'room_detail' room.id %}" class="text-decoration-none">
                            <div class="card h-100 profile-card border-success">
                                <div class="card-header bg-success text-white">
                                    <h5 class="card-title mb-0">{{ room.title }}</h5>
                                </div>
                                <div class="card-body">
                                    <h6 class="card-subtitle mb-2 text-muted">{{ room.city }}{% if room.neighborhood %} • {{ room.neighborhood }}{% endif %}</h6>
                                    {% if room.rent %}
                                        <p class="text-dark mb-2"><strong>Rent:</strong> ${{ room.rent }}</p>
                                    {% endif %}
                                    
                                    {% if room.description %}
                                        <p class="card-text text-dark">{{ room.description }}</p>
                                    {% endif %}
                                    
                                    <div class="mb-3">
                                        <small class="text-muted">
                                            <strong>Contact:</strong> {{ room.contact_email }}
                                        </small>
                                    </div>
                                    
                                    <div class="d-flex flex-wrap gap-1">
                                        {% if room.halal_kitchen %}
                                            <span class="badge bg-success">Halal Kitchen</span>
                                        {% endif %}
                                        {% if room.prayer_friendly %}
                                            <span class="badge bg-info">Prayer Friendly</span>
                                        {% endif %}
                                        {% if room.guests_allowed %}
                                            <span class="badge bg-warning">Guests Allowed</span>
                                        {% endif %}
                                        <span class="badge bg-success">Room Available</span>
                                    </div>
                                </div>
                            </div>
                        </a>
                    </div>
                {% endfor %}
            </div>
        </div>
    {% endif %}

    <!-- People Looking for Rooms Section -->
    {% if profiles %}
        <div class="mb-4">
            <h3 class="text-primary mb-3">
                👥 People Looking for Rooms ({{ profile_count }})
            </h3>
            <div class="row">
                {% for profile in profiles %}
                    <div class="col-md-4 mb-4">
                        <a href="{{ profile.get_absolute_url }}" class="text-decoration-none">
                            <div class="card h-100 profile-card border-primary">
                                <div class="card-header bg-primary text-white">
                                    <h5 class="card-title mb-0">{{ profile.name }}, {{ profile.age }}</h5>
                                </div>
                                <div class="card-body">
                                    <h6 class="card-subtitle mb-2 text-muted">{{ profile.city }} | {{ profile.get_gender_display }}</h6>
                                    
                                    {% if profile.bio %}
                                        <p class="card-text text-dark">{{ profile.bio }}</p>
                                    {% endif %}
                                    
                                    <div class="mb-3">
                                        <small class="text-muted">
                                            <strong>Contact:</strong> {{ profile.contact_email }}
                                        </small>
                                    </div>
                                    
                                    <div class="d-flex flex-wrap gap-1">
                                        {% if profile.halal_kitchen %}
                                            <span class="badge bg-success">Halal Kitchen</span>
                                        {% endif %}
                                        {% if profile.prayer_friendly %}
                                            <span class="badge bg-info">Prayer Friendly</span>
                                        {% endif %}
                                        {% if profile.guests_allowed %}
                                            <span class="badge bg-warning">Guests Allowed</span>
                                        {% endif %}
                                        <span class="badge bg-primary">Looking for Room</span>
                                    </div>
                                </div>
                            </div>
                        </a>
                    </div>
                {% endfor %}
            </div>
        </div>
    {% endif %}

    <!-- No Results Message -->
    {% if not profiles and not available_rooms %}
        <div class="text-center py-5">
            <h3 class="text-muted">No profiles or rooms found</h3>
            <p class="text-muted">
                {% if search_query or city_filter or gender_filter or preference_filter %}
                    Try adjusting your search criteria.
                {% else %}
                    Be the first to create a profile!
                {% endif %}
            </p>
            <a href="{% url 'create_profile' %}" class="btn btn-primary btn-lg">Create Your Profile</a>
        </div>
    {% endif %}

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

### **Key Template Concepts:**

1. **Template Tags:** `{% %}` for logic, `{{ }}` for variables
2. **Conditional Rendering:** `{% if %}` statements
3. **Loops:** `{% for %}` to iterate over lists
4. **URL Generation:** `{% url 'name' %}` for named URLs
5. **Bootstrap Classes:** Responsive design framework

---

## 👤 Profile Detail Template (profile_detail.html)

**Purpose:** Show detailed information about a specific profile.

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ profile.name }} - Muslim Roommate Finder</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>{{ profile.name }}, {{ profile.age }}</h1>
        <div class="d-flex gap-2">
            <a href="{% url 'home' %}" class="btn btn-outline-secondary">← Back to Home</a>
            <a href="{% url 'contact_profile' profile.id %}" class="btn btn-primary">Contact {{ profile.name }}</a>
        </div>
    </div>

    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">About {{ profile.name }}</h5>
                    <p class="card-text">{{ profile.bio|default:"No bio provided." }}</p>
                    
                    <h6>Location</h6>
                    <p>{{ profile.city }}{% if profile.neighborhood %}, {{ profile.neighborhood }}{% endif %}</p>
                    
                    <h6>Contact Information</h6>
                    <p>Email: {{ profile.contact_email }}</p>
                    
                    <h6>Preferences</h6>
                    <div class="d-flex flex-wrap gap-2">
                        {% if profile.halal_kitchen %}
                            <span class="badge bg-success">Halal Kitchen</span>
                        {% endif %}
                        {% if profile.prayer_friendly %}
                            <span class="badge bg-info">Prayer Friendly</span>
                        {% endif %}
                        {% if profile.guests_allowed %}
                            <span class="badge bg-warning">Guests Allowed</span>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">Similar Profiles</h5>
                </div>
                <div class="card-body">
                    {% if similar_profiles %}
                        {% for similar in similar_profiles %}
                            <div class="border-bottom pb-2 mb-2">
                                <h6><a href="{% url 'profile_detail' similar.id %}">{{ similar.name }}, {{ similar.age }}</a></h6>
                                <small class="text-muted">{{ similar.city }} • {{ similar.get_gender_display }}</small>
                            </div>
                        {% endfor %}
                    {% else %}
                        <p class="text-muted">No similar profiles found.</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
```

---

## 📝 Registration Template (register.html)

**Purpose:** User registration form.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Register - Muslim Roommate Finder</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body class="container py-4">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1>Create Account</h1>
                <a href="{% url 'home' %}" class="btn btn-outline-secondary">← Back to Home</a>
            </div>

            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}

            <div class="card">
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}
                        
                        <div class="mb-3">
                            <label for="{{ form.username.id_for_label }}" class="form-label">Username</label>
                            {{ form.username }}
                            {% if form.username.errors %}
                                <div class="text-danger">{{ form.username.errors }}</div>
                            {% endif %}
                        </div>

                        <div class="mb-3">
                            <label for="{{ form.email.id_for_label }}" class="form-label">Email</label>
                            {{ form.email }}
                            {% if form.email.errors %}
                                <div class="text-danger">{{ form.email.errors }}</div>
                            {% endif %}
                        </div>

                        <div class="mb-3">
                            <label for="{{ form.password1.id_for_label }}" class="form-label">Password</label>
                            {{ form.password1 }}
                            {% if form.password1.errors %}
                                <div class="text-danger">{{ form.password1.errors }}</div>
                            {% endif %}
                        </div>

                        <div class="mb-3">
                            <label for="{{ form.password2.id_for_label }}" class="form-label">Confirm Password</label>
                            {{ form.password2 }}
                            {% if form.password2.errors %}
                                <div class="text-danger">{{ form.password2.errors }}</div>
                            {% endif %}
                        </div>

                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary btn-lg">Create Account</button>
                        </div>
                    </form>
                    
                    <div class="text-center mt-3">
                        <p>Already have an account? <a href="{% url 'login' %}">Login here</a></p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

---

## 🔐 Login Template (login.html)

**Purpose:** User authentication form.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Login - Muslim Roommate Finder</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body class="container py-4">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1>Login</h1>
                <a href="{% url 'home' %}" class="btn btn-outline-secondary">← Back to Home</a>
            </div>

            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}

            <div class="card">
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}
                        
                        <div class="mb-3">
                            <label for="{{ form.username.id_for_label }}" class="form-label">Username</label>
                            {{ form.username }}
                            {% if form.username.errors %}
                                <div class="text-danger">{{ form.username.errors }}</div>
                            {% endif %}
                        </div>

                        <div class="mb-3">
                            <label for="{{ form.password.id_for_label }}" class="form-label">Password</label>
                            {{ form.password }}
                            {% if form.password.errors %}
                                <div class="text-danger">{{ form.password.errors }}</div>
                            {% endif %}
                        </div>

                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary btn-lg">Login</button>
                        </div>
                    </form>
                    
                    <div class="text-center mt-3">
                        <p>Don't have an account? <a href="{% url 'register' %}">Register here</a></p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

---

## 📊 Dashboard Template (dashboard.html)

**Purpose:** User's personal dashboard.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - Muslim Roommate Finder</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Welcome, {{ user.username }}!</h1>
        <div class="d-flex gap-2">
            <a href="{% url 'my_listings' %}" class="btn btn-outline-primary">My Listings</a>
            <a href="{% url 'logout' %}" class="btn btn-outline-danger">Logout</a>
        </div>
    </div>

    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        {% endfor %}
    {% endif %}

    <div class="row">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">My Room Listings</h5>
                </div>
                <div class="card-body">
                    {% if rooms %}
                        {% for room in rooms %}
                            <div class="border-bottom pb-2 mb-2">
                                <h6><a href="{% url 'room_detail' room.id %}">{{ room.title }}</a></h6>
                                <small class="text-muted">{{ room.city }} • ${{ room.rent }}</small>
                            </div>
                        {% endfor %}
                        <a href="{% url 'my_listings' %}" class="btn btn-sm btn-outline-primary">View All</a>
                    {% else %}
                        <p class="text-muted">No room listings yet.</p>
                        <a href="{% url 'create_room' %}" class="btn btn-success">List a Room</a>
                    {% endif %}
                </div>
            </div>
        </div>

        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">My Profiles</h5>
                </div>
                <div class="card-body">
                    {% if profiles %}
                        {% for profile in profiles %}
                            <div class="border-bottom pb-2 mb-2">
                                <h6><a href="{% url 'profile_detail' profile.id %}">{{ profile.name }}</a></h6>
                                <small class="text-muted">{{ profile.city }} • {{ profile.get_gender_display }}</small>
                            </div>
                        {% endfor %}
                        <a href="{% url 'my_listings' %}" class="btn btn-sm btn-outline-primary">View All</a>
                    {% else %}
                        <p class="text-muted">No profiles yet.</p>
                        <a href="{% url 'create_profile' %}" class="btn btn-primary">Create Profile</a>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

---

## 🎯 Template Tags and Filters

### **1. Template Tags:**

```html
<!-- Variables -->
{{ variable_name }}

<!-- Template tags -->
{% tag_name %}

<!-- Comments -->
{# This is a comment #}

<!-- If statements -->
{% if condition %}
    content
{% elif other_condition %}
    content
{% else %}
    content
{% endif %}

<!-- For loops -->
{% for item in items %}
    {{ item }}
{% empty %}
    No items found
{% endfor %}

<!-- URL generation -->
{% url 'view_name' parameter %}

<!-- CSRF token -->
{% csrf_token %}

<!-- Include other templates -->
{% include 'template_name.html' %}

<!-- Extend base template -->
{% extends 'base.html' %}
```

### **2. Template Filters:**

```html
<!-- Default value -->
{{ value|default:"No value" }}

<!-- Length -->
{{ list|length }}

<!-- Date formatting -->
{{ date|date:"F j, Y" }}

<!-- Text truncation -->
{{ text|truncatewords:30 }}

<!-- Safe HTML -->
{{ html_content|safe }}

<!-- Escape HTML -->
{{ user_input|escape }}

<!-- Upper/lower case -->
{{ text|upper }}
{{ text|lower }}

<!-- Join list -->
{{ list|join:", " }}
```

---

## 🎨 Bootstrap Integration

### **1. Grid System:**

```html
<div class="container">
    <div class="row">
        <div class="col-md-6">Left column</div>
        <div class="col-md-6">Right column</div>
    </div>
</div>
```

### **2. Components:**

```html
<!-- Cards -->
<div class="card">
    <div class="card-header">Header</div>
    <div class="card-body">Content</div>
</div>

<!-- Buttons -->
<button class="btn btn-primary">Primary</button>
<button class="btn btn-outline-secondary">Outline</button>

<!-- Alerts -->
<div class="alert alert-success">Success message</div>
<div class="alert alert-danger">Error message</div>

<!-- Forms -->
<form class="row g-3">
    <div class="col-md-6">
        <label class="form-label">Label</label>
        <input type="text" class="form-control">
    </div>
</form>

<!-- Badges -->
<span class="badge bg-success">Success</span>
<span class="badge bg-warning">Warning</span>
```

---

## 🔧 URL Patterns Deep Dive

### **1. Path Parameters:**

```python
# Integer parameter
path('profiles/<int:profile_id>/', views.profile_detail, name='profile_detail')

# String parameter
path('users/<str:username>/', views.user_profile, name='user_profile')

# Slug parameter
path('posts/<slug:post_slug>/', views.post_detail, name='post_detail')

# UUID parameter
path('files/<uuid:file_id>/', views.file_detail, name='file_detail')
```

### **2. Optional Parameters:**

```python
# Optional parameter
path('search/', views.search, name='search')
path('search/<str:query>/', views.search, name='search_with_query')
```

### **3. Multiple Parameters:**

```python
# Multiple parameters
path('rooms/<int:room_id>/reviews/<int:review_id>/', views.review_detail, name='review_detail')
```

---

## 🎯 Key Learning Points

### **1. URL Design:**
- **RESTful URLs:** Use nouns, not verbs
- **Hierarchical Structure:** Organize by resource type
- **Named URLs:** Use descriptive names for reverse lookup
- **Parameter Types:** Choose appropriate parameter types

### **2. Template Organization:**
- **Separation of Concerns:** Keep logic in views, presentation in templates
- **Reusability:** Use template inheritance and includes
- **Security:** Always escape user input
- **Performance:** Minimize database queries in templates

### **3. Bootstrap Integration:**
- **Responsive Design:** Use grid system for mobile-friendly layouts
- **Component Library:** Leverage Bootstrap components
- **Customization:** Override Bootstrap classes when needed
- **Consistency:** Maintain consistent styling across pages

### **4. Template Best Practices:**
- **Readability:** Use clear, descriptive variable names
- **Maintainability:** Keep templates simple and focused
- **Performance:** Avoid complex logic in templates
- **Accessibility:** Use semantic HTML and ARIA attributes

---

## 🧪 Practice Questions

1. **How would you create a URL pattern for user profiles with usernames?**
   ```python
   path('users/<str:username>/', views.user_profile, name='user_profile')
   ```

2. **How would you add pagination to a template?**
   ```html
   {% if is_paginated %}
       <nav>
           {% if page_obj.has_previous %}
               <a href="?page={{ page_obj.previous_page_number }}">Previous</a>
           {% endif %}
           <span>Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span>
           {% if page_obj.has_next %}
               <a href="?page={{ page_obj.next_page_number }}">Next</a>
           {% endif %}
       </nav>
   {% endif %}
   ```

3. **How would you create a base template with inheritance?**
   ```html
   <!-- base.html -->
   <!DOCTYPE html>
   <html>
   <head>
       <title>{% block title %}{% endblock %}</title>
       <link rel="stylesheet" href="{% static 'css/style.css' %}">
   </head>
   <body>
       {% block content %}{% endblock %}
   </body>
   </html>

   <!-- child.html -->
   {% extends 'base.html' %}
   {% block title %}Page Title{% endblock %}
   {% block content %}Page content{% endblock %}
   ```

4. **How would you add conditional CSS classes?**
   ```html
   <div class="card {% if user.is_authenticated %}border-primary{% endif %}">
   ```

5. **How would you create a search form that preserves current filters?**
   ```html
   <form method="get">
       <input type="text" name="search" value="{{ request.GET.search }}">
       <input type="hidden" name="city" value="{{ request.GET.city }}">
       <button type="submit">Search</button>
   </form>
   ```

---

## 🚀 Next Steps

1. **Study URL patterns** and RESTful design principles
2. **Practice template inheritance** and includes
3. **Learn about template caching** and performance optimization
4. **Explore advanced template features** like custom template tags
5. **Understand template security** and XSS prevention
