"""
Simple script to seed MongoDB with sample events
Run this after MongoDB is installed and running
"""
from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.events_db
events_collection = db.events

# Sample events to insert
sample_events = [
    {
        "id": "1",
        "title": "Tech Conference 2025",
        "description": "Annual technology conference featuring the latest innovations",
        "date": "2025-11-15T09:00:00",
        "location": "San Francisco, CA",
        "category": "Technology",
        "organizer": "Tech Corp",
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": "2",
        "title": "Music Festival",
        "description": "Three-day outdoor music festival with top artists",
        "date": "2025-08-20T14:00:00",
        "location": "Austin, TX",
        "category": "Music",
        "organizer": "Live Nation",
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": "3",
        "title": "Food & Wine Expo",
        "description": "Culinary experience with renowned chefs",
        "date": "2025-10-05T11:00:00",
        "location": "New York, NY",
        "category": "Food",
        "organizer": "Culinary Institute",
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": "4",
        "title": "Marathon 2025",
        "description": "Annual city marathon for runners of all levels",
        "date": "2025-09-10T07:00:00",
        "location": "Boston, MA",
        "category": "Sports",
        "organizer": "Boston Athletic Association",
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": "5",
        "title": "AI Workshop Bengaluru",
        "description": "Hands-on workshop on machine learning and AI",
        "date": "2025-11-01T10:00:00",
        "location": "Bengaluru, Karnataka",
        "category": "Technology",
        "organizer": "Indian Institute of Science",
        "created_at": datetime.utcnow().isoformat()
    }
]

def seed_database():
    """Insert sample events into MongoDB"""
    try:
        # Clear existing events (optional)
        print("Clearing existing events...")
        events_collection.delete_many({})
        
        # Insert sample events
        print("Inserting sample events...")
        result = events_collection.insert_many(sample_events)
        
        print(f"\n Successfully inserted {len(result.inserted_ids)} events!")
        print("\nInserted Event IDs:")
        for idx, event_id in enumerate(result.inserted_ids, 1):
            print(f"  {idx}. {event_id}")
        
        # Display all events
        print("\n All events in database:")
        for event in events_collection.find():
            print(f"\n  ID: {event['_id']}")
            print(f"  Title: {event['title']}")
            print(f"  Date: {event['date']}")
            print(f"  Location: {event['location']}")
        
        print("\n🎉 Database seeded successfully!")
        print("\nYou can now use these IDs with your API:")
        print("  GET http://localhost:8000/api/events/{event_id}")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        print("\nMake sure MongoDB is running!")
        print("  Windows: net start MongoDB")
    finally:
        client.close()

def add_custom_event():
    """Interactive function to add your own event"""
    print("\n➕ Add a Custom Event\n")
    
    title = input("Event Title: ")
    description = input("Description: ")
    date = input("Date (YYYY-MM-DDTHH:MM:SS, e.g., 2025-12-25T18:00:00): ")
    location = input("Location: ")
    category = input("Category (optional): ") or "General"
    organizer = input("Organizer (optional): ") or "Unknown"
    
    custom_event = {
        "title": title,
        "description": description,
        "date": date,
        "location": location,
        "category": category,
        "organizer": organizer,
        "created_at": datetime.utcnow().isoformat()
    }
    
    try:
        result = events_collection.insert_one(custom_event)
        print(f"\n✅ Event created with ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        print(f"\n❌ Error creating event: {e}")
        return None

def view_all_events():
    """Display all events in the database"""
    print("\n📋 All Events:\n")
    try:
        events = list(events_collection.find())
        if not events:
            print("  No events found in database.")
        else:
            for idx, event in enumerate(events, 1):
                print(f"{idx}. {event['title']}")
                print(f"   ID: {event['_id']}")
                print(f"   Date: {event['date']}")
                print(f"   Location: {event['location']}\n")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("  MongoDB Event Seeder")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("  1. Seed database with sample events")
        print("  2. Add a custom event")
        print("  3. View all events")
        print("  4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            seed_database()
        elif choice == "2":
            add_custom_event()
        elif choice == "3":
            view_all_events()
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please enter 1-4.")
    
    client.close()