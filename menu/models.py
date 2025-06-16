from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

# Helper function to generate unique slugs
def generate_unique_slug(klass, field_name, instance=None):
    """
    Belirtilen alan için benzersiz bir slug üretir.
    Eğer bir instance verilirse ve slug zaten varsa, sonuna bir sayı ekler.
    """
    origin_slug = slugify(field_name)
    unique_slug = origin_slug
    numb = 1
    while klass.objects.filter(slug=unique_slug).exists() and (not instance or instance.slug != unique_slug):
        unique_slug = '%s-%d' % (origin_slug, numb)
        numb += 1
    return unique_slug

class Category(models.Model):
    """
    Menü öğelerinin kategorilerini temsil eder (örn: Makarnalar, İçecekler, Tatlılar).
    Kategoriler hiyerarşik olabilir (ana kategori ve alt kategoriler).
    """
    name = models.CharField(max_length=100, verbose_name="Kategori Adı")
    slug = models.SlugField(max_length=120, unique=True, blank=True, verbose_name="Slug (URL Dostu Ad)")
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE, verbose_name="Ana Kategori")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    image = models.ImageField(upload_to='category_images/', blank=True, null=True, verbose_name="Kategori Resmi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Category, self.name)
        super().save(*args, **kwargs)

class MenuExtra(models.Model):
    """
    Menü öğelerine eklenebilecek ekstra malzemeleri temsil eder (örn: Mantar, Tavuk).
    """
    EXTRA_CATEGORIES = [
        ('protein', 'Protein'),
        ('sauce', 'Sos'),
        ('veggie', 'Sebze'),
        ('cheese', 'Peynir'),
        ('other', 'Diğer'),
    ]
    name = models.CharField(max_length=100, verbose_name="Ekstra Adı")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Fiyatı")
    category = models.CharField(max_length=50, choices=EXTRA_CATEGORIES, verbose_name="Ekstra Kategorisi")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    is_available = models.BooleanField(default=True, verbose_name="Mevcut mu?")

    class Meta:
        verbose_name = "Menü Ekstrası"
        verbose_name_plural = "Menü Ekstraları"
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} (+{self.price} TL)"

class MenuItem(models.Model):
    """
    Menüdeki her bir öğeyi temsil eder (örn: Fettuccine Alfredo).
    """
    name = models.CharField(max_length=150, verbose_name="Ürün Adı")
    slug = models.SlugField(max_length=170, unique=True, blank=True, verbose_name="Slug (URL Dostu Ad)")
    description = models.TextField(verbose_name="Açıklama")
    category = models.ForeignKey(Category, related_name='menu_items', on_delete=models.CASCADE, verbose_name="Kategori")
    base_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Temel Fiyat")
    image = models.ImageField(upload_to='menu_item_images/', blank=True, null=True, verbose_name="Ürün Resmi (16:9 önerilir)")
    # Hazırlık süresi dakika cinsinden saklanacak
    preparation_time_minutes = models.PositiveIntegerField(blank=True, null=True, verbose_name="Hazırlık Süresi (dakika)")
    
    # Ortalama puan ve toplam değerlendirme sayısı, Review modelinden hesaplanabilir veya burada tutulabilir.
    # Basitlik adına burada tutalım, daha sonra Review modelinden güncellenebilir.
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name="Ortalama Puan")
    total_reviews = models.PositiveIntegerField(default=0, verbose_name="Toplam Değerlendirme Sayısı")
    
    available_extras = models.ManyToManyField(MenuExtra, blank=True, verbose_name="Mevcut Ekstralar")
    
    is_available = models.BooleanField(default=True, verbose_name="Mevcut mu? (Stok Durumu)")
    is_chef_recommendation = models.BooleanField(default=False, verbose_name="Şefin Önerisi mi?")
    is_popular = models.BooleanField(default=False, verbose_name="Popüler mi?") # "Bugünün en çok siparişi" gibi
    is_vegetarian = models.BooleanField(default=False, verbose_name="Vejetaryen mi?")
    is_vegan = models.BooleanField(default=False, verbose_name="Vegan mı?")
    is_gluten_free = models.BooleanField(default=False, verbose_name="Glutensiz mi?")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Menü Öğesi"
        verbose_name_plural = "Menü Öğeleri"
        ordering = ['category', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(MenuItem, self.name)
        super().save(*args, **kwargs)

    def get_preparation_time_display(self):
        if self.preparation_time_minutes:
            return f"{self.preparation_time_minutes} dk"
        return "Bilinmiyor"

class Review(models.Model):
    """
    Menü öğeleri için kullanıcı değerlendirmelerini ve yorumlarını saklar.
    """
    menu_item = models.ForeignKey(MenuItem, related_name='reviews', on_delete=models.CASCADE, verbose_name="Menü Öğesi")
    # Gerçek bir kullanıcı modeli entegre edilene kadar basit bir isim alanı
    user_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Kullanıcı Adı (opsiyonel)")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Puan (1-5)")
    comment = models.TextField(blank=True, null=True, verbose_name="Yorum")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Değerlendirme Tarihi")

    class Meta:
        verbose_name = "Değerlendirme"
        verbose_name_plural = "Değerlendirmeler"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.menu_item.name} için {self.rating} yıldızlı değerlendirme"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Değerlendirme kaydedildikten/güncellendikten sonra MenuItem'daki ortalama puanı güncelle
        self.menu_item.total_reviews = self.menu_item.reviews.count()
        self.menu_item.average_rating = self.menu_item.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
        self.menu_item.save(update_fields=['total_reviews', 'average_rating'])

    def delete(self, *args, **kwargs):
        menu_item_instance = self.menu_item
        super().delete(*args, **kwargs)
        # Değerlendirme silindikten sonra MenuItem'daki ortalama puanı güncelle
        menu_item_instance.total_reviews = menu_item_instance.reviews.count()
        if menu_item_instance.total_reviews > 0:
            menu_item_instance.average_rating = menu_item_instance.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
        else:
            menu_item_instance.average_rating = 0
        menu_item_instance.save(update_fields=['total_reviews', 'average_rating'])

# Sipariş ve Operasyonel Özellikler için Temel Modeller (İlerleyen aşamalarda geliştirilebilir)
# class Table(models.Model):
#     table_number = models.CharField(max_length=10, unique=True, verbose_name="Masa Numarası")
#     is_active = models.BooleanField(default=True)
#     def __str__(self):
#         return f"Masa {self.table_number}"

# class Order(models.Model):
#     STATUS_CHOICES = [
#         ('pending', 'Beklemede'),
#         ('preparing', 'Hazırlanıyor'),
#         ('ready', 'Hazır'),
#         ('served', 'Servis Edildi'),
#         ('paid', 'Ödendi'),
#         ('cancelled', 'İptal Edildi'),
#     ]
#     table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Masa") # QR koddan masa bilgisi alınabilir
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Sipariş Durumu")
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Toplam Tutar")
#     # session_key veya user ForeignKey eklenebilir
#     def __str__(self):
#         return f"Sipariş {self.id} - {self.status}"

# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Sipariş")
#     menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, verbose_name="Menü Öğesi")
#     quantity = models.PositiveIntegerField(default=1, verbose_name="Miktar")
#     unit_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Birim Fiyat") # Sipariş anındaki fiyat
#     # Seçilen ekstralar da buraya eklenebilir, belki ManyToManyField ile veya JSONField ile
#     # chosen_extras = models.ManyToManyField(MenuExtra, blank=True)
#     # chosen_extras_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
#     sub_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Alt Toplam")

#     def save(self, *args, **kwargs):
#         self.sub_total = self.menu_item.base_price * self.quantity # + chosen_extras_price
#         super().save(*args, **kwargs)
#         # Siparişin toplam tutarını güncellemek için bir sinyal veya Order modelinde bir metot kullanılabilir.

#     def __str__(self):
#         return f"{self.quantity} x {self.menu_item.name}"
