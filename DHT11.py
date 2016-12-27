import RPi.GPIO as GPIO
import time

class DHT11:
	
	__pin = -1
	ERR_CLEAR = 0
	ERR_MISSING_DATA = 1
	ERR_CRC = 2
	
	#przypisanie pinu DATA czujnika
	def __init__(self, pin):
		self.__pin = pin
	
	#
	def __sendAndWait(self, value, seconds):
		GPIO.output(self.__pin, value)
		time.sleep(seconds)
		
	#oblicz dlugosci okresow sygnalu wysokiego	
	def __parseData(self, data):
		#zmienne opisujace stan sygnalu
		STATE_INIT_PULL_DOWN = 1
		STATE_INIT_PULL_UP = 2
		STATE_DATA_FIRST_PULL_DOWN = 3
		STATE_DATA_PULL_UP = 4
		STATE_DATA_PULL_DOWN = 5
		
		#poczatkowy stan
		state = STATE_INIT_PULL_DOWN
		
		#tablica dlugosci trwania stanu wysokiego
		lengths_of_pull_ups = [] 
		#dlugosc trwania aktualnego stanu wysokiego
		current_length = 0
		
		for i in range(len(data)):
			
			current = data[i]
			current_length += 1
			
			
			if state == STATE_INIT_PULL_DOWN:
				#pierwsza zmiana wartosci sygnalu na 0 przy starcie pomiaru
				if current == GPIO.LOW:
					state = STATE_INIT_PULL_UP
					continue
				else:
					continue
				
			if state == STATE_INIT_PULL_UP:
				#pierwsza zmiana wartosci sygnalu na 1 przy starcie pomiaru
				if current == GPIO.HIGH:
					state = STATE_DATA_FIRST_PULL_DOWN
					continue
				else:
					continue
					
			if state == STATE_DATA_FIRST_PULL_DOWN:
				#stan niski po zainicjowaniu czujnika, nastepny: wysoki
				if current == GPIO.LOW:
					state = STATE_DATA_PULL_UP
					continue
				else:
					continue
					
			if state == STATE_DATA_PULL_UP:
				#zmiana sygnalu na wysoki, w zaleznosci od czasu, 
				#przez jaki sygnal utrzymuje stan wysoki 
				#bedzie to logiczne 0 lub 1
				if current == GPIO.HIGH:
					current_length = 0
					state = STATE_DATA_PULL_DOWN
					continue
				else:
					continue
					
			if state == STATE_DATA_PULL_DOWN:
				#zmiana wartosci sygnalu na niski, zapis dlugosci trwania
				#stanu wysokiego
				if current == GPIO.LOW:
					lengths_of_pull_ups.append(current_length)
					state = STATE_DATA_PULL_UP
					continue
				else:
					continue
			
		return lengths_of_pull_ups
	
	#przeliczenie dlugosci trwania stanow wysokich na bity wyniku
	def __dataToBits(self, lengths_of_pull_ups):
		
		#znajdz srodek zakresu dlugosci stanow wysokich
		#do stwierdzenia, czy sygnal byl krotki, czy dlugi
		shortest_pull_up = min(lengths_of_pull_ups)
		longest_pull_up = max(lengths_of_pull_ups)
		
		avg_pull_up = shortest_pull_up + (longest_pull_up - shortest_pull_up) / 2
		
		bits = []
		
		for i in range(0, len(lengths_of_pull_ups)):
			
			bit = False
			
			if lengths_of_pull_ups[i] > avg_pull_up:
				bit = True
				
			bits.append(bit)
			
		return bits
		
	
	#przeliczenie bitow wyniku na bajty
	def __bitDataToByteData(self, bits):
		
		result_bytes = []
		
		byte = 0
		
		for i in range(0, len(bits)):
			
			byte = byte << 1
			if(bits[i]):
				byte = byte | 1
			else:
				byte = byte | 0
			
			if((i + 1) % 8 == 0):
				result_bytes.append(byte)
				byte = 0
			
		return result_bytes
		
	
	def __checkSum(self, result_bytes):
		return result_bytes[0] + result_bytes[1] + result_bytes[2] + result_bytes[3] & 255
		
	
	def __readMeasurements(self):
		
		#zmienne do odnalezienia konca danych
		#(ciag 100x HIGH oznacza koniec -->rezystor podciagajacy)
		unchanged_count = 0
		max_unchanged_count = 100
		
		last = -1
		data = []
		
		while True:
			current = GPIO.input(self.__pin)
			data.append(current)
			if last != current:
				unchanged_count = 0
				last = current
			else:
				unchanged_count += 1
				if unchanged_count > max_unchanged_count:
					break
			
		return data
		
	
	def getValues(self):
		
		#ustaw pin na wyjsciowy
		GPIO.setup(self.__pin, GPIO.OUT)
		
		#wyslanie inicjujacego stanu wysokiego
		self.__sendAndWait(GPIO.HIGH, 0.05)
		
		#wyslanie inicjujacego stanu niskiego
		self.__sendAndWait(GPIO.LOW, 0.02)
		
		#ustaw pin na wejsciowy
		GPIO.setup(self.__pin, GPIO.IN, GPIO.PUD_UP)
		
		#odczytaj wartosci z czujnika
		data = self.__readMeasurements()
		
		#oblicz okresy trwania stanow wysokich
		lengths_of_pull_ups = self.__parseData(data)
		
		#sprawdz, czy otrzymano odpowiednia ilosc danych
		#5 bajtow -> 40 bitow:
		#2 bajty temperatura
		#2 bajty wilgotnosc
		#1 bajt checksum
		if(len(lengths_of_pull_ups) != 40):
			return self.ERR_MISSING_DATA, 0, 0
			
		#przelicz otrzymane czasy na bity
		bits = self.__dataToBits(lengths_of_pull_ups)
		
		#bity na bajty
		result_bytes = self.__bitDataToByteData(bits)
		
		#oblicz sume kontrolna
		checksum = self.__checkSum(result_bytes)
		
		if result_bytes[4] != checksum:
			return self.ERR_CRC, 0, 0
			
		return self.ERR_CLEAR, result_bytes[2], result_bytes[0]
			
			
		
	
