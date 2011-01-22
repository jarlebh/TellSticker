#
# ------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <eirik.hodne at gmail.com> wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return, eirik.
# ------------------------------------------------------------------------------
#
#
# TellSticker version 0.7 (22th of January, 2011)
#
# ------------------------------------------------------------------------------
# Changelog:
# ------------------------------------------------------------------------------
#
# Version 0.7 (22th of January, 2011)
# - Make it work on Plex/Nine
#
# Version 0.6 (19th of February, 2010)
# - Have to reload the TelldusCore library every time we show the main menu (unfortunately9 to know if there are new or deleted devices
# 
# Version 0.5 (16th of February, 2010)
# - Hopefully fixes some navigational problems; http://forums.plexapp.com/index.php?/topic/12490-tellsticker-a-tellstick-plug-in/page__view__findpost__p__77053
# - Fixed weird "undo" behaviour; http://forums.plexapp.com/index.php?/topic/12490-tellsticker-a-tellstick-plug-in/page__view__findpost__p__77105
#
# Version 0.4 (Xth of February, 2010) 
# - Small memory clean-ups
#
# Version 0.3 (1th of February, 2010) 
# - Able to dim devices that supports it
#
# Version 0.2 (1th of February, 2010)
# - Complete rewrite using TelldusCore C library instead of tdtool command line app
# - Able to bell devices which supports it
#
# Version 0.1
# - Initial version
# - Able to turn devices on or off


# Import Tellstick class definition from tellstick.py:

import tellstick

####################################################################################################

APPLICATIONS_PREFIX = "/applications/tellsticker"

NAME  = "TellSticker"
ART   = "art-default.jpg"
ICON  = "icon-default.png"

####################################################################################################

def Start():

    Plugin.AddPrefixHandler(APPLICATIONS_PREFIX, ApplicationsMainMenu, NAME, ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    ## set some defaults
    
    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)

def ValidatePrefs():
		if(loadTelldusCore()):
			return MessageContainer(
				"Success",
				"Location ok, TelldusCore library loaded."
			)
		else:
			return MessageContainer(
				"Error",
				"TelldusCore library not found. You need to provide a valid location to the library. Usually it is located at /Library/Frameworks/TelldusCore.framework/Versions/Current/TelldusCore"
		)

def loadTelldusCore():
	p = Prefs['tellduscore_path']
	if(Dict['TSLib']):
		Dict['TSLib'].UnLoadLibrary()
		del Dict['TSLib']
	Dict['TSLib'] = tellstick.TellStick(p)
	
	return Dict['TSLib'].LoadLibrary()

def ApplicationsMainMenu():
		dir = MediaContainer(viewGroup="InfoList", noCache=True)
		if(not loadTelldusCore()):
			dir.Append(
				PrefsItem(
				title="Error",
				subtile="Could not load TelldusCore Library",
				summary="Please make sure you have installed TelldusCenter and that you have set a correct location to the TelldusCore library in your preferences.",
				thumb=R('icon-off.png')
				)
			)
		else:
			controls = Dict['TSLib'].GetDevices()
			
			if(controls):
				for c_item in controls:
					dir.Append(getDirItem(c_item))
			
			else:
				dir.Append(
					PrefsItem(
					title="No devices",
					subtile="Could not get any devices",
					summary="Please make sure you have setup some devices in TelldusCenter or tdtool.",
					thumb=R('icon-off.png')
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

def getDirItem(item):
	str_state = Dict['TSLib'].GetDeviceStatusAsString(item[0])
	features = Dict['TSLib'].GetDeviceFeatures(item[0])
	
	if(features & tellstick.TELLSTICK_DIM):
		diritem = PopupDirectoryItem(
							showDimMenu,
							item[1],
							subtitle=str_state.upper(),
							summary="Press enter to control this device.",
							thumb=R('icon-' + str_state + '.png'),
							art=R(ART)
						)
	elif(features & tellstick.TELLSTICK_BELL):
		diritem = DirectoryItem(
							bellDevice,
							item[1],
							subtitle="BELL",
							summary="Press enter to bell device.",
							thumb=R('icon-on.png'),
							art=R(ART)
						)
		
	elif(features & tellstick.TELLSTICK_TURNON and features & tellstick.TELLSTICK_TURNOFF):
		diritem = DirectoryItem(
							switchDevice,
							item[1],
							subtitle=str_state.upper(),
							summary="Press enter to turn device " + reverseStatus(str_state) + ".",
							thumb=R('icon-' + str_state + '.png'),
							art=R(ART)
						)
	else:
		diritem = DirectoryItem(
							doNothing,
							"Error",
							subtitle="Unsupported features",
							summary="This device does not support being switched on/off or being belled. These are the only operations this software can handle.",
							thumb=R('icon-off.png'),
							art=R(ART)
						)
	return Function(diritem, status = item[2], subtitle = diritem.subtitle, summary = diritem.summary)
								
def switchDevice(sender, status, subtitle, summary):
	
	if(status == tellstick.TELLSTICK_TURNOFF):
		retval = Dict['TSLib'].TurnOn(Dict['TSLib'].GetDeviceIdFromName(sender.itemTitle))
	elif (status == tellstick.TELLSTICK_TURNON):
		retval = Dict['TSLib'].TurnOff(Dict['TSLib'].GetDeviceIdFromName(sender.itemTitle))
	else:
		retval = tellstick.TELLSTICK_ERROR_UNKNOWN
	
	if(retval != tellstick.TELLSTICK_SUCCESS):
		return MessageContainer(
			"TellStick Error:",
			Dict['TSLib'].GetErrorString(retval)
		)
	
	setStatus(reverseStatus(Dict['TSLib'].GetDeviceStatusAsString(sender.itemTitle)),listitem)
	
def bellDevice(sender, status, subtitle, summary):
	
	retval = Dict['TSLib'].Bell(Dict['TSLib'].GetDeviceIdFromName(sender.itemTitle))
		
	if(retval != tellstick.TELLSTICK_SUCCESS):
		return MessageContainer(
			"TellStick Error:",
			Dict['TSLib'].GetErrorString(retval)
		)

def doNothing(sender, status, subtitle, summary):
	return 0

def showDimMenu(sender,status,listitem):
	dir = MediaContainer(viewGroup="InfoList", noCache=True)

	itemid = Dict['TSLib'].GetDeviceIdFromName(sender.itemTitle)
	item = Dict['TSLib'].GetDevice(itemid)
	
	# ON SWITCH
	diritem = PopupDirectoryItem(
							handleDimMenu,
							"Turn on",
							subtitle="ON",
							summary="Press enter to turn on this device.",
						)
	dir.Append(Function(diritem, id = itemid, action = tellstick.TELLSTICK_TURNON))
	# OFF SWITCH
	diritem = PopupDirectoryItem(
							handleDimMenu,
							"Turn off",
							subtitle="OFF",
							summary="Press enter to turn off this device.",
						)
	dir.Append(Function(diritem, id = itemid, action = tellstick.TELLSTICK_TURNOFF))
	
	for i in range(0,6):
		dimlevel = i * 20
		dimlevel_str = unicode(dimlevel)
		diritem = PopupDirectoryItem(
							handleDimMenu,
							"Dim to " + dimlevel_str + "%",
							subtitle="Dim " + dimlevel_str + " %",
							summary="Press enter to dim this device to " + dimlevel_str + " %.",
						)
		dir.Append(Function(diritem, id = itemid, action = tellstick.TELLSTICK_DIM, level = dimlevel))
	return dir
	
def handleDimMenu(sender,id,action, level = 0):
	if (action & tellstick.TELLSTICK_TURNON):
		retval = Dict['TSLib'].TurnOn(id)
	elif (action & tellstick.TELLSTICK_TURNOFF):
		retval = Dict['TSLib'].TurnOff(id)
	elif (action & tellstick.TELLSTICK_DIM):
		retval = Dict['TSLib'].Dim(id,level)
	else:
		retval = tellstick.TELLSTICK_ERROR_UNKOWN
	
	if(retval != tellstick.TELLSTICK_SUCCESS):
		return MessageContainer(
			"TellStick Error:",
			Dict['TSLib'].GetErrorString(retval)
		)

def setStatus(status, subtitle, summary):
	subtitle = status.upper()
	summary = "Device status: " + status.upper()
	thumb=R('icon-' + status.lower() + '.png')
	
def reverseStatus(curStatus):
	if(curStatus.lower() == "off"):
		return "on"
	elif(curStatus.lower() == "on"):
		return "off"
	else:
		return "unknown state"