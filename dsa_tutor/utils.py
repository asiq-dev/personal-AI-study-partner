from openai import OpenAI
import random
import string
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import requests
from accounts.models import CustomUser
from dsa_tutor.instructions import instruction
from personal_study_partner import settings


# Constants for Google Sheets API and OpenWeather API
GOOGLE_CREDENTIALS_FILE = "credentials/personal-ai-study-partner-66175870c255.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
WEATHER_API_KEY = settings.WEATHER_API_KEY


## Function to create a chatbot assistant with specific capabilities
def create_chatbot_assistant(chatbot_name, openai_key, gpt_model):
    # Define instructions
    instructions = instruction()

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
        },

        {
            "type": "function",
            "function": {
                "name": "verify_email_exists",
                "description": "Verifies if the email exists in the system and is it requested user's email.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "The email to verify."
                        }
                    },
                    "required": ["email"],
                }
            }
        },

        {
            "type": "function",
            "function": {
                "name": "reset_password",
                "description": "Resets the password for the requested user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "the email of the user given and whose password is to be reset."
                        },
                        "new_password": {
                            "type": "string",
                            "description": "The new password for the user."
                        },
                    },
                    "required": ["email", "new_password"],
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
            model=gpt_model,
            tools=tools_list,
        )
        return my_assistant.id
    except Exception as e:
        print(f"Error creating assistant: {e}")
        raise



## some functions for weather and google sheets data fetching helper functions

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

# for generating random string for unique id of chatbot
def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


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


def verify_email_exists(email, current_user_email):
    #check your user database to see if the email exists and email is of the user who is requesting it
    if current_user_email != email:
        return {"error": "You are not authorized to verify this email."}

    result = CustomUser.objects.filter(email=email).exists()
    if not result:
        return {"error": "Email does not exist."}
    return {"message": f"Email {email} exists in the system."}


def reset_password(email, new_password):
    # Here you would typically call your user management system to reset the password
    user = CustomUser.objects.filter(email=email).first()
    user.set_password(new_password)
    user.save()

    return {"message": f"Password for {email} has been reset successfully."}