from .models import Message
from .forms import UserCreationForm
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.shortcuts import  render, redirect
from .forms import NewUserForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
import json
import os
import openai
from dotenv import load_dotenv
load_dotenv()

# Square API credentials
openai.api_key = os.getenv("OPEN_AI_KEY")

class SignUp(CreateView):
    print('what the heck')
    form_class = UserCreationForm
    print(form_class)
    success_url = reverse_lazy("chat")
    template_name = "registration/signup.html"

def logout_view(request):
    logout(request)
    print('here')
    return redirect('landing_page')

def register(request):
	if request.method == "POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("chat")
		else:
			# Form is invalid, print out the errors
			print(form.errors)
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = UserCreationForm()
	return render (request=request, template_name="registration/signup.html", context={"register_form":form})

'''
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        form = NewUserForm(request.POST)
        print(form) 
        user = authenticate(username=email, password=password)
        
        if user is not None:
            # Authentication succeeded
            login(request, user)
            redirect('chat')
            # Redirect the user to a success page
        else:
            print('auth failed')
            # Authentication failed
            # Display an error message or redirect back to the login page
    else:
        # Render the login form
        return render(request, 'login.html')

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        form = NewUserForm(request.POST)
        print()

        user = User.objects.create_user(username=email, email=email, password=password)        
        # Authenticate the user
        authenticated_user = authenticate(request, username=email, password=password)
        if authenticated_user:
            login(request, authenticated_user)  # Log in the user
            return redirect('chat')  # Redirect to the home page
        else:
            # Check if the email already exists in the database
            return render(request, 'register.html')

    return render(request, 'register.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(request, f'Your account has been created. You can log in now!')    
            return redirect('login')
    else:
        form = UserCreationForm()

    context = {'form': form}
    return render(request, 'register.html', context)
'''

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def save_message(request):

    if request.method == 'POST' and is_ajax(request):
        message_text = request.POST.get('message')
        user = request.user
        
        Message(user=user, text=message_text, is_bot_message=False).save()
        response = openai.Completion.create(
          model="text-davinci-003",
          prompt="The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman:{}\nAI:".format(message_text),
          temperature=0.9,
          max_tokens=150,
          top_p=1,
          frequency_penalty=0.0,
          presence_penalty=0.6,
          stop=[" Human:", " AI:"]
        )
        chatbot_response = response['choices'][0]['text']
 
        # Save the message associated with the logged-in user
        Message(user=user, text=chatbot_response, is_bot_message=True).save()
        
        response = {
          'ai_message': chatbot_response,
          'success': True
        }
        return JsonResponse(response)
    return JsonResponse({'success': False})

def chat(request):
    curr_user = str(request.user)
    print(curr_user)     
    m = Message.objects.filter(user=request.user)
 
    messages = {}
    messages[curr_user] = []
    for message in m:
        messages[curr_user].append([message.is_bot_message, message.text, int(message.created_at.timestamp())])

    print(messages)
 
    messages = json.dumps(messages)
    #print(messages)
    return render(request, 'chat.html', {'messages': messages})

def landing_page(request):
    return render(request, 'landing_page.html')
