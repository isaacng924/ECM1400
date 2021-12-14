import sched
import time
import requests
import logging
from flask import request
from time_conver import hhmm_to_seconds, current_time_hhmm

global news

news_data = sched.scheduler(time.time, time.sleep)


def news_API_request(covid_terms: str = "Covid COVID-19 coronavirus"):
    """
    This function get the news from the news API according to the given keywords.

    :arg
        covid_terms (str): Keywords of the news that you want to get

    :return:
        Json file: A json file containing the news that you get

    """
    logging.info("getting the news with the keywords: " + covid_terms)
    base_url = "https://newsapi.org/v2/everything?"
    api_key = "f59ef4d22d7540f39636e99e44b9d0e6"
    keywords = "Covid&COVID-19&coronavirus&"
    language = "en&"
    sort = "publishedAt&"
    full_url = base_url + "qInTitle=" + keywords + "sortBy=" + sort + "language=" + language + "apiKey=" + api_key
    r = requests.get(full_url)
    return r.json()


def update_news():
    """
    This function check whether there is a schedule update of the news articles according to the time,
    if yes then schedule the update.

    """
    logging.info("checking whether there is a scheduled news update")
    update_time = request.args.get("update")
    if update_time is not None:
        update_time_sec = hhmm_to_seconds(update_time)
        current_time_sec = hhmm_to_seconds(current_time_hhmm())
        update_interval = update_time_sec - current_time_sec
        text_field = request.args.get("news")
        if text_field == "news":
            logging.info("scheduling the update")
            sche_update_news(update_interval)


def add_news() -> list:
    """
    This function get the newest news articles from news API and add it into a list.

    :return
        list: A list with the newest news articles

    """
    logging.info("getting the newest news articles")
    global news
    news = []
    data = news_API_request()
    articles = data["articles"]
    title = []
    content = []
    for n in articles:
        title.append(n["title"])
        content.append(n["content"])
    for i in range(len(title)):
        news.append({
            "title": title[i],
            "content": content[i]
        })
    return news


def remove_news(news_title: str):
    """
    This function removes the corresponding news articles from the list.

    :arg
        news_title (string):  The news title that you want to remove

    """
    logging.info("removing the news article with the title: " + news_title)
    global news
    for n in news:
        if n["title"] == news_title:
            news.remove(n)


def sche_update_news(update_interval: int):
    """
    This function schedule the data update with the given time interval.

    :arg
        update_interval (integer): Number of second that the update will be processed

    """
    logging.info("the covid data will be updated in " + str(update_interval) + "seconds")
    repeat_field = request.args.get("repeat")
    news_data.enter(update_interval, 1, add_news)
    if repeat_field == "repeat":
        logging.info("the schedule update will be repeated")
        news_data.enter(update_interval, 2, lambda: sche_update_news(24 * 60 * 60))
    news_data.run(blocking=False)
