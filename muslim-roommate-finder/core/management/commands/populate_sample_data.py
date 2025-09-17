from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import (
    Profile, RoomType, Amenity, Room, RoomImage, 
    RoommateProfile, Contact, Message
)
from decimal import Decimal
import random
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Populate the database with sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            RoomImage.objects.all().delete()
            Room.objects.all().delete()
            Profile.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            RoomType.objects.all().delete()
            Amenity.objects.all().delete()

        self.stdout.write('Creating sample data...')

        # Create room types
        room_types = [
            'Private Room',
            'Shared Room',
            'Studio',
            '1 Bedroom',
            '2 Bedroom',
        ]
        for rt in room_types:
            RoomType.objects.get_or_create(name=rt)

        # Create amenities
        amenities = [
            'WiFi',
            'Air Conditioning',
            'Heating',
            'Parking',
            'Laundry',
            'Kitchen',
            'Balcony',
            'Gym',
            'Pool',
            'Pet Friendly',
        ]
        for amenity in amenities:
            Amenity.objects.get_or_create(name=amenity)

        # Create sample users and profiles
        cities = ['Charleston', 'Mount Pleasant', 'West Ashley', 'James Island']
        neighborhoods = ['Downtown', 'Historic District', 'French Quarter', 'South of Broad']
        
        for i in range(10):
            username = f'user{i+1}'
            email = f'user{i+1}@example.com'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'User{i+1}',
                    'last_name': 'Test',
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()

            # Get or create profile (signal should have created it)
            try:
                profile = Profile.objects.get(user=user)
                # Update the profile with sample data
                profile.name = f'User {i+1}'
                profile.age = random.randint(20, 35)
                profile.gender = random.choice(['male', 'female'])
                profile.city = random.choice(cities)
                profile.neighborhood = random.choice(neighborhoods)
                profile.is_looking_for_room = random.choice([True, False])
                profile.halal_kitchen = random.choice([True, False])
                profile.prayer_friendly = random.choice([True, False])
                profile.guests_allowed = random.choice([True, False])
                profile.bio = f'This is a sample bio for User {i+1}. Looking for a great roommate!'
                profile.contact_email = email
                profile.save()
            except Profile.DoesNotExist:
                # Create profile if signal didn't work
                profile = Profile.objects.create(
                    user=user,
                    name=f'User {i+1}',
                    age=random.randint(20, 35),
                    gender=random.choice(['male', 'female']),
                    city=random.choice(cities),
                    neighborhood=random.choice(neighborhoods),
                    is_looking_for_room=random.choice([True, False]),
                    halal_kitchen=random.choice([True, False]),
                    prayer_friendly=random.choice([True, False]),
                    guests_allowed=random.choice([True, False]),
                    bio=f'This is a sample bio for User {i+1}. Looking for a great roommate!',
                    contact_email=email,
                )

            # Create roommate profile for some users
            if random.choice([True, False]):
                RoommateProfile.objects.get_or_create(
                    profile=profile,
                    defaults={
                        'budget': random.randint(500, 1500),
                        'occupation': random.choice(['Student', 'Engineer', 'Teacher', 'Nurse', 'Developer']),
                    }
                )

        # Create sample rooms
        room_types = list(RoomType.objects.all())
        amenities = list(Amenity.objects.all())
        profiles = list(Profile.objects.all())

        for i in range(15):
            room_type = random.choice(room_types)
            owner = random.choice(profiles)
            city = random.choice(cities)
            neighborhood = random.choice(neighborhoods)
            
            room, created = Room.objects.get_or_create(
                title=f'Sample Room {i+1} in {city}',
                defaults={
                    'user': owner,
                    'description': f'This is a beautiful {room_type.name.lower()} in {neighborhood}, {city}. Perfect for students and professionals.',
                    'room_type': room_type,
                    'city': city,
                    'neighborhood': neighborhood,
                    'price': Decimal(str(random.randint(600, 1200))),
                    'available_from': date.today() + timedelta(days=random.randint(1, 30)),
                    'halal_kitchen': random.choice([True, False]),
                    'prayer_friendly': random.choice([True, False]),
                    'guests_allowed': random.choice([True, False]),
                    'contact_email': owner.contact_email or owner.user.email,
                    'is_active': True,
                }
            )

            if created:
                # Add random amenities
                room.amenities.set(random.sample(amenities, random.randint(2, 5)))

        self.stdout.write(
            self.style.SUCCESS('Successfully populated sample data!')
        )
        self.stdout.write(f'Created {User.objects.count()} users')
        self.stdout.write(f'Created {Profile.objects.count()} profiles')
        self.stdout.write(f'Created {Room.objects.count()} rooms')
        self.stdout.write(f'Created {RoomType.objects.count()} room types')
        self.stdout.write(f'Created {Amenity.objects.count()} amenities')