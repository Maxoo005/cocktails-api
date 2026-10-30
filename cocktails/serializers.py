from django.db import transaction
from rest_framework import serializers
from rest_framework import serializers


from .models import Ingredient, Cocktail, CocktailIngredient

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields =[
            "id",
            "name",
            "description",
            "is_alcoholic",
            "image_url",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Nazwa składnika musi mieć co najmniej 2 znaki.")
        return value

class IngredientFilterSerializer(serializers.Serializer):
    is_alcoholic = serializers.BooleanField(required=False)
    search = serializers.CharField(required=False, max_length=100)

class CocktailIngredientSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all()
    )
    name=serializers.CharField(source='ingredient.name', read_only=True)
    is_alcoholic=serializers.BooleanField(source='ingredient.is_alcoholic', read_only=True)

    class Meta:
        model = CocktailIngredient
        fields = ['ingredient_id', 'name', 'is_alcoholic', 'amount', 'unit']

class CocktailSerializer(serializers.ModelSerializer):
    ingredients = CocktailIngredientSerializer(
        source='cocktail_ingredients', many=True
    )

    class Meta:
        model = Cocktail
        fields = [
            "id",
            "name",
            "category",
            "instructions",
            "ingredients",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Nazwa koktajlu musi mieć co najmniej 2 znaki.")
        return value
   
    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError("Koktajl musi mieć co najmniej jeden składnik.")
        ids = [item['ingredient'].id for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Koktajl nie może mieć powtórzonych składników.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('cocktail_ingredients')
        cocktail = Cocktail.objects.create(**validated_data)
        self._save_ingredients(cocktail, ingredients_data)
        return cocktail

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('cocktail_ingredients', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if ingredients_data is not None:
            instance.cocktail_ingredients.all().delete()
            self._save_ingredients(instance, ingredients_data)
        return instance

    def _save_ingredients(self, cocktail, ingredients_data):
        CocktailIngredient.objects.bulk_create([CocktailIngredient(cocktail=cocktail, **item) for item in ingredients_data])

class CocktailFilterSerializer(serializers.Serializer):
    ORDERING_CHOICES = ["name", "-name", "created_at", "-created_at"]

    category = serializers.ChoiceField(choices=Cocktail.Category.choices, required=False)

    search = serializers.CharField(required=False, max_length=100)
    ingredient = serializers.CharField(required=False, max_length=100)
    is_alcoholic = serializers.BooleanField(required=False)
    ordering = serializers.ChoiceField(choices=ORDERING_CHOICES, required=False)

    