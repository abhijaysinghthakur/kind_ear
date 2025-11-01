"""
Seed database with test users
Run with: python scripts/seed_db.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.models.user import User
from app.extensions import init_db
from app import create_app
from flask import Flask

def seed_database():
    """Create test users for development."""
    app = create_app('development')

    with app.app_context():
        print("Seeding database with test users...")

        # Check if users already exist
        if User.find_by_email('admin@example.com'):
            print("Users already exist. Skipping seed.")
            return

        # 1. Admin user
        admin = User.create({
            'email': 'admin@example.com',
            'password': 'Admin123!',
            'pseudonym': 'AdminUser',
            'roles': ['sharer', 'listener'],
            'is_admin': True,
            'interests': ['platform management'],
            'languages': ['English']
        })
        print(f"Created admin: {admin['email']}")

        # 2. Test Sharer
        sharer = User.create({
            'email': 'sharer@example.com',
            'password': 'Sharer123!',
            'pseudonym': 'TestSharer',
            'roles': ['sharer'],
            'interests': ['anxiety', 'stress'],
            'languages': ['English']
        })
        print(f"Created sharer: {sharer['email']}")

        # 3. Test Listener 1
        listener1 = User.create({
            'email': 'listener1@example.com',
            'password': 'Listener123!',
            'pseudonym': 'CaringListener',
            'roles': ['listener'],
            'bio': 'Here to help with anxiety and stress',
            'interests': ['mental health', 'empathy'],
            'languages': ['English'],
            'listener_topics': ['anxiety', 'stress', 'depression'],
            'listener_rating': 4.8,
            'listener_total_chats': 45
        })
        User.update_availability(listener1['_id'], 'available')
        print(f"Created listener1: {listener1['email']}")

        # 4. Test Listener 2
        listener2 = User.create({
            'email': 'listener2@example.com',
            'password': 'Listener123!',
            'pseudonym': 'EmpathyFirst',
            'roles': ['listener'],
            'bio': 'Experienced with mental health topics',
            'interests': ['relationships', 'empathy'],
            'languages': ['English', 'Spanish'],
            'listener_topics': ['anxiety', 'depression', 'relationships'],
            'listener_rating': 4.5,
            'listener_total_chats': 32
        })
        User.update_availability(listener2['_id'], 'available')
        print(f"Created listener2: {listener2['email']}")

        # 5. Test Dual Role User
        both = User.create({
            'email': 'both@example.com',
            'password': 'Both123!',
            'pseudonym': 'FlexibleHelper',
            'roles': ['sharer', 'listener'],
            'bio': 'Sometimes I need to talk, sometimes I listen',
            'interests': ['loneliness', 'support'],
            'languages': ['English'],
            'listener_topics': ['loneliness', 'isolation'],
            'listener_rating': 4.2,
            'listener_total_chats': 15
        })
        print(f"Created dual-role user: {both['email']}")

        print("\n=== Database seeding complete! ===")
        print("\nTest accounts created:")
        print("- Admin: admin@example.com / Admin123!")
        print("- Sharer: sharer@example.com / Sharer123!")
        print("- Listener1: listener1@example.com / Listener123!")
        print("- Listener2: listener2@example.com / Listener123!")
        print("- Both roles: both@example.com / Both123!")

if __name__ == '__main__':
    seed_database()
