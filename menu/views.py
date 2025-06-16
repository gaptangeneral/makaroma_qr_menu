from django.shortcuts import render, get_object_or_404
from .models import Category, MenuItem # Modellerimizi import ediyoruz

def menu_item_detay_modal_view(request, item_slug):
    """
    Belirli bir ürünün detaylarını (AJAX isteği için HTML fragment olarak) döndürür.
    Bu fonksiyon, 'menu/partials/urun_karti_modal_icerik.html' şablonunu render eder.
    """
    # item_slug'a göre aktif olan MenuItem nesnesini çekiyoruz.
    # Eğer nesne bulunamazsa veya is_available=False ise 404 hatası döner.
    menu_ogesi = get_object_or_404(MenuItem, slug=item_slug, is_available=True)
    
    # Ürüne ait yorumları da çekebiliriz, ancak şablonda item.reviews.all() ile de erişilebilir.
    # Eğer özel bir sıralama veya filtreleme gerekiyorsa burada yapmak daha iyi olabilir.
    # Örneğin: yorumlar = menu_ogesi.reviews.filter(is_approved=True).order_by('-created_at')
    # Şimdilik şablonun item.reviews.all() kullanacağını varsayalım.

    context = {
        'item': menu_ogesi,
        # 'yorumlar': yorumlar # Eğer yukarıda yorumları ayrı çektiyseniz context'e ekleyin
    }
    
    # Sadece modalın içeriğini oluşturan partial HTML'i render ediyoruz.
    return render(request, 'menu/partials/urun_karti_modal_icerik.html', context)

def tek_sayfa_menu_view(request):
    """
    Tüm aktif ana kategorileri ve her birine ait aktif menü öğelerini
    tek bir sayfada göstermek için veri hazırlar.
    """
    # Aktif olan ve parent'ı olmayan (ana kategori) kategorileri çekiyoruz.
    # Her kategoriye ait aktif ürünleri de önceden çekmek (prefetch_related)
    # veritabanı sorgu sayısını azaltarak performansı artırır.
    aktif_kategoriler = Category.objects.filter(
        is_active=True, 
        parent__isnull=True # Sadece ana kategoriler
    ).prefetch_related(
        'menu_items' # MenuItem modelindeki Category'ye olan ForeignKey'in related_name'i
                     # Eğer related_name belirtilmemişse varsayılan olarak 'menuitem_set' olur.
                     # Bizim modelimizde 'menu_items' olarak belirtmiştik.
    ).order_by('name') # Kategorileri isme göre sırala

    # Şablonun kolayca işleyebileceği bir veri yapısı oluşturalım.
    # Her kategori için, o kategoriye ait aktif ürünleri de ekleyeceğiz.
    menu_icerigi = []
    for kategori in aktif_kategoriler:
        # Kategoriye ait sadece aktif (is_available=True) olan ürünleri alalım.
        # prefetch_related sayesinde bu sorgu optimize edilmiş olacak.
        urunler = [item for item in kategori.menu_items.all() if item.is_available]
        
        # Sadece içinde ürün olan kategorileri gösterelim (isteğe bağlı)
        if urunler: # Eğer bu kategori altında hiç aktif ürün yoksa, o kategoriyi hiç göstermeyebiliriz.
            menu_icerigi.append({
                'kategori_adi': kategori.name,
                'kategori_slug': kategori.slug, # Section ID'leri için kullanılacak
                'kategori_aciklamasi': kategori.description,
                'kategori_resmi_url': kategori.image.url if kategori.image else None,
                'urunler': urunler
            })

    context = {
        'menu_icerigi': menu_icerigi,
        'sayfa_basligi': 'Makaroma - Tüm Menümüz' # Şablondaki <title> için
    }
    
    # Gönderdiğiniz şablonun adını buraya yazın.
    # Örneğin, eğer şablonunuz menu/templates/menu/yeni_tek_sayfa_menu.html ise:
    return render(request, 'menu/menu.html', context)