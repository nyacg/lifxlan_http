#!/usr/bin/env python 
from flask import Flask, g, current_app
from lifxlan import *
import time
from multiprocessing import Pool


app = Flask(__name__)

lifx = LifxLAN()
bulbs = {}
global finished
finished = True
print "Finding bulbs"
for bulb in lifx.get_lights():
	lit = True if bulb.get_power() > 0 else False
	bulbs[bulb.get_label().lower()] = {'bulb': bulb, 'lit': lit, 'color': bulb.get_color()}
print "bulbs found"

@app.route("/")
def hello():

	return "Hello Guys!"

@app.route("/list")
def list_bulbs():

	return ', '.join(bulbs.keys())

@app.route("/toggle/<label>")
def toggle_label(label = None):
	bulb = bulbs.get(label.lower())	
	if bulb is not None:
		bulb_obj = bulb['bulb']
		state = bulb['lit']

		if state:
			bulb_obj.set_power("off", True)
			bulbs[label]['lit'] = False
		else:
			bulb_obj.set_power("on", True)
			bulbs[label]['lit'] = True

		return "Toggling " + label
	else: 
		return "Could not find bulb with label " + label

@app.route("/flash/<label>")
def flash_label(label = None):
	bulb = bulbs.get(label.lower())	
	if bulb is not None:
		bulb_obj = bulb['bulb']
		state = bulb['lit']

		if state:
			bulb_obj.set_power("off", False)
			time.sleep(0.2)
			bulb_obj.set_power("on", False)
			time.sleep(0.5)
			bulb_obj.set_power("off", False)
			time.sleep(0.2)
			bulb_obj.set_power("on", False)
		else:
			bulb_obj.set_power("on", False)
			time.sleep(0.5)
			bulb_obj.set_power("off", False)
			time.sleep(0.2)
			bulb_obj.set_power("on", False)
			time.sleep(0.5)
			bulb_obj.set_power("off", False)

		return "Flashing " + label
	else: 
		return "Could not find bulb with label " + label

@app.route("/setbrightness/<label>/<int:brightness>")
def brightness_label(label = None, brightness = 65535):
	bulb = bulbs.get(label.lower())	

	if brightness > 65535:
		brightness = 65532
	elif brightness < 0:
		brightness = 0

	if bulb is not None:
		bulb_obj = bulb['bulb']
		lit = bulb['lit']

		if not lit:
			# turn on if not already on
			bulb_obj.set_power("on", True)
			bulbs[label]['lit'] = True
		
		# now set brightness for current colour
		color = bulb['color']
		list_color = list(color)
		list_color[2] = brightness
		color = tuple(list_color)
		bulbs[label]['color'] = color

		bulb_obj.set_color(color, True)

		return "Setting brightness to " + str(brightness) + " for " + label
	else: 
		return "Could not find bulb with label " + label	


@app.route("/set/<label>/<int:brightness>/<int:hue>")
def color_label(label = None, brightness = 65535, hue = 10):
	start = time.time()

	bulb = bulbs.get(label.lower())	

	if brightness > 65535:
		brightness = 65535
	elif brightness < 0:
		brightness = 0

	if hue > 65535:
		hue = 65535
	elif hue < 0:
		hue = 0

	if bulb is not None:
		bulb_obj = bulb['bulb']
		lit = bulb['lit']

		if not lit:
			# turn on if not already on
			bulb_obj.set_power("on", True)
			bulbs[label]['lit'] = True
		global finished
		if finished:
			finished = False
			# now set brightness for current colour
			color = bulb['color']
			list_color = list(color)	# HSBK
			list_color[0] = hue			# hue
			list_color[1] = brightness 	# saturation
			list_color[2] = 65535		# brightness
			list_color[3] = 4000		# Kelvin
			color = tuple(list_color)
			bulbs[label]['color'] = color

			bulb_obj.set_color(color, True)
			finished = True


		#print bulb_obj.get_color();

		elapsed = time.time() - start
		print "Time elapsed " + str(elapsed)

		return "Setting brightness to " + str(brightness) + " and other " + str(hue) + " for " + label 
	else: 
		return "Could not find bulb with label " + label	


if __name__ == "__main__":
	app.run("0.0.0.0", debug=True)