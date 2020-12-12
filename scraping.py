import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import urllib.request
import re
import os

chemin = os.getcwd()
host = 'http://books.toscrape.com/catalogue'

def connect (url):
    try: 
       response = requests.get(url)
       if response.ok:
           soup = BeautifulSoup(response.content, 'html.parser')
       return soup
    except:
       print('Lien non valide: ' + url +'\n' )


def scraping (url1):    
   try:
      infos =[]
      soup = connect(url1)

      infos.append(url1) #On ajoute l'URL
      infos.append(soup.find('li', {'class':'active' } ).string) #On ajoute le titre
      infos.append(soup.find('ul', {"class":"breadcrumb"}).findAll('li')[2].find('a').string) #On ajoute la catégorie

      #Ajout des autres informations qui sont dans les <td> en discriminant les <tr> contenant Product type et Tax. 
      trs = soup.findAll('tr')
      for tr in trs:     
           th = tr.find('th')
           td = tr.find('td')
           if (th.string != "Product Type") and (th.string !="Tax"):
 
               if (th.string == "Price (excl. tax)") or (th.string == "Price (incl. tax)"): 
                   infos.append(td.string[2:])
                
               elif th.string == "Availability":
                   infos.append(td.string[10:-11])
               else: infos.append(td.string)

      if soup.find('div', id ='product_description') is not None: #Ajout de la déscription si elle existe
         infos.append(soup.findAll('p')[3])
      else:
         infos.append('')
      infos.append(host.rpartition('/')[0] + soup.find('div',{'class':'item active'}).find('img')['src'][5:]) #Ajout du lien de l'image 
      save_pic (infos[9], infos[1])
      save_infos (infos)
   except:
      print('Erreur  scrapping() ' + url1 + ','+ infos +'\n' )
   
#Sur la page on référence tous les livres, et on stock leurs URL dans la liste livre
def scan (url2):
    try:
      livres= []
      soup = connect(url2)
      livre = soup.find('div',{'class':'col-sm-8 col-md-9'}).findAll('div', {'class':'image_container'})
      for i in livre:
         livres.append(host +'/'+ i.find('a')['href'][9:])
      return livres
    except:
        print('Erreur scan() ' + url2 + ','+ livres +'\n' )


 
#La fonction permet de savoir si c'est la dernière page ou non, puis enregistre les liens qui seront envoyé à la fonc scan
def scan_page (url3):
   scanp =[]
   i = 1  
   try:
      while True: #On référence la page, tant qu'on trouve la class 'next' on incrémente la page puis on modifie directement sa valeur (Utilisation du module urlparse pour segementer l'url).
         soup = connect(url3) 
         if i == 1:                 
               scanp.append(url3)
               i += 1
         if  soup.find('li', {'class':'next'})  is not None:
            url3 = url3.rpartition('/')[0] + "/page-{}.html".format(i)
            if i > 1:
                scanp.append(url3.rpartition('/')[0] + "/page-{}.html".format(i))
                i +=1
         else: return scanp
   except:
       print('Erreur scan_page(): ' + url3 + ','+ scanp +'\n' )

         



# On scan les cats du site puis on les enregistre dans la cat
def get_cat(url4):
    cat=[]
    soup = connect(url4)
    try: 
       cats = soup.find('ul', {'class':'nav nav-list'}).findAll('li')[1:] #on dicrimine le premier élément
       for i in cats:
           cat.append(url4 + i.find('a')['href'])
       return cat
    except:
        print('Erreur scancat(): ' + url4 + 'avec les infos suivantes'+ cat +'\n' )

def directory():
    try:
       path = os.getcwd()
       print(path)
       os.mkdir(path + '\images')
       os.mkdir(path + '\catégories')
    except:
        pass

def save_infos (infos):
    try:
      if os.path.isfile(chemin +'/catégories/' + infos[2] +'.csv'):
          
          with open('catégories/' + infos[2]+".csv","a",newline="", encoding="utf-8") as f:
              ecriture = csv.writer(f)
              ecriture.writerow([infos[0], infos[3], infos[1], infos[4], infos[5], infos[6], infos[8], infos[2], infos[7], infos[9]])

      else:
        with open('catégories/' + infos[2] +".csv","a",newline="", encoding="utf-8") as f:
          ecriture = csv.writer(f)
          ecriture.writerow(['product_page_url', 'universal_product_code', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description', 'category', 'review_rating', 'image_url'])
          ecriture.writerow([infos[0], infos[3], infos[1], infos[4], infos[5], infos[6], infos[8], infos[2], infos[7], infos[9]])
          
    except:
        print('Erreur enreg():' + infos)
   


def save_pic (img,titre):
    try:
        titremod = re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,*]", "", titre)
        urllib.request.urlretrieve(img, "images/" + titremod + ".jpg")

    except:
        print('Erreur enregimg(): ' + titre + img )


directory()
category = get_cat('http://books.toscrape.com/')
get_page = []
get_book = []
for i in category:
    print(i +'\n\n')
    get_page.extend(scan_page(i)) 
for j in get_page:
    print (j +'\n\n')
    get_book.extend(scan(j))
for k in get_book:
    print(k +'\n\n')
    scraping(k)



