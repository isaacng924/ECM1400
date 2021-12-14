from flask import request
from typing import Tuple
from uk_covid19 import Cov19API
import sched
import time
import logging

covid_data = sched.scheduler(time.time, time.sleep)


def parse_csv_data(csv_filename: str) -> list:
    """
    This function convert all data in csv file into list.

    :arg
        csv_filename (string): The path of the csv file e.g. "csvfile.csv"

    :return
        List: A list contain all the data in the csv file.

    """
    logging.info("parsing csv data")
    data = open(csv_filename, "r")
    list = []
    for x in data:
        list.append(x)
    data.close()
    return list


def process_covid_csv_data(covid_csv_data: list) -> Tuple[int, int, int]:
    """
    This function processes the list of the csv data and takes out the useful elements from the list.

    :arg
        covid_csv_data (list): A list containing the csv data

    :return
        Tuple: A tuple with 3 integer element which are last_7days_cases, current_hospital_cases and total_death

    """
    logging.info("processing the covid csv data into a tuple of 3 integers")
    last_7days_cases = 0
    for i in range(3, 10):
        last_7days_cases += int(covid_csv_data[i].split(",")[6])
    for i in covid_csv_data:
        if (len(i.split(",")[4]) != 0) and i.split(",")[4] != "cumDailyNsoDeathsByDeathDate":
            total_death = int(i.split(",")[4])
            break
    current_hospital_cases = int(covid_csv_data[1].split(",")[5])
    return last_7days_cases, current_hospital_cases, total_death


def covid_API_request(location: str = "Exeter", location_type: str = "ltla") -> str:
    """
    This function get the current covid data form the API and convert it into a string of list.

    :arg
        location (string): A location that you want to get the covid data from, which is defaulted in "Exeter"
        location_type (string): The location type of the given location, which is defaulted in 'ltla"

    :return:
        String: A string of a list with the data extracted in a json file

    """
    logging.info("requesting the covid API in " + location + " with the type " + location_type)
    england_only = [
        'areaType=' + location_type,
        'areaName=' + location
    ]

    cases_and_deaths = {
        "date": "date",
        "areaName": "areaName",
        "areaCode": "areaCode",
        "newCasesByPublishDate": "newCasesByPublishDate",
        "cumCasesByPublishDate": "cumCasesByPublishDate",
        "newDeaths28DaysByDeathDate": "newDeaths28DaysByDeathDate",
        "cumDeaths28DaysByDeathDate": "cumDeaths28DaysByDeathDate",
        "hospitalCases": "hospitalCases",
    }

    api = Cov19API(filters=england_only, structure=cases_and_deaths)

    data = api.get_json()["data"]
    return data


def add_covid_data() -> Tuple[str, int, str, int, str, str]:
    """
    This function process the covid API data and takes out the useful elements from it.

    :return: Tuple: A tuple with the current covid data which are local_area, local_new_case, nation_area,
                    nation_new_case, nation_hospital_cases, and total_death.

    """
    logging.info("taking out different parameters from the covid API")
    exeter_data = covid_API_request()
    local_area = exeter_data[0]["areaName"]
    local_new_case = 0
    for x in range(7):
        local_new_case += exeter_data[x]["newCasesByPublishDate"]
    uk_data = covid_API_request("England", "nation")
    nation_area = uk_data[0]["areaName"]
    nation_new_case = 0
    nation_hospital_cases = uk_data[2]["hospitalCases"]
    for x in range(7):
        nation_new_case += uk_data[x]["newCasesByPublishDate"]
    total_death = uk_data[1]["cumDeaths28DaysByDeathDate"]
    return local_area, local_new_case, nation_area, nation_new_case, nation_hospital_cases, total_death


def schedule_covid_updates(update_interval: int, update_name: str):
    """
    This function schedule the covid data update with the given time and the given name.

    :arg
        update_interval (integer): Number of second that the update will be processed
        update_name (string): The name of the scheduled update

    """
    logging.info("the covid data will be updated in " + str(update_interval) + "seconds with the update name:" + update_name)
    repeat_field = request.args.get("repeat")
    covid_data.enter(update_interval, 1, add_covid_data)
    if repeat_field == "repeat":
        covid_data.enter(update_interval, 2, lambda: schedule_covid_updates(24 * 60 * 60, update_name))
    covid_data.run(blocking=False)



