from rest_framework import status
from rest_framework.test import APITestCase

from .models import Ingredient

# Create your tests here.

class CocktailApiTests(APITestCase):
    def setUp(self):
        self.rum = Ingredient.objects.create(name="Biały rum", is_alcoholic=True)
        self.mint = Ingredient.objects.create(name="Mięta")
        self.lime = Ingredient.objects.create(name="Limonka")

    def create_cocktail(self, name, ingredients):
        return self.client.post(
            "/api/cocktails/",
            {
                "name": name,
                "category": "long_drink",
                "instructions": "Wymieszaj wszystkie składniki.",
                "ingredients": ingredients,
            },
            format="json",
        )

    def item(self, ingredient, amount="1", unit="piece"):
        return {"ingredient_id": ingredient.id, "amount": amount, "unit": unit}

    def test_create_cocktail_with_ingredients(self):
        response = self.create_cocktail(
            "Mojito", [self.item(self.rum, "50", "ml"), self.item(self.mint, "8")]
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["ingredients"]), 2)

    def test_cocktail_requires_ingredients(self):
        response = self.create_cocktail("Pusty", [])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cocktail_rejects_duplicate_ingredients(self):
        response = self.create_cocktail(
            "Dubel", [self.item(self.mint), self.item(self.mint)]
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_non_alcoholic_with_mint(self):
        self.create_cocktail("Mojito", [self.item(self.rum), self.item(self.mint)])
        self.create_cocktail(
            "Virgin Mojito", [self.item(self.mint), self.item(self.lime)]
        )
        response = self.client.get(
            "/api/cocktails/", {"is_alcoholic": "false", "ingredient": "mięta"}
        )
        names = [cocktail["name"] for cocktail in response.data["results"]]
        self.assertEqual(names, ["Virgin Mojito"])

    def test_invalid_ordering_returns_400(self):
        response = self.client.get("/api/cocktails/", {"ordering": "price"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_delete_ingredient_used_in_cocktail(self):
        self.create_cocktail("Mojito", [self.item(self.mint)])
        response = self.client.delete(f"/api/ingredients/{self.mint.id}/")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

