from django.shortcuts import render

from django.http import JsonResponse
from django.shortcuts import render

from dsa_tutor.utils import create_chatbot_assistant, generate_random_string
from .models import ChatThread, Chatbot, OpenaiCredential, Message  # Assuming these models exist
from django.contrib.auth.decorators import login_required

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from openai import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import json


# Create your views here.
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'tutor/home.html'


@login_required
def list_tutors(request):
    chatbots = Chatbot.objects.filter(owner=request.user)
    return render(request, 'tutor/tutor_list.html', {'chatbots': chatbots})

WEATHER_API_KEY = "your-openweather-api-key"
GOOGLE_CREDENTIALS_FILE = "path/to/your/credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

@csrf_exempt
@login_required
def chat(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")
        chatbot_id = data.get("chatbot_id", "")

        chatbot = Chatbot.objects.get(id=chatbot_id, owner=request.user)
        openai_cred = OpenaiCredential.objects.get(chatbot=chatbot)
        client = OpenAI(api_key=openai_cred.api_key)

        thread, _ = ChatThread.objects.get_or_create(chatbot=chatbot, owner=request.user)
        Message.objects.create(thread=thread, role="user", content=user_message)

        client.beta.threads.messages.create(
            thread_id=thread.thread_id,
            role="user",
            content=user_message
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.thread_id,
            assistant_id=openai_cred.assistant_id
        )

        while run.status in ["queued", "in_progress"]:
            run = client.beta.threads.runs.retrieve(thread_id=thread.thread_id, run_id=run.id)
            if run.status == "requires_action":
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                for tool_call in tool_calls:
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    if func_name == "get_weather":
                        result = get_weather(args["city"])
                    elif func_name == "fetch_google_sheet":
                        result = fetch_google_sheet(args["spreadsheet_id"], args["range_name"])
                    else:
                        result = {"error": "Unknown function"}
                    tool_outputs.append({"tool_call_id": tool_call.id, "output": json.dumps(result)})
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

        messages = client.beta.threads.messages.list(thread_id=thread.thread_id)
        assistant_reply = messages.data[0].content[0].text.value
        Message.objects.create(thread=thread, role="assistant", content=assistant_reply)

        return JsonResponse({"reply": assistant_reply})
    return JsonResponse({"error": "Invalid request"}, status=400)


# Tool Functions
def get_weather(city):
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={WEATHER_API_KEY}"
    geo_response = requests.get(geo_url).json()
    if not geo_response:
        return {"error": "City not found"}
    lat, lon = geo_response[0]["lat"], geo_response[0]["lon"]
    weather_data = {}
    for i in range(3, 0, -1):
        past_time = int((datetime.now() - timedelta(hours=i)).timestamp())
        weather_url = f"https://api.openweathermap.org/data/2.5/onecall/timemachine?lat={lat}&lon={lon}&dt={past_time}&appid={WEATHER_API_KEY}"
        response = requests.get(weather_url).json()
        weather_data[f"{i} hour(s) ago"] = response.get("current", {}).get("weather", [])
    return weather_data



def fetch_google_sheet(spreadsheet_id, range_name):
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get("values", [])
    return {"data": values} if values else {"message": "No data found"}




@login_required
def create_tutor(request):
    if request.method == "POST":
        try:
            # Extract form data
            chatbot_name = request.POST.get("chatbot_name").strip()
            openai_api_key = request.POST.get("openai_api_key").strip()
            gpt_model = request.POST.get("gpt_model").strip()

            # Step 1: Create the assistant
            assistant_id = create_chatbot_assistant(chatbot_name, openai_api_key)

            # Step 2: Create a unique ID and save the chatbot
            unique_id = generate_random_string(10)  # Reuse your function
            new_chatbot = Chatbot.objects.create(
                owner=request.user,  # Tie it to the logged-in user instead of restaurant
                unique_id=unique_id,
                chatbot_name=chatbot_name,
            )

            # Step 3: Save OpenAI credentials
            new_openai_item = OpenaiCredential.objects.create(
                owner=request.user,
                chatbot=new_chatbot,
                api_key=openai_api_key,
                gpt_model=gpt_model,
                assistant_id=assistant_id,
            )

            return JsonResponse({"success": True, "chatbot_id": new_chatbot.id})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    else:
        return render(request, "tutor/create_tutor.html", {"owner": request.user})
    

@login_required
def chat_view(request, tutor_id):
    chatbot = Chatbot.objects.get(id=tutor_id, owner=request.user)
    open_cred = OpenaiCredential.objects.get(chatbot=chatbot)
    thread, created = ChatThread.objects.get_or_create(chatbot=chatbot, owner=request.user)
    if created:
        client = OpenAI(api_key=open_cred.api_key)
        thread_obj = client.beta.threads.create()
        thread.thread_id = thread_obj.id
        thread.save()
    messages = Message.objects.filter(thread=thread).order_by('created_at')
    return render(request, 'tutor/home.html', {'chatbot': chatbot, 'thread': thread, 'messages': messages})