# importações necessárias do Django
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .models import Personagem

# página inicial — verifica se o usuário está logado e redireciona
def index(request):
    # verifica se o usuário está logado
    if request.user.is_authenticated:
        # busca todos os personagens do usuário
        personagens = Personagem.objects.filter(usuario=request.user)
        # se tiver personagens, vai para seleção
        if personagens.exists():
            return redirect('selecionar_personagem')
        # se não tiver, vai para criar personagem
        return redirect('criar_personagem')
    # se não estiver logado, vai para o login
    return redirect('login')


# página de cadastro de novo usuário
def cadastro(request):
    # se o formulário foi enviado
    if request.method == 'POST':
        # pega os dados do formulário
        usuario = request.POST['usuario']
        senha = request.POST['senha']
        # verifica se o usuário já existe
        if User.objects.filter(username=usuario).exists():
            # retorna erro se já existir
            return render(request, 'game/cadastro.html', {'erro': 'Usuário já existe!'})
        # cria o usuário no banco
        User.objects.create_user(username=usuario, password=senha)
        # redireciona para o login
        return redirect('login')
    # se não foi enviado, mostra o formulário vazio
    return render(request, 'game/cadastro.html')


# página de login
def login_view(request):
    # se o formulário foi enviado
    if request.method == 'POST':
        # pega os dados do formulário
        usuario = request.POST['usuario']
        senha = request.POST['senha']
        # verifica se o usuário e senha estão corretos
        user = authenticate(request, username=usuario, password=senha)
        # se estiver correto
        if user:
            # registra o login na sessão
            login(request, user)
            # verifica se já tem personagens
            personagens = Personagem.objects.filter(usuario=user)
            if personagens.exists():
                # se tiver, vai para seleção de personagem
                return redirect('selecionar_personagem')
            # se não tiver, vai para criar personagem
            return redirect('criar_personagem')
    # se não foi enviado, mostra o formulário vazio
    return render(request, 'game/login.html')


# página de logout — encerra a sessão
def logout_view(request):
    logout(request)
    return redirect('login')


# página de criação de personagem
def criar_personagem(request):
 # se o formulário foi enviado
    if request.method == 'POST':
        # pega os dados do formulário
        nome = request.POST['nome']
        classe = request.POST['classe']
        # atributos iniciais de cada classe
        ATRIBUTOS = {
            'guerreiro': {'hp': 150, 'mp': 20, 'ataque': 15, 'defesa': 10},
            'mago':      {'hp': 70,  'mp': 100,'ataque': 8,  'defesa': 3},
            'ladrao':    {'hp': 90,  'mp': 40, 'ataque': 12, 'defesa': 6},
            'arqueiro':  {'hp': 100, 'mp': 30, 'ataque': 13, 'defesa': 5},
        }
        # pega os atributos da classe escolhida
        atributos = ATRIBUTOS[classe]
        # cria o personagem no banco com os atributos da classe
        Personagem.objects.create(
            usuario=request.user,     # vincula ao usuário logado
            nome=nome,                # nome escolhido
            classe=classe,            # classe escolhida
            hp_maximo=atributos['hp'],
            hp_atual=atributos['hp'],
            mp_maximo=atributos['mp'],
            mp_atual=atributos['mp'],
            ataque=atributos['ataque'],
            defesa=atributos['defesa'],
        )
        # redireciona para o mapa após criar
        return redirect('mundo')
    # se não foi enviado, mostra o formulário vazio
    return render(request, 'game/criar_personagem.html')


# página de seleção de personagem
def selecionar_personagem(request):
    # busca todos os personagens do usuário logado
    personagens = Personagem.objects.filter(usuario=request.user)
    return render(request, 'game/selecionar_personagem.html', {'personagens': personagens})


# página que registra qual personagem foi escolhido
def entrar_personagem(request, personagem_id):
    personagem = Personagem.objects.get(id=personagem_id, usuario=request.user)
    request.session['personagem_id'] = personagem_id
    # redireciona para o mapa mundo após selecionar personagem
    return redirect('mundo')


# página do mapa — mostra as áreas disponíveis
def mapa(request):
    # pega o id do personagem salvo na sessão
    personagem_id = request.session.get('personagem_id')
    # se não tiver personagem selecionado, manda selecionar
    if not personagem_id:
        return redirect('selecionar_personagem')
    # busca o personagem no banco
    personagem = Personagem.objects.get(id=personagem_id)
    return render(request, 'game/mapa.html', {'personagem': personagem})


# página da vila — lobby de cada área
def vila(request, area):
    # pega o id do personagem salvo na sessão
    personagem_id = request.session.get('personagem_id')
    # se não tiver personagem selecionado, manda selecionar
    if not personagem_id:
        return redirect('selecionar_personagem')
    # busca o personagem no banco pelo id
    personagem = Personagem.objects.get(id=personagem_id)
    # checkpoint — salva o ouro atual caso o personagem morra
    personagem.gold_salvo = personagem.gold
    # atualiza a área atual do personagem
    personagem.area_atual = area
    # reseta as batalhas ao entrar na vila
    personagem.batalhas_na_area = 0
    # reseta as fugas disponíveis
    personagem.fugas_restantes = 2
    # salva tudo no banco
    personagem.save()
    return render(request, 'game/vila.html', {'personagem': personagem, 'area': area})

# página do mapa mundo — mostra os reinos disponíveis
def mundo(request):
    # pega o id do personagem salvo na sessão
    personagem_id = request.session.get('personagem_id')
    # se não tiver personagem selecionado, manda selecionar
    if not personagem_id:
        return redirect('selecionar_personagem')
    # busca o personagem no banco
    personagem = Personagem.objects.get(id=personagem_id)
    return render(request, 'game/mundo.html', {'personagem': personagem})