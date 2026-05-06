from django.db import models
from django.contrib.auth.models import User

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

    def __str__(self):
        return f"{self.nome} - Nível {self.nivel}"

class Inimigo(models.Model):
    AREAS = [
        ('floresta', 'Floresta'),
        ('caverna', 'Caverna'),
        ('castelo', 'Castelo'),
    ]

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