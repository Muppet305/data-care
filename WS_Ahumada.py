from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd
import numpy as np
import sqlite3
import sys

# Conextions with Chrome Driver
ser = Service("./chromedriver")
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")

# Definition of drivers
driver_urls = webdriver.Chrome(options=options)
driver_last_page = webdriver.Chrome(options=options)
driver_products = webdriver.Chrome(options=options)

def get_max_page_catalog():
    # Getting the number of the last page into the catalog
    last = 10000000
    page = f'https://www.farmaciasahumada.cl/medicamentos.html?p={last}'
    driver_last_page.get(page)
    last_page = driver_last_page.find_elements(By.XPATH,'//*[@id="maincontent"]/div[4]/div[1]/div[4]/div[2]/ul/li[1]/a')
    for value in last_page:
            url_last_page = (value.get_attribute('href'))
            n = url_last_page[-3:]
            n = int(n)
    return n

def get_url_from_catalog_ahumada(n):
    list_url = [] 
    for i in range(n):
        page = f'https://www.farmaciasahumada.cl/medicamentos.html?p={i+1}'
        driver_urls.get(page)
        list = driver_urls.find_elements(By.XPATH,"//strong[contains(@class,'product name product-item-name truncate')]/a[contains(@class,'product-item-link')]")
        for i in range(len(list)):
                    url = list[i].get_attribute('href')
                    list_url.append(url)
        time.sleep(2)
    return list_url

def extract_info_web_site_ahumada(list_url):
    list_product_variables = []
    for url in list_url:
        dic_product_variables = {}
        driver_products.get(url)
        # URL
        dic_product_variables["link"] = url
        # Laboratory
        try:
            dic_product_variables["lab"] = driver_products.find_element(By.XPATH,"// h3[contains(@class,'product-brand')]").text
        except NoSuchElementException:
            dic_product_variables["lab"] = 'No Laboratory'
        # Description
        try:
            dic_product_variables["Product_description"] = driver_products.find_element(By.XPATH,"// div[contains(@class,'page-title-wrapper product')]/h1[contains(@class,'page-title')]/span[contains(@class,'base')]").text
        except NoSuchElementException:
            dic_product_variables["Product_description"] = 'No description'
        # Special price
        try:
            dic_product_variables["Special_price"] = driver_products.find_element(By.XPATH,"//span[contains(@class,'special-price')]/span[contains(@class,'price-container price-final_price tax weee prueba')]/span[contains(@class,'price')]").text
        except NoSuchElementException:
            dic_product_variables["Special_price"] = 'No special price'
        # normal price
        try:
            dic_product_variables["Normal_price"] = driver_products.find_element(By.XPATH,"//span[contains(@class,'old-price')]/span[contains(@class,'price-container price-final_price tax weee')]/span[contains(@class,'price-wrapper ')]/span[contains(@class,'price')]").text
        except NoSuchElementException:
            dic_product_variables["Normal_price"] = 'No normal price'
        # Internet Price
        try:
            dic_product_variables["Internet_price"] = driver_products.find_element(By.XPATH,"//span[contains(@class,'price-wrapper')]/span[contains(@class,'price')]").text
        except NoSuchElementException:
            dic_product_variables["Internet_price"] = 'No internet price'
        # SKU
        try:
            dic_product_variables["sku"] = driver_products.find_element(By.XPATH,"//*[@id='maincontent']/div[3]/div/div[2]/div[3]/div[2]/div/div").text
        except NoSuchElementException:
            dic_product_variables["sku"] = 'No sku'

        list_product_variables.append(dic_product_variables)

    df_ahumada = pd.DataFrame(list_product_variables)
    return df_ahumada

# CREATE TABLE Catalog_cruz_verde
def create_if_not_exist_ahumada():
    c.execute("""CREATE TABLE IF NOT EXISTS Catalog_Ahumada(link TEXT, 
                                            lab TEXT, 
                                            Product_description TEXT, 
                                            Special_price TEXT,
                                            Normal_price TEXT,
                                            Internet_price TEXT,
                                            sku TEXT)""")


# INSERT DATA INTO SQL TABLE
def insert_df_sql_ahumada(df_ahumada):
    for ind in df_ahumada.index:
        c.execute("insert into Catalog_Ahumada VALUES(?,?,?,?,?,?,?)",\
        (df_ahumada.link[ind],\
        df_ahumada.lab[ind],\
        df_ahumada.Product_description[ind],\
        df_ahumada.Special_price[ind],\
        df_ahumada.Normal_price[ind],\
        df_ahumada.Internet_price[ind],\
        df_ahumada.sku[ind]))

    

conn = sqlite3.connect('Catalog_pharmacies.db')
c = conn.cursor()

create_if_not_exist_ahumada()
conn.commit()

n = get_max_page_catalog()
list_url= get_url_from_catalog_ahumada(n)
df_ahumada = extract_info_web_site_ahumada(list_url)
insert_df_sql_ahumada(df_ahumada)

conn.commit()
c.close()
conn.close()
sys.exit()