from django.shortcuts import render, redirect
from .models import AIChat, Message
from django.contrib.auth.decorators import login_required
from .forms import ChatForm
import requests
import os
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest

from django.shortcuts import render
from .models import Message
import requests

# index view
def index(request):
    return render(request, 'chatbot/index.html')

@login_required
def chat_view(request, pk):
    if request.method == "POST":
        user_id = request.user.id 
        user_message = request.POST.get('user_message') 
        if not user_message:
            return HttpResponseBadRequest("User message is required.")
        user_instance = User.objects.get(id=user_id)
        
        ai_chat_title = "AI Chat" 
        ai_chat, created = AIChat.objects.get_or_create(
            title=ai_chat_title,
            defaults={"author": user_instance},
            pk=pk
            )
        
        bot_message = get_ai_response(user_message)
        Message.objects.create(
            user_message=user_message,
            bot_message=bot_message,
            aichat=ai_chat,
            chat_user=request.user 
        )
    messages = Message.objects.all()

    return render(
        request, 
        'chatbot/chat_detail.html', 
        {   
            
            'messages': messages.order_by(
                'timestamp', 
                'aichat',
                'sequence_number'),
                  'pk': pk})


def get_ai_response(user_input: str) -> str:
    # Set up the API endpoint and headers
    endpoint = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
        "Content-Type": "application/json",
    }

    # Data payload
    messages = get_existing_messages()
    messages.append({"role": "user", "content": f"{user_input}"})
    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "temperature": 0.7
    }
    response = requests.post(
        endpoint, 
        headers=headers, 
        json=data
        )
    response_data = response.json()
    print(f'{response_data = }')
    ai_message = response_data['choices'][0]['message']['content']
    return ai_message


def get_existing_messages() -> list:
    """
    Get all messages from the database and format them for the API.
    """
    formatted_messages = []

    for message in Message.objects.values('user_message', 'bot_message'):
        formatted_messages.append({"role": "user", "content": message['user_message']})
        formatted_messages.append({"role": "assistant", "content": message['bot_message']})

    return formatted_messages


# CRUD operations
def chat_list(request):
    chats = AIChat.objects.all()
    return render(
        request, 
        'chatbot/chat_list.html', 
        {'chats': chats}
        )


def create_chat(request, pk):
    chat = AIChat.objects.get(pk=pk)

    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            chat = form.save()
            return redirect('chat_detail', pk=chat.pk)
    else:
        form = ChatForm()
    return render(
        request, 
        'chatbot/chat_form.html', 
        {'form': form, 'chat': chat}
        )
        

# @login_required
# def chat_edit(request, pk):
#     chat = AIChat.objects.get(pk=pk)
#     if request.method == 'POST':
#         form = ChatForm(request.POST, instance=chat)
#         if form.is_valid():
#             chat = form.save()
#             return redirect('chat_detail', pk=chat.pk)
#     else:
#         form = ChatForm(instance=chat)
#     return render(request, 'chatbot/chat_form.html', {'form': form})

# @login_required
# def chat_delete(request, pk):
#     AIChat.objects.get(pk=pk).delete()
#     return redirect('chat_list')

# # Chatbot
# def chatbot(request):
#     if request.method == 'POST':
#         message = request.POST.get('message')
#         response = requests.get(f'http://localhost:5005/webhooks/rest/webhook?message={message}')
#         response = response.json()
#         response = response[0]['text']
#         Message.objects.create(sender='user', content=message)
#         Message.objects.create(sender='bot', content=response)
#         return render(request, 'chatbot/chatbot.html', {'response': response})
#     return render(request, 'chatbot/chatbot.html')

