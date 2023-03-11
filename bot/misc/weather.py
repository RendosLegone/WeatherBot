from bs4 import BeautifulSoup
import requests
from .slug import genSlug
from fake_useragent import UserAgent


def getWeather(loc, days=1):
    locSlug = genSlug(loc)
    response = requests.get(f"https://world-weather.ru/pogoda/russia/{locSlug}",
                            headers={"User-Agent": UserAgent().chrome})
    soup = BeautifulSoup(response.text, 'lxml')
    if days <= 2:
        weatherDescription = soup.find_all("span", attrs={"class": "dw-into"})
        weatherDescription = weatherDescription[0].text.replace("погода   ", "").replace("  ", " ") \
            .replace("рт. ", "рт.").replace(". ", "\n").replace("Скрыть", "").replace("Подробнее", "")
        if days == 1:
            weatherDescription = weatherDescription.split("Завтра")[0]
        return weatherDescription
    else:
        dayWeek = soup.find_all("div", attrs={"class": "day-week"})
        dayMonth = soup.find_all("div", attrs={"class": "numbers-month"})
        month = soup.find_all("div", attrs={"class": "month"})
        dayTemperature = soup.find_all("div", attrs={"class": "day-temperature"})
        nightTemperature = soup.find_all("div", attrs={"class": "night-temperature"})
        weatherData = ""
        for i in range(days):
            i -= 1
            weatherData += f"""
{dayWeek[i].text}, {dayMonth[i].text} {month[i].text}:
Днём: {dayTemperature[i].text}
Ночью: {nightTemperature[i].text}
"""
        return weatherData


def getCertainWeather(loc, date):
    locSlug = genSlug(loc)
    months = {1: "january", 2: "febraury", 3: "march",
              4: "april", 5: "may", 6: "june",
              7: "july", 8: "august", 9: "september",
              10: "october", 11: "november", 12: "december"
              }
    response = requests.get(f"https://world-weather.ru/pogoda/russia/{locSlug}/{date[0]}-{months[date[1]]}",
                            headers={"User-Agent": UserAgent().chrome})
    soup = BeautifulSoup(response.text, 'lxml')
    weatherDay = soup.find_all("td", attrs={"class": "weather-day"})
    weatherTemperature = soup.find_all("td", attrs={"class": "weather-temperature"})
    weatherFeeling = soup.find_all("td", attrs={"class": "weather-feeling"})
    weatherPressure = soup.find_all("td", attrs={"class": "weather-pressure"})
    weatherHumidity = soup.find_all("td", attrs={"class": "weather-humidity"})
    windWWI = soup.find_all("span", attrs={"class": "tooltip"})
    windSpeed = soup.find_all("span", attrs={"class": "tooltip"})
    formattedData = ""
    for i in range(0, 4):
        formattedData += f"""
{weatherDay[i].text}:
Температура: {weatherTemperature[i].text}
Ощущается как: {weatherFeeling[i].text}
Давление: {weatherPressure[i].text}мм рт.ст.
Влажность воздуха: {weatherHumidity[i].text}
Ветер: {windWWI[i].attrs["title"]}, {windSpeed[i + 1].attrs["title"]}
"""
    return formattedData
