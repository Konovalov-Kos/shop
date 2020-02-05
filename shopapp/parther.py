import os
import time
from django.core.cache import cache
import requests
import pprint
from bs4 import BeautifulSoup
from shopapp.tasks import get_way, img_loader
url1 = "https://www.foxtrot.com.ua/ru"
def parse_treas(url):
    if cache.get(url):
        page_content = cache.get(url)
    else:
        site = requests.get(url)
        cache.set(url1, site.text, 86400)
        page_content = site.text
    def link2dic(link):
        href = link.get('href')
        #print(link.get('class'))
        if link.get('class') == ['link-text']:
            href = ''
        text = link.text
        return {f'{text.strip()}': {'href' : href}}
    def colect_li(li):
        if li.find('a', {'class': 'link-text'}):
            link = li.find('a', {'class': 'link-text'})
        else:
            link = li.find('a', {'class': 'category-list-item__link'})
        if link.text == 'Все категории':
            return
        d = link2dic(link)
        categ_menu = {}
        if li.find('div', {'class': 'category-item'}):
            categ_menu.update(colect_div(li))
            d.get(link.text).update(categ_menu)
        return d
    def colect_ul(div):
        ul = div.find_all('li', {'class': 'category-list-item'})
        sub_category = {}
        for li in ul:
            if not colect_li(li):
                continue
            sub_category.update(colect_li(li))
        return sub_category
    def colect_div(li):
        div_lists = li.find_all('div', {'class':'category-item'})
        categ = {}
        for div in div_lists:
            categ.update(link2dic(div.find('a', {'class': 'category-item__title'})))
            categ.get(div.find('a', {'class': 'category-item__title'}).text).update(colect_ul(div))
        return categ
    def find_categories_treas(site):
        categories_treas = {}
        soup = BeautifulSoup(site, 'html.parser')
        menu = soup.find("ul", {"class": 'catalog-submenu categories'})
        treas = menu.find_all("li", {'class': 'submenu-item'})
        for trea in treas:
            categories_treas.update(colect_li(trea))
        return categories_treas
    return find_categories_treas(page_content)

def colect_url(treas):
    urls = []
    def rec_read(treas):
        for i, j in treas.items():
            if i == 'href':
                urls.append(j)
            elif type(j) == dict:
                rec_read(j)
    rec_read(treas)
    return urls
def parse_urls_items(url):
    url = 'https://www.foxtrot.com.ua' + url
    if cache.get(url):
        page_content = cache.get(url)
    else:
        site = requests.get(url)
        cache.set(url1, site.text, 86400)
        page_content = site.text
    urls_items = []
    soup = BeautifulSoup(page_content, 'html.parser')
    links = soup.find_all('a', {'class': 'listing-item__img-container detail-link'})
    for link in links:
        urls_items.append(link.get('href'))
    return urls_items
def colect_urls_items(urls):
    urls_items = []
    for i in urls:
        urls_items.extend(parse_urls_items(i))
    return urls_items


def parse_items(urls_items):
    url = 'https://www.foxtrot.com.ua' + urls_items
    i = 10
    while i > 0:
        if cache.get(url):
            page_content = cache.get(url)
        else:
            site = requests.get(url)
            if site.status_code != 200:
                time.sleep(1)
                i -= 1
                continue
            cache.set(url1, site.text, 86400)
            page_content = site.text

        soup = BeautifulSoup(page_content, 'html.parser')
        try:
            name = soup.find('meta', {'itemprop': "name"}).get('content')
            price = soup.find('div', {'class': 'price__relevant'})
            price = price.find('span', {'class': 'numb'}).text.replace(' ', '')
            desc = soup.find('div', {'class': 'about'})
            brand = soup.find('meta', {'itemprop': "brand"}).get('content')
        except:
            return None
        try:
            price_not_relevant = soup.find('div', {'class': 'price__not-relevant'})
            price_not_relevant = price_not_relevant.find('span', {'class': 'numb'}).text.replace(' ','')
        except:
            price_not_relevant = 0
        try:
            url_img = soup.find('img', {'class': "slider-image owl-lazy"}).get('data-src')
            image_way, img = get_way(url_img, 'prod')
            img_loader(url_img, image_way)
        except:
            img = ''
        try:
            spec = soup.find('div', {'class': "characteristic", 'id': 'characteristic'})
        except:
            spec = ''
        try:
            images_desc = desc.find_all('img')
            if len(images_desc) > 1:
                for img2 in images_desc:
                    if img2.get('data-src'):
                        link = img2.get('data-src')
                        url_desc_img = 'https' + link
                        way, way_img = get_way(url_desc_img, 'desc')
                        img_loader.delay(url_desc_img, way)
                        img2['data-src'] = way_img
                    elif img2.get('src'):
                        img2['src'] = os.path.join('static/img/arrow-down.png')
        except:
            pass
        return {'name': name,
                'prev_price': price_not_relevant,
                'price': price,
                'image': img,
                'specification': spec.text,
                'description': desc.text,
                'brand': brand
                }



