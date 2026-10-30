from django.shortcuts import render

from django.db.models import ProtectedError, Exists, OuterRef
from rest_framework import viewsets
from rest_framework.exceptions import APIException

from .models import Ingredient, Cocktail, CocktailIngredient
from .serializers import IngredientSerializer, IngredientFilterSerializer, CocktailSerializer, CocktailIngredientSerializer
from .pagination import StandardPagination

# Create your views here.
class IngredientInUse(APIException):
    status_code = 409
    default_detail = "Nie można usunąć składnika użytego koktajlu"
    default_code = "ingredient_in_use"

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action != 'list':
            return queryset

        filters = IngredientFilterSerializer(data=self.request.query_params.dict())
        filters.is_valid(raise_exception=True)
        params = filters.validated_data

        if 'is_alcoholic' in params:
            queryset = queryset.filter(is_alcoholic=params['is_alcoholic'])

        if 'search' in params:
            queryset = queryset.filter(name__icontains=params['search'])

        return queryset

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise IngredientInUse()

class CocktailViewSet(viewsets.ModelViewSet):
    queryset = Cocktail.objects.prefetch_related("cocktail_ingredients__ingredient")
    serializer_class = CocktailSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action != 'list':
            return queryset

        filters = CocktailFilterSerializer(data=self.request.query_params.dict())
        filters.is_valid(raise_exception=True)
        params = filters.validated_data

        if 'category' in params:
            queryset = queryset.filter(category=params['category'])

        if 'search' in params:
            queryset = queryset.filter(name__icontains=params['search'])
        
        if 'ingredient_id' in params:
            has_ingredient = CocktailIngredient.objects.filter(
                CocktailIngredient.objects.filter(
                    cocktail=OuterRef('pk'),
                    ingredient__name__icontrains=params["ingredient"]
                )
            )
            queryset = queryset.filter(has_ingredient)
        if "is_alcoholic" in params:
            has_alcohol = Exists(
                CocktailIngredient.objects.filter(
                    cocktail=OuterRef('pk'),
                    ingredient__is_alkoholic=True,
                )
            )
            queryset = queryset.filter(
                has_alcohol if params["is_alcoholic"] else ~has_alcohol
            )
        return queryset.order_by(params.get("ordering", "name"))
