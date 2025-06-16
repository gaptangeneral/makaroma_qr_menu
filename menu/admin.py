from django.contrib import admin
from .models import Category, MenuItem, MenuExtra, Review

# Admin panelinde modellerin nasıl görüneceğini ve yönetileceğini özelleştirebiliriz.
# Şimdilik temel kayıt işlemlerini yapacağız.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'is_active', 'updated_at')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)} # Slug alanını name alanından otomatik doldurur
    ordering = ('name',)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'base_price', 'is_available', 'is_chef_recommendation', 'average_rating', 'updated_at')
    list_filter = ('is_available', 'is_chef_recommendation', 'category', 'is_vegetarian', 'is_vegan', 'is_gluten_free')
    search_fields = ('name', 'description', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('category', 'name',)
    # ManyToMany alanlarını daha kullanıcı dostu göstermek için filter_horizontal veya filter_vertical kullanılabilir
    filter_horizontal = ('available_extras',) # veya filter_vertical

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'description', 'base_price', 'image')
        }),
        ('Detaylar ve Etiketler', {
            'classes': ('collapse',), # Bu bölüm başlangıçta kapalı gelir
            'fields': ('preparation_time_minutes', 'is_vegetarian', 'is_vegan', 'is_gluten_free'),
        }),
        ('Durum ve Öne Çıkanlar', {
            'fields': ('is_available', 'is_chef_recommendation', 'is_popular'),
        }),
        ('Ekstralar', {
            'fields': ('available_extras',),
        }),
        ('Değerlendirmeler (Otomatik Hesaplanır)', {
            'fields': ('average_rating', 'total_reviews'),
        }),
    )
    readonly_fields = ('average_rating', 'total_reviews', 'updated_at', 'created_at') # Bu alanlar admin panelinden düzenlenemez

@admin.register(MenuExtra)
class MenuExtraAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description')
    ordering = ('category', 'name',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('menu_item', 'user_name', 'rating', 'created_at')
    list_filter = ('rating', 'menu_item__category') # İlişkili model üzerinden filtreleme
    search_fields = ('menu_item__name', 'user_name', 'comment')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',) # Oluşturulma tarihi değiştirilemez

    # Yorumları doğrudan admin panelinden eklemek/düzenlemek yerine
    # genellikle kullanıcı arayüzünden gelmesi beklenir.
    # Bu yüzden bazı alanları sadece okunabilir yapabilir veya
    # admin panelinde yorum ekleme özelliğini kısıtlayabiliriz.
    # Örneğin, yeni yorum eklemeyi engellemek için:
    # def has_add_permission(self, request):
    #     return False
