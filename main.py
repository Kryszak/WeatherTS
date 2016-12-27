import RPi.GPIO as GPIO
from DHT11 import DHT11
from LPS331AP import LPS331AP
import time
import datetime
import urllib2

apiCode = "Y8JUJSJ241XJSR1B"
baseUrl = "https://api.thingspeak.com/update?api_key=%s" % apiCode
sleepPeriod = 3
dht11Pin = 14

def gpioSetup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()


def main():
    gpioSetup()
    sensor = DHT11(dht11Pin)  # odczyt DHT11 na pinie 14
    sensor_2 = LPS331AP()

    while True:
        err_code, temperature, humidity = sensor.getValues()
        pressure = sensor_2.getPressure()
        altitude = sensor_2.getAltitude()
        if err_code == 0:
            print(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
            print("Temperatura: %d *C" % temperature)
            print("Wilgotnosc powietrza: %d %%" % humidity)
            print("Cisnienie powietrza: %.2f mb" % pressure)
            print("Wysokosc: %.2f m" % altitude)
            print("-----------------------------")
            urllib2.urlopen(baseUrl +
                            "&field1=%s&field2=%s&field3=%s" % (temperature, humidity, pressure) +
                            "&field4=%s" % altitude)
        else:
            print(err_code)
        time.sleep(sleepPeriod)


main()
