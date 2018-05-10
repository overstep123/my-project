from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login,logout

# Create your views here.

def index(req):
    t = 'ABVC'
    return render(req, 'index.html', {'t': t})


def user_index(req):
    username = req.user.username
    return render(req,'user_index.html',{'username':username})

def signup(req):
    if req.method == 'POST':
        form = UserCreationForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect('/signup')
    else:
        form = UserCreationForm()
    return render(req, 'signup.html', {'form': form})


def log_in(req):
    if req.method == 'POST':
        form = AuthenticationForm(req.POST)
        if form.is_valid():
            user = form.get_user()
            login(req, user)
            return redirect('/user_index')
    else:
        form = AuthenticationForm()
    return render(req,'login.html',{'form':form})

def log_out(req):
    if req.method == 'POST':
        logout(req)
        return redirect('/login')