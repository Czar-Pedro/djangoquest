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
]
def mapa(request):
    return render(request, 'game/mapa.html')