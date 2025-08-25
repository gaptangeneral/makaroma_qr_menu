from django.urls import path
from . import views

app_name = 'menu' 

urlpatterns = [
    # Ana menü sayfası
    path('', views.tek_sayfa_menu_view, name='tek_sayfa_menu'),
    
    # Admin login/logout
    path('admin-panel/login/', views.admin_login_view, name='admin_login'),
    path('admin-panel/logout/', views.admin_logout_view, name='admin_logout'),
    
    # Admin dashboard
    path('admin-panel/', views.admin_dashboard_view, name='admin_dashboard'),
    
    # Yemek yönetimi
    path('admin-panel/yemek-ekle/', views.admin_add_item_view, name='admin_add_item'),
    path('admin-panel/yemekler/', views.admin_manage_items_view, name='admin_manage_items'),
    path('admin-panel/yemek-duzenle/<int:item_id>/', views.admin_edit_item_view, name='admin_edit_item'),
    path('admin-panel/yemek-sil/<int:item_id>/', views.admin_delete_item_view, name='admin_delete_item'),
    
    # Kategori yönetimi
    path('admin-panel/kategoriler/', views.admin_manage_categories_view, name='admin_manage_categories'),
    
    # Eklenti yönetimi
    path('admin-panel/eklentiler/', views.admin_manage_extras_view, name='admin_manage_extras'),
]