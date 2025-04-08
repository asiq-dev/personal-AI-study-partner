from django.db import models
from accounts.models import CustomUser
from django.utils import timezone


# Create your models here.

class Chatbot(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    unique_id = models.CharField(max_length=10, unique=True)
    chatbot_name = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.chatbot_name

class OpenaiCredential(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    chatbot = models.ForeignKey(Chatbot, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=255)
    gpt_model = models.CharField(max_length=50)
    assistant_id = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class ChatThread(models.Model):
    chatbot = models.ForeignKey(Chatbot, on_delete=models.CASCADE)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    thread_id = models.CharField(max_length=50, unique=True)  # OpenAI thread ID
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('chatbot', 'owner')

    def __str__(self):
        return f"Thread {self.thread_id} for {self.chatbot.chatbot_name}"
    

class Message(models.Model):
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[('user', 'User'), ('assistant', 'Assistant')])
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."