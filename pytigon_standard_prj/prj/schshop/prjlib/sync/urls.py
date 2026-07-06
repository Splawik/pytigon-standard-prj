from django.conf.urls import url
from django.urls import include, path

from . import views

urlpatterns = [
    url(r'sync_customers/$',  views.sync_customers, name='sync_customers'),    
    url(r'sync_products/$',  views.sync_products, name='sync_products'),        
    url(r'sync_stack/$',  views.sync_stack, name='sync_stack'),    
    url(r'sync_price_list/$',  views.sync_price_list, name='sync_price_list'),    
    url(r'sync_orders/$',  views.sync_orders, name='sync_orders'),    
    url(r'sync_sale/$',  views.sync_sale, name='sync_sale'),    
    path('list_images/',  views.list_images, name='list_images'),    
    path('add_image/<int:symkar>/<str:name>/',  views.add_image, name='add_image'),    
    path('remove_image/<int:symkar>/<str:name>/',  views.remove_image, name='remove_image'),    
]
