from django.contrib import admin
from .models import CarMake, CarModel


class CarModelInline(admin.StackedInline):
    """Inline configuration for CarModel within CarMake admin."""
    model = CarModel
    extra = 5


class CarMakeAdmin(admin.ModelAdmin):
    """Custom admin for CarMake with inline CarModels."""
    inlines = [CarModelInline]


# Register CarMake with custom admin
admin.site.register(CarMake, CarMakeAdmin)

# Register CarModel with default admin
admin.site.register(CarModel)
