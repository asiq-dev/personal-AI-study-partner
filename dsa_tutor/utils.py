from openai import OpenAI
import random
import string

def create_chatbot_assistant(chatbot_name, openai_key):
    # Define instructions
    instructions = """
    You are a helpful chatbot with three main capabilities:
    1. Teach data structures and algorithms: Provide clear explanations, examples, and Python code snippets when asked about topics like arrays, linked lists, sorting algorithms, etc.That means only data structures and algorithms related topics not other things. Not means not.
    2. Fetch weather data: When asked about the weather, use the 'get_weather' function to retrieve the last 3 hours of weather data from the OpenWeather API based on a city name.
    3. Fetch Google Sheets data: When asked to retrieve data from a Google Sheet, use the 'fetch_google_sheet' function to access the specified spreadsheet and range.

    For any other questions, respond conversationally and helpfully. If a user request matches one of your capabilities, call the appropriate tool function.
    """

    # Define tools
    tools_list = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Fetches the last 3 hours of weather data for a given city using the OpenWeather API.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The name of the city to fetch weather data for."
                        }
                    },
                    "required": ["city"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "fetch_google_sheet",
                "description": "Fetches data from a specified Google Sheet range.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "spreadsheet_id": {
                            "type": "string",
                            "description": "The ID of the Google Sheet."
                        },
                        "range_name": {
                            "type": "string",
                            "description": "The range to fetch (e.g., Sheet1!A1:B10)."
                        }
                    },
                    "required": ["spreadsheet_id", "range_name"]
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