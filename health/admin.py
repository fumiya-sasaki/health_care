from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from health.models import Weight
# Register your models here.

class WeightResource(resources.ModelResource):
    class Meta:
        model = Weight

class WeightAdmin(ImportExportModelAdmin):
    list_display = ['date', 'weight']
    ordering = ('-date',)

    resource_class = WeightResource

admin.site.register(Weight, WeightAdmin)