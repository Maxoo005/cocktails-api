from django.shortcuts import render

from django.db.models import ProtectedError
from rest_framework import viewsets
from rest_framework.exceptions import APIException

from .models import Ingredient
from .serializers import IngredientSerializer, IngredientFilterSerializer
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

