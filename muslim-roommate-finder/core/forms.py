from django import forms
from .models import Profile, Contact, Room, RoomImage
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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

class ContactForm(forms.ModelForm):
    """
    Form for contacting profile owners.
    
    This form allows users to send messages to profile owners while
    maintaining privacy and tracking contact history.
    """
    
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'email': forms.EmailInput(attrs={
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
            'name': 'Your Name',
            'email': 'Your Email',
            'message': 'Your Message',
        }
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the form with custom help text and validation.
        
        This method is called when the form is created and allows us to
        customize the form's appearance and behavior.
        """
        super().__init__(*args, **kwargs)
        
        # Add help text to explain the contact process
        self.fields['name'].help_text = 'This will be shared with the profile owner.'
        self.fields['email'].help_text = 'This will be shared with the profile owner so they can reply to you.'
        self.fields['message'].help_text = 'Be respectful and include relevant information about yourself and your roommate preferences.'
    
    def clean_message(self):
        """
        Custom validation for the message field.
        
        This method is called automatically by Django when the form is validated.
        It allows us to add custom validation rules.
        """
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
        """
        Custom validation for the sender name field.
        """
        name = self.cleaned_data.get('name')
        
        # Check if name contains only letters and spaces
        if not name.replace(' ', '').replace('-', '').replace("'", '').isalpha():
            raise forms.ValidationError(
                'Please enter a valid name (letters, spaces, hyphens, and apostrophes only).'
            )
        
        return name.strip() 


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'owner', 'title', 'description',
            'city', 'neighborhood',
            'price', 
            'halal_kitchen', 'prayer_friendly', 'guests_allowed',
            'contact_email',
        ]
        widgets = {
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Room in Downtown Charleston'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'halal_kitchen': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'prayer_friendly': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'guests_allowed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class RoomImageForm(forms.ModelForm):
    class Meta:
        model = RoomImage
        fields = ['image', 'is_primary']  # remove 'caption' if it doesn't exist
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
