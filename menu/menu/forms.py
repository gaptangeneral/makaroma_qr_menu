from django import forms
from .models import MenuItem, Category, MenuExtra

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = [
            'name', 'description', 'category', 'base_price', 'image',
            'preparation_time_minutes', 'available_extras', 'is_available',
            'is_chef_recommendation', 'is_popular', 'is_vegetarian', 
            'is_vegan', 'is_gluten_free'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Yemek adını girin'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Yemek açıklamasını girin'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'base_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'preparation_time_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Dakika cinsinden'
            }),
            'available_extras': forms.CheckboxSelectMultiple(),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_chef_recommendation': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_popular': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_vegetarian': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_vegan': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_gluten_free': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': 'Yemek Adı',
            'description': 'Açıklama',
            'category': 'Kategori',
            'base_price': 'Fiyat (₺)',
            'image': 'Yemek Resmi',
            'preparation_time_minutes': 'Hazırlık Süresi (dakika)',
            'available_extras': 'Mevcut Eklentiler',
            'is_available': 'Mevcut',
            'is_chef_recommendation': 'Şef Önerisi',
            'is_popular': 'Popüler',
            'is_vegetarian': 'Vejetaryen',
            'is_vegan': 'Vegan',
            'is_gluten_free': 'Glutensiz',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sadece aktif kategorileri göster
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        # Sadece mevcut eklentileri göster
        self.fields['available_extras'].queryset = MenuExtra.objects.filter(is_available=True)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'parent', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Kategori adını girin'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Kategori açıklamasını girin (isteğe bağlı)'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': 'Kategori Adı',
            'description': 'Açıklama',
            'image': 'Kategori Resmi',
            'parent': 'Ana Kategori',
            'is_active': 'Aktif',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Parent seçiminde kendi kendini gösterme
        if self.instance.pk:
            self.fields['parent'].queryset = Category.objects.filter(is_active=True).exclude(pk=self.instance.pk)
        else:
            self.fields['parent'].queryset = Category.objects.filter(is_active=True)

class MenuExtraForm(forms.ModelForm):
    class Meta:
        model = MenuExtra
        fields = ['name', 'price', 'category', 'description', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Eklenti adını girin'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Eklenti açıklamasını girin (isteğe bağlı)'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': 'Eklenti Adı',
            'price': 'Fiyat (₺)',
            'category': 'Kategori',
            'description': 'Açıklama',
            'is_available': 'Mevcut',
        }