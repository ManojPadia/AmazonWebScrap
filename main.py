import csv
import json
from bs4 import BeautifulSoup
from requests_html import HTMLSession


s = HTMLSession()


def get_url(search_term):
    template = 'https://www.amazon.in/s?k={}'
    search_term = search_term.replace(' ', '+')

    url = template.format(search_term)

    url += '&page={}'

    return url


def extract_record(item):
    # Description and Url
    description = item.h2.a.text.strip()
    url = 'https://www.amazon.in' + item.h2.a.get('href')

    try:
        image_parent = item.find('span', 'rush-component')
        image_url = image_parent.find('img').get('src')
    except AttributeError:
        image_url = ''
    #                          div[1] / div / div / span / a / div / img

    try:
        # Price
        price_parent = item.find('span', 'a-price')
        price = price_parent.find('span', 'a-offscreen').text
        price = price[1:]
    except AttributeError:
        price = ''

    try:
        rating = item.i.text
        review_count = item.find('span', {'class': 'a-size-base', 'dir': 'auto'}).text
    except AttributeError:
        rating = ''
        review_count = ''

    result = {
        'Description': description,
        'Price': price,
        'Rating': rating,
        'Review Count': review_count,
        'Url': url,
        'image_url': image_url,
    }

    return result


def getRange(query):
    response = s.get(query)
    soup = BeautifulSoup(response.content, 'html.parser')
    last = soup.find('li', {'class': 'a-last'})
    results = last.find_previous('li', {'class': 'a-disabled'})
    return results.text


def requestData(search_term):
    url = get_url(search_term)
    res = []
    results = []

    reg = int(getRange(url))

    print('Fetching Links...')
    [res.append(s.get(url.format(page))) for page in range(1, reg + 1)]

    print('Fetching pages...')
    [results.extend(i for i in BeautifulSoup(pages.content, 'html.parser')
                    .find_all('div', {'data-component-type': 's-search-result'})) for pages in res]

    print('Extracting records...')
    records = [record for item in results if (record := extract_record(item))]

    print('Total Data fetch = ', len(records))
    jsonData = json.dumps(records, indent=4)
    print(jsonData)

    # print('Writing in file...')
    # with open(search_term + '.csv', 'w', newline='', encoding='utf-8') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(['Description', 'Price', 'Rating', 'ReviewCount', 'Url'])
    #     writer.writerows(records)


requestData('Gaming mouse')
