"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie (Election Scraper)
author: Václav Holub
email: vaclavholub5@seznam.cz
discord: .avalok
"""
import os
import csv
import sys
import requests as rq
from bs4 import BeautifulSoup as bs


"""
Vložení vstupních parametrů
    uživatel při spouštění programu přes příkazový řádek musí poskytnout 2 argumenty
        1. je odkaz na územní celek, který chce zpracovat takže pro Prostějov např. 
            https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103
        2. je jméno výstupního souboru (např. vysledky_prostejov.csv)
to se udělá pomocí podmínky, že sys.argv musí obsahovat platný odkaz (nejspíš to jde udělat tak, že string musí obsahovat "volby.cz")
a také druhý argument, což by mělo jít ošetřit pomocí podmínky len(sys.argv) == 3

Získání odkazů k relevnatním datům
    na odkazu poskytnutém uživatelem vyberu všechy <tr> elementy
        uložím informace ze všech jejich <tr> child elementů tedy:
            číslo - název a hrefu
            název - název obce
            odkaz na výběr okrsku - a href
        tyto inforamce uložím do dictu, do kterého budou následně uloženy i samotná volební data
        tento dict uložím do master dictu celého okrsku
    odkaz vedoucí k volebním datům může u některých obcí vést na další podvýběr okrsků
    v tom případě do separátního listu, uložím všechy a hraf obsažené v elementu <td> s headers="s1"     
        tento list uložím do dictu dané obce v master dictu

Vypsání volebních údajů
    data, která mě zajímají a budou tvořit jeden řádek v csv:
        kód obce,
            získán v přechozím kroku při sběru odkazů - uložen v dictu dané obce
        název obce,
            získán v přechozím kroku při sběru odkazů - uložen v dictu dané obce
        voliči v seznamu,
            uloženo v elementu <td> s headers="sa2" - vzit a uložit do dictu obce jako key = "registered", value = "number"
        vydané obálky
            uloženo v elementu <td> s headers="sa3" - vzit a uložit do dictu obce jako key = "envelopes", value = "number"
        platné hlasy
            uloženo v elementu <td> s headers="sa6" - vzit a uložit do dictu obce jako key = "valid", value = "number"
        kandidující strany (počet hlasů pro všechny hlasy, i když je to 0)
            vzít všechny <tr> elementy 
            z každého <tr> elementu uložit do dictu obce jako key <td> element s class="overflow_name" (jméno strany)
            a jako value <td> element s headers="t1sa2 t1sb3"
    poté co se v loopu zvolí odkaz na stránku dané obce, se musí zavolat request.get na danný odkaz, který se uloží do dočasné proměnné response
    pak se musí pomocí bs parsovat obsah proměnné response a uložit do dočasné proměnné content
        poté získat data dle popisu nahoře
    přejít v loopu na další odkaz a zopakovat to samé

Export do CSV


"""

sys.argv.extend(
    [
        "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103",
        "prostejov_results.csv",
    ]
)


def system_arg_validity() -> None:
    if (
        len(sys.argv) != 3
        or "volby.cz" not in sys.argv[1]
        or sys.argv[2][-4:] != ".csv"
    ):
        print("Zadejte 2 validni argumenty.")
        sys.exit()


def main():
    system_arg_validity()


main()
"""
years = [2016, 2017, 2018, 2019, 2020, 2021]


def format_link(year: int):
    return f"https://cs.wikipedia.org/wiki/Wikipedie:%C4%8Cl%C3%A1nek_t%C3%BDdne/{year}"


def get_parsed_page(link: str) -> list:
    response = rq.get(link)
    return bs(response.text, features="html.parser")


def a_tag_extractor(parsed_text: list) -> list:
    a_tags = list()
    a_tags = parsed_text.find_all("a", {"class": "mw-file-description"})
    return a_tags


def title_extractor(a_tags: list):
    title_list = list()
    for a in a_tags:
        if "title" in a.attrs:
            title_list.append(a.attrs["title"].replace("\xa0", " "))
        else:
            title_list.append("Chybí klíč 'title'")
    return title_list


def csv_exporter(articles: dict):
    with open(
        os.path.join("articles_list_2016-2021.csv"),
        mode="w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.writer(file)
        for i in articles:
            for k in articles[i]:
                writer.writerow([k])


def main():
    all_articles = dict()
    for year in years:
        parsed_text = get_parsed_page(format_link(year))
        a_tags = a_tag_extractor(parsed_text)
        all_articles[year] = title_extractor(a_tags)
    csv_exporter(all_articles)


main()
"""
