from django.urls import path
from .views import ParameterListView, find_parts_chain
from .views import find_parts_chain_by_price

urlpatterns = [
    path('parameters/', ParameterListView.as_view(), name='parameter-list'),
    path('find-parts-chain/', find_parts_chain, name='find-parts-chain'),
    path('find-parts-chain-by-price/', find_parts_chain_by_price, name='find-parts-chain-by-price'),
]
