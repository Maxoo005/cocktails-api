from rest_framework import serializers

from .models import Ingredient

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

    