import requests
from bs4 import BeautifulSoup
import pandas as pd

base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"
pagelimit = 20  # ((0) - to extract all page, (any number>0)- to extract specific number of pages)
remove_sponsored = True  # (True) -remove sponsored products or (False) - keep sponsored products)

pagecount = 0
Headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"}

ProductURL = []
ProductName = []
ProductPrice = []
Rating = []
Numberofreviews = []
asin = []
description = []
manufacturer = []


def getpage(url):
    s = requests.get(url, headers=Headers).text
    soup = BeautifulSoup(s, 'html.parser')
    return soup


def getsearchresults(soup):
    x = soup.find_all('div', {'data-component-type': 's-search-result'})
    for z in x:
        if not z.find('span',
                      {'class': 'puis-label-popover-hover'}) or not remove_sponsored:  ### to remove sponsored products
            url = "https://www.amazon.in" + str(z.find('a', {'class': 'a-link-normal s-no-outline'})['href'])
            name = z.find('span', {'class': 'a-size-medium a-color-base a-text-normal'}).text

            price = ''
            rate = ''
            revno = ''
            if z.find('span', {'class': 'a-offscreen'}):
                price = z.find('span', {'class': 'a-offscreen'}).text.lstrip('₹').replace(',', '')

            if z.find('span', {'class': 'a-icon-alt'}):
                rate = z.find('span', {'class': 'a-icon-alt'}).text.split()[0]

            if z.find('span', {'class': 'a-size-base s-underline-text'}):
                revno = z.find('span', {'class': 'a-size-base s-underline-text'}).text
                revno = revno.lstrip('(').rstrip(')').replace(',', '')

            asino = z['data-asin']

            ProductURL.append(url)
            ProductName.append(name)
            ProductPrice.append(float(price) if price else price)
            Rating.append(float(rate) if rate else rate)
            Numberofreviews.append(int(revno) if revno else revno)
            asin.append(asino)


def nextpage(soup):
    page = soup.find('span', {'class': 's-pagination-strip'})
    if not page.find('span', {'class': 's-pagination-item s-pagination-next s-pagination-disabled'}):
        url = "https://www.amazon.in" + str(
            page.find('a', {'class': 's-pagination-item s-pagination-next s-pagination-button s-pagination-separator'})[
                'href'])
        return url
    else:
        return


def getproductcontent(soup):
    desc0 = soup.find('div', {'id': 'feature-bullets'})
    if desc0:
        desc1 = desc0.find_all('span', {'class': 'a-list-item'})
        desc = ""
        if len(desc1) > 0:
            for x in desc1:
                if desc == "":
                    desc += x.text.strip()
                else:
                    desc += "\n" + x.text.strip()
        description.append(desc)

    pdet0 = soup.find_all('table', {'class': 'a-keyvalue prodDetTable'})
    pdet1 = []
    manu = ""
    for x in pdet0:
        pdet1 += x.find_all('tr')
    if pdet1:
        for t in pdet1:
            if t.th.text.strip().lower() == 'manufacturer':
                manu = t.td.text.strip()
                manu = manu.lstrip('\u200e')
                break
    else:
        pdet2 = soup.find('div', {'id': 'detailBullets_feature_div'})
        if pdet2:
            pdet4 = pdet2.find_all('span', {'class': 'a-text-bold'})
            pdet5 = pdet2.find_all('span', {'class': None})
            if pdet4:
                for z in range(len(pdet4)):
                    if (pdet4[z].text.replace(':', "").replace("\u200e", '').replace("\u200f",'').strip().lower() == 'manufacturer'):
                        manu = pdet5[z].text.strip()
                        break
    manufacturer.append(manu)


while pagecount <= pagelimit:
    soup = getpage(base_url)
    getsearchresults(soup)
    base_url = nextpage(soup)
    if pagelimit > 0:
        if pagecount > 0:
            pagecount += 1
        else:
            pagecount += 2
    if not base_url:
        break

for link in ProductURL:
    productsoup = getpage(link)
    getproductcontent(productsoup)

csv_dict = {'ProductURL': ProductURL,
            'ProductName': ProductName,
            'ProductPrice': ProductPrice,
            'Rating': Rating,
            'Numberofreviews': Numberofreviews,
            'Description': description,
            'ASIN': asin,
            'Manufacturer': manufacturer}
df = pd.DataFrame(csv_dict)
df.to_csv('ProductResults.csv', index=False)
