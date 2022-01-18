from numpy import random
import requests

from .state import State


# This class is response for manipulating the state
class Delta:
    __state: State

    def __init__(self, state: State, hour, day, month):
        self.__state: State = state

        # Time between simulation updates. One update = one hour has passed
        self.__update_frequency = 10

            # Real time
        # Daily hour. Starts at 0 and ends at 23.
        self.__hour: int = hour
        # Day of the month. Starts at 0 and ends at either 27, 29 or 30 (leap years dont exist (for now)).
        self.__day: int = day - 1
        # Month on the year. Starts at 0 and ends at 11.
        self.__month: int = month - 1

        # Conditions used
        self.__update_daily_ws_mu()
        self.__hourly_ws_mu: float = 0
        self.__hourly_temp: float = 0
        self.__hourly_market_price: float = 0
        self.__hourly_consumption: float = 0

        self.__storing = 0.5     # Percentage [0.0 - 1.0]
        self.__using = 0.5      # Percentage [0.0 - 1.0]

    # Simulate conditions for one hour.
    # Temperature is not actually simulated, but fetched from an api.
    # The wind simulation is split up into two parts: simulating daily and hourly wind.
    # The daily wind is based upon observations from
    # https://weatherspark.com/y/89129/Average-Weather-in-Lule%C3%A5-Sweden-Year-Round
    # and drawn from a normal distribution.
    # The hourly wind is based upon the daily wind and drawn from a normal distribution
    # The market_price and consumption is drawn from a uniform distribution from
    # https://www.worlddata.info/europe/sweden/energy-consumption.php and
    # https://www.statista.com/statistics/596262/electricity-industry-price-sweden/, respectively
    def tick_hour(self):
        days_in_month = [30, 27, 30, 29, 30, 29, 30, 30, 29, 30, 29, 30]
        if self.__hour == 24:
            # New day!
            self.__update_daily_ws_mu()

            self.__hour = 0
            self.__day = self.__day + 1
            if self.__day > days_in_month[self.__month]:
                self.__day = 0
                self.__month = (self.__month + 1) % 12
        else:
            self.__hour += 1

        # Update hourly wind!
        std_dev_hour = self.__daily_ws_mu * 0.01
        self.__hourly_ws_mu = random.normal(self.__daily_ws_mu, std_dev_hour, None)

        # Update hourly temp!
        self.__hourly_temp = self.__fetch_temp()

        # Update hourly market price!
        self.__hourly_market_price = random.uniform(0.5, 0.8)  # [kr/kWh]

        # Update hourly consumption rate. 12.894 kWh is the average annual household consumption in sweden per capita
        # 12.894/365/24 = 1.47191780822 kWh per hour
        self.__hourly_consumption = random.uniform(1.104, 1.84)

    def update_state(self):
        new_storing, new_using = self.__state.update_state_conditions(self.__hourly_ws_mu, self.__hourly_temp,
                                                                      self.__hourly_market_price,
                                                                      self.__hourly_consumption,
                                                                      self.__storing, self.__using)
        self.__storing = new_storing
        self.__using = new_using
        #print("Storing: " + str(self.__storing))
        #print("Using: " + str(self.__using))
        #print("Updating every " + str(self.__update_frequency) + " seconds")

    def get_conditions(self, filter_slug):
        result = {}
        filter_list = filter_slug.split('-')
        if len(filter_list) == 0 or filter_list[0].lower() == 'all':
            result["date_time"] = str(self.__day + 1) + '/' + str(self.__month + 1) + " " + str(self.__hour) + ":00:00"
            result["delta"] = self.__update_frequency
            result["saving"] = self.__storing
            result["using"] = self.__using
        else:
            for condition in filter_list:
                if condition.lower() == "current_time":
                    result["date_time"] = str(self.__day + 1) + '/' + str(self.__month) + 1 + " " + str(self.__hour) + ":00:00"
                if condition.lower() == "delta":
                    result["delta"] = self.__update_frequency
                if condition.lower() == "saving":
                    result["saving"] = self.__storing
                if condition.lower() == "using":
                    result["using"] = self.__using
        return result

    def get_delta(self):
        return self.__update_frequency

    def set_delta(self, delta: int):
        self.__update_frequency = delta

    def get_state(self):
        return self.__state

    def set_ratios(self, storing, using):
        self.__storing = storing
        self.__using = using

    def __update_daily_ws_mu(self):
        # Average Wind Speed (mph) montly (Jan to Dec) [8.2, 7.8, 7.5, 6.8, 6.4, 6.2, 6.3, 6.8, 7.6, 8.2, 8.3, 8.4]
        # source: https://weatherspark.com/y/89129/Average-Weather-in-Lule%C3%A5-Sweden-Year-Round
        avg_ws_month = [8.2, 7.8, 7.5, 6.8, 6.4, 6.2, 6.3, 6.8, 7.6, 8.2, 8.3, 8.4]
        monthly_mu = avg_ws_month[self.__month] * 0.44704  # convert from mph to m/s
        # "The standard deviation of annual mean wind speed over the
        # 20 year period is approximately 5 per cent of the mean"
        # source: https://www.wind-energy-the-facts.org/the-annual-variability-of-wind-speed.html
        std_dev_day = monthly_mu * 0.10
        self.__daily_ws_mu = random.normal(monthly_mu, std_dev_day, None)

    def __fetch_temp(self):
        # Fetches the current temperature in Luleå from temperatur.nu!
        # Returns the result and also updates the state
        url = "http://api.temperatur.nu/tnu_1.17.php"
        # "https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/22/station/162870/period/latest-months/data.json"
        # "https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/22/station/162860.json"

        # defining a params dict for the parameters to be sent to the api
        params = {
            "p": "mjolkudden",
            "cli": "wind_turbine_simulator_LTU_M7011E"
        }

        # sending get request and saving the response as response object
        r = requests.get(url=url, params=params)

        # extracting data in json format
        data = r.json()
        self.__temp = float(data["stations"][0]["temp"])
        return float(data["stations"][0]["temp"])
