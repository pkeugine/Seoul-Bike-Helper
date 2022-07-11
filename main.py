from flask import Flask, request
from flask_crontab import Crontab
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import requests
import datetime
import os
import pandas as pd
import json
import csv

from webdriver_manager.chrome import ChromeDriverManager

application = Flask(__name__)
crontab = Crontab(application)


def current_date():
    return datetime.date.today()


class BikeStation:
    def __init__(self, rack_total_count, name, parking_bike_total_count, shared, latitude, longitude, id):
        self.station_id = id
        self.station_latitude = latitude
        self.station_longitude = longitude

        self.name = name
        self.rack_total_count = int(rack_total_count)
        self.parking_bike_total_count = int(parking_bike_total_count)
        self.shared = int(shared)

    def __str__(self):
        return self.station_id


class User:
    def __init__(self, id, password):
        self.id = id
        self.password = password


class Webpage:
    def __init__(self, driver, main_url, user):
        self.driver = driver
        self.main_url = main_url
        self.user = user

    def login(self):
        self.driver.get(self.main_url)

        id_box = self.driver.find_element(by=By.NAME, value="j_username")
        password_box = self.driver.find_element(by=By.NAME, value="j_password")
        login_button = self.driver.find_element(by=By.ID, value="loginBtn")

        id_box.send_keys(self.user.id)
        password_box.send_keys(self.user.password)
        login_button.click()

    def move_to_my_page(self):
        self.login()
        my_page_button = self.driver.find_element(by=By.CLASS_NAME, value="join")
        my_page_button.click()

    def save_weekly_ranking(self):
        self.move_to_my_page()

        ranking_button = self.driver.find_element(by=By.ID, value="useinfo_manage_ranking")
        ranking_button.click()

        id_name = 'tab-1'
        file_name = 'weekly_rank_history.csv'
        self.save_ranking(id_name, file_name)

    def save_monthly_ranking(self):
        self.move_to_my_page()

        ranking_button = self.driver.find_element(by=By.ID, value="useinfo_manage_ranking")
        ranking_button.click()

        weekly_button = self.driver.find_elements(by=By.CLASS_NAME, value="tab-link")[1]
        weekly_button.click()

        id_name = 'tab-2'
        file_name = 'monthly_rank_history.csv'
        self.save_ranking(id_name, file_name)

    def save_ranking(self, id_name, file_name):
        element = self.driver.find_element(By.ID, id_name)
        info_elements = element.find_elements(By.TAG_NAME, 'td')

        ranking_dict = {
            'Save_Date': [current_date()],
            'Rank': [info_elements[0].text],
            'Distance': [info_elements[2].text]
        }

        df = pd.DataFrame(ranking_dict)
        df.to_csv(file_name, mode='a', index=False, header=not os.path.exists(file_name))

    def save_monthly_info(self):
        self.move_to_my_page()
        one_month_button = self.driver.find_element(by=By.ID, value="oneMBtn")
        file_name = "monthly_info_history.csv"
        self.save_info(one_month_button, file_name)

    def save_weekly_info(self):
        self.move_to_my_page()
        one_week_button = self.driver.find_element(by=By.ID, value="weekBtn")
        file_name = "weekly_info_history.csv"
        self.save_info(one_week_button, file_name)

    def save_daily_info(self):
        self.move_to_my_page()
        today = current_date()
        yesterday = today - datetime.timedelta(days=1)
        self.driver.execute_script("document.getElementsByClassName('hasDatepicker')[0].value = '" + str(yesterday) + "'")
        self.driver.execute_script("document.getElementsByClassName('hasDatepicker')[1].value = '" + str(yesterday) + "'")
        search_button = self.driver.find_element(by=By.ID, value="searchBtn")
        file_name = "daily_info_history.csv"
        self.save_info(search_button, file_name)

    def save_info(self, button, file_name):
        button.click()

        element = self.driver.find_element(By.CLASS_NAME, "kcal_box")
        info_elements = element.find_elements(By.TAG_NAME, 'p')

        use_time = format_info(info_elements[0].text, "분")
        distance = format_info(info_elements[1].text, "km")
        calories = format_info(info_elements[2].text, "kcal")
        carbon_saving = format_info(info_elements[3].text, "kg")

        info_dict = {
            'Save_Date': [current_date()],
            'Use_Time': [use_time],
            'Distance': [distance],
            'Calories': [calories],
            'Carbon_Saving': [carbon_saving]
        }

        df = pd.DataFrame(info_dict)
        df.to_csv(file_name, mode='a', index=False, header=not os.path.exists(file_name))


def format_info(info, unit):
    value = "0"
    if info != unit:
        value = info[:len(info) - len(unit)]
    return "{0} {1}".format(value, unit)


@crontab.job(minute="*/5")
def get_live_station_infos():
    first_url = 'http://openapi.seoul.go.kr:8088/{your-validation-key}/json/bikeList/1/1000'
    second_url = 'http://openapi.seoul.go.kr:8088/{your-validation-key}/json/bikeList/1001/2000'
    third_url = 'http://openapi.seoul.go.kr:8088/{your-validation-key}/json/bikeList/2001/3000'

    station_infos = get_station_infos(first_url)
    station_infos.extend(get_station_infos(second_url))
    station_infos.extend(get_station_infos(third_url))

    fieldnames = [
        'rackTotCnt',
        'stationName',
        'parkingBikeTotCnt',
        'shared',
        'stationLatitude',
        'stationLongitude',
        'stationId'
    ]

    with open('live_station_info.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(station_infos)


def get_station_infos(url):
    response = requests.get(url)
    result = response.content
    result = result.decode('utf-8')

    data = json.loads(result)
    return data['rentBikeStatus']['row']


def create_webpage():
    options = webdriver.ChromeOptions()
    options.headless = False
    options.add_argument("window-size=2560x1600")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    my_id = "{your-id}"
    my_password = "{your-password}"
    url = "https://www.bikeseoul.com/"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    user = User(my_id, my_password)
    return Webpage(driver, url, user)


@crontab.job(minute="0", hour="10")
def save_daily_info():
    webpage = create_webpage()
    webpage.save_daily_info()


@crontab.job(minute="0", hour="10", day_of_week="MON")
def save_weekly_info():
    webpage = create_webpage()
    webpage.save_weekly_info()


@crontab.job(minute="0", hour="10", day="1")
def save_monthly_info():
    webpage = create_webpage()
    webpage.save_monthly_info()


@crontab.job(minute="1", hour="10", day_of_week="MON")
def save_weekly_ranking():
    webpage = create_webpage()
    webpage.save_weekly_ranking()


@crontab.job(minute="1", hour="10", day="1")
def save_monthly_ranking():
    webpage = create_webpage()
    webpage.save_monthly_ranking()


@application.route('/stations', methods=['POST'])
def my_station_info():
    # this is an example
    my_station_ids = ['ST-748', 'ST-2704', 'ST-2667', 'ST-578', 'ST-747', 'ST-382', 'ST-765', 'ST-2520', 'ST-765', 'ST-237', 'ST-360']
    return search_live_station_info(my_station_ids)


def search_live_station_info(station_ids):
    live_df = pd.read_csv('live_station_info.csv')
    live_results = live_df[live_df['stationId'].isin(station_ids)]
    print(live_results)

    search_data = [tuple(row) for row in live_results.values]
    print(search_data)

    final_data = format_tuple_data(search_data)
    return create_station_carousel(final_data)


def create_station_carousel(full_data):
    station_name_index = 1
    bicycle_count_index = 2
    latitude_index = -3
    longitude_index = -2

    congnamul_xy = [get_congnamul(data[latitude_index], data[longitude_index]) for data in full_data]

    carousel = {
      "version": "2.0",
      "template": {
        "outputs": [
          {
            "carousel": {
              "type": "basicCard",
              "items": [{"title": data[station_name_index],
                         "description": f'대여가능 자전거 수 : {data[bicycle_count_index]}',
                         "thumbnail": {
                           "imageUrl": f"https://spi.maps.daum.net/map2/map/imageservice?IW=550&IH=350&MX={congnamul_xy[idx][0]}&MY={congnamul_xy[idx][1]}&CX={congnamul_xy[idx][0]}&CY={congnamul_xy[idx][1]}&SCALE=2.5&service=open#.png"},
                         "buttons": [
                           {
                             "action": "webLink",
                             "label": "🗺 위치 보기",
                             "webLinkUrl": f'https://map.kakao.com/link/map/{data[station_name_index]},{data[latitude_index]},{data[longitude_index]}'
                           },
                           {
                             "action": "webLink",
                             "label": "🚴‍♂️ 길 찾기",
                             "webLinkUrl": f'https://map.kakao.com/link/to/{data[station_name_index]},{data[latitude_index]},{data[longitude_index]}'
                           },
                           {
                             "action": "message",
                             "label": "↩️ 메인 메뉴 가기",
                             "messageText": "기본 메뉴"
                           }
                         ]} for idx, data in enumerate(full_data)]
            }
          }
        ]
      }
    }
    return carousel


def get_congnamul(latitude, longitude):
    url = 'https://dapi.kakao.com/v2/local/geo/transcoord.json'
    params = {'x': longitude, 'y': latitude, 'output_coord': 'WCONGNAMUL'}
    headers = {"Authorization": "{your-kakao-api-authorization}"}

    result = requests.get(url, params=params, headers=headers).json()['documents'][0]
    return int(result['x']), int(result['y'])


def format_tuple_data(tuple_data):
    formatted_data = []
    for data in tuple_data:
        data_to_list = list(data)
        data_to_list[1] = clean_name(data_to_list[1])
        formatted_data.append(tuple(data_to_list))
    return formatted_data


def clean_name(name):
    period_index = name.find(".")
    sliced_name = name[period_index + 1:]
    return sliced_name.strip()


@application.route('/search', methods=['POST'])
def search_station_info():
    response = request.get_json()
    keywords = response['action']['params']
    location = keywords['firstKeyword']
    if len(keywords) > 1:
        location = location + " " + keywords['secondKeyword']
    if len(keywords) > 2:
        location = location + " " + keywords['thirdKeyword']

    df = pd.read_csv('station_info.csv')
    results = df[(df['주소1'].str.contains(location) == True) | (df['주소2'].str.contains(location) == True)]
    station_ids = results.대여소_ID.to_list()
    print(station_ids)
    return search_live_station_info(station_ids)


@application.route('/{your-user-name}', methods=['POST'])
def my_info():
    daily_df = pd.read_csv('daily_info_history.csv')
    yesterday_data = tuple(daily_df.iloc[-1])
    print(yesterday_data)

    weekly_df = pd.read_csv('weekly_info_history.csv')
    last_week_data = tuple(weekly_df.iloc[-1])
    print(last_week_data)

    monthly_df = pd.read_csv('monthly_info_history.csv')
    last_month_data = tuple(monthly_df.iloc[-1])
    print(last_month_data)

    list_carousel = {
      "version": "2.0",
      "template": {
        "outputs": [
            {
              "carousel": {
                "type": "listCard",
                "items": [
                  my_report("🚴‍♂️ 어제의 기록", yesterday_data),
                  my_report("🤖 저번 주의 기록", last_week_data),
                  my_report("👽 저번 달의 기록", last_month_data)
                ]
              }
            }
        ]
      }
    }
    return list_carousel


def my_report(title, data):
    item = {
      "header": {
        "title": f'{title}'
      },
      "items": [
        {
          "title": "⏳ 주행 시간",
          "description": f'{data[1]}',
          "imageUrl": "https://i.imgur.com/psrsu3b.jpg"
        },
        {
          "title": "🚸 주행 거리",
          "description": f'{data[2]}',
          "imageUrl": "https://i.imgur.com/Rhb4FEV.jpg"
        },
        {
          "title": "🍔 소비 칼로리",
          "description": f'{data[3]}',
          "imageUrl": "https://i.imgur.com/Lefwk5a.jpg"
        },
        {
          "title": "🌳 탄소 절감 효과",
          "description": f'{data[4]}',
          "imageUrl": "https://i.imgur.com/9pF5k9v.jpg"
        }
      ],
      "buttons": [
        {
          "label": "↩️ 메인 메뉴 가기",
          "action": "message",
          "messageText": "기본 메뉴"
        }
      ]
    }
    return item


@application.route('/rank/weekly', methods=['POST'])
def my_weekly_rank():
    weekly_df = pd.read_csv('weekly_rank_history.csv')
    title = "🔥 저번 주의 랭킹"
    image = "https://i.imgur.com/3lw89Sg.jpg"
    last_week_data = tuple(weekly_df.iloc[-1])
    two_weeks_before_data = tuple(weekly_df.iloc[-2])
    return create_rank_carousel(title, image, last_week_data, two_weeks_before_data)


@application.route('/rank/monthly', methods=['POST'])
def my_monthly_rank():
    monthly_df = pd.read_csv('monthly_rank_history.csv')
    title = "👩‍🚒 저번 달의 랭킹"
    image = "https://i.imgur.com/9TrX1G4.jpg"
    last_month_data = tuple(monthly_df.iloc[-1])
    two_months_before_data = tuple(monthly_df.iloc[-2])
    return create_rank_carousel(title, image, last_month_data, two_months_before_data)


def create_rank_carousel(title, image, last, second_last):
    ranking = last[1]
    distance = last[2]

    last_ranking = second_last[1]
    last_distance = second_last[2]

    ranking_change = int(ranking.split(" ")[0]) - int(last_ranking.split(" ")[0])
    distance_change = int(distance.split(" ")[0]) - int(last_distance.split(" ")[0])

    if ranking_change >= 0:
        string_ranking_change = "+" + str(ranking_change)
    else:
        string_ranking_change = str(ranking_change)

    if distance_change >= 0:
        string_distance_change = "+" + str(distance_change)
    else:
        string_distance_change = str(distance_change)

    item = {
      "version": "2.0",
      "template": {
        "outputs": [
          {
            "carousel": {
              "type": "basicCard",
              "items": [
                {
                  "title": f'{title}',
                  "description": f'{ranking} ({string_ranking_change}등), {distance} ({string_distance_change}km)',
                  "thumbnail": {
                    "imageUrl": f'{image}'
                  },
                  "buttons": [
                    {
                      "label": "↩️ 메인 메뉴 가기",
                      "action": "message",
                      "messageText": "기본 메뉴"
                    }
                  ]
                }
              ]
            }
          }
        ]
      }
    }
    return item


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5000, debug=False)
