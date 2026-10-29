from django.contrib import admin
from .models import Ingredient, Cocktail, CocktailIngredient

# Register your models here.

class CocktailIngredientInline(admin.TabularInline):
    model = CocktailIngredient
    extra = 1

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_alcoholic']
    search_fields = ['name']
    list_filter = ['is_alcoholic']

@admin.register(Cocktail)
class CocktailAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    search_fields = ['name']
    list_filter = ['category']
    inlines = [CocktailIngredientInline]

    