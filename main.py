"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie (Election Scraper)
author: Václav Holub
email: vaclavholub5@seznam.cz
discord: .avalok
"""
from os import path
import csv
import sys
import requests as rq
from bs4 import BeautifulSoup as bs
import pandas as pd
import pathvalidate


def system_argv_validity() -> None:
    try:
        pathvalidate.validate_filename(sys.argv[2])
        if (
            len(sys.argv) != 3
            or "https://volby.cz/pls/ps2017nss/" not in sys.argv[1]
            or sys.argv[2][-4:] != ".csv"
        ):
            print(
                "Input two valid arguments.\nThe first argument must contain a part of the following url: https://volby.cz/pls/ps2017nss/\nThe second argument must end in .csv"
            )
            sys.exit()
    except pathvalidate.error.InvalidCharError:
        print(
            "Second argument contains forbidden characters.\nPlease refer to your OS file naming conventions."
        )
        sys.exit()


def html_parser(URL: str) -> bs:
    response = rq.get(URL)
    if response.status_code == 200:
        return bs(response.text, features="html.parser")
    else:
        print(f"URL error {response.status_code}")
        sys.exit()


def town_name_extractor(parsed_html: bs, town_ids) -> list:
    names = list()
    td_tags_overflow = parsed_html.find_all("td", {"class": "overflow_name"})
    td_tags_alternate = parsed_html.find_all(
        "td", {"headers": ["t1sa1 t1sb2", "t2sa1 t2sb2", "t3sa1 t3sb2"]}
    )
    if len(td_tags_overflow) < len(town_ids):
        for name in td_tags_alternate:
            names.append(name.text)
        for name in td_tags_alternate:
            if name.find("a") != None:
                names.append(name.find("a").text)
    else:
        for name in td_tags_overflow:
            names.append(name.text)
    return names


def town_ID_extractor(td_tags: bs) -> list:
    town_id = list()
    for tag in td_tags:
        town_id.append(tag.find("a").text)
    return town_id


def town_link_extractor(td_tags: bs) -> list:
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


def basic_town_info_extractor(parsed_html: bs) -> list:
    td_tags = parsed_html.find_all("td", {"class": "cislo"})
    town_links = town_link_extractor(td_tags)
    town_ids = town_ID_extractor(td_tags)
    town_names = town_name_extractor(parsed_html, town_ids)
    return town_links, town_ids, town_names


def master_dict_builder(town_links: list, town_IDs: list, town_names: list) -> dict:
    master_dict = dict()
    count = 0
    while count <= len(town_IDs) - 1:
        keys = ["code", "location", "URL"]
        values = [town_IDs[count], town_names[count], town_links[count]]
        town_dict = dict(zip(keys, values))
        master_dict[count] = town_dict
        count += 1
    return master_dict


def town_page_data_extractor(master_dict: dict) -> None:
    for i in master_dict:
        content = html_parser(master_dict[i]["URL"])
        registered = content.find("td", {"headers": "sa2"})
        master_dict[i]["registered"] = registered.text.replace("\xa0", " ")
        envelope = content.find("td", {"headers": "sa3"})
        master_dict[i]["envelopes"] = envelope.text.replace("\xa0", " ")
        valid = content.find("td", {"headers": "sa6"})
        master_dict[i]["valid"] = valid.text.replace("\xa0", " ")
        master_dict[i].update(p_party_scrape(content))


def p_party_scrape(content: bs) -> dict:
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


def pandas_csv_export(master_dict: dict) -> None:
    for i in master_dict:
        master_dict[i].pop("URL")
    df = pd.DataFrame(data=master_dict).T
    df.to_csv(path.join(sys.argv[2]), sep=";", encoding="utf-8-sig", index=False)


def single_town_csv_export(master_dict: dict) -> None:
    master_dict[0].pop("URL")
    with open(
        path.join(sys.argv[2]), mode="w", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=master_dict[0].keys(), delimiter=";")
        writer.writeheader()
        writer.writerow(master_dict[0])


def main():
    system_argv_validity()
    basic_town_info = basic_town_info_extractor(html_parser(sys.argv[1]))
    master_dict = master_dict_builder(
        town_links=basic_town_info[0],
        town_IDs=basic_town_info[1],
        town_names=basic_town_info[2],
    )
    town_page_data_extractor(master_dict)
    if len(master_dict) > 1:
        pandas_csv_export(master_dict)
    else:
        single_town_csv_export(master_dict)


if __name__ == "__main__":
    main()


# Test functions that allow to go through all avaliable dictricts except 'Zahranici'
# For it to work, all sys.argv variables in the code have to be replaced with the arguments list

"""
def test():
    content = html_parser("https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ")
    c = 1
    href_list = list()
    while c < 15:
        td_tags = list()
        td = content.find_all("td", {"headers": f"t{c}sa3"})
        for i in td:
            td_tags.append(i.find_all("a"))
        for i in td_tags:
            for k in i:
                href_list.append("https://volby.cz/pls/ps2017nss/" + k.get("href"))
        c = c + 1
    href_list.remove("https://volby.cz/pls/ps2017nss/ps36?xjazyk=CZ")
    return href_list

def main_test():
    master_urls = test()
    for i in master_urls:
        argumets = [
            i,
            f"test_{master_urls.index(i)+1}_results.csv",
        ]
        system_argv_validity(argumets)
        basic_town_info = basic_town_info_extractor(html_parser(argumets[0]))
        master_dict = master_dict_builder(
            town_links=basic_town_info[0],
            town_IDs=basic_town_info[1],
            town_names=basic_town_info[2],
        )
        town_page_data_extractor(master_dict)
        if len(master_dict) > 1:
        pandas_csv_export(master_dict, argumets)
        else:
        single_town_csv_export(master_dict, argumets)
    """
