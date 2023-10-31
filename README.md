# OBS Hot Mic Indicator for use with Raspberry Pi Pico LED device
### Introduction
A script pair in Python and Micropython to have communication between OBS and a Raspberry Pi Pico micro controller that
indicates the state of the microphone. This is meant for those who are looking to create a small LED microprocessor 
device. Currently in beta, but the plan is to increase capability and give these to my friends and family. As it stands,
there is only tracking for one OBS source as the pico device I am working with is currently only using 1 LED. There is 
no update schedule as this is a side project, but as features are added and expanded I will add them here. Pico device 
features will likely be slower because I enjoy working on it with my sister. 

### Features 
- One "Hot" LED Indecator
- Serial Bus Communication
- Script internal Debug tools
- Standardized Communication that is Scalable and Expandable
- Internal Structure Ready for Expanded Features and Backward Compatability
- Simple End User Functionality - Plug it in and Select the source from the drop down of audio sources!

### Installation
1. Set up the Raspberry Pi Pico to have a LED on pin 20 (GP15). I am not an electrical engineer by trade, but I was 
reccomended to use a resistor between about 50 and 330 ohms. 

I reccomend using this tutorial:  
https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico/6

2. Load the Pico Device with `main.py`. This is also covered in the previous tutorial

3. Check the Port used by the Pico Device by going into the device manager. If the Pico Device is on COM4, you're good 
to go! If not, in `obsConnection.py` adjust line 18 `PORT = COM4` to match. I.E. if the device manager says that the 
Pico uses port COM31 then the line would be `PORT = COM31`.

4. Add the python script `obsConnection.py` to OBS using the Scripts management window. If updating file after adding 
the script, remember to refresh your scripts in OBS!

You can find a thorough guide on how do that here:  
https://obsproject.com/kb/scripting-guide

### Usage
Once all is connected and installed simply go into the script properties and select. If a source in not listed, please
check that it is attached to any audio track. This is how the script detects which sources are audio sources.
If a recently made source is not listed, press the Refresh button to have it populate into the dropdown menu.
The communication is a little delicate at the moment. If the device loses power, the script will need to be reloaded to 
reconnect. OBS closing and opening should maintain functionality. One can check if there is serial bus connection and 
which source is being tracked by using Log Info button in properties. 
As the device is still in beta, there is a Resynch button just in case the LED and OBS Muted State do not match. This 
was useful to test the Mute state detection, and have left it in just in case it is useful for further testing. 

### Near Future Goals
- 3 Lights that track seperate sources
- OBS Closing detection
- Pico Loss of Power detection
- Streaming/Recording Source tracking
- On/Off Switch for Pico
