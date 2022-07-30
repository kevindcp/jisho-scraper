import csv
import os
import sys
from dotenv import load_dotenv
from typing import List
from selenium import webdriver


HEADERS = [
    "Kanji", "Kun'yomi", "On'yomi", "JLPT", "Frequency (Out of 2500)", "Kun'yomi Examples", "On'yomi examples"
    ]
def clean_words(words: List):
    words_arr = words.text.split('\n')
    for i in range(len(words_arr)):
        words_arr[i] = words_arr[i].split(" ")
        words_arr[i] = words_arr[i][0:2]
        words_arr[i][1] = words_arr[i][1].replace("【","(").replace("】", ")")
        words_arr[i] = " ".join(map(str,words_arr[i]))
    cleaned_words = "\n".join(words_arr[1:])
    return cleaned_words

def get_kanji_info(driver):
    kanji_info = []
    kanji = driver.find_element_by_xpath(
        "/html/body/div[3]/div/div/div[1]/div/div[1]/div[1]/div/div[1]/h1"
        )
    kanji_info.append(kanji.text)
    try:
        kun_readings = driver.find_element_by_xpath(
        "/html/body/div[3]/div/div/div[1]/div/div[1]/div[2]/div/div[1]/div[2]/dl[1]"
        )
        if "Kun:" in kun_readings.text:
            kanji_info.append(kun_readings.text.replace("Kun: ", ""))
        else: 
            kanji_info.append("")
            on_readings = kun_readings
            kanji_info.append(on_readings.text.replace("On: ", ""))
    except:
        kanji_info.append("")
    try:
        on_readings = driver.find_element_by_xpath(
            "/html/body/div[3]/div/div/div[1]/div/div[1]/div[2]/div/div[1]/div[2]/dl[2]"
            )
        if "On:" in on_readings.text:
            kanji_info.append(on_readings.text.replace("On: ", ""))
    except:
        if len(kanji_info) < 3: kanji_info.append("")
    try:
        jlpt = driver.find_element_by_xpath(
            "/html/body/div[3]/div/div/div[1]/div/div[1]/div[2]/div/div[2]/div/div[2]"
            ) 
        kanji_info.append(jlpt.text.replace("JLPT level ", ""))
    except:
        kanji_info.append("")
    try:
        frequency = driver.find_element_by_xpath(
            "/html/body/div[3]/div/div/div[1]/div/div[1]/div[2]/div/div[2]/div/div[3]"
            )
        if "of 2500 most used kanji in newspapers" in frequency.text:
            kanji_info.append(frequency.text.replace(" of 2500 most used kanji in newspapers", ""))
    except:
        kanji_info.append("")
    try:
        words_kun = driver.find_element_by_xpath(
            "/html/body/div[3]/div/div/div[1]/div/div[3]/div[2]/div/div/div[1]/div[2]"
            )
        if "Kun" in words_kun.text:
            kanji_info.append(clean_words(words_kun))
        else:
            kanji.append("")
            words_on = words_kun
            kanji_info.append(clean_words(words_on))
    except:
        kanji_info.append("")
    try:
        words_on = driver.find_element_by_xpath(
            "/html/body/div[3]/div/div/div[1]/div/div[3]/div[2]/div/div/div[1]/div[1]"
            )
        if "On" in words_on.text:
            kanji_info.append(clean_words(words_on))
    except:
        if len(kanji_info) < 7: kanji_info.append("")
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