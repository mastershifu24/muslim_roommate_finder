# Study Guide: Forms (forms.py) - Complete Code Analysis

## 🎯 Forms Deep Dive

Forms are the bridge between your users and your data. They handle user input, validate data, and create/update database objects. This guide covers all the forms in your Muslim Roommate Finder app.

---

## 📋 Imports and Setup

```python
from django import forms
from .models import Profile, Contact, Room, RoomImage
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
```

### **Key Imports Explained:**

1. **`forms`**: Django's form framework
2. **`UserCreationForm`**: Django's built-in user registration form
3. **`User`**: Django's built-in user model
4. **Model imports**: Your custom models

---

## 👤 UserRegistrationForm

**Purpose:** Extend Django's built-in user registration with additional fields.

```python
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm password'})
```

### **Key Concepts:**

1. **Inheritance:** Extends `UserCreationForm` to add email field
2. **Meta Class:** Specifies model and fields
3. **Widgets:** Customize form field appearance
4. **__init__ Method:** Customize field attributes after form creation

### **How It Works:**

1. **Inherits from UserCreationForm:** Gets username and password fields
2. **Adds Email Field:** Required email field
3. **Customizes Widgets:** Adds Bootstrap classes and placeholders
4. **Updates Password Fields:** Applies styling to password fields

---

## 👤 ProfileForm

**Purpose:** Create and edit user profiles.

```python
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'age', 'gender', 'city', 'neighborhood', 'is_looking_for_room', 'bio', 'contact_email', 
                 'halal_kitchen', 'prayer_friendly', 'guests_allowed']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your age'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Charleston, Mount Pleasant, West Ashley, James Island'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Downtown, West Ashley, Mount Pleasant'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about yourself, your lifestyle, and what you\'re looking for in a roommate...'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'}),
            'is_looking_for_room': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'halal_kitchen': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'prayer_friendly': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'guests_allowed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_looking_for_room': 'I am looking for a room',
            'halal_kitchen': 'Prefer halal kitchen',
            'prayer_friendly': 'Prefer prayer-friendly environment',
            'guests_allowed': 'Allow guests in shared spaces',
        }
```

### **Key Concepts:**

1. **ModelForm:** Automatically creates form fields from model
2. **Fields List:** Specify which model fields to include
3. **Widgets:** Customize how each field is rendered
4. **Labels:** Human-readable field names
5. **Bootstrap Classes:** Consistent styling

### **Field Types Used:**

- **TextInput:** Single-line text (name, city, neighborhood)
- **NumberInput:** Numeric input (age)
- **Select:** Dropdown (gender)
- **Textarea:** Multi-line text (bio)
- **EmailInput:** Email validation (contact_email)
- **CheckboxInput:** Boolean fields (preferences)

---

## 📞 ContactForm

**Purpose:** Handle contact messages between users.

```python
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['sender_name', 'sender_email', 'message']
        widgets = {
            'sender_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'sender_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Tell them about yourself and why you\'re interested in being roommates...'
            }),
        }
        labels = {
            'sender_name': 'Your Name',
            'sender_email': 'Your Email',
            'message': 'Your Message',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text to explain the contact process
        self.fields['sender_name'].help_text = 'This will be shared with the profile owner.'
        self.fields['sender_email'].help_text = 'This will be shared with the profile owner so they can reply to you.'
        self.fields['message'].help_text = 'Be respectful and include relevant information about yourself and your roommate preferences.'
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        
        # Check if message is too short
        if len(message.strip()) < 10:
            raise forms.ValidationError(
                'Please write a more detailed message (at least 10 characters).'
            )
        
        # Check if message is too long
        if len(message) > 1000:
            raise forms.ValidationError(
                'Message is too long. Please keep it under 1000 characters.'
            )
        
        return message
    
    def clean_sender_name(self):
        name = self.cleaned_data.get('sender_name')
        
        # Check if name contains only letters and spaces
        if not name.replace(' ', '').replace('-', '').replace("'", '').isalpha():
            raise forms.ValidationError(
                'Please enter a valid name (letters, spaces, hyphens, and apostrophes only).'
            )
        
        return name.strip()
```

### **Key Concepts:**

1. **Custom Validation:** `clean_*` methods for field-specific validation
2. **Help Text:** User guidance for each field
3. **Length Validation:** Ensure messages are appropriate length
4. **Character Validation:** Ensure names contain valid characters
5. **Data Cleaning:** Strip whitespace and normalize data

### **Validation Methods:**

- **`clean_message()`:** Validates message length and content
- **`clean_sender_name()`:** Validates name format and cleans data

---

## 🏠 RoomForm

**Purpose:** Create and edit room listings.

```python
class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'owner', 'title', 'description',
            'city', 'neighborhood',
            'rent', 'available_from',
            'halal_kitchen', 'prayer_friendly', 'guests_allowed',
            'contact_email',
        ]
        widgets = {
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Room in Downtown Charleston'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control'}),
            'rent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'available_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'halal_kitchen': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'prayer_friendly': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'guests_allowed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
```

### **Key Concepts:**

1. **Owner Field:** Dropdown to select profile owner
2. **Date Input:** HTML5 date picker for availability
3. **Decimal Input:** Step attribute for precise rent amounts
4. **Checkbox Fields:** Boolean preferences
5. **Textarea:** Detailed room description

### **Field Types:**

- **Select:** Owner dropdown
- **TextInput:** Title, city, neighborhood
- **Textarea:** Description
- **NumberInput:** Rent with decimal precision
- **DateInput:** Available from date
- **EmailInput:** Contact email
- **CheckboxInput:** Boolean preferences

---

## 🖼️ RoomImageForm

**Purpose:** Handle room image uploads.

```python
class RoomImageForm(forms.ModelForm):
    class Meta:
        model = RoomImage
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
```

### **Key Concepts:**

1. **FileInput:** File upload widget
2. **Image Handling:** Django handles image processing
3. **Caption Field:** Optional image description
4. **Primary Flag:** Mark main image for room

---

## 🎯 Form Validation Deep Dive

### **1. Built-in Validation:**

```python
# Email validation (automatic)
email = forms.EmailField()

# Required field validation (automatic)
name = forms.CharField(required=True)

# Length validation (automatic)
bio = forms.TextField(max_length=1000)
```

### **2. Custom Validation Methods:**

```python
def clean_fieldname(self):
    """Custom validation for a specific field."""
    field_value = self.cleaned_data.get('fieldname')
    
    # Your validation logic here
    if not valid_condition:
        raise forms.ValidationError('Error message')
    
    return field_value

def clean(self):
    """Validate multiple fields together."""
    cleaned_data = super().clean()
    field1 = cleaned_data.get('field1')
    field2 = cleaned_data.get('field2')
    
    # Cross-field validation
    if field1 and field2 and not compatible(field1, field2):
        raise forms.ValidationError('Fields are not compatible')
    
    return cleaned_data
```

### **3. Validation Examples:**

```python
# Length validation
def clean_message(self):
    message = self.cleaned_data.get('message')
    if len(message.strip()) < 10:
        raise forms.ValidationError('Message too short')
    return message

# Character validation
def clean_name(self):
    name = self.cleaned_data.get('name')
    if not name.replace(' ', '').isalpha():
        raise forms.ValidationError('Name must contain only letters')
    return name.strip()

# Date validation
def clean_available_from(self):
    date = self.cleaned_data.get('available_from')
    if date and date < timezone.now().date():
        raise forms.ValidationError('Date cannot be in the past')
    return date
```

---

## 🎨 Widget Customization

### **1. Bootstrap Classes:**

```python
widgets = {
    'field': forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter value...',
        'id': 'field-id'
    })
}
```

### **2. Common Widget Types:**

```python
# Text input
forms.TextInput(attrs={'class': 'form-control'})

# Text area
forms.Textarea(attrs={'class': 'form-control', 'rows': 4})

# Select dropdown
forms.Select(attrs={'class': 'form-select'})

# Checkbox
forms.CheckboxInput(attrs={'class': 'form-check-input'})

# File upload
forms.FileInput(attrs={'class': 'form-control'})

# Date picker
forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})

# Number input
forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
```

### **3. Custom Widgets:**

```python
class CustomDateWidget(forms.DateInput):
    def __init__(self, *args, **kwargs):
        kwargs['attrs'] = {
            'class': 'form-control',
            'type': 'date',
            'data-date-format': 'YYYY-MM-DD'
        }
        super().__init__(*args, **kwargs)

# Usage
class MyForm(forms.ModelForm):
    class Meta:
        model = MyModel
        fields = ['date_field']
        widgets = {
            'date_field': CustomDateWidget()
        }
```

---

## 🔧 Form Processing in Views

### **1. Basic Form Handling:**

```python
def my_view(request):
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            # Process valid form data
            form.save()
            return redirect('success')
    else:
        form = MyForm()
    
    return render(request, 'template.html', {'form': form})
```

### **2. Form with Files:**

```python
def upload_view(request):
    if request.method == 'POST':
        form = RoomImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = RoomImageForm()
    
    return render(request, 'template.html', {'form': form})
```

### **3. Form with Instance (Edit):**

```python
def edit_view(request, pk):
    instance = get_object_or_404(MyModel, pk=pk)
    
    if request.method == 'POST':
        form = MyForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = MyForm(instance=instance)
    
    return render(request, 'template.html', {'form': form})
```

---

## 🎯 Key Learning Points

### **1. Form Types:**
- **ModelForm:** Automatically creates fields from model
- **Form:** Manual field definition
- **UserCreationForm:** Built-in user registration

### **2. Validation Levels:**
- **Field-level:** Built-in validation (required, max_length, etc.)
- **Custom field:** `clean_fieldname()` methods
- **Form-level:** `clean()` method for cross-field validation

### **3. Widget Customization:**
- **CSS Classes:** Bootstrap styling
- **Attributes:** HTML attributes (placeholder, type, etc.)
- **Custom Widgets:** Reusable widget classes

### **4. Form Processing:**
- **GET:** Show empty form
- **POST:** Process form data
- **Validation:** Check data validity
- **Saving:** Create/update database objects

### **5. Security:**
- **CSRF Protection:** Automatic in Django
- **Data Cleaning:** Sanitize user input
- **Validation:** Prevent invalid data

---

## 🧪 Practice Questions

1. **How would you add a custom validator to ensure rent is positive?**
   ```python
   def clean_rent(self):
       rent = self.cleaned_data.get('rent')
       if rent and rent <= 0:
           raise forms.ValidationError('Rent must be positive')
       return rent
   ```

2. **How would you create a form that only shows certain fields?**
   ```python
   class PartialProfileForm(forms.ModelForm):
       class Meta:
           model = Profile
           fields = ['name', 'age', 'city']  # Only these fields
   ```

3. **How would you add a custom widget for phone numbers?**
   ```python
   class PhoneWidget(forms.TextInput):
       def __init__(self, *args, **kwargs):
           kwargs['attrs'] = {
               'class': 'form-control',
               'placeholder': '(555) 123-4567',
               'pattern': r'\(\d{3}\) \d{3}-\d{4}'
           }
           super().__init__(*args, **kwargs)
   ```

4. **How would you validate that two date fields are in order?**
   ```python
   def clean(self):
       cleaned_data = super().clean()
       start_date = cleaned_data.get('start_date')
       end_date = cleaned_data.get('end_date')
       
       if start_date and end_date and start_date >= end_date:
           raise forms.ValidationError('End date must be after start date')
       
       return cleaned_data
   ```

5. **How would you create a form that excludes certain fields?**
   ```python
   class ExcludeFieldsForm(forms.ModelForm):
       class Meta:
           model = Profile
           exclude = ['created_at', 'updated_at']  # Exclude these fields
   ```

---

## 🚀 Next Steps

1. **Study form validation** patterns and best practices
2. **Practice creating custom forms** for specific use cases
3. **Learn about form widgets** and customization
4. **Explore Django's form processing** in detail
5. **Understand form security** and CSRF protection
