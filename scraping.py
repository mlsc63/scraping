import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import urllib.request
import re
import os

host = 'http://books.toscrape.com/catalogue'


def connect(url):
    soup = ()
    try:
        response = requests.get(url)
        if response.ok:
            soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except:
        raise ('Error: ' + url + '\n')

def scraping(url1):
    try:
        information = []
        soup = connect(url1)

        information.append(url1)
        information.append(soup.find('li', {'class': 'active'}).string)
        information.append(
            soup.find('ul', {"class": "breadcrumb"}).findAll('li')[2].find('a').string)

        trs = soup.findAll('tr')
        for tr in trs:
            th = tr.find('th')
            td = tr.find('td')
            if (th.string != "Product Type") and (th.string != "Tax"):

                if (th.string == "Price (excl. tax)") or (th.string == "Price (incl. tax)"):
                    information.append(td.string[2:])

                elif th.string == "Availability":
                    information.append(td.string[10:-11])
                else:
                    information.append(td.string)

        if soup.find('div', id='product_description') is not None:
            information.append(soup.findAll('p')[3])
        else:
            information.append('')
        information.append(host.rpartition('/')[0] + soup.find('div', {'class': 'item active'}).find('img')['src'][5:])
        save_pic(information[9], information[1])
        save_information(information)
    except:
        raise('Error  scrapping() ' + url1 + ',' + '\n')


def scan(url2):
    try:
        book = []
        soup = connect(url2)
        all_book = soup.find('div', {'class': 'col-sm-8 col-md-9'}).findAll('div', {'class': 'image_container'})
        for i in all_book:
            book.append(host + '/' + i.find('a')['href'][9:])
        return book
    except:
        raise ('Error scan() ' + url2 + ',' + '\n')



def scan_page(url3):
    browse_page = []
    i = 1
    try:
        while True:
            soup = connect(url3)
            if i == 1:
                browse_page.append(url3)
                i += 1
            if soup.find('li', {'class': 'next'}) is not None:
                url3 = url3.rpartition('/')[0] + "/page-{}.html".format(i)
                if i > 1:
                    browse_page.append(url3.rpartition('/')[0] + "/page-{}.html".format(i))
                    i += 1
            else:
                return browse_page
    except:
        raise('Error: ' + url3 + '\n')



def get_cat(url4):
    all_categories = []
    soup = connect(url4)
    try:
        cats = soup.find('ul', {'class': 'nav nav-list'}).findAll('li')[1:]
        for i in cats:
            all_categories.append(url4 + i.find('a')['href'])
        return all_categories
    except:
        raise('Error: ' + url4 + '\n')


def directory():
    try:
        os.mkdir('./images')
        os.mkdir('./categories')
    except:
        pass



def save_information(all_information):
    try:
        if os.path.isfile('/categories/' + all_information[2] + '.csv'):

            with open('categories/' + all_information[2] + ".csv", "a", newline="", encoding="utf-8") as f:
                writing = csv.writer(f)
                writing.writerow(
                    [all_information[0], all_information[3], all_information[1], all_information[4], all_information[5], all_information[6], all_information[8], all_information[2], all_information[7],
                     all_information[9]])

        else:
            with open('categories/' + all_information[2] + ".csv", "a", newline="", encoding="utf-8") as f:
                writing = csv.writer(f)
                writing.writerow(['product_page_url', 'universal_product_code', 'title', 'price_including_tax',
                                   'price_excluding_tax', 'number_available', 'product_description', 'category',
                                   'review_rating', 'image_url'])
                writing.writerow(
                    [all_information[0], all_information[3], all_information[1], all_information[4], all_information[5], all_information[6], all_information[8], all_information[2], all_information[7],
                     all_information[9]])

    except:
        raise('Error:' + all_information)


def save_pic(img, titre):
    try:
        title_picture = re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,*]", "", titre)
        urllib.request.urlretrieve(img, "images/" + title_picture + ".jpg")

    except:
        raise('Error: ' + titre + img)


directory()
categories = get_cat('http://books.toscrape.com/')
get_pages = []
get_books = []
for category in categories:
    print(category + '\n\n')
    get_pages.extend(scan_page(category))
for get_page in get_pages:
    print(get_page + '\n\n')
    get_books.extend(scan(get_page))
for get_book in get_books:
    print(get_book + '\n\n')
    scraping(get_book)


