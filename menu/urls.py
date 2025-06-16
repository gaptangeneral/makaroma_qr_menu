from django.urls import path
from . import views # menu uygulamasının views.py dosyasını import ediyoruz

# Uygulama ad alanı (app_name), template'lerde URL'leri tersine çevirirken (reverse URL lookup)
# isim çakışmalarını önlemek için önemlidir.
app_name = 'menu' 

urlpatterns = [
        path('', views.tek_sayfa_menu_view, name='tek_sayfa_menu'), 
        path('urun-detay-modal/<slug:item_slug>/', views.menu_item_detay_modal_view, name='menu_item_detay_modal'),



]
