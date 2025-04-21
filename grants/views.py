# grants/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Grant
from datetime import datetime, timedelta

def home(request):
    return render(request, 'grants/home.html')

# grants/views.py (relevant snippet)
def grants_list(request):
    grants = Grant.objects.all()
    today = datetime.today().date()
    
    for grant in grants:
        days_until_deadline = (grant.deadline - today).days
        if days_until_deadline <= 7:
            grant.deadline_status = 'red'
        elif days_until_deadline <= 30:
            grant.deadline_status = 'orange'
        else:
            grant.deadline_status = 'green'
    
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

# ... (other views remain unchanged)