# importações necessárias do Django
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .models import Personagem, Item, Inventario, Batalha, Inimigo
from django.shortcuts import get_object_or_404
import random

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
        # cria o personagem no banco e guarda o objeto retornado
        # (antes era só Personagem.objects.create(...) sem salvar o retorno)
        personagem = Personagem.objects.create(
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
        # salva o id do novo personagem na sessão imediatamente
        # força int para evitar conflito de tipo entre string e int na sessão
        request.session['personagem_id'] = int(personagem.id)
        # marca a sessão como modificada para garantir que o Django salve
        request.session.modified = True
        # redireciona para o mundo já com o novo personagem ativo
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
    # busca o personagem garantindo que pertence ao usuário logado
    personagem = Personagem.objects.get(id=personagem_id, usuario=request.user)
    # força int para evitar conflito de tipo na sessão
    # (a URL entrega string, mas a sessão pode comparar com int — causando bug)
    request.session['personagem_id'] = int(personagem_id)
    # marca a sessão como modificada para garantir que o Django salve
    request.session.modified = True
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

# página da loja — mostra itens para comprar e vender
def loja(request):
    # pega o id do personagem salvo na sessão
    personagem_id = request.session.get('personagem_id')
    # se não tiver personagem selecionado, manda selecionar
    if not personagem_id:
        return redirect('selecionar_personagem')
    # busca o personagem no banco
    personagem = Personagem.objects.get(id=personagem_id)
    # busca itens disponíveis para a classe do personagem
    armas = Item.objects.filter(tipo='arma', classes_permitidas__contains=personagem.classe)
    armaduras = Item.objects.filter(tipo='armadura', classes_permitidas__contains=personagem.classe)
    consumiveis = Item.objects.filter(tipo='consumivel', classes_permitidas__contains=personagem.classe)
    
    # busca o inventário do personagem
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
    # pega o personagem da sessão
    personagem_id = request.session.get('personagem_id')
    personagem = Personagem.objects.get(id=personagem_id)
    # busca o item pelo id
    item = Item.objects.get(id=item_id)
    
    # verifica se tem gold suficiente
    if personagem.gold < item.preco:
        return redirect('loja')
    
    # subtrai o gold do personagem
    personagem.gold -= item.preco
    personagem.save()
    
    # verifica se o item já está no inventário
    inventario_item = Inventario.objects.filter(personagem=personagem, item=item).first()
    if inventario_item:
        # se já tiver, aumenta a quantidade
        inventario_item.qtd += 1
        inventario_item.save()
    else:
        # se não tiver, cria novo registro
        Inventario.objects.create(personagem=personagem, item=item, qtd=1)
    
    return redirect('loja')


# ação de vender item
def vender_item(request, item_id):
    # pega o personagem da sessão
    personagem_id = request.session.get('personagem_id')
    personagem = Personagem.objects.get(id=personagem_id)
    # busca o item no inventário
    item = Item.objects.get(id=item_id)
    inventario_item = Inventario.objects.filter(personagem=personagem, item=item).first()
    
    # se tiver o item no inventário
    if inventario_item:
        # adiciona metade do preço ao gold (venda por metade do valor)
        personagem.gold += item.preco // 2
        personagem.save()
        
        # se tiver mais de 1, diminui a quantidade
        if inventario_item.qtd > 1:
            inventario_item.qtd -= 1
            inventario_item.save()
        else:
            # se tiver só 1, remove do inventário
            inventario_item.delete()
    
    return redirect('loja')

# verifica e aplica o level up do personagem
def verificar_level_up(personagem):
    # xp necessário para cada nível
    xp_necessario = personagem.nivel * 100 + (personagem.nivel - 1) * 50
    
    # verifica se tem xp suficiente
    if personagem.experiencia >= xp_necessario:
        # sobe de nível
        personagem.nivel += 1
        
        # ganhos por classe ao subir de nível
        GANHOS = {
            'guerreiro': {'hp': 20, 'mp': 5,  'ataque': 3, 'defesa': 3},
            'mago':      {'hp': 10, 'mp': 20, 'ataque': 2, 'defesa': 1},
            'ladrao':    {'hp': 15, 'mp': 8,  'ataque': 3, 'defesa': 2},
            'arqueiro':  {'hp': 15, 'mp': 8,  'ataque': 3, 'defesa': 2},
        }
        
        ganhos = GANHOS[personagem.classe]
        
        # aplica os ganhos
        personagem.hp_maximo += ganhos['hp']
        personagem.hp_atual += ganhos['hp']  # cura ao subir de nível
        personagem.mp_maximo += ganhos['mp']
        personagem.mp_atual += ganhos['mp']
        personagem.ataque += ganhos['ataque']
        personagem.defesa += ganhos['defesa']
        personagem.save()
        
        # retorna True para avisar que subiu de nível
        return True
    return False
# inicia uma nova batalha sorteando um inimigo da área
def iniciar_batalha(request):
    # pega o personagem da sessão
    personagem_id = request.session.get('personagem_id')
    if not personagem_id:
        return redirect('selecionar_personagem')
    personagem = Personagem.objects.get(id=personagem_id)
    
    # verifica quantas batalhas já fez na área
    if personagem.batalhas_na_area >= 5:
        return redirect('vila', area=personagem.area_atual)
    
    # batalha 5 é sempre o boss
    if personagem.batalhas_na_area == 4:
        inimigo = Inimigo.objects.filter(area=personagem.area_atual, is_boss=True).first()
        quantidade = 1
    else:
        # sorteia um inimigo normal da área com peso
        inimigos = list(Inimigo.objects.filter(area=personagem.area_atual, is_boss=False))
        pesos = [i.peso for i in inimigos]
        inimigo = random.choices(inimigos, weights=pesos, k=1)[0]
        
        # sorteia quantidade com peso decrescente (1 é mais comum que 2, que é mais comum que 3)
        quantidade_opcoes = list(range(inimigo.qtd_min, inimigo.qtd_max + 1))
        pesos_qtd = [1 / q for q in quantidade_opcoes]
        quantidade = random.choices(quantidade_opcoes, weights=pesos_qtd, k=1)[0]

    # salva sessão (vale pra boss e inimigo normal)
    request.session['batalha'] = {
        'inimigo_id': inimigo.id,
        'inimigo_hp': inimigo.hp * quantidade,
        'quantidade': quantidade,
        'defendendo': False,
    }
    
    return render(request, 'game/batalha.html', {
        'personagem': personagem,
        'inimigo': inimigo,
        'inimigo_hp': inimigo.hp * quantidade,
        'quantidade': quantidade,
        'mensagem': f'{"Uma horda de " + str(quantidade) + "x " if quantidade > 1 else "Um "}{inimigo.nome} apareceu!',
        'inventario': Inventario.objects.filter(personagem=personagem),
    })


# processa a ação do jogador no turno
def acao_batalha(request):
    if request.method != 'POST':
        return redirect('iniciar_batalha')
    
    # pega o personagem e o estado da batalha
    personagem_id = request.session.get('personagem_id')
    personagem = Personagem.objects.get(id=personagem_id)
    batalha = request.session.get('batalha')
    inimigo = Inimigo.objects.get(id=batalha['inimigo_id'])
    inimigo_hp = batalha['inimigo_hp']
    quantidade = batalha.get('quantidade', 1)
    
    # pega a ação escolhida pelo jogador
    acao = request.POST.get('acao')
    mensagem = ''
    
    # --- AÇÃO: ATACAR ---
    if acao == 'atacar':
        # calcula ataque real somando bônus da arma equipada
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
        # boss não pode fugir
        if inimigo.is_boss:
            mensagem = 'Não é possível fugir de um boss!'
        elif personagem.fugas_restantes <= 0:
            mensagem = 'Você não tem mais fugas disponíveis!'
        else:
            # 70% de chance de fugir
            if random.random() < 0.7:
                # perde 10% do ouro
                personagem.gold = int(personagem.gold * 0.9)
                personagem.fugas_restantes -= 1
                personagem.save()
                # fuga
                b = Batalha()
                b.personagem = personagem
                b.inimigo = inimigo
                b.resultado = 'fuga'
                b.save()

                # salva o resultado na sessão para exibir na tela de resultado
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
        # calcula defesa real somando bônus da armadura equipada
        defesa_base = personagem.defesa + (personagem.armadura_equipada.bonus_defesa if personagem.armadura_equipada else 0)
        # aplica bônus de 30% se estiver defendendo
        defesa_atual = int(defesa_base * 1.3) if batalha['defendendo'] else defesa_base
        # fator de horda — cada inimigo adicional contribui 70% do dano
        fator_horda = 1 + (quantidade - 1) * 0.7
        # calcula dano do inimigo ao personagem
        dano_inimigo = max(1, int((inimigo.ataque - defesa_atual) * fator_horda))
        personagem.hp_atual -= dano_inimigo
        mensagem += f' {inimigo.nome} causou {dano_inimigo} de dano em você!'
    batalha['defendendo'] = False
    
   # --- VERIFICA SE O INIMIGO MORREU ---
    if inimigo_hp <= 0:
        personagem.experiencia += inimigo.experiencia * quantidade
        personagem.gold += inimigo.gold * quantidade
        personagem.batalhas_na_area += 1
        personagem.save()
        
        # verifica level up
        subiu_nivel = verificar_level_up(personagem)
        
        # verifica se venceu o boss e desbloqueia próxima área
        area_desbloqueada = False
        if inimigo.is_boss:
            PROXIMA_AREA = {
                'floresta': 'caverna',
                'caverna': 'castelo',
                'castelo': None,  # última área
            }
            proxima = PROXIMA_AREA.get(personagem.area_atual)
            if proxima and personagem.area_desbloqueada == personagem.area_atual:
                # desbloqueia a próxima área
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
            'exp_ganho': inimigo.experiencia * quantidade,  # muda aqui
            'gold_ganho': inimigo.gold * quantidade,        # e aqui
            'subiu_nivel': subiu_nivel,
            'nivel_atual': personagem.nivel,
            'area_desbloqueada': area_desbloqueada,
            'proxima_area': proxima if inimigo.is_boss else None,
        }
        return redirect('resultado_batalha')
    
    # --- VERIFICA SE O PERSONAGEM MORREU ---
    if personagem.hp_atual <= 0:
        # perde todo o ouro voltando ao checkpoint
        personagem.gold = personagem.gold_salvo
        personagem.hp_atual = personagem.hp_maximo
        personagem.save()
        # derrota
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
    
    # atualiza o estado da batalha na sessão
    batalha['inimigo_hp'] = inimigo_hp
    request.session['batalha'] = batalha
    personagem.save()
    
    return render(request, 'game/batalha.html', {
        'personagem': personagem,
        'inimigo': inimigo,
        'inimigo_hp': inimigo_hp,
        'mensagem': mensagem,
        'inventario': Inventario.objects.filter(personagem=personagem),
        'quantidade': quantidade,
    })


# usa um item consumível durante a batalha, custando uma ação do turno
def usar_item_batalha(request, item_id):
    if request.method != 'POST':
        return redirect('iniciar_batalha')
    
    # pega o personagem e o estado atual da batalha
    personagem_id = request.session.get('personagem_id')
    personagem = Personagem.objects.get(id=personagem_id)
    batalha = request.session.get('batalha')
    inimigo = Inimigo.objects.get(id=batalha['inimigo_id'])
    inimigo_hp = batalha['inimigo_hp']
    
    # busca o item no inventário do personagem, garantindo que é consumível
    inventario_item = Inventario.objects.filter(personagem=personagem, item__id=item_id, item__tipo='consumivel').first()
    
    if inventario_item:
        item = inventario_item.item
        
        # aplica cura de HP sem ultrapassar o máximo
        personagem.hp_atual = min(personagem.hp_maximo, personagem.hp_atual + item.bonus_hp)
        # aplica recuperação de MP sem ultrapassar o máximo
        personagem.mp_atual = min(personagem.mp_maximo, personagem.mp_atual + item.bonus_mp)
        
        # monta a mensagem de uso do item
        mensagem = f'Você usou {item.nome}!'
        if item.bonus_hp > 0:
            mensagem += f' +{item.bonus_hp} HP'
        if item.bonus_mp > 0:
            mensagem += f' +{item.bonus_mp} MP'
        
        # remove 1 unidade do inventário, ou deleta o registro se era o último
        if inventario_item.qtd > 1:
            inventario_item.qtd -= 1
            inventario_item.save()
        else:
            inventario_item.delete()
    else:
        # item não encontrado ou não é consumível
        mensagem = 'Item não encontrado no inventário!'
    
    # inimigo ataca em resposta ao turno gasto
    if inimigo_hp > 0:
        # calcula defesa real somando bônus da armadura equipada
        defesa_real = personagem.defesa + (personagem.armadura_equipada.bonus_defesa if personagem.armadura_equipada else 0)
        dano_inimigo = max(1, inimigo.ataque - defesa_real)
        personagem.hp_atual -= dano_inimigo
        mensagem += f' {inimigo.nome} causou {dano_inimigo} de dano em você!'
    
    # verifica se o personagem morreu após o ataque do inimigo
    if personagem.hp_atual <= 0:
        # reverte o ouro para o último checkpoint salvo na vila
        personagem.gold = personagem.gold_salvo
        # ressuscita o personagem com HP cheio
        personagem.hp_atual = personagem.hp_maximo
        # reseta o progresso da área
        personagem.batalhas_na_area = 0
        personagem.fugas_restantes = 2
        personagem.save()
        # registra a derrota no banco
        b = Batalha(personagem=personagem, inimigo=inimigo, resultado='derrota')
        b.save()
        request.session['resultado'] = {
            'resultado': 'derrota',
            'inimigo_nome': inimigo.nome,
        }
        return redirect('resultado_batalha')
    
    # atualiza o hp do inimigo na sessão
    batalha['inimigo_hp'] = inimigo_hp
    request.session['batalha'] = batalha
    personagem.save()
    
    # busca o inventário atualizado para renderizar na tela
    inventario = Inventario.objects.filter(personagem=personagem)
    
    return render(request, 'game/batalha.html', {
        'personagem': personagem,
        'inimigo': inimigo,
        'inimigo_hp': inimigo_hp,
        'mensagem': mensagem,
        'inventario': inventario,
        'quantidade': batalha.get('quantidade', 1),
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

# página de inventário do personagem — mostra itens e equipamentos atuais
def inventario(request):
    personagem_id = request.session.get('personagem_id')
    if not personagem_id:
        return redirect('selecionar_personagem')
    personagem = Personagem.objects.get(id=personagem_id)
    
    # busca todos os itens do inventário separados por tipo
    armas = Inventario.objects.filter(personagem=personagem, item__tipo='arma')
    armaduras = Inventario.objects.filter(personagem=personagem, item__tipo='armadura')
    consumiveis = Inventario.objects.filter(personagem=personagem, item__tipo='consumivel')
    
    # calcula ataque e defesa reais com equipamentos
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
    
    # verifica se o item está no inventário do personagem
    if not Inventario.objects.filter(personagem=personagem, item=item).exists():
        return redirect('inventario')
    
    # equipa ou desequipa arma
    if item.tipo == 'arma':
        if personagem.arma_equipada == item:
            # desequipa se já estava equipada
            personagem.arma_equipada = None
        else:
            # equipa a nova arma
            personagem.arma_equipada = item
    
    # equipa ou desequipa armadura
    elif item.tipo == 'armadura':
        if personagem.armadura_equipada == item:
            # desequipa se já estava equipada
            personagem.armadura_equipada = None
        else:
            # equipa a nova armadura
            personagem.armadura_equipada = item
    
    personagem.save()
    return redirect('inventario')

# deleta um personagem do usuário logado
def deletar_personagem(request, personagem_id):
    # só executa se a requisição for POST — evita deleção acidental via link (GET)
    if request.method == 'POST':
        # busca o personagem garantindo que pertence ao usuário logado
        # se não encontrar, retorna 404 em vez de crashar
        personagem = get_object_or_404(Personagem, id=personagem_id, usuario=request.user)

        # força int na comparação — mesmo motivo do entrar_personagem
        if request.session.get('personagem_id') == int(personagem_id):
            del request.session['personagem_id']

        # deleta o personagem do banco de dados
        personagem.delete()

    # redireciona para a tela de seleção em qualquer caso
    return redirect('selecionar_personagem')