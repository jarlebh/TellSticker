# PMS plugin framework
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

import os, subprocess, string

from ctypes import *
from ctypes.util import find_library

####################################################################################################

APPLICATIONS_PREFIX = "/applications/tellsticker"

NAME = L('Title')

ART           = 'art-default.png'
ICON          = 'icon-default.png'

####################################################################################################

def Start():

    Plugin.AddPrefixHandler(APPLICATIONS_PREFIX, ApplicationsMainMenu, L('ApplicationsTitle'), ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    ## set some defaults
    
    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)

def CreatePrefs():
    Prefs.Add(id='tdtool_path', type='text', default='/usr/bin/', label='Path to tdtool (default: /usr/bin/)')

def ValidatePrefs():
		if(canFindTdtool()):
			return MessageContainer(
				"Success",
				"Path ok"
			)
		else:
			return MessageContainer(
				"Error",
				"tdtool not found. You need to provide a valid path to tdtool"
		)

  
def canFindTdtool():
	p = Prefs.Get('tdtool_path')
	if(p[-1] != "/"):
		Prefs.Set('tdtool_path',Prefs.Get('tdtool_path') + "/")
	
	findRequest = subprocess.Popen(Prefs.Get('tdtool_path') + "tdtool --version", shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	stdout_value, stderr_value = findRequest.communicate()
	
	found = stdout_value.find("tdtool")
	
	if(found == -1):
		return 0
	else:
		return 1
		
def getTdTool():
	if(canFindTdtool()):
		return Prefs.Get('tdtool_path') + "tdtool"
	return 0

def ApplicationsMainMenu():

		dir = MediaContainer(viewGroup="InfoList", noCache=True)
		
		try:
			cdll.LoadLibrary("/Library/Frameworks/TelldusCore.framenwork/Versions/Current/TelldusCore")
		except OSError:
			Log("TellSticker: Could not load TelldusCore library from")
			if(not canFindTdtool()):
				myitem = DirectoryItem(
							null,
							"Library error",
							subtitle="Could not access Telldus Library or tdtool",
							summary="The program couldn't find the TelldusCore library nor the command line tdtool application. Please install TelldusCenter (and specify custom paths in the preferences if you have installed it to a custom location.",
							thumb=R('icon-off.png'),
							art=R(ART)
						)
				dir.Append(
					Function(
						myitem
						)
					)
		

		controls = getControls()

		if(controls):

			for c_item in controls:
				myitem = DirectoryItem(
							switchDevice,
								c_item[1],
								subtitle=c_item[2],
								summary="Press enter to turn device " + reverseStatus(c_item[2]) + ".",
								thumb=R('icon-' + c_item[2].lower() + '.png'),
								art=R(ART)
							)
				dir.Append(
					Function(
						myitem, status = c_item[2], listitem = myitem
						)
					)


		dir.Append(
			PrefsItem(
			title="Setup",
			subtile="TellSticker Preferences",
			summary="Lets you set preferences",
			thumb=R(ICON)
			)
		)
		return dir

def switchDevice(sender, status, listitem):
		if(status == "OFF"):
			setstatus = "on"
		else:
			setstatus = "off"
		switchRequest = subprocess.Popen(getTdTool() + " --" + setstatus + " \"" + sender.itemTitle + "\"", shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		stdout_value, stderr_value = switchRequest.communicate()
		switchOutput = stdout_value.strip()
		notFound = switchOutput.find("TellStick not found")
		if(notFound != -1):
			return MessageContainer(
				"TellStick not found",
				"Unfortunately your TellStick could not be found.\n\nAre you sure it's connected?"
			)
		
		setStatus(setstatus,listitem)

def getControls():
	controllerRequest = subprocess.Popen(getTdTool() + " -l", shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	stdout_value, stderr_value = controllerRequest.communicate()
	controls = string.split(repr(stdout_value),'\\n')
	
	numOfDevices = controls[0][-1]
	
	try:
		numOfDevices = int(numOfDevices)
	except ValueError:
		return 0

	controls_data = [[0]*3 for i in range(numOfDevices)]
	for i in range(1, numOfDevices + 1):
		control_data = string.split(controls[i],"\\t")
		controls_data[i-1][0] = control_data[0]
		controls_data[i-1][1] = control_data[1]
		controls_data[i-1][2] = control_data[2]
	
	return controls_data

def setStatus(status, listitem):
	listitem.subtitle = status.upper()
	listitem.summary = "Device status: " + status.upper()
	thumb=R('icon-' + status.lower() + '.png')
	
def reverseStatus(curStatus):
	if(curStatus.lower() == "off"):
		return "on"
	else:
		return "off"