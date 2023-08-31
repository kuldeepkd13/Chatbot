from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User,auth

# Create your views here.

def home(request):
    return render(request, 'home.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Logged in successfully.', extra_tags='success')
            return redirect('home')
        else:
            # Check if the username exists in the database
            if auth.models.User.objects.filter(username=username).exists():
                messages.error(request, 'Invalid password for the provided username.', extra_tags='error')
            else:
                messages.error(request, 'Invalid username or password.', extra_tags='error')
            return redirect('login')
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.', extra_tags='error')
                return redirect('register')
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                user.save()
                messages.success(request, 'User registered successfully.', extra_tags='success')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.', extra_tags='error')
            return redirect('register')
    else:
        return render(request, 'signup.html')
    

def logout_user(request):
    username = request.user.username  # Get the username of the logged-out user
    auth.logout(request)
    messages.success(request, f"Thanks, {username}, for visiting our website!", extra_tags='success')
    return redirect('home')