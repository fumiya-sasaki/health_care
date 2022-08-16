from django.urls import path
from . import views

app_name = 'health'

urlpatterns = [
    path('', views.WeightList.as_view(), name='weight_list'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('weight_create/',views.WeightCreate.as_view(),name='weight_create'),
    path('weight_update/<int:pk>',views.WeightUpdate.as_view(),name='weight_update'),
    path('weight_delete/<int:pk>',views.WeightDelete.as_view(),name='weight_delete'),
    path('month_dashboard/<int:year>/<int:month>/', views.MonthDashboard.as_view(), name='month_dashboard'),
]