from django.db import models
from django.contrib.auth.models import User

AREAS = [
        ('floresta', 'Floresta'),
        ('caverna', 'Caverna'),
        ('castelo', 'Castelo'),
    ]

class Personagem(models.Model):
    CLASSES = [
        ('guerreiro', 'Guerreiro'),
        ('mago', 'Mago'),
        ('ladrao', 'Ladrão'),
        ('arqueiro', 'Arqueiro'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    classe = models.CharField(max_length=20, choices=CLASSES)
    nivel = models.IntegerField(default=1)
    experiencia = models.IntegerField(default=0)
    hp_maximo = models.IntegerField(default=100)
    hp_atual = models.IntegerField(default=100)
    mp_maximo = models.IntegerField(default=50)
    mp_atual = models.IntegerField(default=50)
    ataque = models.IntegerField(default=10)
    defesa = models.IntegerField(default=5)
    gold = models.IntegerField(default=100)
    area_atual = models.CharField(max_length=100, choices=AREAS)
    batalhas_na_area = models.IntegerField(default=0)
    fugas_restantes = models.IntegerField(default=2)
    area_desbloqueada = models.CharField(max_length=20, choices=AREAS, default='floresta')
    gold_salvo = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nome} - Nível {self.nivel}"

class Inimigo(models.Model):
    
    nome = models.CharField(max_length=100)
    area = models.CharField(max_length=20, choices=AREAS)
    hp = models.IntegerField()
    ataque = models.IntegerField()
    defesa = models.IntegerField()
    experiencia = models.IntegerField()
    gold = models.IntegerField()
    is_boss = models.BooleanField(default=False)
    imagem = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nome} ({'Boss' if self.is_boss else 'Normal'})"
    
class Item(models.Model):
    TIPOS = [
        ('arma', 'Arma'),
        ('armadura', 'Armadura'),
        ('consumivel', 'Consumivel'),
    ]
    
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100, choices=TIPOS)
    preco = models.IntegerField(default=0)
    bonus_ataque = models.IntegerField(default=0)
    bonus_defesa = models.IntegerField(default=0)
    bonus_hp = models.IntegerField(default=0)
    bonus_mp = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"
    
class Inventario(models.Model):
     personagem = models.ForeignKey(Personagem, on_delete=models.CASCADE)
     item = models.ForeignKey(Item, on_delete=models.CASCADE)
     qtd = models.IntegerField(default=1)

     def __str__(self):
        return f"{self.personagem.nome} - {self.item.nome} x{self.qtd}" 
     
class Batalha(models.Model):
    RESULTADOS = [
        ('derrota', 'DERROTA'),
        ('vitoria', 'VITORIA'),
        ('fuga', 'FUGA'),


    ]
    personagem = models.ForeignKey(Personagem, on_delete=models.CASCADE),
    inimigo = models.ForeignKey(Inimigo, on_delete=models.CASCADE),
    resultado = models.CharField(max_length= 10, choices= RESULTADOS),
    data = models.DateField(auto_now_add=True),
    def __str__(self):
        return f"{self.personagem.nome} vs {self.inimigo.nome} - {self.resultado}"
