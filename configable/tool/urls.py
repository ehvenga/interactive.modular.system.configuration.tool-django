from django.urls import path
from .views import ParameterListView, FunctionListView, find_parts_chain, find_parts_chain_by_function
from .views import find_parts_chain_by_price, find_parts_chain_by_reputation

urlpatterns = [
    path('parameters/', ParameterListView.as_view(), name='parameter-list'),
    path('functions/', FunctionListView.as_view(), name='function-list'),
    path('find-parts-chain/', find_parts_chain, name='find-parts-chain'),
    path('find-parts-chain-by-function/', find_parts_chain_by_function, name='find-parts-chain-by-function'),
    path('find-parts-chain-by-price/', find_parts_chain_by_price, name='find-parts-chain-by-price'),
    path('find-parts-chain-by-reputation/', find_parts_chain_by_reputation, name='find-parts-chain-by-reputation'),
]
