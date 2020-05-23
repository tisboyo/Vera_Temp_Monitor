A simple python script running in a Docker container to monitor the internal temperature from my thermostat on my VeraPlus

The script SSH's into the Vera and monitors the log file, then pushes the results to Postgresql as an additional data point on my aquriums graph.