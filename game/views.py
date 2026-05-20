# importações necessárias do Django
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .models import Personagem, Item, Inventario, Batalha, Inimigo
from django.shortcuts import get_object_or_404
import random


# página inicial — verifica se o usuário está logado e redireciona
def index(request):
    if request.user.is_authenticated:
        personagens = Personagem.objects.filter(usuario=request.user)
        if personagens.exists():
            return redirect('selecionar_personagem')
        return redirect('criar_personagem')
    return redirect('login')


# página de cadastro de novo usuário
def cadastro(request):
    if request.method == 'POST':
        usuario = request.POST['usuario']
        senha = request.POST['senha']
        if User.objects.filter(username=usuario).exists():
            return render(request, 'game/cadastro.html', {'erro': 'Usuário já existe!'})
        User.objects.create_user(username=usuario, password=senha)
        return redirect('login')
    return render(request, 'game/cadastro.html')


# página de login
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


# página de logout — encerra a sessão
def logout_view(request):
    logout(request)
    return redirect('login')


# página de criação de personagem
def criar_personagem(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        classe = request.POST['classe']
        ATRIBUTOS = {
            'guerreiro': {'hp': 150, 'mp': 20,  'ataque': 15, 'defesa': 10},
            'mago':      {'hp': 70,  'mp': 100, 'ataque': 8,  'defesa': 3},
            'ladrao':    {'hp': 90,  'mp': 40,  'ataque': 12, 'defesa': 6},
            'arqueiro':  {'hp': 100, 'mp': 30,  'ataque': 13, 'defesa': 5},
        }
        atributos = ATRIBUTOS[classe]
        personagem = Personagem.objects.create(
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
        request.session['personagem_id'] = int(personagem.id)
        request.session.modified = True
        return redirect('mundo')
    return render(request, 'game/criar_personagem.html')


# página de seleção de personagem
def selecionar_personagem(request):
    personagens = Personagem.objects.filter(usuario=request.user)
    return render(request, 'game/selecionar_personagem.html', {'personagens': personagens})


# registra qual personagem foi escolhido
def entrar_personagem(request, personagem_id):
    personagem = Personagem.objects.get(id=personagem_id, usuario=request.user)
    request.session['personagem_id'] = int(personagem_id)
    request.session.modified = True
    return redirect('mundo')


# página do mapa — mostra as áreas disponíveis
def mapa(request):
    personagem_id = request.session.get('personagem_id')
    if not personagem_id:
        return redirect('selecionar_personagem')
    personagem = Personagem.objects.get(id=personagem_id)
    return render(request, 'game/mapa.html', {'personagem': personagem})


# página da vila — lobby de cada área
def vila(request, area):
    personagem_id = request.session.get('personagem_id')
    if not personagem_id:
        return redirect('selecionar_personagem')
    personagem = Personagem.objects.get(id=personagem_id)
    personagem.gold_salvo = personagem.gold
    personagem.area_atual = area
    personagem.batalhas_na_area = 0
    personagem.fugas_restantes = 2
    personagem.save()
    return render(request, 'game/vila.html', {'personagem': personagem, 'area': area})


# página do mapa mundo — mostra os reinos disponíveis
def mundo(request):
    personagem_id = request.session.get('personagem_id')
    if not personagem_id:
        return redirect('selecionar_personagem')
    personagem = Personagem.objects.get(id=personagem_id)
    return render(request, 'game/mundo.html', {'personagem': personagem})


# página da loja
def loja(request):
    personagem_id = request.session.get('personagem_id')
    if not personagem_id:
        return redirect('selecionar_personagem')
    personagem = Personagem.objects.get(id=personagem_id)
    armas = Item.objects.filter(tipo='arma', classes_permitidas__contains=personagem.classe)
    armaduras = Item.objects.filter(tipo='armadura', classes_permitidas__contains=personagem.classe)
    consumiveis = Item.objects.filter(tipo='consumivel', classes_permitidas__contains=personagem.classe)
    inventario = Inventario.objects.filter(personagem=personagem)
    return render(request, 'game/loja.html', {
        'personagem': personagem,
        'armas': armas,
        'armaduras': armaduras,
        'consumiveis': consumiveis,
        'inventario': inventario,
    })


# ação de comprar item
def comprar_item(request, item_id):
    personagem_id = request.session.get('personagem_id')
    personagem = Personagem.objects.get(id=personagem_id)
    item = Item.objects.get(id=item_id)
    if personagem.gold < item.preco:
        return redirect('loja')
    personagem.gold -= item.preco
    personagem.save()
    inventario_item = Inventario.objects.filter(personagem=personagem, item=item).first()
    if inventario_item:
        inventario_item.qtd += 1
        inventario_item.save()
    else:
        Inventario.objects.create(personagem=personagem, item=item, qtd=1)
    return redirect('loja')


# ação de vender item
def vender_item(request, item_id):
    personagem_id = request.session.get('personagem_id')
    personagem = Personagem.objects.get(id=personagem_id)
    item = Item.objects.get(id=item_id)
    inventario_item = Inventario.objects.filter(personagem=personagem, item=item).first()
    if inventario_item:
        personagem.gold += item.preco // 2
        personagem.save()
        if inventario_item.qtd > 1:
            inventario_item.qtd -= 1
            inventario_item.save()
        else:
            inventario_item.delete()
    return redirect('loja')


# verifica e aplica o level up do personagem
def verificar_level_up(personagem):
    xp_necessario = personagem.nivel * 100 + (personagem.nivel - 1) * 50
    if personagem.experiencia >= xp_necessario:
        personagem.nivel += 1
        GANHOS = {
            'guerreiro': {'hp': 20, 'mp': 5,  'ataque': 3, 'defesa': 3},
            'mago':      {'hp': 10, 'mp': 20, 'ataque': 2, 'defesa': 1},
            'ladrao':    {'hp': 15, 'mp': 8,  'ataque': 3, 'defesa': 2},
            'arqueiro':  {'hp': 15, 'mp': 8,  'ataque': 3, 'defesa': 2},
        }
        ganhos = GANHOS[personagem.classe]
        personagem.hp_maximo += ganhos['hp']
        personagem.hp_atual += ganhos['hp']
        personagem.mp_maximo += ganhos['mp']
        personagem.mp_atual += ganhos['mp']
        personagem.ataque += ganhos['ataque']
        personagem.defesa += ganhos['defesa']
        personagem.save()
        return True
    return False


# inicia uma nova batalha sorteando um inimigo da área
def iniciar_batalha(request):
    personagem_id = request.session.get('personagem_id')
    if not personagem_id:
        return redirect('selecionar_personagem')
    personagem = Personagem.objects.get(id=personagem_id)

    if personagem.batalhas_na_area >= 5:
        return redirect('vila', area=personagem.area_atual)

    # batalha 5 é sempre o boss
    if personagem.batalhas_na_area == 4:
        inimigo = Inimigo.objects.filter(area=personagem.area_atual, is_boss=True).first()
        quantidade = 1
    else:
        # sorteia inimigo com peso
        inimigos = list(Inimigo.objects.filter(area=personagem.area_atual, is_boss=False))
        pesos = [i.peso for i in inimigos]
        inimigo = random.choices(inimigos, weights=pesos, k=1)[0]
        # sorteia quantidade com peso decrescente (1 mais comum que 2, etc)
        quantidade_opcoes = list(range(inimigo.qtd_min, inimigo.qtd_max + 1))
        pesos_qtd = [1 / q for q in quantidade_opcoes]
        quantidade = random.choices(quantidade_opcoes, weights=pesos_qtd, k=1)[0]

    # hp total da horda
    inimigo_hp_max = inimigo.hp * quantidade

    # salva sessão
    request.session['batalha'] = {
        'inimigo_id': inimigo.id,
        'inimigo_hp': inimigo_hp_max,
        'inimigo_hp_max': inimigo_hp_max,
        'quantidade': quantidade,
        'defendendo': False,
    }

    return render(request, 'game/batalha.html', {
        'personagem': personagem,
        'inimigo': inimigo,
        'inimigo_hp': inimigo_hp_max,
        'inimigo_hp_max': inimigo_hp_max,
        'quantidade': quantidade,
        'mensagem': f'{"Uma horda de " + str(quantidade) + "x " if quantidade > 1 else "Um "}{inimigo.nome} apareceu!',
        'inventario': Inventario.objects.filter(personagem=personagem),
    })


# processa a ação do jogador no turno
def acao_batalha(request):
    if request.method != 'POST':
        return redirect('iniciar_batalha')

    personagem_id = request.session.get('personagem_id')
    personagem = Personagem.objects.get(id=personagem_id)
    batalha = request.session.get('batalha')
    inimigo = Inimigo.objects.get(id=batalha['inimigo_id'])
    inimigo_hp = batalha['inimigo_hp']
    inimigo_hp_max = batalha.get('inimigo_hp_max', inimigo.hp)
    quantidade = batalha.get('quantidade', 1)

    acao = request.POST.get('acao')
    mensagem = ''

    # --- AÇÃO: ATACAR ---
    if acao == 'atacar':
        ataque_real = personagem.ataque + (personagem.arma_equipada.bonus_ataque if personagem.arma_equipada else 0)
        dano = max(1, ataque_real - inimigo.defesa)
        inimigo_hp -= dano
        mensagem = f'Você causou {dano} de dano ao {inimigo.nome}!'

    # --- AÇÃO: DEFENDER ---
    elif acao == 'defender':
        batalha['defendendo'] = True
        mensagem = 'Você assume postura defensiva!'

    # --- AÇÃO: FUGIR ---
    elif acao == 'fugir':
        if inimigo.is_boss:
            mensagem = 'Não é possível fugir de um boss!'
        elif personagem.fugas_restantes <= 0:
            mensagem = 'Você não tem mais fugas disponíveis!'
        else:
            if random.random() < 0.7:
                personagem.gold = int(personagem.gold * 0.9)
                personagem.fugas_restantes -= 1
                personagem.save()
                b = Batalha()
                b.personagem = personagem
                b.inimigo = inimigo
                b.resultado = 'fuga'
                b.save()
                request.session['resultado'] = {
                    'resultado': 'fuga',
                    'inimigo_nome': inimigo.nome,
                }
                return redirect('resultado_batalha')
            else:
                personagem.fugas_restantes -= 1
                personagem.save()
                mensagem = 'Fuga falhou! O inimigo bloqueou sua saída!'

    # --- INIMIGO ATACA ---
    if inimigo_hp > 0:
        defesa_base = personagem.defesa + (personagem.armadura_equipada.bonus_defesa if personagem.armadura_equipada else 0)
        defesa_atual = int(defesa_base * 1.3) if batalha['defendendo'] else defesa_base
        # fator de horda — cada inimigo adicional contribui 70% do dano
        fator_horda = 1 + (quantidade - 1) * 0.7
        dano_inimigo = max(1, int((inimigo.ataque - defesa_atual) * fator_horda))
        personagem.hp_atual -= dano_inimigo
        mensagem += f' {inimigo.nome} causou {dano_inimigo} de dano em você!'
    batalha['defendendo'] = False

    # --- INIMIGO MORREU ---
    if inimigo_hp <= 0:
        personagem.experiencia += inimigo.experiencia * quantidade
        personagem.gold += inimigo.gold * quantidade
        personagem.batalhas_na_area += 1
        personagem.save()

        subiu_nivel = verificar_level_up(personagem)

        area_desbloqueada = False
        proxima = None
        if inimigo.is_boss:
            PROXIMA_AREA = {
                'floresta': 'caverna',
                'caverna': 'castelo',
                'castelo': None,
            }
            proxima = PROXIMA_AREA.get(personagem.area_atual)
            if proxima and personagem.area_desbloqueada == personagem.area_atual:
                personagem.area_desbloqueada = proxima
                personagem.save()
                area_desbloqueada = True

        b = Batalha()
        b.personagem = personagem
        b.inimigo = inimigo
        b.resultado = 'vitoria'
        b.save()

        request.session['resultado'] = {
            'resultado': 'vitoria',
            'inimigo_nome': inimigo.nome,
            'exp_ganho': inimigo.experiencia * quantidade,
            'gold_ganho': inimigo.gold * quantidade,
            'subiu_nivel': subiu_nivel,
            'nivel_atual': personagem.nivel,
            'area_desbloqueada': area_desbloqueada,
            'proxima_area': proxima if inimigo.is_boss else None,
        }
        return redirect('resultado_batalha')

    # --- PERSONAGEM MORREU ---
    if personagem.hp_atual <= 0:
        personagem.gold = personagem.gold_salvo
        personagem.hp_atual = personagem.hp_maximo
        personagem.save()
        b = Batalha()
        b.personagem = personagem
        b.inimigo = inimigo
        b.resultado = 'derrota'
        b.save()
        request.session['resultado'] = {
            'resultado': 'derrota',
            'inimigo_nome': inimigo.nome,
        }
        return redirect('resultado_batalha')

    # atualiza sessão
    batalha['inimigo_hp'] = inimigo_hp
    request.session['batalha'] = batalha
    personagem.save()

    return render(request, 'game/batalha.html', {
        'personagem': personagem,
        'inimigo': inimigo,
        'inimigo_hp': inimigo_hp,
        'inimigo_hp_max': inimigo_hp_max,
        'quantidade': quantidade,
        'mensagem': mensagem,
        'inventario': Inventario.objects.filter(personagem=personagem),
    })


# usa um item consumível durante a batalha
def usar_item_batalha(request, item_id):
    if request.method != 'POST':
        return redirect('iniciar_batalha')

    personagem_id = request.session.get('personagem_id')
    personagem = Personagem.objects.get(id=personagem_id)
    batalha = request.session.get('batalha')
    inimigo = Inimigo.objects.get(id=batalha['inimigo_id'])
    inimigo_hp = batalha['inimigo_hp']
    inimigo_hp_max = batalha.get('inimigo_hp_max', inimigo.hp)
    quantidade = batalha.get('quantidade', 1)

    inventario_item = Inventario.objects.filter(personagem=personagem, item__id=item_id, item__tipo='consumivel').first()

    if inventario_item:
        item = inventario_item.item
        personagem.hp_atual = min(personagem.hp_maximo, personagem.hp_atual + item.bonus_hp)
        personagem.mp_atual = min(personagem.mp_maximo, personagem.mp_atual + item.bonus_mp)
        mensagem = f'Você usou {item.nome}!'
        if item.bonus_hp > 0:
            mensagem += f' +{item.bonus_hp} HP'
        if item.bonus_mp > 0:
            mensagem += f' +{item.bonus_mp} MP'
        if inventario_item.qtd > 1:
            inventario_item.qtd -= 1
            inventario_item.save()
        else:
            inventario_item.delete()
    else:
        mensagem = 'Item não encontrado no inventário!'

    # inimigo ataca
    if inimigo_hp > 0:
        defesa_real = personagem.defesa + (personagem.armadura_equipada.bonus_defesa if personagem.armadura_equipada else 0)
        fator_horda = 1 + (quantidade - 1) * 0.7
        dano_inimigo = max(1, int((inimigo.ataque - defesa_real) * fator_horda))
        personagem.hp_atual -= dano_inimigo
        mensagem += f' {inimigo.nome} causou {dano_inimigo} de dano em você!'

    # personagem morreu
    if personagem.hp_atual <= 0:
        personagem.gold = personagem.gold_salvo
        personagem.hp_atual = personagem.hp_maximo
        personagem.batalhas_na_area = 0
        personagem.fugas_restantes = 2
        personagem.save()
        b = Batalha(personagem=personagem, inimigo=inimigo, resultado='derrota')
        b.save()
        request.session['resultado'] = {
            'resultado': 'derrota',
            'inimigo_nome': inimigo.nome,
        }
        return redirect('resultado_batalha')

    batalha['inimigo_hp'] = inimigo_hp
    request.session['batalha'] = batalha
    personagem.save()

    inventario = Inventario.objects.filter(personagem=personagem)

    return render(request, 'game/batalha.html', {
        'personagem': personagem,
        'inimigo': inimigo,
        'inimigo_hp': inimigo_hp,
        'inimigo_hp_max': inimigo_hp_max,
        'quantidade': quantidade,
        'mensagem': mensagem,
        'inventario': inventario,
    })


# mostra o resultado final da batalha
def resultado_batalha(request):
    personagem_id = request.session.get('personagem_id')
    personagem = Personagem.objects.get(id=personagem_id)
    resultado = request.session.get('resultado', {})
    return render(request, 'game/resultado_batalha.html', {
        'personagem': personagem,
        'resultado': resultado,
    })


# página de inventário do personagem
def inventario(request):
    personagem_id = request.session.get('personagem_id')
    if not personagem_id:
        return redirect('selecionar_personagem')
    personagem = Personagem.objects.get(id=personagem_id)
    armas = Inventario.objects.filter(personagem=personagem, item__tipo='arma')
    armaduras = Inventario.objects.filter(personagem=personagem, item__tipo='armadura')
    consumiveis = Inventario.objects.filter(personagem=personagem, item__tipo='consumivel')
    ataque_real = personagem.ataque + (personagem.arma_equipada.bonus_ataque if personagem.arma_equipada else 0)
    defesa_real = personagem.defesa + (personagem.armadura_equipada.bonus_defesa if personagem.armadura_equipada else 0)
    return render(request, 'game/inventario.html', {
        'personagem': personagem,
        'armas': armas,
        'armaduras': armaduras,
        'consumiveis': consumiveis,
        'ataque_real': ataque_real,
        'defesa_real': defesa_real,
    })


# equipa ou desequipa um item
def equipar_item(request, item_id):
    personagem_id = request.session.get('personagem_id')
    personagem = Personagem.objects.get(id=personagem_id)
    item = Item.objects.get(id=item_id)
    if not Inventario.objects.filter(personagem=personagem, item=item).exists():
        return redirect('inventario')
    if item.tipo == 'arma':
        personagem.arma_equipada = None if personagem.arma_equipada == item else item
    elif item.tipo == 'armadura':
        personagem.armadura_equipada = None if personagem.armadura_equipada == item else item
    personagem.save()
    return redirect('inventario')


# deleta um personagem do usuário logado
def deletar_personagem(request, personagem_id):
    if request.method == 'POST':
        personagem = get_object_or_404(Personagem, id=personagem_id, usuario=request.user)
        if request.session.get('personagem_id') == int(personagem_id):
            del request.session['personagem_id']
        personagem.delete()
    return redirect('selecionar_personagem')