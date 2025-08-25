from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Category, MenuItem, MenuExtra
from .forms import MenuItemForm, CategoryForm, MenuExtraForm

def tek_sayfa_menu_view(request):
    """
    Tüm aktif ana kategorileri ve her birine ait aktif menü öğelerini
    tek bir sayfada göstermek için veri hazırlar.
    """
    aktif_kategoriler = Category.objects.filter(
        is_active=True, 
        parent__isnull=True
    ).prefetch_related('menu_items').order_by('name')

    menu_icerigi = []
    for kategori in aktif_kategoriler:
        urunler = [item for item in kategori.menu_items.all() if item.is_available]
        
        if urunler:
            menu_icerigi.append({
                'kategori_adi': kategori.name,
                'kategori_slug': kategori.slug,
                'kategori_aciklamasi': kategori.description,
                'kategori_resmi_url': kategori.image.url if kategori.image else None,
                'urunler': urunler
            })

    context = {
        'menu_icerigi': menu_icerigi,
        'sayfa_basligi': 'Makaroma - Tüm Menümüz'
    }
    
    return render(request, 'menu/menu.html', context)

def admin_login_view(request):
    """
    Admin login sayfası
    """
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('menu:admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, 'Başarıyla giriş yaptınız!')
            return redirect('menu:admin_dashboard')
        else:
            messages.error(request, 'Kullanıcı adı veya şifre hatalı, ya da admin yetkiniz yok!')
    
    return render(request, 'menu/admin_login.html')

@login_required
def admin_logout_view(request):
    """
    Admin logout
    """
    if request.user.is_staff:
        logout(request)
        messages.success(request, 'Başarıyla çıkış yaptınız!')
    return redirect('menu:admin_login')

@login_required
def admin_dashboard_view(request):
    """
    Admin ana panel
    """
    if not request.user.is_staff:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok!')
        return redirect('menu:admin_login')
    
    # İstatistikler
    total_categories = Category.objects.filter(is_active=True).count()
    total_items = MenuItem.objects.filter(is_available=True).count()
    total_extras = MenuExtra.objects.filter(is_available=True).count()
    recent_items = MenuItem.objects.all().order_by('-created_at')[:5]
    
    context = {
        'total_categories': total_categories,
        'total_items': total_items,
        'total_extras': total_extras,
        'recent_items': recent_items,
    }
    
    return render(request, 'menu/admin_dashboard.html', context)

@login_required
def admin_add_item_view(request):
    """
    Yeni yemek ekleme sayfası
    """
    if not request.user.is_staff:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok!')
        return redirect('menu:admin_login')
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Yemek başarıyla eklendi!')
            return redirect('menu:admin_dashboard')
    else:
        form = MenuItemForm()
    
    return render(request, 'menu/admin_add_item.html', {'form': form})

@login_required
def admin_manage_items_view(request):
    """
    Yemekleri listeleme ve düzenleme sayfası
    """
    if not request.user.is_staff:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok!')
        return redirect('menu:admin_login')
    
    items = MenuItem.objects.all().select_related('category').order_by('-created_at')
    categories = Category.objects.filter(is_active=True).order_by('name')
    
    context = {
        'items': items,
        'categories': categories,
    }
    
    return render(request, 'menu/admin_manage_items.html', context)

@login_required
def admin_edit_item_view(request, item_id):
    """
    Yemek düzenleme sayfası
    """
    if not request.user.is_staff:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok!')
        return redirect('menu:admin_login')
    
    item = get_object_or_404(MenuItem, id=item_id)
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Yemek başarıyla güncellendi!')
            return redirect('menu:admin_manage_items')
    else:
        form = MenuItemForm(instance=item)
    
    return render(request, 'menu/admin_edit_item.html', {'form': form, 'item': item})

@login_required
def admin_delete_item_view(request, item_id):
    """
    Yemek silme (AJAX)
    """
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Yetkiniz yok!'})
    
    if request.method == 'POST':
        item = get_object_or_404(MenuItem, id=item_id)
        item_name = item.name
        item.delete()
        return JsonResponse({'success': True, 'message': f'{item_name} başarıyla silindi!'})
    
    return JsonResponse({'success': False, 'message': 'Geçersiz istek!'})

@login_required
def admin_manage_categories_view(request):
    """
    Kategori yönetimi
    """
    if not request.user.is_staff:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok!')
        return redirect('menu:admin_login')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori başarıyla eklendi!')
            return redirect('menu:admin_manage_categories')
    else:
        form = CategoryForm()
    
    categories = Category.objects.all().order_by('name')
    
    context = {
        'form': form,
        'categories': categories,
    }
    
    return render(request, 'menu/admin_manage_categories.html', context)

@login_required
def admin_manage_extras_view(request):
    """
    Eklenti yönetimi
    """
    if not request.user.is_staff:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok!')
        return redirect('menu:admin_login')
    
    if request.method == 'POST':
        form = MenuExtraForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Eklenti başarıyla eklendi!')
            return redirect('menu:admin_manage_extras')
    else:
        form = MenuExtraForm()
    
    extras = MenuExtra.objects.all().order_by('category', 'name')
    
    context = {
        'form': form,
        'extras': extras,
    }
    
    return render(request, 'menu/admin_manage_extras.html', context)