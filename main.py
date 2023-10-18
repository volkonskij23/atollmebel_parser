from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json
import time


"""
    Функция чтения json-файла

    :param     filename: Название файла
    :type      filename: str.
    
    :returns: dict или list
"""


def json_load(filename):
    with open(filename, "r", encoding="utf8") as read_file:
        result = json.load(read_file)
    return result


"""
    Функция записи в json-файл

    :param     filename: Название файла
    :type      filename: str.
    :param     data: Записываемые данные
    :type      data: list or dict.
  
"""


def json_dump(filename, data):
    with open(filename, "w", encoding="utf8") as write_file:
        json.dump(data, write_file, ensure_ascii=False)


"""
    Функция получения списка ссылок на товар
    
    :returns: list
"""


def get_urls():

    urls_list = []
    page = 1
    while True:
        try:
            resp = requests.get(
                "https://store.tildacdn.com/api/getproductslist/?storepartuid=473505895571&recid=464366228&c={}&slice={}&getparts=true&size=36".format(
                    time.time(), page
                )
            ).json()

            print(str(page) + "/" + str(len(resp["products"])))
            if len(resp["products"]) > 0:

                for product in resp["products"]:
                    urls_list.append(product["url"])
            else:
                break

        except:
            json_dump("urls_json.json", urls_list)
            continue
        page += 1
        time.sleep(1)

    return urls_list


urls_list = get_urls()
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

try:
    result = json_load("result.json")
except:
    result = {}


for url in urls_list:
    if url not in result.keys():
        try:
            result[url] = {}
            result[url]["imgs"] = []
            driver.get(url)
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (
                        By.CLASS_NAME,
                        "js-store-price-wrapper.t-store__prod-popup__price-wrapper",
                    )
                )
            )

            while True:

                img_block = driver.find_element(
                    By.CLASS_NAME, "t-slds__thumbsbullet-wrapper"
                )

                for link in img_block.find_elements(
                    By.CLASS_NAME, "t-slds__bgimg.t-bgimg.loaded"
                ):
                    result[url]["imgs"].append(link.get_attribute("data-original"))

                if len(result[url]["imgs"]) > 0:
                    break

            result[url]["name"] = driver.find_element(
                By.CLASS_NAME, "t-store__prod-popup__title-wrapper"
            ).text

            result[url]["path"] = ""
            result[url]["price"] = driver.find_element(
                By.CLASS_NAME,
                "js-store-prod-price.t-store__prod-popup__price.t-store__prod-popup__price-item.t-name.t-name_md",
            ).text
            result[url]["desc"] = ""

            props = driver.find_element(
                By.CLASS_NAME, "t-store__tabs__content.t-descr.t-descr_xxs"
            )

            lines = props.text.split("\n")
            strongs = props.find_elements(By.TAG_NAME, "strong")
            for strong in strongs:
                key_name = strong.text.replace(":", "")
                result[url][key_name] = []
                for line in lines:
                    if strong.text in line:
                        result[url][key_name].append(line.replace(strong.text, ""))
                        for prop_line in lines[lines.index(line) + 1 :]:
                            if strongs.index(strong) == len(strongs) - 1:
                                result[url][key_name].append(prop_line)
                            elif (
                                strongs.index(strong) != len(strongs) - 1
                                and strongs[strongs.index(strong) + 1].text
                                not in prop_line
                            ):
                                result[url][key_name].append(prop_line)
                            else:
                                break

            print(result[url])
        except Exception as e:
            json_dump("result.json", result)
            print(e)
            continue

        if len(result) % 10 == 0:
            json_dump("result.json", result)
