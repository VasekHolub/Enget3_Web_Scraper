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
import re
from bs4 import BeautifulSoup as bs


"""
Vložení vstupních parametrů
    uživatel při spouštění programu přes příkazový řádek musí poskytnout 2 argumenty
        1. je odkaz na územní celek, který chce zpracovat takže pro Prostějov např. 
            https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103
        2. je jméno výstupního souboru (např. vysledky_prostejov.csv)
to se udělá pomocí podmínky, že sys.argv musí obsahovat platný odkaz (nejspíš to jde udělat tak, že string musí obsahovat "volby.cz" a konec druheho stringu ".csv")
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
        kandidující strany (počet hlasů pro všechny strany, i když je to 0)
            vzít všechny <tr> elementy 
            z každého <tr> elementu uložit do dictu obce jako key <td> element s class="overflow_name" (jméno strany)
            a jako value <td> element s headers="t1sa2 t1sb3"
    poté co se v loopu zvolí odkaz na stránku dané obce, se musí zavolat request.get na danný odkaz, který se uloží do dočasné proměnné response
    pak se musí pomocí bs parsovat obsah proměnné response a uložit do dočasné proměnné content
        poté získat data dle popisu nahoře
    přejít v loopu na další odkaz a zopakovat to samé

Export do CSV


"""
# For dev purposes - delete later
sys.argv.extend(
    [
        "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=4&xnumnuts=3201",
        "prostejov_results.csv",
    ]
)


def system_argv_validity() -> None:
    if (
        len(sys.argv) != 3
        or "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&x" not in sys.argv[1]
        or sys.argv[2][-4:] != ".csv"
    ):
        print("Input 2 valid arguments.")
        sys.exit()


def html_parser(URL) -> str:
    response = rq.get(URL)
    if response.status_code == 200:
        return bs(response.text, features="html.parser")
    else:
        print(f"URL error {response.status_code}")


def td_tag_extractor(parsed_html: str) -> list:
    return parsed_html.find_all("td", {"class": "cislo"})


def town_name_extractor(parsed_html):
    names = list()
    for name in parsed_html.find_all("td", {"class": "overflow_name"}):
        names.append(name.text)
    return names


def town_ID_extractor(td_tags):
    town_id = list()
    for tag in td_tags:
        town_id.append(tag.find("a").text)
    return town_id


def link_extractor(td_tags):
    links = list()
    for link in td_tags:
        try:
            if link.find("a")["href"][:2] == "ps" and link.find("a")["href"] not in [
                "ps?xjazyk=CZ",
                "ps3?xjazyk=CZ",
            ]:
                links.append("https://volby.cz/pls/ps2017nss/" + link.find("a")["href"])
        except TypeError:
            break
    return links


def master_dict_builder(town_IDs, town_names, town_links):
    master_dict = dict()
    count = 0
    while count <= len(town_IDs) - 1:
        keys = ["ID", "Name", "URL"]
        values = [town_IDs[count], town_names[count], town_links[count]]
        town_dict = dict(zip(keys, values))
        master_dict[count] = town_dict
        count += 1
    return master_dict


def individual_page_data(master_dict):
    for i in master_dict:
        content = html_parser(master_dict[i]["URL"])
        registered = content.find("td", {"headers": "sa2"})
        master_dict[i]["Registered"] = registered.text.replace("\xa0", " ")
        envelope = content.find("td", {"headers": "sa3"})
        master_dict[i]["Envelopes"] = envelope.text.replace("\xa0", " ")
        valid = content.find("td", {"headers": "sa6"})
        master_dict[i]["Valid"] = valid.text.replace("\xa0", " ")
        master_dict[i].update(party_scrape(content))


def party_scrape(content):
    p_party = content.find_all("td", {"class": "overflow_name"})
    p_party_list = list()
    for i in p_party:
        p_party_list.append(i.text)
    votes = content.find_all("td", {"headers": ["t1sa2 t1sb3", "t2sa2 t2sb3"]})
    votes_list = list()
    for i in votes:
        votes_list.append(i.text)
    party_dict = dict(zip(p_party_list, votes_list))
    return party_dict


def main():
    system_argv_validity()
    td_tags = td_tag_extractor(html_parser(sys.argv[1]))
    town_links = link_extractor(td_tags)
    town_IDs = town_ID_extractor(td_tags)
    town_names = town_name_extractor(html_parser(sys.argv[1]))
    master_dict = master_dict_builder(town_IDs, town_names, town_links)
    individual_page_data(master_dict)
    print(master_dict)


if __name__ == "__main__":
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
