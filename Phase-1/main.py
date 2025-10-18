from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import redis
import json
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI()


redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
CACHE_TTL = 3600  #


MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client.events_db
events_collection = db.events


class Event(BaseModel):
    id: str = Field(..., description="Unique event identifier")
    title: str = Field(..., description="Event title")
    description: str = Field(..., description="Event description")
    date: str = Field(..., description="Event date in ISO format")
    location: str = Field(..., description="Event location")
    category: Optional[str] = Field(None, description="Event category")
    organizer: Optional[str] = Field(None, description="Event organizer")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "1",
                "title": "Tech Conference 2025",
                "description": "Annual technology conference",
                "date": "2025-11-15T09:00:00",
                "location": "San Francisco, CA",
                "category": "Technology",
                "organizer": "Tech Corp"
            }
        }

class EventCreate(BaseModel):
    title: str
    description: str
    date: str
    location: str
    category: Optional[str] = None
    organizer: Optional[str] = None



HARDCODED_EVENTS = [
    Event(
        id="1",
        title="Tech Conference 2025",
        description="Annual technology conference featuring the latest innovations",
        date="2025-11-15T09:00:00",
        location="San Francisco, CA",
        category="Technology",
        organizer="Tech Corp"
    ),
    Event(
        id="2",
        title="Music Festival",
        description="Three-day outdoor music festival with top artists",
        date="2025-08-20T14:00:00",
        location="Austin, TX",
        category="Music",
        organizer="Live Nation"
    ),
    Event(
        id="3",
        title="Food & Wine Expo",
        description="Culinary experience with renowned chefs",
        date="2025-10-05T11:00:00",
        location="New York, NY",
        category="Food",
        organizer="Culinary Institute"
    ),
    Event(
        id="4",
        title="Marathon 2025",
        description="Annual city marathon for runners of all levels",
        date="2025-09-10T07:00:00",
        location="Boston, MA",
        category="Sports",
        organizer="Boston Athletic Association"
    )
]


@app.get("/api/events", response_model=List[Event])
async def get_events():
    """
    Get all events (returns hardcoded list)
    """
    return HARDCODED_EVENTS


@app.get("/api/events/{event_id}", response_model=Event)
async def get_event(event_id: str):
    """
    Get a specific event by ID.
    First checks Redis cache, then falls back to MongoDB.
    """
    
    cache_key = f"event:{event_id}"
    cached_event = redis_client.get(cache_key)
    
    if cached_event:
        print(f"Cache HIT for event {event_id}")
        return Event(**json.loads(cached_event))
    
    print(f"Cache MISS for event {event_id}")
    
    
    event_data = None
    
    
    try:
        if ObjectId.is_valid(event_id):
            event_data = await events_collection.find_one({"_id": ObjectId(event_id)})
    except Exception as e:
        print(f"Error with ObjectId: {e}")
    
    
    if not event_data:
        event_data = await events_collection.find_one({"id": event_id})
    
    if not event_data:
        raise HTTPException(status_code=404, detail=f"Event with id {event_id} not found")
    
    
    if "_id" in event_data:
        event_data["id"] = str(event_data.pop("_id"))
    
    event = Event(**event_data)
    
    
    redis_client.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(event.model_dump())
    )
    
    return event


@app.post("/api/events", response_model=Event, status_code=201)
async def create_event(event: EventCreate):
    """
    Create a new event in MongoDB
    """
    event_dict = event.model_dump()
    event_dict["created_at"] = datetime.utcnow().isoformat()
    
    result = await events_collection.insert_one(event_dict)
    event_dict["id"] = str(result.inserted_id)
    
    return Event(**event_dict)


@app.delete("/api/events/{event_id}")
async def delete_event(event_id: str):
    """
    Delete an event and invalidate cache
    """
    
    cache_key = f"event:{event_id}"
    redis_client.delete(cache_key)
    
   
    try:
        result = await events_collection.delete_one({"_id": ObjectId(event_id)})
    except Exception:
        result = await events_collection.delete_one({"id": event_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Event with id {event_id} not found")
    
    return {"message": f"Event {event_id} deleted successfully"}


@app.get("/health")
async def health_check():
    """
    Check if Redis and MongoDB are accessible
    """
    redis_status = "connected"
    mongo_status = "connected"
    
    try:
        redis_client.ping()
    except Exception as e:
        redis_status = f"disconnected: {str(e)}"
    
    try:
        await db.command("ping")
    except Exception as e:
        mongo_status = f"disconnected: {str(e)}"
    
    return {
        "status": "healthy",
        "redis": redis_status,
        "mongodb": mongo_status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)