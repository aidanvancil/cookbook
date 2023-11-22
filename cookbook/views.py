from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as log, logout as auth_logout

def errors(request):
    context = {
        'error': 404
    }
    return render(request, 'errors.html', context)

def master(request):
    context = {
        
    }
    return render(request, 'master.html', context)

def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        context = {
            
        }

        return render(request, 'signup.html', context)

    context = {
        
    }

    return render(request, 'signup.html', context)


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:    
            log(request, user)
            return redirect('home')
        else:
            error_message = "Username or password is incorrect."
            context = {
                'error_message': error_message,
            }
            
            return render(request, 'login.html', context)
    
    
    context = {
        
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
