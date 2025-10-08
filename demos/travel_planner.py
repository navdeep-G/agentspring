import asyncio
from typing import Dict, List, Optional
from pydantic import BaseModel
from enum import Enum
from datetime import datetime, timedelta
import random

# Import from agentspring
from agentspring.core.agent import BaseAgent
from agentspring.core.extensions import Tool
from agentspring.core.context import Context

# ===== Data Models =====
class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"

class Message(BaseModel):
    role: MessageRole
    content: str

class Flight(BaseModel):
    id: str
    airline: str
    departure: str
    arrival: str
    price: float
    departure_time: str
    arrival_time: str

class Hotel(BaseModel):
    id: str
    name: str
    location: str
    price_per_night: float
    rating: float
    amenities: List[str]

class Itinerary(BaseModel):
    destination: str
    start_date: str
    end_date: str
    flights: List[Flight]
    hotel: Optional[Hotel] = None
    activities: List[str] = []

# ===== Tools =====
class FlightBookingTools:
    @Tool
    async def search_flights(self, origin: str, destination: str, date: str) -> List[Flight]:
        """Search for available flights between two locations on a specific date."""
        # Simulated flight search
        flights = [
            Flight(
                id=f"FL{random.randint(100,999)}",
                airline=random.choice(["Delta", "United", "American", "Southwest"]),
                departure=origin,
                arrival=destination,
                price=round(random.uniform(150, 800), 2),
                departure_time=f"{date}T{random.randint(6,20)}:00:00",
                arrival_time=f"{date}T{random.randint(8,23)}:00:00"
            ) for _ in range(3)
        ]
        return sorted(flights, key=lambda x: x.price)

    @Tool
    async def book_flight(self, flight_id: str, passenger_name: str) -> Dict[str, str]:
        """Book a flight with the given flight ID for a passenger."""
        # In a real implementation, this would call a flight booking API
        return {
            "status": "confirmed",
            "booking_reference": f"BK-{random.randint(10000,99999)}",
            "flight_id": flight_id,
            "passenger": passenger_name
        }

class HotelBookingTools:
    @Tool
    async def search_hotels(self, location: str, check_in: str, check_out: str) -> List[Hotel]:
        """Search for available hotels in a location for specific dates."""
        # Simulated hotel search
        hotels = [
            Hotel(
                id=f"HTL{random.randint(100,999)}",
                name=f"{random.choice(['Grand', 'Royal', 'Plaza', 'Sunset'])} {random.choice(['Hotel', 'Resort', 'Inn'])}",
                location=location,
                price_per_night=round(random.uniform(80, 300), 2),
                rating=round(random.uniform(3.0, 5.0), 1),
                amenities=random.sample(
                    ["pool", "gym", "spa", "restaurant", "wifi", "parking"],
                    k=random.randint(2, 5)
                )
            ) for _ in range(3)
        ]
        return sorted(hotels, key=lambda x: x.price_per_night)

    @Tool
    async def book_hotel(self, hotel_id: str, guest_name: str, check_in: str, check_out: str) -> Dict[str, str]:
        """Book a hotel room for specific dates."""
        return {
            "status": "confirmed",
            "booking_reference": f"HTL-{random.randint(10000,99999)}",
            "hotel_id": hotel_id,
            "guest": guest_name,
            "check_in": check_in,
            "check_out": check_out
        }

class ActivityTools:
    @Tool
    async def search_activities(self, location: str, date: str) -> List[Dict]:
        """Search for activities in a specific location."""
        activities = [
            {"name": f"{random.choice(['Guided', 'Private', 'Sunset'])} {random.choice(['Tour', 'Experience'])} of {location}",
             "price": round(random.uniform(20, 150), 2),
             "duration": f"{random.randint(1, 6)} hours"}
            for _ in range(3)
        ]
        return activities

# ===== Agents =====
class TravelPlannerAgent(BaseAgent):
    """Coordinates the travel planning process by delegating to specialized agents."""
    
    def __init__(self, context: Context):
        super().__init__(context=context)
        self.flight_agent = FlightBookingAgent(context=context)
        self.hotel_agent = HotelBookingAgent(context=context)
        self.activity_agent = ActivityPlanningAgent(context=context)
        
    async def execute(self, messages: List[Message], context: Optional[Dict] = None) -> Message:
        # Extract travel details from user message
        user_request = messages[-1].content.lower()
        
        # Simple intent detection
        if "plan a trip" in user_request or "book travel" in user_request:
            # In a real implementation, you would use NLP to extract these details
            destination = "New York"  # Simplified for example
            start_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
            end_date = (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d")
            passenger = "John Doe"
            
            # Create itinerary
            itinerary = Itinerary(
                destination=destination,
                start_date=start_date,
                end_date=end_date
            )
            
            # Delegate to specialized agents
            flights = await self.flight_agent.search_flights(
                origin="LAX", 
                destination="JFK", 
                date=start_date
            )
            
            if flights:
                itinerary.flights = [flights[0]]  # Pick the cheapest flight
                await self.flight_agent.book_flight(flights[0].id, passenger)
                
                # Find and book hotel
                hotels = await self.hotel_agent.search_hotels(
                    location=destination,
                    check_in=start_date,
                    check_out=end_date
                )
                
                if hotels:
                    itinerary.hotel = hotels[0]
                    await self.hotel_agent.book_hotel(
                        hotel_id=hotels[0].id,
                        guest_name=passenger,
                        check_in=start_date,
                        check_out=end_date
                    )
                    
                    # Find activities
                    activities = await self.activity_agent.search_activities(
                        location=destination,
                        date=start_date
                    )
                    itinerary.activities = [a["name"] for a in activities[:2]]  # Pick 2 activities
                    
                    return Message(
                        role=MessageRole.ASSISTANT,
                        content=f"Your trip to {destination} is all set! Here's your itinerary:\n"
                               f"- Flight: {itinerary.flights[0].airline} from {itinerary.flights[0].departure} to {itinerary.flights[0].arrival}\n"
                               f"- Hotel: {itinerary.hotel.name} for ${itinerary.hotel.price_per_night}/night\n"
                               f"- Activities: {', '.join(itinerary.activities)}"
                    )
        
        return Message(
            role=MessageRole.ASSISTANT,
            content="I'm here to help you plan your trip! Could you please provide more details about your travel plans?"
        )

class FlightBookingAgent(BaseAgent):
    """Specialized agent for handling flight-related tasks."""
    
    def __init__(self, context: Context):
        super().__init__(context=context)
        self.flight_tools = FlightBookingTools()
        context.tool_registry.register_tool(self.flight_tools.search_flights)
        context.tool_registry.register_tool(self.flight_tools.book_flight)
    
    async def search_flights(self, origin: str, destination: str, date: str) -> List[Flight]:
        return await self.flight_tools.search_flights(origin, destination, date)
    
    async def book_flight(self, flight_id: str, passenger_name: str) -> Dict[str, str]:
        return await self.flight_tools.book_flight(flight_id, passenger_name)

class HotelBookingAgent(BaseAgent):
    """Specialized agent for handling hotel-related tasks."""
    
    def __init__(self, context: Context):
        super().__init__(context=context)
        self.hotel_tools = HotelBookingTools()
        context.tool_registry.register_tool(self.hotel_tools.search_hotels)
        context.tool_registry.register_tool(self.hotel_tools.book_hotel)
    
    async def search_hotels(self, location: str, check_in: str, check_out: str) -> List[Hotel]:
        return await self.hotel_tools.search_hotels(location, check_in, check_out)
    
    async def book_hotel(self, hotel_id: str, guest_name: str, check_in: str, check_out: str) -> Dict[str, str]:
        return await self.hotel_tools.book_hotel(hotel_id, guest_name, check_in, check_out)

class ActivityPlanningAgent(BaseAgent):
    """Specialized agent for handling activity planning."""
    
    def __init__(self, context: Context):
        super().__init__(context=context)
        self.activity_tools = ActivityTools()
        context.tool_registry.register_tool(self.activity_tools.search_activities)
    
    async def search_activities(self, location: str, date: str) -> List[Dict]:
        return await self.activity_tools.search_activities(location, date)

# ===== Main Execution =====
async def main():
    print("🌍 Welcome to the Travel Planning System!")
    print("Type 'plan a trip' to get started or 'exit' to quit.")
    
    # Initialize context and register tools
    context = Context()
    
    # Create and register agents
    travel_planner = TravelPlannerAgent(context=context)
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'exit':
            print("Goodbye! Happy travels! ✈️")
            break
            
        # Create message from user input
        messages = [Message(role=MessageRole.USER, content=user_input)]
        
        # Get response from travel planner
        response = await travel_planner.execute(messages)
        print(f"\nAssistant: {response.content}")

if __name__ == "__main__":
    asyncio.run(main())