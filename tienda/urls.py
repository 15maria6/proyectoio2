from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    #path('finalizar/', views.finalizar_pedido, name='finalizar_pedido'),
    path('actualizar-cantidad/', views.actualizar_cantidad, name='actualizar_cantidad'),
path('eliminar-producto/', views.eliminar_producto, name='eliminar_producto'),
path('carrito/actualizar/', views.actualizar_cantidad, name='actualizar_cantidad'),
path('carrito/eliminar/', views.eliminar_producto, name='eliminar_producto'),
path('carrito/finalizar/', views.finalizar_pedido, name='finalizar_pedido'),
path('cuenta/', views.cuenta, name='cuenta'),#cuenta
path('cuenta/vendedor/', views.panel_vendedor, name='panel_vendedor'), 
path('carrito/login/', views.login_view, name='login'),
path('carrito/registro/', views.registro_view, name='registro'),





]
