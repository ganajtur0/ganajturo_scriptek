#!/usr/bin/python3

import requests
import json
import re
import tabulate
from datetime import datetime, timedelta
import curselect
import os

api_url="https://menetrendek.hu/menetrend/interface/index.php"

def megallo_query(q):
    r = requests.post(api_url, json={"func":"getStationOrAddrByTextC",
                                     "params":{
                                         "inputText":q,
                                         },
                                         "networks":[1,2,3,10,11,12,13,14,24,25],
                                         "searchIn":["stations"],
                                         "searchDate":datetime.today().strftime("%Y-%m-%d"),
                                         "maxResults":50,
                                     },)
    print(r.json())
    return r.json()["results"]

def route_query(datum, honnan, hova):
    r = requests.post(api_url,
    json={
            "func":"getRoutes",
            "params": {
                "datum":datum,
                "erk_stype":"megallo",
                "honnan":honnan["lsname"],
                "honnan_ls_id":honnan["ls_id"],
                "honnan_settlement_id":honnan["settlement_id"],
                "honnan_site_code":honnan["site_code"],
                "hova":hova["lsname"],
                "hova_ls_id":hova["ls_id"],
                "hova_settlement_id":hova["settlement_id"],
                "hova_site_code":hova["site_code"],
                "naptipus":"0",
                "hour":"69",
                "min":"420",
                "preferencia":"0"
            }
        })
    return r.json()["results"]["talalatok"]

def date_test(datum):
    if bool(re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", datum)):
        return datum
    elif bool(re.match("ma", datum, re.IGNORECASE)):
        return datetime.today().strftime("%Y-%m-%d")
    elif bool(re.match("holnap", datum, re.IGNORECASE)):
        return (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    return None

honnan=input("honnan> ")

honnan_megallok=megallo_query(honnan)

if len(honnan_megallok) == 0:
    print("Nincs találat!")
    exit(1)

menu = curselect.CurSelect([megallo["lsname"] for megallo in honnan_megallok], honnan + ": ")
honnan = honnan_megallok[menu.activate()]

hova=input("hova> ")

hova_megallok=megallo_query(hova)

if len(hova_megallok) == 0:
    print("Nincs találat!")
    exit(1)

menu = curselect.CurSelect([megallo["lsname"] for megallo in hova_megallok], hova+": ")
hova = hova_megallok[menu.activate()]

datum=date_test(input("mikor (ma/holnap/éééé-hh-nn)> "))

if not datum:
    print("Nem értem, mikor. :(")
    exit(1)

routes = route_query(datum, honnan, hova)

table = []
i=1
while True:

    key = str(i)
    
    if key in routes:
        res = routes[key]
        table.append([res["indulasi_ido"],res["erkezesi_ido"],res["osszido"],str(res["totalFare"])+" Ft"])
        i+=1
    else:
        break

headers = ["indulás", "érkezés", "menetidő", "jegyár"]

print(tabulate.tabulate(table, headers=headers))
