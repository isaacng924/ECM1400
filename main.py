import sched
import time
import logging
from covid_data_handler import add_covid_data, schedule_covid_updates
from covid_news_handling import update_news, remove_news, add_news
from flask import Flask, request
from flask import render_template
from time_conver import hhmm_to_seconds, current_time_hhmm

global news
global local_area
global local_new_case
global nation_area
global nation_new_case
global nation_hospital_cases
global total_death
global update

news_data = sched.scheduler(time.time, time.sleep)
covid_data = sched.scheduler(time.time, time.sleep)
app = Flask(__name__, static_url_path='/static')
logging.basicConfig(filename='log_file.log', level=logging.INFO)

update = []
news = add_news()
local_area, local_new_case, nation_area, nation_new_case, nation_hospital_cases, total_death = add_covid_data()


def add_update(update_name: str, update_interval: str) -> list:
    """
    This function shows the scheduled update with the update name and update interval.

    :arg
        update_name (string): The name of the scheduled update
        update_interval (integer): Number of second that the update will be processed

    :return:
        List: A list containing the update names and update interval

    """
    logging.info("getting the newest scheduled update in " + update_interval + "seconds with the name: " + update_name)
    global update
    update.append({
        "title": update_name,
        "content": update_interval
    })
    return update


def remove_update(update_name: str):
    """
    This function removes the corresponding scheduled update from the update list.

    :arg
        update_name (string): The name of the scheduled update that you want to remove

    """
    logging.info("removing the news article with the title: " + update_name)
    global update
    for n in update:
        if n["title"] == update_name:
            update.remove(n)


def update_covid_data():
    """
    This function check whether there is a schedule update of the covid data according to the time,
    if yes then schedule the update.

    """
    logging.info("checking whether there is a scheduled covid data update")
    global update
    update_name = request.args.get("two")
    update_time = request.args.get("update")
    covid_field = request.args.get("covid-data")
    if update_time is not None:
        add_update(update_name, update_time)
        update_time_sec = hhmm_to_seconds(update_time)
        current_time_sec = hhmm_to_seconds(current_time_hhmm())
        update_interval = update_time_sec - current_time_sec
        if covid_field == "covid-data":
            logging.info("scheduling the update")
            schedule_covid_updates(update_interval, update_name)


@app.route('/index')
def web():
    global update
    update_news()
    update_covid_data()
    news_title = request.args.get("notif")
    if news_title is not None:
        remove_news(news_title)
    update_name = request.args.get("update_item")
    if update_name is not None:
        remove_update(update_name)
    return render_template(
        'index.html',
        title='Daily update',
        news_articles=news[0:4],
        location=local_area,
        local_7day_infections=local_new_case,
        nation_location=nation_area,
        national_7day_infections=nation_new_case,
        hospital_cases=nation_hospital_cases,
        deaths_total=total_death,
        updates=update,
        image='covid.jpg'
    )


if __name__ == '__main__':
    app.run()
