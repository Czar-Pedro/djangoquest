from django.contrib import admin
from .models import Personagem, Inimigo, Item, Inventario, Batalha

admin.site.register(Personagem)
admin.site.register(Inimigo)
admin.site.register(Item)
admin.site.register(Inventario)
admin.site.register(Batalha)