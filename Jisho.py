import csv
import os
import sys
from dotenv import load_dotenv
from typing import List
from selenium import webdriver


HEADERS = [
    "Kanji", "Meanings", "Kun'yomi", "On'yomi", "JLPT", "Frequency (Out of 2500)", "Kun'yomi Examples", "On'yomi examples"
]


def clean_fun(words_arr: List):
    words_arr = words_arr.split(" ")
    words_arr[1] = words_arr[1].replace("【", "(").replace("】", ")")
    words_arr.insert(2, ":")
    words_arr = " ".join(map(str, words_arr))
    return words_arr


def clean_words(words: List):
    words_arr = words.text.split('\n')
    cleaned_words = '\n'.join([clean_fun(word) for word in words_arr][1:])
    return cleaned_words


def get_field(xpath, pattern="", alt_pattern="", position=1, info_array=[], words=False):
    try:
        field = driver.find_element_by_xpath(xpath)
        if pattern in field.text:
            if not words:
                info_array.append(field.text.replace(pattern, ""))
                return
            info_array.append(clean_words(field))
            return
        else:
            info_array.append("")
            if not words:
                info_array.append(field.text.replace(alt_pattern, ""))
                return
            info_array.append(clean_words(field))
    except:
        if len(info_array) < position:
            info_array.append("")


def get_kanji_info(driver):
    kanji_info = []
    kanji_xpath = "/html/body/div[3]/div/div/div[1]/div/div[1]/div[1]/div/div[1]/h1"
    get_field(kanji_xpath, info_array=kanji_info)
    meanings_xpath = "/html/body/div[3]/div/div/div[1]/div/div[1]/div[2]/div/div[1]/div[1]"
    get_field(meanings_xpath, info_array=kanji_info)
    kun_reading_xpath = "/html/body/div[3]/div/div/div[1]/div/div[1]/div[2]/div/div[1]/div[2]/dl[1]"
    get_field(
        kun_reading_xpath, pattern="Kun: ", alt_pattern="On: ", position=3, info_array=kanji_info
    )
    on_reading_xpath = "/html/body/div[3]/div/div/div[1]/div/div[1]/div[2]/div/div[1]/div[2]/dl[2]"
    get_field(
        on_reading_xpath, pattern="On: ", alt_pattern="", position=4, info_array=kanji_info
    )
    jlpt_xpath = "/html/body/div[3]/div/div/div[1]/div/div[1]/div[2]/div/div[2]/div/div[2]"
    get_field(
        jlpt_xpath, pattern="JLPT level", position=5, info_array=kanji_info
    )
    frequency_xpath = "/html/body/div[3]/div/div/div[1]/div/div[1]/div[2]/div/div[2]/div/div[3]"
    get_field(
        frequency_xpath, pattern=" of 2500 most used kanji in newspapers", position=6, info_array=kanji_info
    )
    kun_words_xpath = "/html/body/div[3]/div/div/div[1]/div/div[3]/div[2]/div/div/div[1]/div[2]"
    get_field(
        kun_words_xpath, pattern="Kun", alt_pattern="", position=7, info_array=kanji_info, words=True
    )
    on_words_xpath = "/html/body/div[3]/div/div/div[1]/div/div[3]/div[2]/div/div/div[1]/div[1]"
    get_field(
        on_words_xpath, pattern="On", alt_pattern="", position=8, info_array=kanji_info, words=True
    )
    return kanji_info


if __name__ == "__main__":
    load_dotenv()
    DRIVER_PATH = os.getenv('DRIVER_PATH')
    try:
        SOURCE = sys.argv[1]
        OUTPUT = sys.argv[2]
    except:
        print("Bad arguments.\nUse: jisho_scrapper <Source> <Output file>")
        sys.exit(1)
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)
    driver.get(SOURCE)
    try:
        file = open(OUTPUT, "w", encoding="UTF8", newline='')
    except:
        print("Not a valid output file.")
        driver.quit()
        sys.exit(1)
    writer = csv.writer(file)
    writer.writerow(HEADERS)
    while True:
        kanjis = driver.find_elements_by_class_name(
            "character"
        )
        for i in range(len(kanjis)):
            kanjis[i].click()
            kanji_info = get_kanji_info(driver)
            writer.writerow(kanji_info)
            driver.back()
            kanjis = driver.find_elements_by_class_name(
                "character"
            )
        try:
            more = driver.find_element_by_class_name("more")
        except:
            break
        more.click()
    file.close()
    driver.quit()
