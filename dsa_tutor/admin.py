from django.contrib import admin

# Register your models here.

from .models import Chatbot, OpenaiCredential, ChatThread, Message

admin.site.register(Chatbot)
admin.site.register(OpenaiCredential)
admin.site.register(ChatThread)
admin.site.register(Message)
