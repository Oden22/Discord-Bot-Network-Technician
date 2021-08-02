import pyspeedtest  
import subprocess as sub
import who_is_on_my_wifi as w
import subprocess
import json
import os

class Network:
	''' This class is used to gain information on of a wireless network
	 and provide solutions to slow internet'''
	def __init__(self):
		self._dict_important_info = {}
		self._interface = ""
		self._working_dir = str(os.getcwd())
		self.st = pyspeedtest.SpeedTest()

	def get_net_info(self):
		"""Get the interface and SSID"""
		#Get WLAN details using subprocess
		network_details = str(
			sub.check_output("netsh wlan show all")
			).split("\\r\\n")

		# Store WLAN info in a .txt file
		with open('WLAN_INFO.txt', 'w+') as file:
			for line in network_details:
				file.write(f"{line}\n")

		count = 0 #Used to only count items from current network

		#Extract important details from the network deatils list
		#Split used to seperate lable and value
		for string in network_details:
			if 'interface name' in string.lower() and count < 1:
				count += 1 
				self._interface = string.split(":", 1)[1].strip()
				self._dict_important_info['Interface'] = self._interface
			if 'Interface' in self._dict_important_info:
				if 'ssid 1' in string.lower() and count < 2:
					count += 1
					self.ssid = string.split(":",1)[1].strip()
					self._dict_important_info['SSID'] = self.ssid
				if 'signal' in string.lower() and count < 3:
					count += 1
					signal_strength = int(string.split(":",1)[1].strip().replace('%', ''))
					self._dict_important_info['Signal'] = signal_strength

	def get_nearby_networks(self):
		''' Get the surronding networks '''

		visable_networks = []
		total_networks = 0

		surrounding_networks = str(
			sub.check_output("netsh wlan show networks")
			).split("\\r\\n")

		#Get nearby networks
		for string in surrounding_networks:
			if 'ssid' in string.lower():
				total_networks += 1
				network = string.split(":",1)[1].strip()
				if network != '':
					visable_networks.append(network)
				self._dict_important_info["Total Nearby Networks"] = total_networks

		self._dict_important_info['Visable Networks'] = visable_networks

	def get_signal_strength(self, chat = False):
		""" Get the rssi of the current connection """
		print("Getting Signal")
		self.get_net_info()
		signal = self._dict_important_info['Signal']

		if signal >= 60:
			strength = "high"
		elif signal >= 40:
			strength = "medium"
		else:
			strength = "low"
		if chat == True:
			self._dict_important_info['Signal Strength'] = strength
			return f'{strength} signal: {signal}%'
		else:
			self._dict_important_info['Signal Strength'] = strength

	def get_latency(self, site = "google.com"):
		""" Measure network latency """
		print("Getting latency")
		try:
			# Ping site and get average time
			ping = str(sub.check_output("ping " + site + " -n 8")).split("\\r\\n")
			latency = ping[-2][-4:-2]
			self._dict_important_info['Latency'] = latency

		except subprocess.CalledProcessError:
			self._dict_important_info['Latency'] =  f"Non Existent Address: {site}"

	def get_throughput(self):
		""" Get the throughput of the current connection """
		print("Getting throughput")

		try:
			#Test the throughput 3 times
			throughput = round(self.st.download() / 1000000, 2)
			self._dict_important_info['Throughput'] = int(throughput)
		except:
			print("Attribute Error: edit the pyspeedtest.py file as per requirments")
			self._dict_important_info['Throughput'] = ('Please edit the pyspeedtest.py file '
												 'according to the requirments')

	def get_packets(self):
		""" Capture network packets """
		print("Getting Packets")

		self.get_net_info()

		try:
			# Open command prompt and capture 1000 packets saving to a pcap file
			sub.call(
				f'tshark -i{self._interface} -w "{self._working_dir}/test123.pcap" -c 1000',
				cwd="C:/Program Files/Wireshark",
				shell=True
				)

			#Open command prompt and read the pcap file and filter for retranmsissions
			sub.call(
				(f'tshark -r "{self._working_dir}/test123.pcap" -Y (tcp.analysis.retransmission) > "{self._working_dir}/retransmissions.txt"'),
				cwd="C:/Program Files/Wireshark",
				shell=True
				)

		except FileNotFoundError:
			return 'Could not find the Working file'

		self._dict_important_info['Dropped Packets'] = 0 

		# Read in the text file containing retransmitted packets
		with open(f"{self._working_dir}/retransmissions.txt", 'r+') as file:
			for line in file:
				if line != '\n':
					self._dict_important_info['Dropped Packets'] += 1

	def clients_on_wifi(self, show_devices = False):
		""" Get info on network Clients """
		print("Getting network device info")
		#Check Who is on the network
		try:
			WHO = w.who() # who(n)
			#Run three times to retry client collection
			if len(WHO) == 1:
				count = 0
				while count < 5:
					print(f'Try: {count+1}')
					WHO = w.who() # who(n)
					if len(WHO) > 1:
						break
					count += 1
			#Add Devices to important dict
			self._dict_important_info['Device Info'] = WHO

			#Add to total devices to important dict
			self._dict_important_info['Total Devices'] = len(WHO)

			# Return list of device info
			if show_devices == True:
				return WHO
			else: 
				return self._dict_important_info['Total Devices'] 
		except IndexError:
			# Return if there is an index error
			return 'IndexError, network is most likely blocking device discovery!'

	def get_all(self, find_packets, find_throughput, find_latency):
		""" Call all functions """
		self.get_signal_strength(False)
		self.clients_on_wifi()
		self.get_nearby_networks()

		if find_packets == True:
			self.get_packets()

		if find_throughput == True:
			self.get_throughput()

		if find_latency == True:
			self.get_latency()

	def slow_connection(self):
		""" Diagnose slow internet """
		self.get_throughput()
		self.get_latency()
		latency = int(self._dict_important_info['Latency'])
		throughput = int(self._dict_important_info['Throughput'])

		if throughput < 15:
			#Call all functions, get packets but not throughput or latency
			self.get_all(True, False, False)
			signal = self._dict_important_info['Signal Strength']
			total_devices = self._dict_important_info['Total Devices']
			dropped_pkts = self._dict_important_info['Dropped Packets']
			nearby_networks = self._dict_important_info['Total Nearby Networks']

			if dropped_pkts > 10:
				if signal != 'high':
					soloution = ("Poor signal creating packet drops. #Signal :" 
								f"{self._dict_important_info['Signal']}% move closer to the AP")
					return soloution

				elif total_devices > 15:
					soloution = ("Congested network causing packet drops : #Lost"
								f"{dropped_pkts}	consider spreading devices across 2.4Ghz and 5Ghz")
					return soloution

				elif latency > 50:
					soloution = ("High packet loss causing latency : #latency" 
								f"{latency} consider restarting the modem")
					return soloution

				elif nearby_networks >= 5:
					soloution = ("May be overlap in Wi-Fi channels: #Nearby networks"
								f"{nearby_networks} consider changing channel or restart modem")
					return soloution
				else:
					return 'Unsure of issue :('
			elif signal != 'high':
				soloution = f"Try Moving closer to the AP : Low signal {signal}"
				return soloution
			else:
				soloution = f"Poor throughput, unsure of cause : {throughput}Mbps"
				return soloution
		elif latency > 40 and throughput > 15:
			soloution = (f"High latency {latency}ms and "
						 f"good throughput {throughput}Mbps, potentially busy server")
			return soloution		
		else:
			return False

	def output_file(self):
		""" Output all the important details to a .json file """
		self.get_all(False, True, True)
		output_file = open("Important_Network_Info.json", "w")
		json.dump(self._dict_important_info, output_file, indent = 6)
		output_file.close()