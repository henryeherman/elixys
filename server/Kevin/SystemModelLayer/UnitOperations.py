"""Unit operations

Elixys Unit Operations
"""

## TO DO:
## MAKE list of all private variables
## UPDATE list of constants
##

from threading import Thread

#Z Positions
UP = "UP"
DOWN = "DOWN"

#Reactor X Positions
REACT_A = "REACTA"
REACT_B = "REACTB"
INSTALL = "INSTALL"
TRANSFER = "TRANSFER"
RADIATION = "RADIATION"
EVAPORATE = "EVAPORATE"
ADDREAGENT = "ADDREAGENT"
VIALREMOVE = "VIALREMOVE"
ON = 1
OFF = 0

#Robot Coordinate positions:
LOAD_A = "LOAD_A"
LOAD_B = "LOAD_B"
VAIL_1 = "VIAL_1"
VIAL_2 = "VIAL_2"
VIAL_3 = "VIAL_3"
VIAL_4 = "VIAL_4"
VIAL_5 = "VIAL_5"
VIAL_6 = "VIAL_6"
VIAL_7 = "VIAL_7"
VIAL_8 = "VIAL_8"

#Comparators for 'waitForCondition' function
EQUAL = "="
GREATER = ">"
LESS = "<"

#Private Variables by function:
#All Unit Operations
##self.params (List of all parameters for a unit operation)
##self.ReactorID (ID of current reactor)
##self.delay (Time in milliseconds to delay between polling variables for each step in unit operations -- defaults to 50ms if not changed)
##self.isRunning  (Running flag, when set Sequence will poll data and send to client)
##self.isPaused (Pause flag, when set, unit operation will pause after next set of instructions)
##self.stepCount (Keeps track of each step of a unit operation)
##self.stepDescription (String that describes current step in this format "Moving to position:Moving down"
##self.currentAction (String that describes what is happening inside the unit operation)

#React Operation
##
##
##
##
#Evaporate Operation
##
##
##
##
#User Input Operation
##
##
##
##
class UnitOperation(Thread):
  def __init__(self,systemModel):
    Thread.__init__(self)
    self.params = {"param":"value"}
    self.systemModel = systemModel
    self.currentStepNumber = 0
    self.isRunning = False
    self.isPaused = False
    
      #Temporary implementation to be changed.
  def setParams(self,params): #Params come in as Dict, we can loop through and assign each 'key' to a variable. Eg. self.'key' = 'value'
    for paramname in params.keys():
      if paramname=="Temp":
        self.Temp = paramname['Temp']
      if paramname=="Time":
        self.Time = paramname['Time']
      if paramname=="coolTemp":
        self.coolTemp = paramname['coolTemp']
      if paramname=="ReactorID":
        self.ReactorID = paramname['ReactorID']
      if paramname=="ReagentID":
        self.ReagentID = paramname['ReagentID']
      if paramname=="stirSpeed":
        self.stirSpeed = paramname['stirSpeed']
      if paramname=="isCheckbox":
        self.isCheckbox = paramname['isCheckbox']
      if paramname=="userMessage":
        self.userMessage = paramname['userMessage']
      if paramname=="description":
        self.description = paramname['description']
      if paramname=="stopcockPosition":
        self.stopcockPosition = paramname['stopcockPosition']
      if paramname=="transferReactorID":
      self.transferReactorID = paramname['transferReactorID']
      if paramname=="reagentLoadPosition":
        self.reagentLoadPosition = paramname['reagentLoadPosition']
      if paramname=="reactPosition":
        self.reactPosition = paramname['reactPosition']
        
  def logError(self,error):
    """Get current error from hardware comm."""
    print error
    #error.log("error")
    
  def beginNextStep(self,nextStepText = ""):
    if self.pause:
      self.paused()
    if nextStepText:
      self.stepDescription = nextStepText
    self.currentStepNumber+=1
    self.setDescription()
  
  def setReactorPosition(self,reactorPosition,ReactorID = self.ReactorID):
    storeDelayValue= self.delay #Save the current value for after this is finished.
    self.delay = 1000 # Set delay to 1 second
    if not(self.waitForCondition(self.systemModel[ReactorID]['motion'].getCurrentXPosition,self.reactPosition,EQUAL)):
      self.setDescription("Moving Reactor%s down." % ReactorID)
      self.systemModel[ReactorID]['motion'].setZPosition(DOWN)
      self.waitForCondition(self.systemModel[ReactorID]['motion'].getCurrentZPosition,DOWN,EQUAL)
      self.setDescription("Moving Reactor%s to position %s." % (ReactorID,reactorPosition))
      self.systemModel[ReactorID]['motion'].setXPosition(reactorPosition)
      self.waitForCondition(self.systemModel[ReactorID]['motion'].getCurrentXPosition,reactorPosition,EQUAL)
      self.setDescription("Moving Reactor%s up." % ReactorID)
      self.systemModel[ReactorID]['motion'].setZPosition(UP)
      self.waitForCondition(self.systemModel[ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
    else: #We're in the right position, check if we're sealed.
      if not(self.waitForCondition(self.systemModel[ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)):
        self.setDescription("Moving Reactor%s down." % ReactorID)
        self.systemModel[ReactorID]['motion'].setZPosition(UP)
        self.waitForCondition(self.systemModel[ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
      else:
        self.setDescription("Reactor%s already in position %s." % (ReactorID,reactorPosition))
    self.delay = storeDelayValue #Restore previous delay value
    
  def waitForCondition(function,condition,comparator,timeout=3): #Timeout in seconds, default to 3.
    startTime = time.time()
    if comparator == EQUAL:
      while not(function() == condition):
        self.timeDelay(self.delay)
        if isTimerExpired(startTime,timeout):
          logError("ERROR: waitForCondition call timed out on function:%s class:%s" % (function.__name__,function.im_class))
          #ERROR
    elif comparator == GREATER:
      if not(function() >= condition):
        self.timeDelay(self.delay)
        if isTimerExpired(startTime,timeout):
          logError ("ERROR: waitForCondition call timed out on function:%s class:%s" % (function.__name__,function.im_class))
          #ERROR
    elif comparator == LESS:
      if not(function() <= condition):
        self.timeDelay(self.delay)
        if isTimerExpired(startTime,timeout):
          logError ("ERROR: waitForCondition call timed out on function:%s class:%s" % (function.__name__,function.im_class))
          #ERROR
    else:
      LogError("Error: Invalid comparator.")
      return False
    return True
    
  def checkForCondition(function,condition,comparator):
    if comparator == EQUAL:
      while not(function() == condition):
        return False
    elif comparator == GREATER:
      if not(function() >= condition):
        return False
    elif comparator == LESS:
      if not(function() <= condition):
        return False
    else:
      logError("Error: Invalid comparator.")
      return False
    return True
    
  def startTimer(self,timerLength): #In seconds
    timerStartTime = time.time()  #Create a time
    while not(isTimerExpired(timerStartTime,timerLength)):
      setDescription("Time remaining:%s" % formatTime(timerLength-timerStartTime))
      self.timeDelay() #Sleep 50ms between checks
      
  def isTimerExpired(startTime,timeout):
    if (time.time()-startTime >= timeout):
      return True
    return False
    
  def formatTime(timeValue):
    hours = 0
    minutes = 0
    seconds = 0
    if timeValue >= 3600:
      hours = int(timeValue/3600)
      timeValue = timeValue % 3600 
    if timeValue >= 60:
      minutes = int(timeValue/60)
      seconds = timeValue % 60 
    if timeValue < 60:
      seconds = int(timeValue)
    if hours:
      return("%.2d:%.2d:%.2d" % (hours,minutes,seconds))
    elif minutes:
      return("00:%.2d:%.2d" % (minutes,seconds))
    else:
      return("00:00:%.2d" % seconds)
    
  def timeDelay(self,delay=50): #delay = time in milliseconds, default to 50ms
    if delay:
      time.sleep(self.delay/1000.00) #If a value is set, use it, otherwise default. Divide by 1000.00 to get ms as a float.
    else:
      time.sleep(0.05)#default if delay = None or delay = 0
    
  def setUnpause(self):
    self.pause = False
    
  def setPause(self):
    self.pause = True
    
  def paused(self):
    while self.pause:
      pass
      
  def setDescription(newDescription = ""):
    if newDescription:
      self.currentStepDescription = self.stepDescription+":"+newDescription
      
  def abort():
    #Safely abort -> Do not move, turn off heaters, turn set points to zero.
    self.systemModel[self.ReactorID]['temperature_controller'].setTemperature(0)
    
  def getTotalSteps(self):
    return self.steps #Integer
    
  def isRunning(self):
    return self.isRunning
    
  def getCurrentStepNumber(self):
    return self.stepCounter

  def getCurrentStepName(self):
    return self.currentStep

  def setParam(self,name,value): #(String,Any)
    self.params[name] = value
    
  def getParam(self,name): #String
    return self.params[name]
    
    

   
class React(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
    #self.Temp
    #self.time
    #self.coolTemp
    #self.reactPosition
  def run(self):
    self.beginNextStep("Starting React Operation")
    self.beginNextStep("Moving to position")
    self.setReactorPosition(self.reactPosition)#REACTA OR REACTB
    self.beginNextStep("Setting reactor temperature")
    self.setTemp()
    self.beginNextStep("Starting stir motor")
    self.currentAction("Starting heater")
    self.setStirring()
    self.startHeating()
    self.stepDescription("Starting timer")
    self.startTimer(self.Time)
    self.beginNextStep("Starting cooling")
    self.setCool()
    self.beginNextStep("React Operation Complete!")

  def setStirring(self):
    self.systemModel[self.ReactorID]['stir_motor'].setSpeed(self.stirSpeed) #Set analog value on PLC
    self.waitForCondition(self.systemModel[self.ReactorID]['stir_motor'].getCurrentSpeed,self.stirSpeed,EQUAL) #Read analog value from PLC... should be equal
  
  def setTemp(self):
    self.systemModel[self.ReactorID]['temperature_controller'].setTemperature(self.Temp)
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getCurrentTemperature,self.Temp,GREATER)
   
  def setCool(self):
    self.systemModel[self.ReactorID]['temperature_controller'].setHeaterState(OFF)
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getHeaterState,OFF,EQUAL)
    self.systemModel[self.ReactorID]['cooling_system'].setCooling(ON)
    self.waitForCondition(self.systemModel[self.ReactorID]['cooling_system'].getCooling,ON,EQUAL)
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getTemperature(),self.coolTemp) 
    self.systemModel[self.ReactorID]['cooling_system'].setCooling(OFF)
    self.waitForCondition(self.systemModel[self.ReactorID]['cooling_system'].getCooling,OFF,EQUAL)

class AddReagent(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
    #self.ReagentID
    #self.reagentLoadPosition

  def run(self):
    self.steps=["Starting add reagent operation","Moving to addition position","Adding reagent","Removing empty vial"]
    self.beginNextStep()
    self.setReactorPosition(self.reagentPosition)
    self.beginNextStep()
    self.setGripperPlace()
    self.timeDelay()
    self.beginNextStep()
    self.setGripperRemove()
    self.beginNextStep()

  def setGripperPlace():
    if self.checkForCondition(self.systemModel[self.Gripper].getGripperState,GRIP,EQUAL):
      if self.checkForCondition(self.systemModel[self.Gripper].getCurrentZPosition,DOWN,EQUAL):
        if (self.checkForCondition(self.systemModel[self.Gripper].getCoordinate,LOAD_A,EQUAL) or self.checkForCondition(self.systemModel[self.Gripper].getCoordinate,LOAD_B,EQUAL)):
          #We are in the load position, we should not be here. Error.
          logError("ERROR: In load position, calling setGripperPlace()")
        else:
          #We are gripped and down, just ungrip?
          logError("ERROR: setGripperPlace() called while already gripped in down position.")
      else:
        #Error, why are we already gripped and not in a down position? 
        logError("ERROR: setGripperPlace() called while already gripped in raised position.")
    if not(self.waitCheckCondition(self.systemModel[self.Gripper].getCoordinate,self.ReagentID,EQUAL)):
      self.systemModel[self.Gripper].setZPosition(UP)
      self.waitForCondition(self.systemModel[self.Gripper].getCurrentZPosition,UP,EQUAL)
      self.systemModel[self.Gripper].setCoordinate(self.ReagentID)
      self.waitForCondition(self.systemModel[self.Gripper].getCoordinate,self.ReagentID,EQUAL)
      self.systemModel[self.Gripper].setZPosition(DOWN)
      self.waitForCondition(self.systemModel[self.Gripper].getCurrentZPosition,DOWN,EQUAL)
      self.systemModel[self.Gripper].setGripperState(GRIP)
      self.waitForCondition(self.systemModel[self.Gripper].getGripperState,GRIP,EQUAL)
    else: #We're in the right position, make sure we're down on the vial and grip it.
      self.systemModel[self.Gripper].setZPosition(DOWN)
      self.waitForCondition(self.systemModel[self.Gripper].getCurrentZPosition,DOWN,EQUAL)
      self.systemModel[self.Gripper].setGripperState(GRIP)
      self.waitForCondition(self.systemModel[self.Gripper].getGripperState,GRIP,EQUAL)
    #Regardless of above, when all is said and done, we want to move up and over to the position where the vial should go.
    self.systemModel[self.Gripper].setZPosition(UP)
    self.waitForCondition(self.systemModel[self.Gripper].getCurrentZPosition,UP,EQUAL)
    self.systemModel[self.Gripper].setCoordinate(self.reagentLoadPosition)
    self.waitForCondition(self.systemModel[self.Gripper].getCoordinate,self.reagentLoadPosition,EQUAL)
    self.systemModel[self.Gripper].setZPosition(DOWN)
    self.waitForCondition(self.systemModel[self.Gripper].getCurrentZPosition,DOWN,EQUAL)
    
  def setGripperRemove():
    if self.checkForCondition(self.systemModel[self.Gripper].getCoordinate,self.reagentLoadPosition,EQUAL):
      if self.checkForCondition(self.systemModel[self.Gripper].getCurrentZPosition,DOWN,EQUAL):
        self.systemModel[self.Gripper].setGripperState(GRIP)
        self.waitForCondition(self.systemModel[self.Gripper].getGripperState,GRIP,EQUAL)
        self.systemModel[self.Gripper].setZPosition(UP)
        self.waitForCondition(self.systemModel[self.Gripper].getCurrentZPosition,UP,EQUAL)
        self.systemModel[self.Gripper].setCoordinate(self.ReagentID)
        self.waitForCondition(self.systemModel[self.Gripper].getCoordinate,self.ReagentID,EQUAL)
        self.systemModel[self.Gripper].setZPosition(DOWN)
        self.waitForCondition(self.systemModel[self.Gripper].getCurrentZPosition,DOWN,EQUAL)
        self.systemModel[self.Gripper].setGripperState(UNGRIP)
        self.waitForCondition(self.systemModel[self.Gripper].getGripperState,UNGRIP,EQUAL)
        self.systemModel[self.Gripper].setZPosition(UP)
        self.waitForCondition(self.systemModel[self.Gripper].getCurrentZPosition,UP,EQUAL)
        self.systemModel[self.Gripper].setCoordinate(HOME)
        self.waitForCondition(self.systemModel[self.Gripper].getCoordinate,HOME,EQUAL)
      else:
        logError("Gripper in correct position for removal, but not in down position.")
    else:
      logError("Gripper not in correct position for removal when setGripperRemove() called.")

class Evaporate(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
    #self.Temp
    #self.Time
    #self.coolTemp
    #self.stirSpeed
    
  def run(self):
    self.beginNextStep()
    self.setReactorPosition(EVAPORATE)
    self.beginNextStep()
    self.setTemp()
    self.beginNextStep()
    startVacuum()
    self.startStirring()
    self.startHeating()
    self.startTimer()
    self.beginNextStep()
    self.setCool()
    self.stopStirring()
    self.stopVacuum()
    self.beginNextStep()
    
  def startStirring(self):
    self.systemModel[self.ReactorID]['stir_motor'].setSpeed(self.stirSpeed) #Set analog value on PLC
    self.waitForCondition(self.systemModel[self.ReactorID]['stir_motor'].getCurrentSpeed,self.stirSpeed,EQUAL) #Read value from PLC memory... should be equal
  
  def stopStirring(self):
    self.systemModel[self.ReactorID]['stir_motor'].setSpeed(OFF)
    self.waitForCondition(self.systemModel[self.ReactorID]['stir_motor'].getCurrentSpeed,OFF,EQUAL)
    
  def startVacuum(self):
    self.systemModel[self.ReactorID]['vacuum'].setVacuum(ON)
    self.waitForCondition(self.systemModel[self.ReactorID]['vacuum'].getVacuum,OFF,EQUAL) 
  
  def stopSVacuum(self):
    self.systemModel[self.ReactorID]['vacuum'].setVacuum(OFF)
    self.waitForCondition(self.systemModel[self.ReactorID]['vacuum'].getVacuum(OFF),ZERO,EQUAL)
 
  def getTemperatureController(): #Not sure why we need this?
    return self.systemModel[self.ReactorID]['temperature_controller']
    
  def setTemp(self):
    self.systemModel[self.ReactorID]['temperature_controller'].setSetPoint(self.Temp)
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getSetPoint,self.Temp,GREATER)
    
  def startHeating(self):
    self.systemModel[self.ReactorID]['temperature_controller'].setHeaterState(ON)
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getHeaterState,ON,EQUAL)
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getCurrentTemperature,self.Temp,GREATER)
  
  def setCool(self):
    self.systemModel[self.ReactorID]['temperature_controller'].setHeaterState(OFF)
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getHeaterState,OFF,EQUAL)
    self.systemModel[self.ReactorID]['cooling_system'].setCooling(ON)
    self.waitForCondition(self.systemModel[self.ReactorID]['cooling_system'].getCooling,ON,EQUAL)
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getTemperature(),self.coolTemp) 
    self.systemModel[self.ReactorID]['cooling_system'].setCooling(OFF)
    self.waitForCondition(self.systemModel[self.ReactorID]['cooling_system'].getCooling,OFF,EQUAL)
    
  def getTemp(self):
    self.systemModel[self.ReactorID]['temperature_controller'].getCurrentTemperature()
    
class InstallVial(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
  def run(self):
    self.steps=["Starting install vial operation","Moving to vial installation position"]
    self.beginNextStep()
    self.setReactorPosition(INSTALL)
    self.beginNextStep()
    
class TransferToHPLC(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
    
  def run(self):
    self.steps=["Starting HPLC Transfer operation","Moving to transfer position","Transferring product to HPLC","Switching injection valve"]
    self.beginNextStep()
    self.setReactorPosition(TRANSFER)
    self.beginNextStep()
    self.setTransfer()
    self.beginNextStep()
    self.setHPLCValve()
    self.beginNextStep()

  def setTransfer(self):
    self.systemModel[self.ReactorID]['transfer'].setTransfer(HPLC)
    self.waitForCondition(self.systemModel[self.ReactorID]['transfer'].getTransfer(),HPLC,EQUAL)
    
  def setHPLCValve(self):
    self.systemModel[self.ReactorID]['transfer'].setHPLC(INJECT)       
    self.waitForCondition(self.systemModel[self.ReactorID]['transfer'].getHPLC(),INJECT,EQUAL) 
  
class TransferElute(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
    #self.stopcockPosition
    
  def run(self):
    self.beginNextStep()
    self.setReactorPosition(TRANSFER)
    self.beginNextStep()
    self.setStopcock()
    self.beginNextStep()
    self.setTransfer()
    self.beginNextStep()
  
  def setStopcock(self):
    self.systemModel[self.ReactorID]['stopcock'].setStopcock(self.stopcockPosition)       
    self.waitForCondition(self.systemModel[self.ReactorID]['stopcock'].getStopcock(),self.stopcockPosition,EQUAL) 
    
  def setTransfer(self):
    self.systemModel[self.ReactorID]['transfer'].setTransfer(self.transferPosition)
    self.waitForCondition(self.systemModel[self.ReactorID]['transfer'].getTransfer(),self.transferPosition,EQUAL)
   
class Transfer(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
    #self.transferReactorID
    
  def run(self):
    self.steps=["Starting Transfer operation","Moving to transfer position","Transferring product"]
    self.beginNextStep()
    self.setReactorPosition(TRANSFER)
    self.beginNextStep()
    self.setReactorPosition(ADDREAGENT,self.transferReactorID)
    self.startTransfer()
    self.beginNextStep()

  def startTransfer(self):
    self.systemModel[self.ReactorID]['transfer'].setTransfer(self.transferPosition)
    
    self.waitForCondition(self.systemModel[self.ReactorID]['transfer'].getTransfer,self.transferPosition,EQUAL)
 
class UserInput(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.userMessage
    #self.isCheckbox
    #self.description
  def run(self):
    self.currentAction="Starting User Input operation"
    self.beginNextStep()
    self.currentAction="Message box"
    self.setMessageBox()
    self.beginNextStep()
    
  def setMessageBox(self):
    self.setDescription("Waiting for user input")
    self.waitForUser = True
    self.waitForCondition(self.getUserInput,True,EQUAL) # Zero timeout = Infinite
    self.setDescription()
    
  def getUserInput(self):
    return not(self.waitForUser)
    
class DetectRadiation(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
    
  def run(self):
    self.steps=["Starting radiation detector operation","Moving to radiation detector position","Detecting radiation"]
    self.beginNextStep()
    self.setReactorPosition(RADIATION)
    self.beginNextStep()
    self.getRadiation()
    self.beginNextStep()


  def getRadiation(self):
    self.systemModel[self.ReactorID]['radiation_detector'].getCalibratedReading()
    self.waitForCondition(self.systemModel[self.ReactorID]['radiation_detector'].getCalibratedReading,self.calibrationCoefficient,GREATER)
    
def test():
  react1 = React()
  react1.run()

    
if __name__=="__main__":
    test()