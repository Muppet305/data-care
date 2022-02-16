from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd
import numpy as np
import sqlite3


# Conextions with Chrome Driver
ser = Service("./chromedriver")
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")

# Definition of drivers
driver = webdriver.Chrome(options=options)
driver_links = webdriver.Chrome(options=options)
driver_2 = webdriver.Chrome(options=options)

def get_url_from_catalog_CruzVerde():
    # Access to Cruz Verde Web Site
    driver.get('https://www.cruzverde.cl/medicamentos/')
    pages = driver.find_element(By.XPATH,"//*[@id='product-search-results']/div/div[2]/div/div[19]/div[2]/button[6]").text
    pages = int(pages)
    # List with URLs
    list_url = []
    # For loop to get URLs from catalog (Horizontal Web Scraping)
    counter = 0
    for j in range(pages):
            n = str(j*18)
            page = f'https://www.cruzverde.cl/medicamentos/?start={n}&sz=18&maxsize=18'
            driver_links.get(page)
            list = driver_links.find_elements(By.XPATH,"//div[contains(@class,'pdp-link')]/a[contains(@class,'link')]")
            for i in range(len(list)):
                    url = list[i].get_attribute('href')
                    list_url.append(url)      
            time.sleep(2)
    return list_url

# For loop to get different values
# We extract the next values:
# * Link
# * Laboratory
# * Prodcut description
# * Normal Price
# * Club Price
# * Offer price
# 
# Once extracted the values, we append these ones into a list and then we create DataFrame

def extract_info_web_site_cruz_verde(list_url):
# Extract of information from URLs with products information
    list_product_variables = []
    for url in list_url:
        dic_product_variables = {}
        driver_2.get(url)
        dic_product_variables["link"] = url
        # Laboratory
        try:
            dic_product_variables["lab"] = driver_2.find_element(By.XPATH,"// div[contains(@class,'row d-none d-lg-flex')]/div[contains(@class,'col')]/a").text
        except NoSuchElementException:
            dic_product_variables["lab"] = 'No Laboratory'
        # Product description
        try:
            dic_product_variables["Product_description"] = driver_2.find_element(By.XPATH,"// div[contains(@class,'row d-none d-lg-flex')]/div[contains(@class,'col')]/h2").text
        except NoSuchElementException:
            dic_product_variables["Product_description"] = 'No Description'
        # Normal Price
        try:  
            dic_product_variables["Price_normal"] = driver_2.find_element(By.XPATH,"//div[contains(@class,'prices')]/div[contains(@class,'price')]//span[@class='price-original']/span[@class='original-value']").text
        except NoSuchElementException:
            try:
                dic_product_variables["Price_normal"] = driver_2.find_element(By.XPATH,"//*[@id='maincontent']/div[1]/div[3]/div/div[3]/div[2]/div/span/span[2]/span/span[2]/span/div/span").text
            except NoSuchElementException:
                try:
                    dic_product_variables["Price_normal"] = driver_2.find_element(By.XPATH,"//*[@id='maincontent']/div[1]/div[2]/div/div[3]/div[2]/div/span/span[2]/span/span[2]/span/div/span").text
                except NoSuchElementException:
                    dic_product_variables["Price_normal"] = 'No price'
        # Club Price
        try:
            dic_product_variables["Price_club"] = driver_2.find_element(By.XPATH,"// div[contains(@class,'prices')]/div[contains(@class,'price')]/span/span[contains(@class,'sales d-flex flex-wrap mb-1 align-items-center')]//span[@class = 'value pr-2']").text
        except NoSuchElementException:
            dic_product_variables["Price_club"] = 'No price'
        # Offer Price
        try:
            dic_product_variables["Price_offer"] = driver_2.find_element(By.XPATH,"// div[contains(@class,'prices')]/div[contains(@class,'price')]/span/span[contains(@class,'sales d-flex flex-wrap mb-1 align-items-center')]//span[@class = 'value']").text
        except NoSuchElementException:
            dic_product_variables["Price_offer"] = 'No price' 
        
        list_product_variables.append(dic_product_variables)

    df_cruz_verde = pd.DataFrame(list_product_variables)
    return df_cruz_verde


# CREATE TABLE Catalog_cruz_verde
def create_if_not_exist_cruz_verde():
    c.execute("""CREATE TABLE IF NOT EXISTS Catalog_cruz_verde(link TEXT, 
                                            lab TEXT, 
                                            Product_description TEXT, 
                                            Price_normal TEXT,
                                            Price_club TEXT,
                                            Price_offer TEXT)""")


# INSERT DATA INTO SQL TABLE
def insert_df_sql_cruz_verde(df_cruz_verde):
    for ind in df_cruz_verde.index:
        c.execute("insert into Catalog_cruz_verde VALUES(?,?,?,?,?,?)",\
        (df_cruz_verde.link[ind],\
        df_cruz_verde.lab[ind],\
        df_cruz_verde.Product_description[ind],\
        df_cruz_verde.Price_normal[ind],\
        df_cruz_verde.Price_club[ind],\
        df_cruz_verde.Price_offer[ind]))

   
conn = sqlite3.connect('Catalog_pharmacies.db')
c = conn.cursor()

create_if_not_exist_cruz_verde()
conn.commit()
insert_df_sql_cruz_verde(extract_info_web_site_cruz_verde(get_url_from_catalog_CruzVerde()))
conn.commit()
c.close()
conn.close()