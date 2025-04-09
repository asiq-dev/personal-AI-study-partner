import time
from django.shortcuts import render

from django.http import JsonResponse
from django.shortcuts import render

from dsa_tutor.utils import create_chatbot_assistant, fetch_google_sheet, generate_random_string, get_location_from_ip, get_weather

from .models import ChatThread, Chatbot, OpenaiCredential, Message  # Assuming these models exist
from django.contrib.auth.decorators import login_required

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from openai import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


# Create your views here.
# class HomeView(LoginRequiredMixin, TemplateView):
#     template_name = 'tutor/home.html'


@login_required
def list_tutors(request):
    chatbots = Chatbot.objects.filter(owner=request.user)
    return render(request, 'tutor/tutor_list.html', {'chatbots': chatbots})



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
        
        # Add the user message to the OpenAI thread
        client.beta.threads.messages.create(
            thread_id=thread.thread_id,
            role="user",
            content=user_message
        )

        # Create and run the assistant
        print("🧠 Starting assistant run...")
        run = client.beta.threads.runs.create(
            thread_id=thread.thread_id,
            assistant_id=openai_cred.assistant_id
        )

        # Wait for the run to complete
        while True:
            run = client.beta.threads.runs.retrieve(thread_id=thread.thread_id, run_id=run.id)
            print(f"⏳ Run status: {run.status}")
            if run.status == "completed":
                print("✅ Run completed.")
                break
            elif run.status == "requires_action":
                print("🔧 Assistant requested tool actions...")
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                for tool_call in tool_calls:
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    print(f"📦 Tool call: {func_name} with args {args}")

                    if func_name == "get_weather":
                        # Get location from IP
                        lat, lon = get_location_from_ip()
                        print(f"Using location: Latitude={lat}, Longitude={lon}")
                        result = get_weather(lat, lon)

                    elif func_name == "fetch_google_sheet":
                        result = fetch_google_sheet(args["spreadsheet_id"])
                    else:
                        result = {"error": "Unknown function"}
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(result)
                    })
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
                print("🔁 Submitted tool outputs. Waiting for next step...")

            elif run.status in ["failed", "cancelled", "expired"]:
                print(f"❌ Run ended with error: {run.status}")
                return JsonResponse({"error": f"Run failed with status: {run.status}"}, status=500)

            time.sleep(0.5)  # Avoid overwhelming the API with requests

        # Get the assistant’s response
        messages = client.beta.threads.messages.list(thread_id=thread.thread_id)
        assistant_reply = messages.data[0].content[0].text.value
        Message.objects.create(thread=thread, role="assistant", content=assistant_reply)

        return JsonResponse({"reply": assistant_reply})
    return JsonResponse({"error": "Invalid request"}, status=400)


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
    return render(request, 'tutor/chat_view.html', {'chatbot': chatbot, 'thread': thread, 'messages': messages})