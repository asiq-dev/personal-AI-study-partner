from openai import OpenAI
import random
import string

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
    - When a user asks about the weather, directly call the `get_weather` tool function.
    - Do NOT ask the user for their location. It will be provided via tool calling with latitude and longitude.

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