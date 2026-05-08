from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('criar-personagem/', views.criar_personagem, name='criar_personagem'),
    path('mapa/', views.mapa, name='mapa'),
    path('vila/<str:area>/', views.vila, name='vila'),
    path('selecionar-personagem/', views.selecionar_personagem, name='selecionar_personagem'),
    path('entrar-personagem/<int:personagem_id>/', views.entrar_personagem, name='entrar_personagem'),
    path('mundo/', views.mundo, name='mundo'),
]