# General idea
# Crawl serveral financial feeds
# Python Package feedparser
# Determine similarity
# Jaccard coefficient, Lexical similarity
# Semantic similarity?
# Create readable 'new' text (Summaries)
# extractive summarization
# abstractive summarization
# Text Rank Algorithm

import feedparser
import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np
import datetime
import json

# RSS FEEDS

with open("data_file.json", "r") as read_file:
    data = json.load(read_file)

print(data)

financialFeeds = [  'https://seekingalpha.com/market_currents.xml',
                    'https://www.investing.com/rss/news.rss',
                    'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
                    'https://www.cnbc.com/id/10000664/device/rss/rss.html',
                    #'https://www1.cbn.com/rss-cbn-news-finance.xml',
                    #'https://www.business-standard.com/rss/finance-news-10301.rss',
                    #'https://www.telegraph.co.uk/finance/rssfeeds/',
                    #'https://fortune.com/feed',
                    #'https://www.ft.com/?format=rss'
                    #'https://www.theguardian.com/uk/rss'
                    ]

# Getting titles and links from the RSS-Feeds and saving into arrays
def parse_feed(urls):
    title, link, date = ([] for i in range(3))
    for url in urls:
        d = feedparser.parse(url)
        for entry in d.entries:
            title.append(entry.title)
            link.append(entry.link)
            date.append(entry.published)
    return title, link, date

title, link, date = parse_feed(financialFeeds)

# Getting the article text with bs4 from the link list and saving it into an array called text
# Functions for four different news sites
def get_article_from_seeking(url):
    article = []
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.article.find_all('p')
    for paragraph in paragraphs:
        article.append(paragraph.get_text())
    return article

def get_article_from_investing(url):
    article = []
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find("div", class_="WYSIWYG articlePage").find_all('p')
    for paragraph in paragraphs:
        article.append(paragraph.get_text())
    return article

def get_article_from_wsj(url):
    article = []
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find("div", class_="group").find_all('p')
    for paragraph in paragraphs:
        article.append(paragraph.get_text())
    return article

def get_article_from_cnbc(url):
    article = []
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find("div", class_="group").find_all('p')
    for paragraph in paragraphs:
        article.append(paragraph.get_text())
    return article

text = []
for url in link:
    print(f'Reading article from: {url[:50]}...')
    try:
        if url.find('seekingalpha.com') != -1:
            text.append(get_article_from_seeking(url))
        elif url.find('investing.com') != -1:
            text.append(get_article_from_investing(url))
        elif url.find('wsj.com') != -1:
            text.append(get_article_from_wsj(url))
        elif url.find('cnbc.com') != -1:
            text.append(get_article_from_cnbc(url))
        else:
            pass #Raise Error?
    except AttributeError:
        print('Attribute Error')
        text.append(np.nan)

print(len(text))

# Adding arrays to a dict
newsLinks = {'title': title, 'link': link, 'text': text, 'date': date}

# Converting the dict to a DataFrame and change column order
financialFeedsDataFrame = pd.DataFrame.from_dict(newsLinks)
order = ['title', 'link', 'date', 'text']
financialFeedsDataFrame = financialFeedsDataFrame.loc[:,order]

# Export DataFrame to a csv file
financialFeedsDataFrame.to_csv(f'{datetime.date.today()}_financial_feeds.csv', index=False)
