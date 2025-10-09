import os
import json
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
import asyncio
import random
from datetime import datetime, timedelta
from openai import AsyncOpenAI

# Import from agentspring
from agentspring.core.agent import BaseAgent
from agentspring.core.extensions import Tool
from agentspring.core.base import Context

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ===== Data Models =====
class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"

class Message(BaseModel):
    role: MessageRole
    content: str
    name: Optional[str] = None

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
    flights: List[Flight] = Field(default_factory=list)
    hotel: Optional[Hotel] = None
    activities: List[str] = Field(default_factory=list)

# ===== LLM Integration =====
class LLMService:
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.memory = []
    
    async def generate_response(self, messages: List[Dict[str, str]], tools: List[Dict] = None) -> Dict:
        """Generate a response using the LLM with function calling support."""
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools or [],
                tool_choice="auto" if tools else None
            )
            return response.choices[0].message
        except Exception as e:
            print(f"Error calling LLM: {e}")
            raise

    async def extract_travel_details(self, user_input: str) -> Dict[str, Any]:
        """Extract structured travel details from natural language input."""
        system_prompt = """
        You are a helpful travel assistant that extracts travel details from user messages.
        Extract the following information if mentioned:
        - Destination city
        - Travel dates (start and end)
        - Number of travelers
        - Budget range
        - Any specific preferences (e.g., flight class, hotel type)
        
        Return the information as a JSON object.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        response = await self.generate_response(messages)
        
        try:
            # Try to parse the response as JSON
            return json.loads(response.content)
        except json.JSONDecodeError:
            # If response is not JSON, try to extract information conversationally
            return await self._extract_details_conversationally(user_input)
    
    async def _extract_details_conversationally(self, user_input: str) -> Dict[str, Any]:
        """Fallback method to extract details conversationally."""
        # This is a simplified version - in production, you'd want more robust parsing
        details = {}
        
        # Simple keyword matching (this is just a fallback)
        if "new york" in user_input.lower() or "nyc" in user_input.lower():
            details["destination"] = "New York"
        elif "los angeles" in user_input.lower() or "la" in user_input.lower():
            details["destination"] = "Los Angeles"
            
        # Add more sophisticated parsing as needed
        
        return details

# ===== Tools =====
class FlightBookingTools:
    @Tool
    async def search_flights(self, origin: str, destination: str, date: str) -> List[Dict]:
        """Search for available flights between two locations on a specific date."""
        # Simulated flight search
        flights = [
            {
                "id": f"FL{random.randint(100,999)}",
                "airline": random.choice(["Delta", "United", "American", "Southwest"]),
                "departure": origin,
                "arrival": destination,
                "price": round(random.uniform(150, 800), 2),
                "departure_time": f"{date}T{random.randint(6,20)}:00:00",
                "arrival_time": f"{date}T{random.randint(8,23)}:00:00"
            } for _ in range(3)
        ]
        return sorted(flights, key=lambda x: x["price"])

    @Tool
    async def book_flight(self, flight_id: str, passenger_name: str) -> Dict[str, str]:
        """Book a flight with the given flight ID for a passenger."""
        return {
            "status": "confirmed",
            "booking_reference": f"BK-{random.randint(10000,99999)}",
            "flight_id": flight_id,
            "passenger": passenger_name
        }

class HotelBookingTools:
    @Tool
    async def search_hotels(self, location: str, check_in: str, check_out: str) -> List[Dict]:
        """Search for available hotels in a location for specific dates."""
        hotels = [
            {
                "id": f"HTL{random.randint(100,999)}",
                "name": f"{random.choice(['Grand', 'Royal', 'Plaza', 'Sunset'])} {random.choice(['Hotel', 'Resort', 'Inn'])}",
                "location": location,
                "price_per_night": round(random.uniform(80, 300), 2),
                "rating": round(random.uniform(3.0, 5.0), 1),
                "amenities": random.sample(
                    ["pool", "gym", "spa", "restaurant", "wifi", "parking"],
                    k=random.randint(2, 5)
                )
            } for _ in range(3)
        ]
        return sorted(hotels, key=lambda x: x["price_per_night"])

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

# ===== LLM-Powered Agent =====
class LLMTravelAgent(BaseAgent):
    def __init__(self, context: Context):
        super().__init__(context=context)
        self.llm = LLMService()
        self.conversation_history = []
        
        # Initialize tools
        self.flight_tools = FlightBookingTools()
        self.hotel_tools = HotelBookingTools()
        
        # Register tools
        context.tool_registry.register_tool(self.flight_tools.search_flights)
        context.tool_registry.register_tool(self.flight_tools.book_flight)
        context.tool_registry.register_tool(self.hotel_tools.search_hotels)
        context.tool_registry.register_tool(self.hotel_tools.book_hotel)
        
        # Define available tools for the LLM
        self.available_tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_flights",
                    "description": "Search for available flights between two locations on a specific date",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "origin": {"type": "string", "description": "Departure city or airport code"},
                            "destination": {"type": "string", "description": "Arrival city or airport code"},
                            "date": {"type": "string", "description": "Date in YYYY-MM-DD format"}
                        },
                        "required": ["origin", "destination", "date"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "book_flight",
                    "description": "Book a flight with the given flight ID for a passenger",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "flight_id": {"type": "string", "description": "ID of the flight to book"},
                            "passenger_name": {"type": "string", "description": "Name of the passenger"}
                        },
                        "required": ["flight_id", "passenger_name"]
                    }
                }
            },
            # Add other tools similarly...
        ]
    
    async def execute(self, messages: List[Message], context: Optional[Dict] = None) -> Message:
        # Add new messages to conversation history
        self.conversation_history.extend([{"role": msg.role.value, "content": msg.content} for msg in messages])
        
        # Get the latest user message
        user_message = messages[-1].content
        
        # First, try to extract travel details using LLM
        travel_details = await self.llm.extract_travel_details(user_message)
        
        # If we have enough details, proceed with booking
        if "destination" in travel_details:
            # In a real implementation, you would use these details to make actual bookings
            destination = travel_details["destination"]
            start_date = travel_details.get("start_date", (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"))
            
            # Generate a response using the LLM
            response = await self.llm.generate_response(
                messages=self.conversation_history,
                tools=self.available_tools
            )
            
            # Check if the LLM wants to call any tools
            if hasattr(response, 'tool_calls') and response.tool_calls:
                tool_calls = response.tool_calls
                tool_responses = []
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Call the appropriate tool
                    if function_name == "search_flights":
                        result = await self.flight_tools.search_flights(**function_args)
                        tool_responses.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": json.dumps(result)
                        })
                    elif function_name == "book_flight":
                        result = await self.flight_tools.book_flight(**function_args)
                        tool_responses.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": json.dumps(result)
                        })
                    # Add other tool calls as needed
                
                # Add tool responses to conversation history
                self.conversation_history.extend(tool_responses)
                
                # Get final response from LLM with tool results
                response = await self.llm.generate_response(
                    messages=self.conversation_history
                )
            
            return Message(
                role=MessageRole.ASSISTANT,
                content=response.content
            )
        else:
            # Ask for more information
            return Message(
                role=MessageRole.ASSISTANT,
                content="I'd love to help you plan your trip! Could you please tell me your destination and travel dates?"
            )

# ===== Main Execution =====
async def main():
    print("🌍 Welcome to the AI-Powered Travel Planner!")
    print("You can say things like:")
    print("- 'I want to book a trip to Paris next month'")
    print("- 'Find me flights from New York to Los Angeles on October 15th'")
    print("- 'I need a hotel in Tokyo for 3 nights starting next week'")
    print("Type 'exit' to quit.\n")
    
    # Initialize context
    context = Context()
    
    # Create and initialize the LLM agent
    agent = LLMTravelAgent(context=context)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'exit':
                print("\nThank you for using the AI Travel Planner. Have a great trip! ✈️")
                break
                
            # Create message from user input
            messages = [Message(role=MessageRole.USER, content=user_input)]
            
            # Get response from agent
            response = await agent.execute(messages)
            
            # Print assistant's response
            print(f"\nAssistant: {response.content}")
            
        except KeyboardInterrupt:
            print("\nGoodbye! Safe travels! ✈️")
            break
        except Exception as e:
            print(f"\nSorry, I encountered an error: {str(e)}")
            print("Please try again or ask something else.")

if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key before running this script:")
        print("export OPENAI_API_KEY='your-api-key-here'")
    else:
        asyncio.run(main())