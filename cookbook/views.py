from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as log, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms

def errors(request):
    context = {
        'error': 404
    }
    return render(request, 'errors.html', context)
class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'password': forms.PasswordInput(),
        }

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            log(request, user)
            return redirect('home')
    else:
        form = SignUpForm()

    context = {
        'form': form,
    }
    return render(request, 'signup.html', context)


class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

def login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            log(request, user)
            return redirect('home')
    else:
        form = LoginForm()

    context = {
        'form': form,
    }
    return render(request, 'login.html', context)

@login_required(login_url='login')
def logout(request):
    auth_logout(request)
    return redirect('login')

@login_required(login_url='login')
def home(request):
    context = {

    }
    return render(request, 'home.html', context)

@login_required(login_url='login')
def bookmarks(request):
    context = {

    }
    return render(request, 'bookmarks.html', context)
