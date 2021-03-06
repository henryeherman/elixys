""" FakePLC.py

Behaves like a PLC for testing and demo purposes """

### Imports
import socket
import configobj
import select
import time	
import sys
sys.path.append("/opt/elixys/hardware/")
sys.path.append("/opt/elixys/core/")
from HardwareComm import *
from SystemModel import SystemModel
import Utilities
from CoolingThread import CoolingThread
from PressureRegulatorThread import PressureRegulatorThread
from HomeReagentRobotThread import HomeReagentRobotThread
from MoveReagentRobotThread import MoveReagentRobotThread
from HomeReactorRobotThread import HomeReactorRobotThread
from MoveReactorLinearThread import MoveReactorLinearThread
from MoveReactorVerticalThread import MoveReactorVerticalThread
from HeatingThread import HeatingThread
import os
from daemon import daemon
import signal

import logging
import logging.config
import traceback;

logging.config.fileConfig("/opt/elixys/config/elixyslog.conf")
log = logging.getLogger("elixys.plc")
log.info("Starting Elixys FakePLC Server")

# Fake PLC class
class FakePLC():
    def __init__(self):
        """Fake PLC class constructor"""
        log.debug("Initialize FakePLC")
        # Initialize variables
        self.__pCoolingThread = None
        self.__pPressureRegulator1Thread = None
        self.__pPressureRegulator2Thread = None
        self.__pHomeReagentRobotThread = None
        self.__pMoveReagentRobotThread = None
        self.__pReactor1HomeThread = None
        self.__pReactor2HomeThread = None
        self.__pReactor3HomeThread = None
        self.__pReactor1LinearMovementThread = None
        self.__pReactor2LinearMovementThread = None
        self.__pReactor3LinearMovementThread = None
        self.__pReactor1VerticalMovementThread = None
        self.__pReactor2VerticalMovementThread = None
        self.__pReactor3VerticalMovementThread = None
        self.__pReactor1HeatingThread = None
        self.__pReactor2HeatingThread = None
        self.__pReactor3HeatingThread = None
        
    def StartUp(self):
        """Starts up the fake PLC"""
        log.debug("Start up the FakePLC")
        # Create the hardware layer
        self.__pHardwareComm = HardwareComm()
  
        # Determine the memory range we need to emulate
        self.__nMemoryLower, self.__nMemoryUpper = self.__pHardwareComm.CalculateMemoryRange()

        # Create and fill the memory buffer with zeros
        self.__pMemory = []
        for x in range(self.__nMemoryLower, self.__nMemoryUpper + 1):
            self.__pMemory.append(0)
            
        # Fill the memory buffer from the PLC memory dump
        self.__FillMemoryBuffer("/opt/elixys/hardware/fakeplc/PLC.MEM")

        # Pass a reference to the memory buffer to the HardwareComm 
        #  so we can read from it and write to it at a higher level
        self.__pHardwareComm.FakePLC_SetMemory(self.__pMemory, 
                self.__nMemoryLower, self.__nMemoryUpper)
        
        # Create the system model
        self.__pSystemModel = SystemModel(self.__pHardwareComm, None)
        self.__pSystemModel.StartUp()

        # Create the socket
        self.__pSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__pSocket.setblocking(False)
        self.__pSocket.bind(("", 9600))
            
    def Run(self):
        """Runs the fake PLC"""
        # Packet processing loop
        log.info("Fake PLC running, type 'q' and press enter to quit...")
        while True:
            # Check if the user pressed 'q' to quit
            if Utilities.CheckForQuit():
                return
        
            # Check socket availability
            pRead, pWrite, pError = select.select([self.__pSocket], [], [], 0.25)
            #log.info("Spinning")
            for pReadable in pRead:
                #log.info("It is readable")
                if pReadable == self.__pSocket:
                    # Data is available for receiving
                    pBinaryPacket = self.__pSocket.recv(1024)
                    sPacket = pBinaryPacket.encode("hex")
                    #log.debug("Received Packet of length %d" % len(sPacket))
                    # Check the message length
                    if len(sPacket) >= 36:
                        # Handle read and write messages
                        if sPacket[20:24] == "0101":
                            self.__HandleRead(sPacket)
                        elif sPacket[20:24] == "0102":
                            self.__HandleWrite(sPacket)
                        else:
                            log.error("FakePLC: Unknown command, ignoring")
                    else:
                        log.error("FakePLC: Packet too short, discarding")
            
            # Update the state of the PLC
            try:
                self.__UpdatePLC()
            except Exception as ex:
                log.error("Traceback:\r\n%s\r\n" % traceback.format_exc())
                log.error("UpdatePLC error %s" % str(ex))

    def ShutDown(self):
        """Shuts down the fake PLC"""
        # Clean up
        self.__pSocket.close()
        self.__pSocket = None
        self.__pSystemModel.ShutDown()

    def __FillMemoryBuffer(self, sFilename):
        """Fill the buffer from the file containing a dump of the actual PLC memory"""
        log.debug("FakePLC: Fille the memory buffer")
        # Open the PLC memory file
        pMemoryFile = open(sFilename, "r")
        pMemoryFileLines = pMemoryFile.readlines()
    
        # Search for the CIO memory
        sCIO = None
        for sLine in pMemoryFileLines:
            if sLine.startswith("CIO="):
                sCIO = sLine
                break
    
        # Handle error
        if sCIO == None:
            raise Exception("Failed to find CIO memory")
    
        # Trim off the "CIO=" string and split into components
        sCIO = sCIO[4:]
        pCIO = sCIO.split(",")
    
        # Fill the memory
        for pComponent in pCIO:
            # Extract the memory range
            sRange = pComponent.split(":")[0]
            pRangeComponents = sRange.split("-")
            nRangeStart = int(pRangeComponents[0])
            if len(pRangeComponents) > 1:
                nRangeEnd = int(pRangeComponents[1])
            else:
                nRangeEnd = nRangeStart
            
            # Extract the value
            nValue = int(pComponent.split(":")[1], 16)
        
            # Fill in the memory array
            for nOffset in range(nRangeStart, nRangeEnd + 1):
                if (nOffset >= self.__nMemoryLower) and (nOffset <= self.__nMemoryUpper):
                    self.__pMemory[nOffset - self.__nMemoryLower] = nValue
        
        # Clean up
        pMemoryFile.close()
        
    def __HandleRead(self, sPacket):
        """Handle the read command"""
        #log.debug("FakePLC: HandleRead")
        # We only read words
        if sPacket[24:26] != "b0":
            log.error("Invalid I/O memory area code")
            return

        # Determine the read offset and length
        nReadOffsetWord = int(sPacket[26:30], 16)
        nReadLength = int(sPacket[32:36], 16)
        
        # Read the memory
        sMemory = self.__pHardwareComm.FakePLC_ReadMemory(nReadOffsetWord, nReadLength)

        # Create and send the response
        sResponse = "0000000000000000000001010000" + sMemory
        pBinaryResponse = sResponse.decode("hex")
        self.__pSocket.sendto(pBinaryResponse, ("127.0.0.1", 9601))

    def __HandleWrite(self, sPacket):
        """Handle the write command"""
        log.debug("FakePLC:HandleWrite")
        # Determine the write offsets and length
        nWriteOffsetWord = int(sPacket[26:30], 16)
        nWriteOffsetBit = int(sPacket[30:32], 16)
        nWriteLength = int(sPacket[32:36], 16)

        # Are we writing bits or bytes?
        if sPacket[24:26] == "30":
            # Bits.  We're only writing this for a single bit at this time
            if nWriteLength != 1:
                log.error("Implement multibit writing if needed")
                return
                
            # Verify the packet length
            if len(sPacket) != 38:
                log.error("Invalid packet length")
                return

            # Extract the boolean value
            bValue = (sPacket[37] == "1")

            # Set the target bit
            self.__pHardwareComm.FakePLC_SetBinaryValue(nWriteOffsetWord, nWriteOffsetBit, bValue)
        elif sPacket[24:26] == "b0":
            # Bytes.  We're only writing this for a single byte at this time
            if nWriteLength != 1:
                log.error("Implement multibyte writing if needed")
                return
                
            # Verify the packet length
            if len(sPacket) != 40:
                log.error("Invalid packet length")
                return

            # Extract the integer value
            nValue = int(sPacket[36:40], 0x10)

            # Set the target word
            self.__pHardwareComm.FakePLC_SetWordValue(nWriteOffsetWord, nValue)
        else:
            log.error("Invalid I/O memory area code")
            return

        # Send a success packet
        sResponse = "0000000000000000000001020000"
        pBinaryResponse = sResponse.decode("hex")
        self.__pSocket.sendto(pBinaryResponse, ("127.0.0.1", 9601))

    def __UpdatePLC(self):
        """Updates the PLC in response to any changes to system changes"""
        # Check for errors
        #log.info("FakePLC: UpdatePLC")
        self.__pSystemModel.CheckForError()
        #log.info("Done with CheckForError")
        # Update the various system components
        self.__UpdateVacuumPressure()
        self.__UpdateCoolingSystem()
        self.__UpdatePressureRegulator(1)
        self.__UpdatePressureRegulator(2)
        self.__UpdateCoolingSystem()
        self.__UpdateReagentRobotStatus()
        self.__UpdateReagentRobotPosition()
        #log.info("After components")
        self.__UpdateReagentRobotGripper()
        self.__UpdateReactorRobotStatus(1)
        self.__UpdateReactorRobotStatus(2)
        self.__UpdateReactorRobotStatus(3)
        self.__UpdateReactorPosition(1)
        self.__UpdateReactorPosition(2)
        self.__UpdateReactorPosition(3)
        self.__UpdateReactorHeating(1)
        self.__UpdateReactorHeating(2)
        self.__UpdateReactorHeating(3)

    def __UpdateVacuumPressure(self):
        """Updates the vacuum pressure in response to system changes"""
        # Check if the vacuum is on and determine the target pressure
        if self.__pSystemModel.model["VacuumSystem"].getVacuumSystemOn():
            nTargetPressure = -12.4
        else:
            nTargetPressure = -71.9
        
        # Compare the pressures.  Add leeway to account for rounding errors
        nActualPressure = self.__pSystemModel.model["VacuumSystem"].getVacuumSystemPressure()
        if ((nActualPressure + 1) < nTargetPressure) or ((nActualPressure - 1) > nTargetPressure):
            # Update the actual pressure to the target pressure
            self.__pHardwareComm.FakePLC_SetVacuumPressure(nTargetPressure)
            
    def __UpdateCoolingSystem(self):
        """Updates the cooling system in response to system changes"""
        # Check if the cooling system is on
        bCoolingSystemOn = self.__pSystemModel.model["CoolingSystem"].getCoolingSystemOn()
        if bCoolingSystemOn:
            # Yes.  Check if the cooling thread is running
            if (self.__pCoolingThread == None) or not self.__pCoolingThread.is_alive():
                # No, so kill any running heating threads
                if (self.__pReactor1HeatingThread != None) and self.__pReactor1HeatingThread.is_alive():
                    self.__pReactor1HeatingThread.Stop()
                    self.__pReactor1HeatingThread.join()
                if (self.__pReactor2HeatingThread != None) and self.__pReactor2HeatingThread.is_alive():
                    self.__pReactor2HeatingThread.Stop()
                    self.__pReactor2HeatingThread.join()
                if (self.__pReactor3HeatingThread != None) and self.__pReactor3HeatingThread.is_alive():
                    self.__pReactor3HeatingThread.Stop()
                    self.__pReactor3HeatingThread.join()
 
                # Kick off the cooling thread
                self.__pCoolingThread = CoolingThread()
                self.__pCoolingThread.SetParameters(self.__pHardwareComm, self.__pSystemModel.model["Reactor1"]["Thermocouple"].getHeater1CurrentTemperature(),
                    self.__pSystemModel.model["Reactor1"]["Thermocouple"].getHeater2CurrentTemperature(), 
                    self.__pSystemModel.model["Reactor1"]["Thermocouple"].getHeater3CurrentTemperature(),
                    self.__pSystemModel.model["Reactor2"]["Thermocouple"].getHeater1CurrentTemperature(),
                    self.__pSystemModel.model["Reactor2"]["Thermocouple"].getHeater2CurrentTemperature(), 
                    self.__pSystemModel.model["Reactor2"]["Thermocouple"].getHeater3CurrentTemperature(),
                    self.__pSystemModel.model["Reactor3"]["Thermocouple"].getHeater1CurrentTemperature(),
                    self.__pSystemModel.model["Reactor3"]["Thermocouple"].getHeater2CurrentTemperature(), 
                    self.__pSystemModel.model["Reactor3"]["Thermocouple"].getHeater3CurrentTemperature())
                self.__pCoolingThread.setDaemon(True)
                self.__pCoolingThread.start()
        else:
            # No, so kill the cooling thread if it is running
            if (self.__pCoolingThread != None) and self.__pCoolingThread.is_alive():
                self.__pCoolingThread.Stop()
                self.__pCoolingThread.join()
        
    def __UpdatePressureRegulator(self, nPressureRegulator):
        """Updates the pressure regulator in response to system changes"""
        # Get the set and actual pressures
        nSetPressure = self.__pSystemModel.model["PressureRegulator" + str(nPressureRegulator)].getSetPressure()
        nActualPressure = self.__pSystemModel.model["PressureRegulator" + str(nPressureRegulator)].getCurrentPressure()
        
        # Compare the pressures.  Add leeway to account for rounding errors
        if ((nActualPressure + 1) < nSetPressure) or ((nActualPressure - 1) > nSetPressure):
            # Get a reference to the pressure regulator thread
            log.debug("Actual: %f,Setpt: %f" % (nActualPressure,nSetPressure))
            if nPressureRegulator == 1:
                pThread = self.__pPressureRegulator1Thread
            else:
                pThread = self.__pPressureRegulator2Thread

            # Check if the pressure regulator thread is running
            if (pThread == None) or not pThread.is_alive():
                # No, so kick off the thread
                pThread = PressureRegulatorThread()
                pThread.SetParameters(self.__pHardwareComm, nPressureRegulator, nActualPressure, nSetPressure)
                pThread.setDaemon(True)
                pThread.start()
                
                # Save the new reference
                if nPressureRegulator == 1:
                    self.__pPressureRegulator1Thread = pThread
                else:
                    self.__pPressureRegulator2Thread = pThread

    def __UpdateReagentRobotStatus(self):
        """Updates the reagent robot status in response to system changes"""
        # Get the reagent robot control and check words
        nControlWordX, nCheckWordX = self.__pSystemModel.model["ReagentDelivery"].getRobotXControlWords()
        nControlWordY, nCheckWordY = self.__pSystemModel.model["ReagentDelivery"].getRobotYControlWords()

        # Enable or disable the robots
        if (nControlWordX == 0x10) and not ((nCheckWordX >> ROBONET_STATUS_READY) & 1):
            self.__pHardwareComm.FakePLC_EnableReagentRobotX()
        elif (nControlWordX == 0x08) and ((nCheckWordX >> ROBONET_STATUS_READY) & 1):
            self.__pHardwareComm.FakePLC_DisableReagentRobotX()
        if (nControlWordY == 0x10) and not ((nCheckWordY >> ROBONET_STATUS_READY) & 1):
            self.__pHardwareComm.FakePLC_EnableReagentRobotY()
        elif (nControlWordY == 0x08) and ((nCheckWordX >> ROBONET_STATUS_READY) & 1):
            self.__pHardwareComm.FakePLC_DisableReagentRobotY()

        # Home the robots
        if self.__pHardwareComm.FakePLC_CheckForHomingReagentRobotX() and self.__pHardwareComm.FakePLC_CheckForHomingReagentRobotY():
            # Check either of the reagent robots movement threads are running
            if ((self.__pHomeReagentRobotThread == None) or not self.__pHomeReagentRobotThread.is_alive()) and \
               ((self.__pMoveReagentRobotThread == None) or not self.__pMoveReagentRobotThread.is_alive()):
                # No, so kick off the homing thread
                nReagentRobotActualPositionRawX, nReagentRobotActualPositionRawZ = self.__pSystemModel.model["ReagentDelivery"].getCurrentPositionRaw()
                self.__pHomeReagentRobotThread = HomeReagentRobotThread()
                self.__pHomeReagentRobotThread.SetParameters(self.__pHardwareComm, nReagentRobotActualPositionRawX, nReagentRobotActualPositionRawZ)
                self.__pHomeReagentRobotThread.setDaemon(True)
                self.__pHomeReagentRobotThread.start()

            # Clear the homing flags
            self.__pHardwareComm.FakePLC_ResetReagentRobotHoming()

    def __UpdateReagentRobotPosition(self):
        """Updates the reagent robot position in response to system changes"""
        # Get the set and actual positions
        nReagentRobotSetPositionRawX, nReagentRobotSetPositionRawZ = self.__pSystemModel.model["ReagentDelivery"].getSetPositionRaw()
        nReagentRobotActualPositionRawX, nReagentRobotActualPositionRawZ = self.__pSystemModel.model["ReagentDelivery"].getCurrentPositionRaw()
        # Compare the positions.  Add leeway to account for motor positioning errors
        if ((nReagentRobotSetPositionRawX + 5) < nReagentRobotActualPositionRawX) or ((nReagentRobotSetPositionRawX - 5) > nReagentRobotActualPositionRawX) or \
           ((nReagentRobotSetPositionRawZ + 5) < nReagentRobotActualPositionRawZ) or ((nReagentRobotSetPositionRawZ - 5) > nReagentRobotActualPositionRawZ):
            # Check if either of the reagent robot movement threads are running
            if ((self.__pMoveReagentRobotThread == None) or not self.__pMoveReagentRobotThread.is_alive()) and \
               ((self.__pHomeReagentRobotThread == None) or not self.__pHomeReagentRobotThread.is_alive()):
                # No, so kick off the movement thread
                self.__pMoveReagentRobotThread = MoveReagentRobotThread()
                self.__pMoveReagentRobotThread.SetParameters(self.__pHardwareComm, nReagentRobotActualPositionRawX, nReagentRobotActualPositionRawZ, \
                    nReagentRobotSetPositionRawX, nReagentRobotSetPositionRawZ)
                self.__pMoveReagentRobotThread.setDaemon(True)
                self.__pMoveReagentRobotThread.start()

    def __UpdateReagentRobotGripper(self):
        """Updates the reagent robot gripper in response to system changes"""
        # Get the gripper set values
        bGripperSetUp = self.__pSystemModel.model["ReagentDelivery"].getSetGripperUp()
        bGripperSetDown = self.__pSystemModel.model["ReagentDelivery"].getSetGripperDown()
        bGripperSetOpen = self.__pSystemModel.model["ReagentDelivery"].getSetGripperOpen()
        bGripperSetClose = self.__pSystemModel.model["ReagentDelivery"].getSetGripperClose()
        bSetGasTransferUp = self.__pSystemModel.model["ReagentDelivery"].getSetGasTransferUp()
        bSetGasTransferDown = self.__pSystemModel.model["ReagentDelivery"].getSetGasTransferDown()
        
        # Set the current gripper values
        self.__pHardwareComm.FakePLC_SetReagentRobotGripper(bGripperSetUp, bGripperSetDown, bGripperSetOpen, bGripperSetClose, bSetGasTransferUp, bSetGasTransferDown)

    def __UpdateReactorRobotStatus(self, nReactor):
        """Updates the reactor robot status in response to system changes"""
        # Get the reactor robot control and check words
        nControlWord, nCheckWord = self.__pSystemModel.model["Reactor" + str(nReactor)]["Motion"].getCurrentRobotControlWords()

        # Enable or disable the robot
        if (nControlWord == 0x10) and not ((nCheckWord >> ROBONET_STATUS_READY) & 1):
            self.__pHardwareComm.FakePLC_EnableReactorRobot(nReactor)
        elif (nControlWord == 0x08) and ((nCheckWord >> ROBONET_STATUS_READY) & 1):
            self.__pHardwareComm.FakePLC_DisableReactorRobot(nReactor)

        # Home the robots
        for nReactor in range(1, 4):
            # Set reactor-specific parameters
            if nReactor == 1:
                pReactorHomeThread = self.__pReactor1HomeThread
                pReactorLinearMovementThread = self.__pReactor1LinearMovementThread
            elif nReactor == 2:
                pReactorHomeThread = self.__pReactor2HomeThread
                pReactorLinearMovementThread = self.__pReactor2LinearMovementThread
            else:
                pReactorHomeThread = self.__pReactor3HomeThread
                pReactorLinearMovementThread = self.__pReactor3LinearMovementThread

            # Check if we need to home
            if self.__pHardwareComm.FakePLC_CheckForHomingReactorRobot(nReactor):
                # Check either of the reactor robots movement threads are running
                if ((pReactorHomeThread == None) or not pReactorHomeThread.is_alive()) and \
                   ((pReactorLinearMovementThread == None) or not pReactorLinearMovementThread.is_alive()):
                    # No, so kick off the homing thread
                    nReactorActualPositionY = self.__pSystemModel.model["Reactor" + str(nReactor)]["Motion"].getCurrentPositionRaw()
                    pReactorHomeThread = HomeReactorRobotThread()
                    pReactorHomeThread.SetParameters(self.__pHardwareComm, nReactor, nReactorActualPositionY)
                    pReactorHomeThread.setDaemon(True)
                    pReactorHomeThread.start()

                    # Remember the thread
                    if nReactor == 1:
                        self.__pReactor1HomeThread = pReactorHomeThread
                    elif nReactor == 2:
                        self.__pReactor2HomeThread = pReactorHomeThread
                    else:
                        self.__pReactor3HomeThread = pReactorHomeThread

                # Clear the homing flags
                self.__pHardwareComm.FakePLC_ResetReactorRobotHoming(nReactor)

    def __UpdateReactorPosition(self, nReactor):
        """Updates the reactor position in response to system changes"""
        # Get the set and actual linear positions
        nReactorSetPositionZ = self.__pSystemModel.model["Reactor" + str(nReactor)]["Motion"].getSetPositionRaw()
        nReactorActualPositionZ = self.__pSystemModel.model["Reactor" + str(nReactor)]["Motion"].getCurrentPositionRaw()

        # Compare the linear positions.  Add leeway to account for motor positioning errors
        if ((nReactorSetPositionZ + 5) < nReactorActualPositionZ) or ((nReactorSetPositionZ - 5) > nReactorActualPositionZ):
            # Get a reference to the reactor linear movement thread
            if nReactor == 1:
                pThread = self.__pReactor1LinearMovementThread
            elif nReactor == 2:
                pThread = self.__pReactor2LinearMovementThread
            else:
                pThread = self.__pReactor3LinearMovementThread

            # Check if the reactor linear movement thread is running
            if (pThread == None) or not pThread.is_alive():
                # No, so kick off the thread
                pThread = MoveReactorLinearThread()
                pThread.SetParameters(self.__pHardwareComm, nReactor, nReactorActualPositionZ, nReactorSetPositionZ)
                pThread.setDaemon(True)
                pThread.start()
                
                # Save the new reference
                if nReactor == 1:
                    self.__pReactor1LinearMovementThread = pThread
                elif nReactor == 2:
                    self.__pReactor2LinearMovementThread = pThread
                else:
                    self.__pReactor3LinearMovementThread = pThread

        # Get the set and actual vertical positions
        bReactorSetUp = self.__pSystemModel.model["Reactor" + str(nReactor)]["Motion"].getSetReactorUp()
        bReactorSetDown = self.__pSystemModel.model["Reactor" + str(nReactor)]["Motion"].getSetReactorDown()
        bReactorActualUp = self.__pSystemModel.model["Reactor" + str(nReactor)]["Motion"].getCurrentReactorUp()
        bReactorActualDown = self.__pSystemModel.model["Reactor" + str(nReactor)]["Motion"].getCurrentReactorDown()
            
        # Compare the vertical positions
        if (bReactorSetUp != bReactorActualUp) or (bReactorSetDown != bReactorActualDown):
            # Get a reference to the reactor vertical movement thread
            if nReactor == 1:
                pThread = self.__pReactor1VerticalMovementThread
            elif nReactor == 2:
                pThread = self.__pReactor2VerticalMovementThread
            else:
                pThread = self.__pReactor3VerticalMovementThread

            # Check if the reactor linear movement thread is running
            if (pThread == None) or not pThread.is_alive():
                # No, so kick off the thread
                pThread = MoveReactorVerticalThread()
                pThread.SetParameters(self.__pHardwareComm, nReactor, bReactorSetUp)
                pThread.setDaemon(True)
                pThread.start()
                
                # Save the new reference
                if nReactor == 1:
                    self.__pReactor1VerticalMovementThread = pThread
                elif nReactor == 2:
                    self.__pReactor2VerticalMovementThread = pThread
                else:
                    self.__pReactor3VerticalMovementThread = pThread
        
    def __UpdateReactorHeating(self, nReactor):
        """Updates the reactor heating in response to system changes"""
        # Check if the heater is on
        bHeaterOn = self.__pSystemModel.model["Reactor" + str(nReactor)]["Thermocouple"].getHeaterOn()
        if bHeaterOn:
            # Yes.  Check if the cooling system is on and return if it is
            bCoolingSystemOn = self.__pSystemModel.model["CoolingSystem"].getCoolingSystemOn()
            if bCoolingSystemOn:
                return

            # Get the set and actual temperatures
            nReactorSetTemperature = self.__pSystemModel.model["Reactor" + str(nReactor)]["Thermocouple"].getSetTemperature()
            nReactorActualTemperature = self.__pSystemModel.model["Reactor" + str(nReactor)]["Thermocouple"].getCurrentTemperature()

            # Compare the temperatures to see if we need to turn on the heater.  Add leeway to account for small variations
            if (nReactorSetTemperature + 2) > nReactorActualTemperature:
                # Get a reference to the heating thread
                if nReactor == 1:
                    pThread = self.__pReactor1HeatingThread
                elif nReactor == 2:
                    pThread = self.__pReactor2HeatingThread
                else:
                    pThread = self.__pReactor3HeatingThread

                # Check if the heating thread is running
                if (pThread == None) or not pThread.is_alive():
                    # No, so kick off the thread
                    pThread = HeatingThread()
                    pThread.SetParameters(self.__pHardwareComm, nReactor, self.__pSystemModel.model["Reactor" + str(nReactor)]["Thermocouple"].getHeater1On(),
                        self.__pSystemModel.model["Reactor" + str(nReactor)]["Thermocouple"].getHeater2On(),
                        self.__pSystemModel.model["Reactor" + str(nReactor)]["Thermocouple"].getHeater3On(),
                        self.__pSystemModel.model["Reactor" + str(nReactor)]["Thermocouple"].getHeater1CurrentTemperature(),
                        self.__pSystemModel.model["Reactor" + str(nReactor)]["Thermocouple"].getHeater2CurrentTemperature(),
                        self.__pSystemModel.model["Reactor" + str(nReactor)]["Thermocouple"].getHeater3CurrentTemperature(),
                        self.__pSystemModel.model["Reactor" + str(nReactor)]["Thermocouple"].getHeater1SetTemperature(),
                        self.__pSystemModel.model["Reactor" + str(nReactor)]["Thermocouple"].getHeater2SetTemperature(),
                        self.__pSystemModel.model["Reactor" + str(nReactor)]["Thermocouple"].getHeater3SetTemperature())
                    pThread.setDaemon(True)
                    pThread.start()
                
                    # Save the new reference
                    if nReactor == 1:
                        self.__pReactor1HeatingThread = pThread
                    elif nReactor == 2:
                        self.__pReactor2HeatingThread = pThread
                    else:
                        self.__pReactor3HeatingThread = pThread
        else:
            # No, so kill the heating thread if it is running
            if nReactor == 1:
                pThread = self.__pReactor1HeatingThread
            elif nReactor == 2:
                pThread = self.__pReactor2HeatingThread
            else:
                pThread = self.__pReactor3HeatingThread
            if (pThread != None) and pThread.is_alive():
                pThread.Stop()
                pThread.join()
        
# Fake PLC daemon exit function
gFakePLCDaemon = None
def OnExit(pFakePLCDaemon, signal, func = None):
    if gFakePLCDaemon != None:
        gFakePLCDaemon.bTerminate = True

# Fake PLC daemon
class FakePLCDaemon(daemon):
    def __init__(self, sPidFile):
        """Initializes the fake PLC daemon"""
        global gFakePLCDaemon
        daemon.__init__(self, sPidFile, "/opt/elixys/logs/FakePLC.log")
        log.debug("FakePLCDaemon starting")
        self.bTerminate = False
        gFakePLCDaemon = self
    def start(self):
        log.debug("We really called start... I swear")
        super(FakePLCDaemon,self).start()
    def run(self):
        """Runs the fake PLC daemon"""
        # Make sure we're in demo mode
        log.debug("Run FakePLC")
        global gFakePLCDaemon
        if not os.path.isfile("/opt/elixys/demomode"):
            log.error("Not in demo mode")
            self.bTerminate = True

        # Run loop
        while not self.bTerminate:
            try:
                # Create the fake PLC and run
                log.debug("Create a FakePLC object")
                pFakePLC = FakePLC()
                log.debug("Start a FakePLC object")
                pFakePLC.StartUp()
                log.debug("Run a FakePLC object")
                pFakePLC.Run()
            except Exception as ex:
                log.error("Traceback:\r\n%s\r\n" % traceback.format_exc())
                log.error("Fake PLC error: %s" % str(ex))
            finally:
                pFakePLC.ShutDown()

            # Sleep for a second before we respawn
            if not self.bTerminate:
                time.sleep(1)
        gFakePLCDaemon = None

# Main function
if __name__ == "__main__":
    if len(sys.argv) == 3:
        pDaemon = FakePLCDaemon(sys.argv[2])
        if 'start' == sys.argv[1]:
            log.info("Calling start")
            pDaemon.start()
        elif 'stop' == sys.argv[1]:
            pDaemon.stop()
        elif 'restart' == sys.argv[1]:
            pDaemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart pidfile" % sys.argv[0]
        sys.exit(2)

