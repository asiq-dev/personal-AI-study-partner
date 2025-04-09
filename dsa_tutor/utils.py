from openai import OpenAI
import random
import string
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import requests
from personal_study_partner import settings


# Constants for Google Sheets API and OpenWeather API
GOOGLE_CREDENTIALS_FILE = "credentials/personal-ai-study-partner-66175870c255.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
WEATHER_API_KEY = settings.WEATHER_API_KEY


## Function to create a chatbot assistant with specific capabilities
def create_chatbot_assistant(chatbot_name, openai_key):
    # Define instructions
    instructions = """
    You are an AI study partner assistant with three main capabilities. You must not answer questions outside these capabilities.

    🔒 You are NOT allowed to:
    - Answer questions unrelated to your capabilities.
    - Share or discuss information about other people.
    - Answer general knowledge, personal, or opinion-based queries.
    - Do NOT ask users for latitude or longitude. You will receive it via tool call arguments.

    ✅ You are ONLY allowed to perform the following:

    1. 📘 Teach Data Structures and Algorithms:
    - Provide clear explanations, examples, and Python code for topics such as arrays, linked lists, trees, graphs, recursion, sorting, searching, etc.
    - ONLY respond to topics directly related to data structures and algorithms. Do NOT respond to general computer science, system design, or unrelated programming topics.

    2. 🌤️ Fetch Weather Data:
    - When a user asks about the weather, directly call the 'get_weather' function.
    - Do NOT ask the user for their location. Their coordinates will be automatically injected by the system.

    3. 📊 Fetch Google Sheets Data:
    Show to-do list: When asked to show the data from sheet like for todo list, use the 'fetch_google_sheet' function to retrieve and display the entire list from a Google Sheet with columns 'no', 'name', and 'status'. Use the spreadsheet ID. If user doesn't provide it, ask them to provide the spreadsheet ID.

    If a request doesn't match one of these three categories, politely decline to answer and explain your limitations.
    """

    # Define tools
    tools_list = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Fetches current weather data based on the user's current location (auto-detected).",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "fetch_google_sheet",
                "description": "Fetches a to-do list from a entire Google Sheet with columns 'no', 'name', and 'status'. Returns the list in a readable format.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "spreadsheet_id": {
                            "type": "string",
                            "description": "The ID of the Google Sheet containing data."
                        },
                    },
                    "required": ["spreadsheet_id",]
                }
            }
        }
    ]

    # Create the assistant
    client = OpenAI(api_key=openai_key)
    try:
        my_assistant = client.beta.assistants.create(
            name=chatbot_name,
            description="A chatbot for teaching DS/Algo, fetching weather, and Google Sheets data.",
            instructions=instructions,
            model="gpt-4o",
            tools=tools_list,
        )
        return my_assistant.id
    except Exception as e:
        print(f"Error creating assistant: {e}")
        raise


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


## some functions for weather and google sheets data fetching

#for dynamic weather data of user current location
def get_location_from_ip():
    try:
        response = requests.get("https://ipinfo.io")
        data = response.json()
        loc = data.get("loc")  # returns something like '37.7749,-122.4194'
        if loc:
            lat, lon = map(float, loc.split(','))
            return lat, lon
    except Exception as e:
        print("🌍 Failed to fetch location:", e)
    return 0.0, 0.0  # fallback


## Tool Functions

def get_weather(latitude, longitude):
    weather_data = {}
    # OpenWeather API URL for current weather
    weather_url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={latitude}&lon={longitude}&appid={WEATHER_API_KEY}&units=metric"
    )
    print(f"making api call to {weather_url}")

    response = requests.get(weather_url).json()

    # Check if API returns an error message
    if response.get("cod") != 200:
        print(f"OpenWeather API error: {response.get('message')}")
        return {"error": "Failed to fetch weather data"}
    
    # Extract and format the weather information
    weather_data = {
        "location": response["name"],
        "temperature": response["main"]["temp"],
        "weather": response["weather"][0]["description"],
        "humidity": response["main"]["humidity"],
        "wind_speed": response["wind"]["speed"]
    }    
    return weather_data



def fetch_google_sheet(spreadsheet_id):
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)

    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheet = spreadsheet.get("sheets")[0]
    sheet_name = sheet['properties']['title']

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}"  # Just the sheet name fetches all data
    ).execute()
    values = result.get("values", [])

    if not values:
        return {"message": "No to-do items found in the sheet."}
    
    # Assuming the first row is a header (no, name, status), skip it
    todo_list = values[1:] if len(values) > 1 else values

    # Format the to-do list as a readable string
    formatted_list = "Your To-Do List:\n"
    for row in todo_list:
        no = row[0] if len(row) > 0 else ""
        name = row[1] if len(row) > 1 else ""
        status = row[2] if len(row) > 2 else ""
        formatted_list += f"- #{no}: {name} (Status: {status})\n"

    return {"data": formatted_list.strip()} if todo_list else {"message": "No to-do items found after the header."}
