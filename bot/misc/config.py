import yaml
from yaml import load

with open("/home/maxim/PycharmProjects/WeatherBot/bot/config.yaml", encoding="UTF-8") as f:
    config = load(f, yaml.FullLoader)
configDetails = {}
configPrice = {}
configDiscounts = {}
for key in config["ONE_MONTH_SUBSCRIBE_DETAILS"]:
    value = config["ONE_MONTH_SUBSCRIBE_DETAILS"][key]
    configDetails[key] = value
for key in config["DISCOUNTS"]:
    value = config["DISCOUNTS"][key]
    configDiscounts[key] = value
