import datetime
import json

from django.template.loader import get_template
from django.template import Context

from big_company.models import UserData, get_profile
from django.template.response import TemplateResponse

def page_promocje(request, page, is_visible):    
    profile = get_profile()

    if profile:
        platnik = profile.platnik
        budowa = profile.budowa
        magazyn = profile.magazyn
    else:
        platnik = '34543'
        budowa = ""
        magazyn = ""       
    
    platnik = '9616'

    deklaracje = UserData.objects.filter(typ='deklaracje', platnik=platnik)
    punkty = UserData.objects.filter(typ='punkty', platnik=platnik)
    punkty_nal = UserData.objects.filter(typ='punkty_nal', platnik=platnik)
    punkty_wyk = UserData.objects.filter(typ='punkty_wyk', platnik=platnik)

    context = { 'page': page, 'is_visible': is_visible, 'deklaracje': deklaracje, 'punkty': punkty, 'punkty_nal': punkty_nal, 'punkty_wyk': punkty_wyk }

    return TemplateResponse(request,'pages/promotion.html', context)


def page_informacjefin(request, page, is_visible):
    profile = get_profile()

    if profile:
        platnik = profile.platnik
        budowa = profile.budowa
        magazyn = profile.magazyn
    else:
        platnik = '34543'
        budowa = ""
        magazyn = ""       
    platnik = '9616'

    def _get_value(tab):
        if len(tab)>0:                        
            row = tab[0].get_row()
            if row:
                if len(row)>0 and row[0]:
                    return row[0]
                else:
                    return 0
        return 0

    limit = _get_value(UserData.objects.filter(typ='limit', platnik=platnik))
    saldo = _get_value(UserData.objects.filter(typ='saldo', platnik=platnik))
    stan = _get_value(UserData.objects.filter(typ='stan', platnik=platnik))
    nierozliczone = _get_value(UserData.objects.filter(typ='nierozliczone', platnik=platnik))
    nierozzal = _get_value(UserData.objects.filter(typ='nierozzal', platnik=platnik))
    context = {'page': page, 'is_visible': is_visible, 'limit': limit, 'saldo': saldo, 'stan': stan, 'nierozliczone': nierozliczone, 'nierozzal': nierozzal}
    
    return TemplateResponse(request,'pages/informacjefin.html', context)
