from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .models import Personagem

def index(request):
    if request.user.is_authenticated:
        personagens = Personagem.objects.filter(usuario=request.user)
        if personagens.exists():
            return redirect('selecionar_personagem')
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
            personagens = Personagem.objects.filter(usuario=user)
            if personagens.exists():
                return redirect('selecionar_personagem')
            return redirect('criar_personagem')
    return render(request, 'game/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def criar_personagem(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        classe = request.POST['classe']
        
        ATRIBUTOS = {
            'guerreiro': {'hp': 150, 'mp': 20, 'ataque': 15, 'defesa': 10},
            'mago':      {'hp': 70,  'mp': 100,'ataque': 8,  'defesa': 3},
            'ladrao':    {'hp': 90,  'mp': 40, 'ataque': 12, 'defesa': 6},
            'arqueiro':  {'hp': 100, 'mp': 30, 'ataque': 13, 'defesa': 5},
        }
        
        atributos = ATRIBUTOS[classe]
        
        Personagem.objects.create(
            usuario=request.user,
            nome=nome,
            classe=classe,
            hp_maximo=atributos['hp'],
            hp_atual=atributos['hp'],
            mp_maximo=atributos['mp'],
            mp_atual=atributos['mp'],
            ataque=atributos['ataque'],
            defesa=atributos['defesa'],
        )
        return redirect('mapa')
    return render(request, 'game/criar_personagem.html')

def mapa(request):
    personagem_id = request.session.get('personagem_id')
    if not personagem_id:
        return redirect('selecionar_personagem')
    personagem = Personagem.objects.get(id=personagem_id)
    return render(request, 'game/mapa.html', {'personagem': personagem})

def selecionar_personagem(request):
    personagens = Personagem.objects.filter(usuario=request.user)
    return render(request, 'game/selecionar_personagem.html', {'personagens': personagens})

def entrar_personagem(request, personagem_id):
    personagem = Personagem.objects.get(id=personagem_id, usuario=request.user)
    request.session['personagem_id'] = personagem_id
    return redirect('mapa')

def vila(request, area):
    personagem_id = request.session.get('personagem_id')
    if not personagem_id:
        return redirect('selecionar_personagem')
    personagem = Personagem.objects.get(id=personagem_id)
    return render(request, 'game/vila.html', {'personagem': personagem, 'area': area})