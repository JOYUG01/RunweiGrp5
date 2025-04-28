# grants/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Grant
from datetime import datetime, timedelta
import os
from django.conf import settings

import requests
from bs4 import BeautifulSoup
from google.oauth2 import service_account
from googleapiclient.discovery import build
import urllib.parse

def home(request):
    return render(request, 'grants/home.html')

# grants/views.py (relevant snippet)
def grants_list(request):
    # grants = Grant.objects.all()
    # today = datetime.today().date()
    print("Grants being passed:", grants)

    # for grant in grants:
    #     days_until_deadline = (grant.deadline - today).days
    #     if days_until_deadline <= 7:
    #         grant.deadline_status = 'red'
    #     elif days_until_deadline <= 30:
    #         grant.deadline_status = 'orange'
    #     else:
    #         grant.deadline_status = 'green'
    
    return render(request, 'grants/grants_list.html', {'grants': grants})

@login_required
def user_dashboard(request):
    return render(request, 'grants/user_dashboard.html')

@staff_member_required
def admin_dashboard(request):
    return render(request, 'grants/admin_dashboard.html')

# def signup(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('home')
#     else:
#         form = UserCreationForm()
#     return render(request, 'grants/signup.html', {'form': form})


# grants/views.py (partial update)
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LoginView
from .models import Grant
from datetime import datetime, timedelta

# Custom Login View to add placeholders
class CustomLoginView(LoginView):
    template_name = 'grants/login.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['username'].widget.attrs.update({'placeholder': 'Username', 'class': 'form-control'})
        form.fields['password'].widget.attrs.update({'placeholder': 'Password', 'class': 'form-control'})
        return form

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
        # Add placeholders and ensure form-control class
        form.fields['username'].widget.attrs.update({'placeholder': 'Username', 'class': 'form-control'})
        form.fields['password1'].widget.attrs.update({'placeholder': 'Password', 'class': 'form-control'})
        form.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password', 'class': 'form-control'})
    return render(request, 'grants/signup.html', {'form': form})


# Initialize Google Forms API client
def get_forms_service():
    SCOPES = ['https://www.googleapis.com/auth/forms.body']
    creds = service_account.Credentials.from_service_account_file(
        os.path.join(settings.BASE_DIR, 'grounded-burner.json'), scopes=SCOPES)
    return build('forms', 'v1', credentials=creds)

# Hardcoded grant links (you could later move this into a model or a DB)
grants = {
    "Students Grant Application": "https://group05.wufoo.com/forms/q1dq5s0i00ccuiu/",
    "Students Grant Application 2": "https://group05.wufoo.com/forms/q1dq5s0i00ccuiu/",
    "Students Grant Application 3": "https://group05.wufoo.com/forms/q1dq5s0i00ccuiu/"
}

# Google Forms API setup
SCOPES = ['https://www.googleapis.com/auth/forms.body']
SERVICE_ACCOUNT_FILE = os.path.join(settings.BASE_DIR, 'grounded-burner.json')  # Important!

def authenticate_google_forms():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('forms', 'v1', credentials=credentials)
    return service

def scrape_form(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    questions = []
    for label in soup.find_all("label"):
        question_text = label.get_text(strip=True)
        input_tag = label.find_next(["input", "textarea", "select"])

        if input_tag:
            input_type = input_tag.name
            questions.append({
                "question": question_text,
                "type": input_type,
                "options": [option.text for option in input_tag.find_all("option")] if input_tag.name == "select" else None
            })
    return questions

def create_google_form(service, form_title, questions):
    form = {
        "info": {
            "title": form_title
        }
    }
    created_form = service.forms().create(body=form).execute()
    form_id = created_form['formId']

    requests_list = []
    for q in questions:
        item = {
            "createItem": {
                "item": {
                    "title": q["question"],
                    "questionItem": {
                        "question": {
                            "required": True,
                        }
                    }
                },
                "location": {
                    "index": 0
                }
            }
        }

        if q["type"] == "input":
            item["createItem"]["item"]["questionItem"]["question"]["textQuestion"] = {}
        elif q["type"] == "textarea":
            item["createItem"]["item"]["questionItem"]["question"]["textQuestion"] = {
                "paragraph": True
            }
        elif q["type"] == "select" and q["options"]:
            item["createItem"]["item"]["questionItem"]["question"]["choiceQuestion"] = {
                "type": "DROP_DOWN",
                "options": [{"value": opt} for opt in q["options"]]
            }
        
        requests_list.append(item)

    if requests_list:
        batch_update_request = {
            "requests": requests_list
        }
        service.forms().batchUpdate(formId=form_id, body=batch_update_request).execute()
    return created_form['responderUri']  # Public link to the form


def apply(request, grant_name):
    decoded_grant_name = urllib.parse.unquote(grant_name)
    if decoded_grant_name not in grants:
        return render(request, 'grants/grants_list.html', {'error': 'Grant not found.', 'grants': grants})

    original_form_url = grants[decoded_grant_name]

    try:
        # Step 1: Scrape
        questions = scrape_form(original_form_url)
        
        # Step 2: Create Google Form
        service = authenticate_google_forms()
        google_form_link = create_google_form(service, decoded_grant_name, questions)

        # Step 3: Redirect
        return redirect(google_form_link)

    except Exception as e:
        return render(request, 'grants/grants_list.html', {'error': f"Error: {str(e)}", 'grants': grants})
