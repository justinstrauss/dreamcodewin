Justin Strauss and Angela Lin
Software Development Period 7
API Project

In a city where getting from point A to point B in the shortest time possible is of the utmost importance, Citibike has provided a new means to get where you need to go. When most people think of public transit in New York, the first thing that comes to mind is the MTA's subways and buses. Citibike can be considered public transit too and in some cases, it's faster than riding the MTA. 

Google Maps supports conventional public transit directions and biking directions, but it doesn't natively support getting directions that take Citibike station locations into consideration. Our app uses the Citibike and Google Maps APIs to calculate Citibike directions.

Our approach is to break down the trip into 3 legs: walking from your starting point to the closest Citibike station, bicycling from that station to the station closest to your destination, then walking to your destination. We sum the travel travel times for each leg to calculate a total Citibike travel time, which can then be compared to the travel time for Google Maps' subway/bus directions to determine which is faster.