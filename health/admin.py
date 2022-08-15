from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from health.models import Detail, Weight
# Register your models here.


class WeightResource(resources.ModelResource):
    class Meta:
        model = Weight


class WeightAdmin(ImportExportModelAdmin):
    list_display = ['date', 'weight']
    ordering = ('-date',)
    resource_class = WeightResource


class DetailResource(resources.ModelResource):
    class Meta:
        model = Detail


class DetailAdmin(ImportExportModelAdmin):
    list_display = ['height', 'gender', 'age']
    resource_class = DetailResource


admin.site.register(Weight, WeightAdmin)
admin.site.register(Detail, DetailAdmin)
