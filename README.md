# M7011E-Simulation
Simulation service component of github.com/WeRiano/M7011E

# API Documentation

## `api/version/1/`

### `get_current_conditions/<conditions>/`


Returns the current simulation conditions given by the
`conditions` parameter. This parameter is a "slug", 
a hyphen seperated list of conditions. 

The following conditions exists:

* `date_time` - Current simulation time and date.
* `delta` - Simulation update frequency in seconds.
* `saving` - A fraction on the interval [0.0, 1.0] which describes
how much energy should be stored in the case of over-production.
* `using` - A fraction on the interval [0.0, 1.0] which describes
how much energy should be used in the case of under-production.
* `wind_speed` - Simulation wind speed in meters per second.
* `temperature` - Simulation temperature in degrees Celsius.
* `market_price` - Market price of electricity in 
Swedish krona per kilowatt-hour.
* `prod_power` - Energy production from the wind turbine
in kilowatt-hour.
* `buffer_capacity` - Energy stored in the buffer in kilowatt-hour.
* `consumption` - Energy consumption by the users "household" in kilowatt-hour.
* `bank` - Amount of money stored in the users digital wallet.
A negative amount means that the user is "in depth".

### Examples

`127.0.0.1:7999/api/version/1/get_current_conditions/all/`

`127.0.0.1:7999/api/version/1/get_current_conditions/temperature-wind`

`127.0.0.1:7999/api/version/1/get_current_conditions/temperature-wind`

### /get_current_conditions/