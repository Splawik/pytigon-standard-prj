#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import json
from decimal import Decimal

from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404, HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import pgettext_lazy
from django.views.decorators.csrf import csrf_exempt
from django.template.defaultfilters import slugify

from bulk_update.helper import bulk_update
from templated_email import send_templated_mail

from saleor.product.models import Category, Product, ProductType,  Attribute, AttributeValue, ProductVariant, Collection, AssignedProductAttribute, AttributeProduct, ProductImage
from saleor.account.models import User, Address
from big_company.models import CustomerProfile, PriceDoc, UserData
from .models import *
from saleor.product.utils.attributes import associate_attribute_values_to_instance
    
import unidecode
from celery import shared_task

from prices import Money
import datetime
import io
import zipfile
from PIL import Image

@shared_task
def send_email_to_new_user(context, recipient):
    send_templated_mail(
        template_name='sync/new_user',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        context=context)



PRODUCT_CATEGORY_MAP = {
    '01': 'kostki-przemyslowe',
    '02': 'kostki-dekoracyjne',
    '03': 'kostki-szlachetne',
    '04': 'plyty-chodnikowe',
    '05': 'krawezniki-i-obrzeza',
    '06': 'azur-i-scieki',
    '11': 'wyroby-wet-cast',
    '99': 'inne'
}

PRODUCT_ATTRIBUTES_MAP = {
    'pd_S7': 'Faktura',
    'pd_S9': 'Faza',
    'pd_S6': 'Kolor',
    'pd_S3': 'Wysokość',
}


PRODUCT_TYPES = [
    'EEL',
    'EKB',
    'EKR',
    'INNE'
]

MAG_MAP = {
    '51': 'Gdansk  ',
    '53': 'Koszalin',
    '54': 'Florczaki',
    '55': 'Bydgoszcz',
    '56': 'Piechcin',
    '58': 'Lublin (Pancerniaków)',
    '65': 'Debica',
    '77': 'Kraków',
    '81': 'Lodz',
    '83': 'Kielce',
    '86': 'Rzeszow',
    '88': 'Pruszkow',
    '90': 'Lublin (Mełgiewska)',
    '91': 'Warszawa',
    '93': 'Legnica',
    '94': 'Proszkow',
    '96': 'Kotlarnia',
    '97': 'Opole',
    '98': 'Niepolomice',
    '99': 'Tarnowskie Gory',
}


CRETE_NEW_ATTRS = True

ATTRIBUTES_MAP = {}

ADDRESS = None


def init_attributes():
    attributes = {}
    test = False
    for attribute in Attribute.objects.all():
        attributes[attribute.slug] = attribute

    for key, value in PRODUCT_ATTRIBUTES_MAP.items():
        if not key in attributes:
            obj = Attribute()
            obj.name = value
            obj.slug = key
            obj.save()
            test = True
    
    if test:
        return init_attributes()
    else:
        return attributes

def init_product_types():    
    product_types = {}
    test = False
    tmp = ProductType.objects.all()
    for pos in tmp:
        product_types[pos.name] = pos
    for t in PRODUCT_TYPES:
        if not t in product_types:
            obj = ProductType()
            obj.name = t
            obj.slug = t.lower()
            obj.save()
            test = True
    if test:
        return init_product_types()
    else:
        return product_types

def init_categories():
    categories = {}
    test = False
    for category in Category.objects.all():
        categories[category.slug] = category

    for key, value in PRODUCT_CATEGORY_MAP.items():
        if not key in categories:
            obj = Category()
            obj.name = value
            obj.slug = key
            obj.save()
            test = True
    
    if test:
        return init_categories()
    else:
        return categories
    
def assign_attr(obj, pd_name, value, product_attributes):
    if pd_name in product_attributes:        
        attr = product_attributes[pd_name]
        pattrs = AttributeProduct.objects.filter(attribute=attr, product_type=obj.product_type)
        if len(pattrs) > 0:
            pattr = pattrs[0]
            values = attr.values.filter(slug=value)
            if len(values)>0:
                v = values[0]
            else:
                v = AttributeValue()
                v.slug = value
                v.name = value                    
                v.value = value
                v.attribute = attr
                v.save()                
            associate_attribute_values_to_instance(obj, attr, v)


class ProfileRec():
    def __init__(self, rec):
        self.platnik = rec[0]
        self.logo = rec[1]
        self.mag_dod = rec[2]
        self.linkParam = rec[3]
        self.imie = rec[4]
        self.nazwisko = rec[5]
        self.email = rec[6]
        self.nazwa_bud = rec[7]
        self.nazwa_mag = rec[8]
        
        if self.nazwa_mag and '-' in self.nazwa_mag:
            x = self.nazwa_mag.split('-', 1)
            self.nazwa_mag = x[1].strip() + ' (' + x[0].strip() + ")"

        if self.logo and self.nazwa_bud:
            self.name = str(self.logo) + ": " + self.nazwa_bud
        else:
            self.name = ""
        
def save_user(obj, upgrade=True):
    global ADDRESS
    users = User.objects.filter(email=obj.email)
    if upgrade or not users.count() > 0:        
        if users.count() > 0:
            user = users[0]
            new_user = False
        else:
            user = User()
            new_user = True
        user.email = obj.email
        if new_user:
            password = "LosoweHaslo"
            user.set_password(password)
        
        user.first_name = obj.name
        user.last_name = obj.nazwisko + " " + obj.imie
        user.note = ""
        user.default_shipping_address = ADDRESS
        user.default_billing_address = ADDRESS
        user.is_active = True
        user.save()

                
def save_profile(obj):
    profileid = obj.email + "/" + obj.platnik + "/" + obj.logo + "/" + obj.linkParam
    profiles = CustomerProfile.objects.filter(profileid=profileid)
    if not profiles.count() > 0:
        p = CustomerProfile()
    else:
        p = profiles[0]
        
    p.email = obj.email
    p.profileid = profileid
    p.platnik = obj.platnik
    p.budowa = obj.logo
    p.magazyn = obj.linkParam
    p.platnik_name = ""
    p.budowa_name = obj.nazwa_bud
    p.magazyn_name = obj.nazwa_mag    
    p.save()


@csrf_exempt
def sync_customers(request):    
    global ADDRESS
    CustomerProfile.objects.all().delete()
    
    User.objects.exclude(is_staff=True).update(is_active=False)

    object_list = Address.objects.filter(street_address_1="Odbiór własny").order_by("id")
    if len(object_list) < 1:
        address = Address()
        address.street_address_1 = "Odbiór własny"
        address.country = 'PL'
        address.save()
        ADDRESS = address
    else:
        ADDRESS = object_list[0]

    data = json.loads(request.POST.get('data'))
    tab = []
    for row in data:
        tab.append(ProfileRec(row))
            
    old_email = ""
    for pos in tab:
        if pos.platnik and pos.logo:
            if pos.email != old_email:
                save_user(pos)
                old_email = pos.email
            save_profile(pos)
    
    return HttpResponse("OK")


@csrf_exempt
def sync_products(request):
    old_products = []
    object_list = Product.objects.all()
    for pos in object_list:
        old_products.append(pos.seo_title)

    data = json.loads(request.POST.get('data'))
    
    product_types = init_product_types()
    product_categories = init_categories()
    product_attributes = init_attributes()
    
    styles = {}
    for row in data:
        s1 = row[9]
        s2 = row[10]
        if s1 == 'POLBRUK':
            if s2 in styles:
                styles[s2] += 1
            else:
                styles[s2] = 1
    for key, value in styles.items():
        if value > 1:
            slug = slugify(key)
            elements =  Collection.objects.filter(slug = slug)            
            if elements.count() == 0:
                obj = Collection()
                obj.slug = slug
                obj.name = key
                obj.is_published = True
                obj.save()
        
    temp = []

    for row in data:
        new_obj = False
        if row[0] in old_products:
            old_products.remove(row[0])
        x = Product.objects.filter(seo_title=row[0])
        if len(x) > 0:
            obj = x[0]
        else:
            new_obj = True
            obj = Product()
            obj.is_published = True            
            obj.seo_title = row[0]
            obj.description = "-"


        def assign_value(o, attribute, value):
            nonlocal new_obj            
            if getattr(o, attribute) !=value:
                setattr(o, attribute, value)
                new_obj = True

        assign_value(obj, "seo_description", row[3])        
        assign_value(obj, "description", "KOD: "+ row[3] + "\n\n")
        assign_value(obj, "seo_title", row[0])
        assign_value(obj, "name", row[2] + " (" + row[0] + ")")
        assign_value(obj, "group",  row[1])
        
        if row[7] in product_types:
            obj.product_type = product_types[row[7]]
        else:
            obj.product_type = product_types['INNE']
    
        key = row[5][:2]

        if key in product_categories:
            obj.category = product_categories[key]
        else:
            obj.category = product_categories['99']
        if row[19]:
            obj.price = Money(row[19], "PLN")
        else:
            obj.price = Money(0, "PLN")
        
        if new_obj:
            obj.save()

        assign_attr(obj, 'pd_S7', row[8+7], product_attributes)
        assign_attr(obj, 'pd_S9', row[8+9], product_attributes)
        assign_attr(obj, 'pd_S6', row[8+6], product_attributes)
        assign_attr(obj, 'pd_S3', row[8+3], product_attributes)
        
                        
        if row[9] == 'POLBRUK' and row[10] in styles and styles[row[10]]>1:
            slug = slugify(row[10])
            elements =  Collection.objects.filter(slug = slug)
            elements[0].products.add(obj)

    for pos in old_products:
        x = Product.objects.filter(seo_title=pos)
        if len(x)>0:
            x[0].is_published = False
            x[0].save()

    return HttpResponse("OK")

@csrf_exempt
def sync_stack(request):    
    data = json.loads(request.POST.get('data'))
    
    to_create = []
    to_update = []
    
    to_delete = []
    for obj in ProductVariant.objects.all().exclude(sku='paleta'):
        to_delete.append(obj.pk)

    in_database = {}
    
    products = {}
    
    object_list = ProductVariant.objects.all().select_related('product')
    for obj in object_list:
        in_database[obj.sku] = obj
    object_list2 = Product.objects.all()
    for obj in object_list2:
        products[obj.seo_title] = obj
            
    for row in data:
        new_obj = False
        key = row[1]+"/"+row[0]+"/"+row[5]
        
        if row[1] in products:
            product = products[row[1]]
        else:
            continue
        
        if key in in_database:
            obj = in_database[key]
            if obj.pk in to_delete:
                to_delete.remove(obj.pk)
        else:
            obj = ProductVariant()
            obj.sku = key 
            obj.product = product                
            obj.quantity_allocated = 0
            new_obj = True
        if row[0] != row[5]:
            if row[5] in MAG_MAP:
                obj.name = MAG_MAP[row[0]] + " (partia wyprodukowana w:"+row[5]+")"
            else:
                obj.name = MAG_MAP[row[0]] + " (partia "+row[5]+")"
        else:
            obj.name = MAG_MAP[row[0]] #+"/"+row[1]            
        obj.param1 = row[0]
        obj.param2 = row[5]
        
        if row[8] and row[8] != 0 and row[8] != 1:
            obj.price_override = product.price * Decimal(row[8])
            obj.quantity = int(row[3] / row[8])
            obj.cost_price = product.price * Decimal(row[8])
        else:
            obj.price_override = product.price
            obj.quantity = row[3] 
            obj.cost_price = product.price
            
        obj.unit = row[7]
        obj.unit_description = row[9]
        obj.unit2 = row[4]

        obj.weight = row[10]
        obj.weight2 = row[6]
        obj.converter = row[8]
        
        obj.quantity2 = row[3]
        obj.price2 = product.price            

        if new_obj:
            to_create.append(obj)
            if len(to_create)>500:
                ProductVariant.objects.bulk_create(to_create)
                to_create = []
        else:
            to_update.append(obj)
            if len(to_update)>500:
                ProductVariant.objects.bulk_update(to_update, ['name', 'quantity', 'quantity_allocated'])
                to_update = []                
    
    if to_delete:
        for pk in to_delete:
            ProductVariant.objects.get(pk=pk).delete()
    if to_create:
        ProductVariant.objects.bulk_create(to_create)
    if to_update:
        ProductVariant.objects.bulk_update(to_update, ['name', 'quantity', 'quantity_allocated'])
    return HttpResponse("OK")

@csrf_exempt
def sync_price_list(request):

    PriceDoc.objects.all().delete()

    data = json.loads(request.POST.get('data'))
    
    in_database = {}
    for obj in PriceDoc.objects.all():
        key = obj.platnik+"/"+obj.budowa+"/"+obj.mag+"/"+obj.group
        in_database[key] = [obj.koszt_tr, obj.cena, False]
    to_create = []
    to_update = []
    l = 0
    for row in data:        
        l = l+1
        key = row[1]+"/"+row[2]+"/"+row[9]+"/"+row[4]
        if key in in_database:
                objd = in_database[key]
                objd[2] = True
                if not (objd[0] == row[5] and objd[1] == row[6]):
                    obj = PriceDoc.objects.filter(platnik=row[1], budowa=row[2], mag=row[9], group=row[4])[0]
                    obj.doc_name = row[0]
                    obj.symkar = row[3]
                    obj.koszt_tr = row[5]
                    obj.cena = row[6]
                    to_update.append(obj)
                    if len(to_update)>500:
                        bulk_update(to_update)
                        to_update = []
        else:
            obj = PriceDoc()
            obj.platnik = row[1]
            obj.budowa = row[2]
            obj.mag = row[9]
            obj.group = row[4]
            obj.doc_name = row[0]
            obj.symkar = row[3]
            obj.koszt_tr = row[5]
            obj.cena = row[6]
            to_create.append(obj)
                
            if len(to_create)>500:
                PriceDoc.objects.bulk_create(to_create)
                to_create = []

    if to_create:
        PriceDoc.objects.bulk_create(to_create)
    if to_update:
        bulk_update(to_update)
        
    for key, value in in_database.items():
        if not value[2]:
            platnik, budowa, mag, group = key.split('/')
            PriceDoc.objects.filter(platnik=platnik, budowa=budowa, mag=mag, group=group).delete()

    return HttpResponse("OK")

@csrf_exempt
def sync_orders(request):
    return HttpResponse("OK")



@csrf_exempt
def sync_sale(request):
    data = json.loads(request.POST.get('data'))
    for row in data:
        obj = UserData()
        obj.typ = row[0]
        obj.row_id = int(row[1])
        obj.platnik = row[2]
        obj.budowa = row[3]
        obj.magazyn = row[4]
        obj.json_row = row[5]

        if obj.row_id==-1:
            q1 = UserData.objects.filter(typ=obj.typ)
            if obj.platnik:
                q1 = q1.filter(platnik=obj.platnik)
            if obj.budowa:
                q1 = q1.filter(budowa=obj.budowa)
            if obj.magazyn:
                q1 = q1.filter(magazyn=obj.magazyn)
            q1.delete()
        else:
            obj.save() 
    return HttpResponse("OK")


def add_txt(request, symkar, name, data):
    x = Product.objects.filter(seo_title=symkar)
    if len(x) > 0:
        obj = x[0]
        if '<br />' in obj.description:
            x = obj.description.split('<br />', 1)
            obj.description = x[0] + "<br />" + data
        else:
            obj.description = obj.description + "<br />" + data
        obj.save()

    return HttpResponse("OK")

@csrf_exempt
def list_images(request):    
    ret = []
    object_list = ProductImage.objects.all()
    for obj in object_list:
        ret.append((obj.product.seo_title, obj.alt))
    return HttpResponse(json.dumps(ret))

@csrf_exempt
def add_image(request, symkar, name):
    x = Product.objects.filter(seo_title=symkar)
    if len(x) > 0:
        data = io.BytesIO(request.body)
        z = zipfile.ZipFile(data)
        names = z.namelist()
        data2 = z.read(names[0])
        data3 = io.BytesIO(data2)
        
        try:
            image = Image.open(data3)
        except:
            if '.txt' in name.lower():
                try:
                    data4 = data2.decode('utf-8')                    
                except:
                    try:
                        data4 = data2.decode('cp-1250')
                    except:
                        return HttpResponse("ERROR")
                return add_txt(request, symkar, name, data4)
            return HttpResponse("ERROR")
        obj = x[0]
        img = ProductImage()
        img.product = obj
        img.alt = name
        img.image.save(str(symkar)+":"+datetime.datetime.now().isoformat()+".jpeg", data3, True)
        img.save()

    return HttpResponse("OK")

@csrf_exempt
def remove_image(request, symkar, name):
    x = Product.objects.filter(seo_title=symkar)
    if len(x) > 0:
        if name == '-':
            n = ""
        else:
            n = name        
        images = x[0].images.filter(alt=n)
        if len(images) > 0:
            images[0].delete()
    return HttpResponse("OK")

