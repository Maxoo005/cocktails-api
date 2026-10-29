from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator
# Create your models here.

class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_alcoholic = models.BooleanField(default=False)
    image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Cocktail(models.Model):
    class Category(models.TextChoices):
        COCKTAIL = "cocktail", "Koktajl"
        SHOT = "shot", "Shot"
        LONG_DRINK = "long_drink", "Long drink"
        PUNCH = "punch", "Poncz"
        OTHER = "other", "Inne"

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=Category.choices)
    instructions = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='CocktailIngredient',
        related_name='cocktails'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class CocktailIngredient(models.Model):
    class Unit(models.TextChoices):
        ML = "ml", "ml"
        CL =  "cl", "cl"
        OZ = "oz", "oz"
        DASH = "dash", "kropelka"
        TSP = "tsp", "łyżeczka"
        PIECE = "piece", "sztuka"

    cocktail = models.ForeignKey(Cocktail, on_delete=models.CASCADE, related_name='cocktail_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, related_name='ingredient_cocktails')
    amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    unit = models.CharField(max_length=10, choices=Unit.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cocktail", "ingredient"],
                name="unique_ingredient_per_cocktail",
            ),
        ]

    def __str__(self):
        return f"{self.amount} {self.unit} {self.ingredient} w {self.cocktail}"

