from configparser import ConfigParser

config = ConfigParser()
config.read("F:/Программирование/Python проекты/Bot-Site Project/bot/handlers/user/config.ini",
            encoding="UTF-8")
print(config["ONE_MONTH_SUBSCRIBE_DETAILS"])
configDetails = {}
configPrice = {}
for key in config["ONE_MONTH_SUBSCRIBE_DETAILS"]:
    value = config["ONE_MONTH_SUBSCRIBE_DETAILS"][key]
    if "width" in key or "height" in key or "size" in key:
        value = int(value)
    if value == "False":
        value = False
    if value == "True":
        value = True
    configDetails[key] = value
for key in config["ONE_MONTH_SUBSCRIBE_PRICE"]:
    value = config["ONE_MONTH_SUBSCRIBE_PRICE"][key]
    if key == "amount":
        value = int(value)
    configPrice[key] = value

