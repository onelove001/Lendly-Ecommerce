from django.urls import path
from .views import *

urlpatterns = [
    path("home", home.as_view(), name="home"),
    path("product_details/<pk>", product_details.as_view(), name="product_details"),
    path("add_to_cart/<int:product_id>", add_to_cart, name="add_to_cart"),
    path("cart", cart, name="cart"),
    path("remove_from_cart/<item_id>", remove_from_cart, name="remove_from_cart"),
    path("increase_item/<item_id>", increase_item, name="increase_item"),
    path("decrease_item/<item_id>", decrease_item, name="decrease_item"),
    path("payment_checkout", payment_checkout, name="payment_checkout"),
    path("pay", payment, name="payment"),
    path("status", complete_payment_success, name="complete_payment_success"),
    path("purchased/<val_id>/<tran_id>", purchased, name="purchased"),
    path("orders", orders, name="orders"),
    
]
