import math


class State:
    __temp: float               # [degrees celsius]
    __wind_speed: float         # [m/s]
    __prod_power: float         # [kWh]
    __consumption: float        # [kWh]
    __market_price: float       # [kr/kWh]
    __buffer: float = 0.0       # [kWh] - [0, 13.5]
    __bank: float = 0           # [kr]

    __buffer_max = 13.5

    def update_state_conditions(self, ws, temp, market_price, consumption, storing, using):
        self.__wind_speed = ws
        self.__temp = temp
        self.__market_price = market_price
        self.__prod_power = State.__calc_prod_power(ws, temp)
        self.__consumption = consumption
        net = self.__prod_power - consumption
        if net >= 0:
            if self.__buffer + net * storing > State.__buffer_max:
                storing = (State.__buffer_max - self.__buffer) / net
            self.__buffer += net * storing
            self.__bank += net * market_price * (1-storing)
        elif net < 0:
            if self.__buffer + net * using < 0.0:
                using = abs( (0 - self.__buffer) / net )
            self.__buffer += (self.__prod_power - consumption) * using
            self.__bank += net * market_price * (1-using)

        #self.__buffer = max(0, min(self.__buffer, State.__buffer_max))

        self.__log()
        return storing, using

    @staticmethod
    def __calc_prod_power(ws, temp):
        # Calculate and set self.__e_prod_power which depends on the current wind speed and temp

        # https://energyeducation.ca/encyclopedia/Wind_power
        # exponential relationship from cut-in speed to the rated speed
        # (negative) linear relationship from rated speed to the cut-out speed

        # https://www.intechopen.com/chapters/40439
        # The wind power captured by a turbine is commonly expressed as a function of the turbine’s
        # swept area and a coefficient of performance, the air density and the wind speed

        # dimensionless coefficient of performance
        # http://www.wiete.com.au/journals/WTE&TE/Pages/Vol.11,%20No.1%20(2013)/06-Libii-J-N.pdf
        # this varies between 0 all the way to the upper limit of 0.593 (Betz limit)
        # "is defined as the ratio of the power captured by the rotor of the wind turbine, p_r,
        # divided by the total power available in the wind, P
        # TODO: Improve this??? Coefficient varies dependent on wind speed in reality, but how to calc?
        Cp = 0.45

        # ρ is the air density in kg/m3 where (https://en.wikipedia.org/wiki/Density_of_air)
        abs_pr = 101325  # absolute pressure (Pa)
        abs_t = temp + 273.15  # absolute temperature (K)
        r_sp = 287.058  # specific gas constant for dry air (J/kg*K)
        p = abs_pr / (r_sp * abs_t)  # ρ is the air density in kg/m3.

        # A is the swept area of the turbine in m2. Lets pretend that all users have the same turbine and that the
        # length of the rotor blades are ...
        blade_len = 5.5  # [m]
        A = math.pi * (blade_len * blade_len)
        p_turbine = 1 / 2 * Cp * p * A * (ws * ws * ws)  # [W]

        result = p_turbine / 1000
        # TODO: Add cut-in and cut-out values? Is there a wind speed that generates 0 power?
        return result

    def get_total_price(self, demand):
        if demand > self.__prod_power:
            diff = demand - self.__prod_power
            return diff * self.__market_price
        else:
            # Woo I am self sufficient!
            return 0

    def get_market_price(self) -> float:
        return self.__market_price

    def get_wind_speed(self) -> float:
        return self.__wind_speed

    def get_temp(self) -> float:
        return self.__temp

    def get_prod_power(self) -> float:
        return self.__prod_power

    def get_conditions(self, filter_slug):
        result = {}
        filter_list = filter_slug.split("-")
        if len(filter_list) == 0 or filter_list[0] == "all":
            result["wind_speed"] = self.__wind_speed
            result["temperature"] = self.__temp
            result["market_price"] = self.__market_price
            result["prod_power"] = self.__prod_power
            result["buffer_capacity"] = self.__buffer
            result["consumption"] = self.__consumption
            result["bank"] = self.__bank
            return result
        else:
            for condition in filter_list["conditions"]:
                if condition.lower() == "wind_speed":
                    result["wind_speed"] = self.__wind_speed
                    continue
                if condition.lower() == "temperature":
                    result["temperature"] = self.__temp
                    continue
                if condition.lower() == "market_price":
                    result["market_price"] = self.__market_price
                    continue
                if condition.lower() == "prod_power":
                    result["prod_power"] = self.__prod_power
                    continue
                if condition.lower() == "buffer_capacity":
                    result["buffer_capacity"] = self.__buffer
                    continue
                if condition.lower() == "consumption":
                    result["consumption"] = self.__consumption
                    continue
        return result

    def __log(self):
        pass
        #print("The wind turbine is now generating: " + str(self.__prod_power) + " kWh energy every hour")
        #print("The household is currently consuming: " + str(self.__consumption) + " kWh energy every hour")
        #print("Net production: " + str(self.__prod_power - self.__consumption))
        #print("Buffer size: " + str(self.__buffer))
