import smbus

class LPS331AP:
	
	__bus = 0
	__pressure = 0
	__altitude = 0
	
	#inicjalizacja czujnika
	def __init__(self):
		#i2c bus init
		self.__bus = smbus.SMBus(1)
		#"obudzenie" czujnika
		self.__bus.write_byte_data(0x5d, 0x20, 0b10000000)
		
	#funkcja dokonujaca pomiaru
	def __measure(self):
		#ustaw czujnik w tryb single shot: pojedynczy pomiar
		self.__bus.write_byte_data(0x5d, 0x21, 0x01)
		#odczyt bajtow cisnienia
		pressure_low_byte = self.__bus.read_byte_data(0x5d, 0x28) #najmlodszy bajt
		pressure_med_byte = self.__bus.read_byte_data(0x5d, 0x29) #srodkowy bajt
		pressure_high_byte = self.__bus.read_byte_data(0x5d, 0x2a) #najstarszy bajt
		self.__pressure = (pressure_high_byte << 16) | (pressure_med_byte << 8) | pressure_low_byte
		self.__pressure /= 4096.0 #skalowanie @dokumentacja
	
	#funkcja zwracajaca cisnienie
	def getPressure(self):
		self.__measure()
		return self.__pressure
	
	#funkcja zwracajaca wysokosc
	def getAltitude(self):
		self.__measure()
		#wzor z dokumentacji czujnika, cisnienie -> wysokosc w m
		self.__altitude = (1 - pow(self.__pressure/1013.25, 0.190284)) * 145366.45 / 3.280839895
		return self.__altitude
