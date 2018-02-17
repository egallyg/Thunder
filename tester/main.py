#~~~Thunder~~~Written by Erik Gallagher 2017

#~~~Imports:
# pigpio - Basic raspberry pi input/output pin control
# time - used to sleep and keep track of beats/time
# threading - used to simultaneously work and sleep on multiple LED strips
import pigpio
import time
import threading

#~~~Globals:
# pi - initialization of the raspberry pi GPIO commands, specifically noting that we are controlling the local device
# ChannelList - a master list of all channels (LED strips) available to address
pi = pigpio.pi()
ChannelList = []

#~~~Color:
# Mainly for readability during testing
# Upon __init__, takes 3 arguments to denote a color value for each primary color: Red, Green, and Blue
# Used to easily add different Events
class Color:
    def __init__(self,R,G,B):
        self.Red = R
        self.Green = G
        self.Blue = B

#~~~Channel:
# Denotes the division between LED strips
# Inherits from threading - any instance has a "run" function
# that automatically starts when call is made to Channel.start()
# On __init__, takes 3 int values to denote which GPIO pins are linked to this LED strip / Channel
# These values should be made hard-coded and static when a production build is viable
# Additionally, a list called EventList is initialized, that will hold any LED events that occur on this channel
# On run(), any items in EventList are triggered
# This method is called internally - once Channel.start() is called, Thread will call run()
class Channel(threading.Thread):

    def __init__(self,R,G,B):
        threading.Thread.__init__(self)
        self.EventList = []
        self.RedPin = R
        self.BluePin = B
        self.GreenPin = G

    def run(self):
        # print(len(self.EventList))
        for x in self.EventList:
            x.run(self.RedPin,self.GreenPin,self.BluePin)

#~~~Blank:
# An Event defined by a complete power-down of the calling channel (turning the LED strip off)
# On __init__, take in an int that represents how long the channel will wait for the next command
# On run(), take in the red,green,and blue pin numbers from the calling channel
# After that, change the power on the given pins to 0
# Finally, sleep the thread for the given duration
# pi.set_PWM_dutycycle(Pin #, Intensity) sets the given pi's pin # to given intensity, ranging from 0(off) to 255
class Blank:

    def __init__(self,D):
        self.Duration = D

    def run(self,R,G,B):
        self.RPin = R
        self.GPin = G
        self.BPin = B
        pi.set_PWM_dutycycle(self.RPin,0)
        pi.set_PWM_dutycycle(self.GPin,0)
        pi.set_PWM_dutycycle(self.BPin,0)
        print(pi.get_PWM_dutycycle(self.RPin))
        print(pi.get_PWM_dutycycle(self.GPin))
        print(pi.get_PWM_dutycycle(self.BPin))
        # lock.release()

        time.sleep(self.Duration)


        print(pi.get_PWM_dutycycle(self.RPin))
        print(pi.get_PWM_dutycycle(self.GPin))
        print(pi.get_PWM_dutycycle(self.BPin))

#~~~Flash
# An event defining a color being "turned on" then afterwards "turned off"
# On __init__, take in a Color and an int representing the duration
# On run(), take in the 3 GPIO pins from the calling channel to be activated
# The brightness of each pin is set depending upon the Color sent on init
# After the pins have been set, sleep the thread for the duration given in init before accepting new events
# pi.set_PWM_dutycycle(Pin #, Intensity) sets the given pi's pin # to given intensity, ranging from 0(off) to 255
class Flash:

    def __init__(self,C,D):
        self.FlashColor = C
        self.FlashDuration = D

    def run(self,RPin,GPin,BPin):
        pi.set_PWM_dutycycle(RPin,self.FlashColor.Red)
        pi.set_PWM_dutycycle(GPin,self.FlashColor.Green)
        pi.set_PWM_dutycycle(BPin,self.FlashColor.Blue)
        time.sleep(self.FlashDuration)

#~~~Strobe:
# An Event defining repetitive flashing for a certain duration and frequency
# On __init__, take in a Color, an int representing duration, and an int representing frequency
# Frequency = desired flashes per second
# On run(), take in the 3 GPIO pins representing the 3 colors on the calling LED strip/ Channel
# In a loop, first power the Channel to the given color
# Then sleep the thread depending on how many times a second the color needs to be flashed
# Afterwards, turn the Channel off and sleep the same amount of time
# Repeat this loop until the total duration has been satisfied
# May need to be edited in future to include longer/shorter "on" strobes
# pi.set_PWM_dutycycle(Pin #, Intensity) sets the given pi's pin # to given intensity, ranging from 0(off) to 255
class Strobe:
    def __init__(self,C,D,F):
        self.Color = C
        self.Duration = D
        self.Frequency = F

    def run(self,RPin,GPin,BPin):
        for x in range(0, self.Frequency * self.Duration):
            pi.set_PWM_dutycycle(RPin,self.Color.Red)
            pi.set_PWM_dutycycle(GPin, self.Color.Green)
            pi.set_PWM_dutycycle(BPin, self.Color.Blue)
            time.sleep(.5/self.Frequency)
            pi.set_PWM_dutycycle(RPin,0)
            pi.set_PWM_dutycycle(GPin, 0)
            pi.set_PWM_dutycycle(BPin, 0)
            time.sleep(.5/ self.Frequency)

#~~~Fade:
# An event defining a smooth transition between 2 colors
# On init, take in an originating Color, a destination Color, and desired duration of effect
# Init also calculates how "far" each primary color is away from the destination, saved to DRed, DGreen, and DBlue
# On run(), take in the 3 GPIO pins from the calling channel to change colors of
# An arbitrary number of 100 is used to determine how many "steps" the pins take to make the transition smooth
# Each iteration of the main loop changes the pins 1/100 of the way they need to go
# Then the thread is slept 1/100 of the total time
# pi.set_PWM_dutycycle(Pin #, Intensity) sets the given pi's pin # to given intensity, ranging from 0(off) to 255
class Fade:
    def __init__(self,CF,CT,D):
        self.ColorFrom = CF
        self.ColorTo = CT
        self.Duration = D
        self.DRed = self.ColorTo.Red - self.ColorFrom.Red
        self.DGreen = self.ColorTo.Green - self.ColorFrom.Green
        self.DBlue = self.ColorTo.Blue - self.ColorFrom.Blue

    def run(self,R,G,B):
        for x in range(0,100):
            self.RPin = R
            self.GPin = G
            self.BPin = B
            self.ColorFrom.Red += self.DRed/100
            self.ColorFrom.Green += self.DGreen / 100
            self.ColorFrom.Blue += self.DBlue / 100
            pi.set_PWM_dutycycle(self.RPin,self.ColorFrom.Red)
            pi.set_PWM_dutycycle(self.GPin, self.ColorFrom.Green)
            pi.set_PWM_dutycycle(self.BPin, self.ColorFrom.Blue)
            time.sleep(self.Duration/100)


#~~~Load:
# Reads from a file in order to populate each channel with various events.
# Event depends on the first character in each line
# Event parameters are stated afterwards in the file
# Channel change format - C [Channelnumber]
# Fade format - F [from red] [from green] [from blue] [to red] [to green] [to blue] [duration]
# Flash format - f [red] [green] [blue] [duration]
# Blank format - B [duration]
# Strobe format - S [red] [green] [blue] [duration] [frequency/second]
def LoadEvents(F):
    mode = 0
    activeChannel = 0
    File = open(F,"r")
    global ChannelList
    EventFile = File.readlines()
    for line in EventFile:
        words = line.split()
        if(words[0] == "I"): #Init reads line one to make a channel for each.
            for i in range(0,int(words[1])):
                ch = Channel(words[2+(3*i)],words[3+(3*i)],words[4+(3*i)])
                ChannelList.append(ch)
        if (words[0] == "C"): #Changes active channel to append to
            activeChannel = int(words[1])
            print("Changing to channel ", activeChannel) #Debug
        elif(words[0] == "F"): #Fade
            c1 = Color(int(words[1]),int(words[2]),int(words[3]))
            c2 = Color(int(words[4]),int(words[5]),int(words[6]))
            F = Fade(c1,c2,int(words[7]))
            ChannelList[activeChannel].EventList.append(F)
            print("Adding fade to channel ",activeChannel) #Debug
            print("Fade uses colors ",c1.Red,c1.Green,c1.Blue," and ",c2.Red,c2.Green,c2.Blue) #Debug
        elif(words[0] == "f"): #Flash
            c1 = Color(int(words[1]),int(words[2]),int(words[3]))
            f = Flash(c1,int(words[4]))
            ChannelList[activeChannel].EventList.append(f)
            print("Adding flash to channel ",activeChannel)
        elif(words[0] == "B"): #Blank
            B = Blank(int(words[1]))
            ChannelList[activeChannel].EventList.append(B)
            print("Blanking channel ", activeChannel) #Debug
        elif(words[0] == "S"): #Strobe
            C = Color(int(words[1]),int(words[2]),int(words[3]))
            S = Strobe(C, int(words[4]), int(words[5]))
            ChannelList[activeChannel].EventList.append(S)
            print("Adding strobe to channel ",activeChannel)


def Go():
    Channel1 = Channel(16, 20, 21)
    Channel2 = Channel(26, 19, 13)
    #TODO add other 3 channels and pins
    ChannelList.append(Channel1)
    ChannelList.append(Channel2)
    LoadEvents("/home/pi/Desktop/hi")

    for i in ChannelList:
        i.start()
    for i in ChannelList:
        i.join()

Go()
