"""
A module to predict the winning League of Legends team.

Author: Teddy Siker
Date: 30 December, 2020


NOTE: As of 2022, this is not currently functional for two reasons:

	- The API key is omitted.
	- Riot Games changed their API system.
"""
import tkinter as tk
import math
import calendar
import time
from bs4 import BeautifulSoup
from PIL import Image, ImageTk
from riotwatcher import LolWatcher, ApiError
from datetime import date
from datetime import datetime



riot_api_key = 'insert_api_key'
watcher = LolWatcher(riot_api_key)
my_region = 'na1'


def packWidget(widget):
	"""
	Procedural - packs all widgets into window.

	Parameter widget: the widget to pack.
	Precondition: widget is a Tkinter widget.
	"""
	widget.pack()

def create_circle(canvas, x, y, r, fill=None):
	"""
	Creates a circle on the Tkinter canvas.

	Parameter canvas: The canvas to draw on.
	Precondition: canvas is a initialized Tkinter canvas object.

	Parameter x: The x coord for the circle's center.
	Precondition: x is an int > 0 and a point on the canvas.

	Parameter y: The y coord for the circle's center.
	Precondition: y is an int > 0 and a point on the canvas.

	Parameter r: The circle's radius, in pixels.
	Precondition: r is an int > 0. 

	Parameter fill: The circle's fill color.
	Precondition: fill is a string and a valid Tkinter color.
	"""
	x0 = x - r
	y0 = y - r
	x1 = x + r
	y1 = y + r
	return canvas.create_oval(x0,y0,x1,y1, fill=fill)

def rotate_pointer(line, canvas, percentage, team, label):
	"""
	Rotates line a direction by a certain amount of degrees.

	Parameter line: The line to rotate.
	Precondition: line is an intitialized tkinter line object.

	Parameter percentage: The amount of degrees to rotate.
	Precondition: percentage is an 50 <= int <= 100

	Parameter team: Which way to rotate.
	Precondition: team is a string with value 'red' or 'blue'
	"""
	#percentage - 50 times 1.8 % for each degree point. Examples: 
	#100% - 50% = 50% * 1.8 = 90 degrees, flat right

	pointer_end_coords = (395, 300)
	pointer_base_coords = (395, 500)

	if team == 'red':
		percentage = percentage * -1
		angle = (percentage + 50) * 1.8
		new_spot = calculate_point(pointer_base_coords, pointer_end_coords, angle)
		canvas.delete(line)
		canvas.create_line(new_spot[0],new_spot[1],395,500, width=13, fill = 'black')
		label.config(text= '')
		if percentage == -50:
			label.config(text='Tossup')
		elif percentage >= -62.5:
			label.config(text='Tilting no')
		elif percentage >= -62.5 and percentage > -75:
			label.config(text='Likely no')
		elif percentage >= -75 and percentage > -87.5:
			label.config(text='Probably not')
		else:
			label.config(text='Certainly not')

	else:
		angle = (percentage - 50) * 1.8
		new_spot = calculate_point(pointer_base_coords, pointer_end_coords, angle)
		canvas.delete(line)
		canvas.create_line(new_spot[0],new_spot[1],395,500, width=13, fill = 'black')
		label.config(text= '')
		if percentage == 50:
			label.config(text='Tossup')
		elif percentage <= 62.5:
			label.config(text='Tilting yes')
		elif percentage <= 62.5 and percentage <= 75:
			label.config(text='Likely yes')
		elif percentage <= 75 and percentage <= 87.5:
			label.config(text='Probably yes')
		else:
			label.config(text='Certainly yes')


def calculate_point(center, rotater, degrees):
	"""
	Parameter center: The center point (x,y) - the point to rotate about.
	Precondition: center is a tuple with two non-negative integer values.

	Parameter rotater: The point to move (x,y) - the point to rotate.
	Precondition: center is a tuple with two non-negative integer values.

	Parameter degrees: The degrees to rotate.
	Precondition: degrees is either a positive 0 <= int <= 180 or negative -180 <= int <= 0 
	"""
	degrees = math.radians(degrees)
	cx = center[0]
	cy = center[1]

	x = rotater[0]
	y = rotater[1]

	xrot = cx + math.cos(degrees) * (x - cx) - math.sin(degrees) * (y - cy)
	yrot = cy + math.sin(degrees) * (x - cx) + math.cos(degrees) * (y - cy)
	return (xrot, yrot)

def fill_area(canvas, start, hex_code):
	"""
	"""
	center_coords = (395, 500)
	top_coords = [395, 110]
	
	if start < 0:
		end = start - 22.5
		for i in range(-900,0):
			if i < start * 10 and i > end * 10:
				if i / 10 < -45:
					new_top_cords = [top_coords[0] - 3, top_coords[1] + 3]
					fill_coords = calculate_point(center_coords, new_top_cords, i/10)
					canvas.create_line(fill_coords[0],fill_coords[1],395,500, width = 4, fill = hex_code[0])
				else:
					fill_coords = calculate_point(center_coords, top_coords, i/10)
					canvas.create_line(fill_coords[0],fill_coords[1],395,500, width = 4, fill = hex_code[0])
	elif start > 0:
		end = start + 22.5
		for i in range(0, 900):
			if i > start * 10 and i < end * 10:
				if i / 10 > 45:
					new_top_cords = [top_coords[0] + 3, top_coords[1] - 3]
					fill_coords = calculate_point(center_coords, new_top_cords, i/10)
					canvas.create_line(fill_coords[0],fill_coords[1],395,500, width = 4, fill = hex_code[0])
				else:	
					fill_coords = calculate_point(center_coords, top_coords, i/10)
					canvas.create_line(fill_coords[0],fill_coords[1],395,500, width = 4, fill = hex_code[0])
	else:
		for i in range(-225, 0):
			fill_coords = calculate_point(center_coords, top_coords, i/10)
			canvas.create_line(fill_coords[0],fill_coords[1],395,500, width = 2, fill = hex_code[1])
		for i in range(0, 225):
			fill_coords = calculate_point(center_coords, top_coords, i/10)
			canvas.create_line(fill_coords[0],fill_coords[1],395,500, width = 2, fill = hex_code[0])


def get_summoner_id(username):
	"""
	Returns the summoner ID of username as a string.

	Parameter username: The summoner's in game username.
	Precondition: username is a string and a valid username.
	"""
	summoner_info = watcher.summoner.by_name(my_region, username)
	return list(summoner_info.values())[0]


def get_account_id(username):
	"""
	Returns the account ID of username as a string.

	Parameter username: The summoner's in game username.
	Precondition: username is a string and a valid username.
	"""
	summoner_info = watcher.summoner.by_name(my_region, username)
	return list(summoner_info.values())[1]

def get_game_info(encryptedId):
	"""

	Returns the game info json dict response of a riot ID.

	Parameter encryptedId: The user's ID.
	Precondition: encryptedId is a string and a valid Riot ID.
	"""
	game_info = watcher.spectator.by_summoner(my_region, encryptedId)
	return game_info

def get_current_champions(game_info):
	"""
	Parameter game_info: The returned API list of game information by summoner ID.
	Preconditon: game_info is a dictionary containing a valid Riot API spectator response.
	"""
	blue_champions = []
	red_champions = []
	team_info = list(game_info.values())[5]
	champ_info = watcher.data_dragon.champions('11.1.1')
	champ_dict = {}
	for key in list(champ_info['data'].keys()):
		champ_dict[champ_info['data'][key]['key']] = key

	for i in range(10):
		if i < 5:
			blue_champions.append(champ_dict[str(list(game_info.values())[5][i]['championId'])])
		else:
			red_champions.append(champ_dict[str(list(game_info.values())[5][i]['championId'])])
	return {'Blue Side':blue_champions, 'Red Side':red_champions}
	
def get_lp(encryptedId):
	"""
	"""
	standing_info = watcher.league.by_summoner(my_region, encryptedId)
	return standing_info[0]['leaguePoints']

def get_matches_needed(lp):
	"""
	"""
	needed_lp = 100 - lp
	lp_per_win = 16
	return math.ceil(needed_lp / lp_per_win)

def get_today_winrate(encryptedId):
	"""
	Returns an float representing the user's winrate.
	
	Examples: 
		2 wins and 0 losses returns 100%.
		3 wins and 5 losses returns 60%.
		7 wins and 13 losses returns 53.85%.
	"""
	#Get today's epoch time at 9 am.
	today_start_raw = date.today()
	today_year = str(today_start_raw.year)
	today_month = ''
	today_day = ''
	if len(str(today_start_raw.month)) < 2:
		today_month = '0' + str(today_start_raw.month)
	else:
		today_month = str(today_start_raw.month)

	if len(str(today_start_raw.day)) < 2:
		today_day = '0' + str(today_start_raw.day)
	else:
		today_day = str(today_start_raw.day)

	today_epoch = calendar.timegm(time.strptime(today_year + '-' + today_month + '-' + today_day + ' 20:00:00','%Y-%m-%d %H:%M:%S'))
	today_epoch = str(today_epoch)
	today_epoch = today_epoch + '000'
	today_epoch = int(today_epoch)
	user_matches = watcher.match.matchlist_by_account(my_region, encryptedId, begin_time = today_epoch)

	game_ids = {}
	for match in range(len(user_matches['matches'])):
		game_ids[user_matches['matches'][match]['gameId']] = user_matches['matches'][match]['champion']

	team = 100
	wins = 0
	losses = 0
	for game_id in list(game_ids.keys()):
		game = watcher.match.by_id(my_region , game_id)
		for i in range(10):
			if game['participants'][i]['championId'] == game_ids[game_id]:
				if game['participants'][i]['stats']['win']:
					wins += 1
				else:
					losses +=1
	return round(((wins / (wins + losses)) * 100), 2)


def get_average_gametime(encryptedId):
	"""
	"""
	today_start_raw = date.today()
	today_year = str(today_start_raw.year)
	today_month = ''
	today_day = ''
	if len(str(today_start_raw.month)) < 2:
		today_month = '0' + str(today_start_raw.month)
	else:
		today_month = str(today_start_raw.month)

	if len(str(today_start_raw.day)) < 2:
		today_day = '0' + str(today_start_raw.day)
	else:
		today_day = str(today_start_raw.day)

	today_epoch = calendar.timegm(time.strptime(today_year + '-' + today_month + '-' + today_day + ' 17:00:00','%Y-%m-%d %H:%M:%S'))
	today_epoch = str(today_epoch)
	today_epoch = today_epoch + '000'
	today_epoch = int(today_epoch)
	user_matches = watcher.match.matchlist_by_account(my_region, encryptedId, begin_time = today_epoch)
	user_matches = watcher.match.matchlist_by_account(my_region, encryptedId, begin_time = today_epoch)

	game_ids = []
	for match in range(len(user_matches['matches'])):
		game_ids.append(user_matches['matches'][match]['gameId'])

	games = 0
	total_duration = 0
	for game_id in range(len(game_ids)):
	    game = watcher.match.by_id(my_region, game_ids[game_id])
	    games += 1
	    total_duration = total_duration + game['gameDuration']
	average_duration = total_duration / games
	average_duration_mins = round(average_duration / 60)
	return average_duration_mins + 5



def time_remaining():
	"""
	"""
	now = datetime.now()
	time_start = 1020
	current_time = now.strftime("%H:%M:%S")

	current_hour = int(current_time[:2])
	current_minutes = int(current_time[3:5])
	time_used = 0
	if current_hour >= 2 and current_hour < 9:
		return 0
	else:
		time_used = time_start - ((current_hour - 9) * 60) - current_minutes
	return time_used

def get_total_needed_wins(needed_wins, matches_possible):
	"""
	"""
	assert needed_wins <= matches_possible
	for i in range(matches_possible):
		num1 = i + needed_wins
		num2 = i
		if num1 + num2 == matches_possible or num1 + num2 == matches_possible + 1:
			return num1


def get_chances(summoner_name):
	"""
	"""
	user_id = get_summoner_id(summoner_name)
	account_id = get_account_id(summoner_name)

	average_duration = get_average_gametime(account_id)
	time_left = time_remaining()
	winrate = get_today_winrate(account_id)
	current_lp = get_lp(user_id)
	needed_wins = get_matches_needed(current_lp)
	matches_possible = math.floor(time_left / average_duration)
	color = ''

	if needed_wins > matches_possible:
		print(needed_wins)
		print(matches_possible)
		return {'red':50}
	else:
		if int(winrate) == 0:
			winrate = 15
		elif int(winrate) == 100:
			winrate = 85
		chance = winrate / 100
		for i in range(needed_wins):
			if i > 0:
				chance = chance * (winrate / 100)
				print(chance)
		print(chance)
		if chance * 100 < 50:
			chance = chance * 100
			chance = 100 - chance
			color = 'red'
		else:
			chance = chance * 100
			color = 'blue'

		chance = round(chance)
		if chance == 100:
			chance = 99
		print({color:chance})
		return {color:chance}



def main(summoner_name):
	"""
	"""
	window = tk.Tk()
	window.geometry('800x800')

	canvas = tk.Canvas(window, bg = 'white', height = 5000, width = 5000)

	fill_area(canvas, 0, ('#d0efff','#ffbaba'))
	fill_area(canvas, 22.5, ['#2a9df4'])
	fill_area(canvas, 45, ['#187bcd'])
	fill_area(canvas, 67.5, ['#1167b1'])
	fill_area(canvas, -22.5, ['#ff7b7b'])
	fill_area(canvas, -45, ['#ff5252'])
	fill_area(canvas, -67.5, ['#d10404'])


	line22degrees = canvas.create_line(34.687, 350.753, 395, 500, width=2, fill = 'black')
	line45degrees = canvas.create_line(670.772,224.228,395,500, width=2, fill = 'black')
	line67degrees = canvas.create_line(245.753, 139.687, 395, 500, width=2, fill = 'black')
	line90degrees = canvas.create_line(395,110,395,500, width=2, fill = 'black')
	line112degrees = canvas.create_line(544.247, 139.687, 395, 500, width=2, fill = 'black')
	line135degrees = canvas.create_line(119.228,224.228,395,500, width=2, fill = 'black')
	line157degrees = canvas.create_line(755.313,350.753,395,500,width=2, fill = 'black')

	text11degrees = canvas.create_text(149.804, 451.227, text='Implausible', font =('Helvetica',12))
	text33degrees = canvas.create_text(187.133,361.107, text = 'Improbable', font =('Helvetica',12))
	text56degrees = canvas.create_text(256.107,292.133, text='Unlikely', font =('Helvetica',12))
	text88degrees = canvas.create_text(345.158, 255.018, text='Maybe', font =('Helvetica',12))
	text101degrees = canvas.create_text(444.842, 255.018, text='Maybe', font =('Helvetica',12))
	text123degrees = canvas.create_text(533.893,292.133, text='Likely', font =('Helvetica',12))
	text156degrees = canvas.create_text(602.867,361.107, text = 'Probably', font =('Helvetica',12))
	text168degrees = canvas.create_text(640.196,451.227, text = 'Certainly', font =('Helvetica',12))
	spinner = canvas.create_arc(10, 110, 790, 890, start=0, extent=180, fill=None, width=7)

	pointer = canvas.create_line(395, 300, 395, 500, width = 13)
	pointer_base = create_circle(canvas, 395, 500, 20, 'black')

	status_message = tk.Label(window, text='Leaning ...', font=('Helvetica',18), bg='white')
	status_message.place(x=395, y=600, anchor = 'center')
	packWidget(canvas)
	try:
		information = get_chances(summoner_name)
		message_helper = ''
		if list(information.keys())[0] == 'red':
			message_helper = 'stays the same rank.'
		else:
			message_helper = 'moves up one divison.'
		rotate_pointer(pointer, canvas, list(information.values())[0], list(information.keys())[0], status_message)
		percentage_message = tk.Label(window, text=str(list(information.values())[0]) + ' percent chance ' + summoner_name + ' ' + message_helper, font=('Helvetica',18), bg='white')
		percentage_message.place(x=395, y=700, anchor = 'center')
	except:
		percentage_message = tk.Label(window, text=summoner_name + ' has not played today.', font=('Helvetica',18), bg='white')
		percentage_message.place(x=395, y=700, anchor = 'center')
		status_message.config(text = '')



	#IMAGE TUT.
	#bunny_image = Image.open('PythonImages/bunny.jpg')
	#test = ImageTk.PhotoImage(bunny_image)
	#label1 = tk.Label(image = test)
	#label1.image = test
	#label1.place(x=0,y=0)
