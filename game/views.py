from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .models import Personagem

def index(request):
    if request.user.is_authenticated:
        return redirect('criar_personagem')
    return redirect('login')

def cadastro(request):
    if request.method == 'POST':
        usuario = request.POST['usuario']
        senha = request.POST['senha']
        if User.objects.filter(username=usuario).exists():
            return render(request, 'game/cadastro.html', {'erro': 'Usuário já existe!'})
        User.objects.create_user(username=usuario, password=senha)
        return redirect('login')
    return render(request, 'game/cadastro.html')

def login_view(request):
    if request.method == 'POST':
        usuario = request.POST['usuario']
        senha = request.POST['senha']
        user = authenticate(request, username=usuario, password=senha)
        if user:
            login(request, user)
            return redirect('criar_personagem')
    return render(request, 'game/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def criar_personagem(request):
    return render(request, 'game/criar_personagem.html')