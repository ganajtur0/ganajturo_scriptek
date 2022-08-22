#!/usr/bin/python3

import curses

class CurSelect:

    def __init__(self, items, title=None, window=None, pagination=10, char='| ', ret_type="index", highlight=curses.A_STANDOUT):

        if window == None:
            self.auto_init = True
            self.window = self._start_curses()
        else:
            self.window = window
            self.auto_init = False

        self.char = char
        self.pag_start = 0
        self.y = 0
        self.items = items
        self.item_count = len(items)
        self.highlight = highlight
        self.pagination = pagination
        self.current_selection = 0
        self.ret_type = ret_type
        if title:
            self.offset = 3
        else:
            self.offset = 0
        self.title = title

    def _start_curses(self):
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        curses.curs_set(False)
        return stdscr

    def _end_curses(self):
        self._clear()
        curses.curs_set(True)
        curses.nocbreak()
        self.window.keypad(False)
        curses.echo()
        curses.endwin()

    def _clear_line(self, line_num):
        self.window.move(line_num, 0)
        self.window.clrtoeol()

    def _display_item(self, index, attr=0):
        if self.pag_start + index > self.item_count-1:
            return
        self.window.addstr(index+self.offset, 0, self.char+self.items[self.pag_start+index], attr)

    def _update(self, direction):
        self._display_item(self.y+direction)
        self._display_item(self.y, self.highlight)
        self.window.refresh()

    def _clear(self):
        for i in range(self.pagination+2):
            self._clear_line(self.offset + i)

    def _display(self):
        for i in range(self.pagination):
            self._display_item(i)
        self._update(0)

    def activate(self):

        if self.title:
            self.window.addstr(0, 0, self.title, curses.A_BOLD)

        self._display()

        while True:
            try:
                self.window.addstr(self.pagination+1+self.offset, 0, "=== page "+str(self.current_selection//self.pagination+1)+" ===")
                self.window.addstr(self.pagination+2+self.offset, 0, "=== item "+str(self.current_selection+1)+" ===")
                c = self.window.getch()

                if c == ord('q'):
                    if self.auto_init:
                        self._end_curses()
                    return None

                elif c == curses.KEY_ENTER or c == 10:
                    if self.auto_init:
                        self._end_curses()
                    if (self.ret_type=="index"):
                        return self.current_selection
                    elif (self.ret_type=="value"):
                        return self.items[self.current_selection]

                elif c == curses.KEY_DOWN:

                    if self.y < self.pagination-1 and self.current_selection < self.item_count - 1:
                        self.y+=1
                        self.current_selection+=1
                        self._update(-1)
                    elif not (self.pag_start + self.pagination > self.item_count-1):
                        self.y = 0
                        self.current_selection+=1
                        self.pag_start+=self.pagination
                        self._clear()
                        self._display()
                        continue

                elif c == curses.KEY_UP:

                    if self.y > 0 and self.current_selection > 0:
                        self.y-=1
                        self.current_selection-=1
                        self._update(1)
                    elif not (self.pag_start - self.pagination < 0):
                        self.y = self.pagination - 1 
                        self.current_selection-=1
                        self.pag_start-=self.pagination
                        self._clear()
                        self._display()
                        continue

            except KeyboardInterrupt:
                if self.auto_init:
                    self._end_curses()
                return None
import requests
import json
import re
import tabulate
from datetime import datetime, timedelta

api_url="https://menetrendek.hu/menetrend/interface/index.php"

def megallo_query(q):
    r = requests.post(api_url, json={"func":"getStationOrAddrByText", "params":{"inputText":q}})
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

menu = CurSelect([megallo["lsname"] for megallo in honnan_megallok], honnan + ": ")
honnan = honnan_megallok[menu.activate()]

hova=input("hova> ")

hova_megallok=megallo_query(hova)

if len(hova_megallok) == 0:
    print("Nincs találat!")
    exit(1)

menu = CurSelect([megallo["lsname"] for megallo in hova_megallok], hova+" : ")
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
