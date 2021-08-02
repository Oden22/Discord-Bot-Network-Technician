from Network_Resolver import Network
import discord

#Initalisations
client = discord.Client()   
home_network = Network()

#When bot is ready
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

#When a member joins
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.channel.send(
        f'Hi {member.name}, welcome to my Discord server!\n Type help for Info'
    )

#When the bot receives a message
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '1':
    	home_network.get_throughput()
    	if type(home_network._dict_important_info['Throughput']) == int:
    		await message.channel.send(f"throughput: {home_network._dict_important_info['Throughput']}Mbps")
    	else:
    		await message.channel.send(home_network._dict_important_info['Throughput'])

    elif message.content == '2':
    	signal = home_network.get_signal_strength(True)
    	await message.channel.send(signal)

    elif message.content == '3':
    	devices = home_network.clients_on_wifi()

    	await message.channel.send(f"{devices} devices connected")

    elif message.content == '4':
    	WHO = home_network.clients_on_wifi(True)

    	if 'Oops' in WHO:
    		await message.channel.send(WHO)

    	else:
	    	await message.channel.send("Devices:")

	    	# Send the devices information in a neat format
	    	for j in range(0, len(WHO)):
	    		comm = f"\n{WHO[j][0]} {WHO[j][1]}\n {WHO[j][2]} {WHO[j][3]}\n {WHO[j][4]} {WHO[j][5]}\n"
	    		await message.channel.send(comm)

    elif message.content == '5':
    	await message.channel.send("If only your network is visible, open network settings first")
    	home_network.get_nearby_networks()
    	await message.channel.send("nearby networks:")
    	for value in home_network._dict_important_info["Visable Networks"]:
    		await message.channel.send(value)

    elif message.content == '6':
    	await message.channel.send("Please use the internet whilst waiting")
    	home_network.get_packets()
    	await message.channel.send(
    		f"{home_network._dict_important_info['Dropped Packets']} Packets lost"
    	)

    elif '7' in message.content:
    	site = message.content.split('7')
    	#Check if user specified a address to ping, if not ping google
    	if site[1] != '':
    		home_network.get_latency(site[1])
    		#If it cant find the address, dont add ms to the end
    		if 'non' in home_network._dict_important_info['Latency'].lower():
    			await message.channel.send(f"{home_network._dict_important_info['Latency']}")
    		else:
    			await message.channel.send(f"{home_network._dict_important_info['Latency']}ms")
    	else:
    		home_network.get_latency()
    		await message.channel.send(f"{home_network._dict_important_info['Latency']}ms")

    elif message.content == '8':
        soloution = home_network.slow_connection()
        if soloution == False:
        	# If the soloution is false provide the reasons why
        	await message.channel.send('Internet speed is fine.')
        	await message.channel.send('Throughput : '
        							f"{home_network._dict_important_info['Throughput']}Mbps")
        	await message.channel.send('Latency : '
        							f"{home_network._dict_important_info['Latency']}ms")
     		
        else:
        	await message.channel.send(soloution)

    elif message.content == '9':
        home_network.output_file()
        await message.channel.send("JSON file has been Output")

    elif message.content.lower() == 'help':
    	await message.channel.send(
    		"1 : Throughput \n2 : Signal Strength"
    		+ "\n3 : No. of Devices \n4 : Show Connected Devices"
    		+ "\n5 : Show Nearby Networks \n6 : Capture packets"
    		+ "\n7 : Test latency (7 for google, 7 *web.com for specified site"
    		+ "\n8 : SLOW INTERNET DIAGNOSE"
    		+ "\n9 : Output json File"
    		)
    else:
    	await message.channel.send('Type help for list of commands')

client.run(#INSERT CLIENT KEY)