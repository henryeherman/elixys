""" ElixysCLI.py

Implements a CLI interface to the Elixys system """

### Imports
import inspect
import time
import rpyc
import socket
import sys
sys.path.append("../hardware/")
sys.path.append("../core/")
from HardwareComm import HardwareComm
from SystemModel import SystemModel
from UnitOperationsWrapper import UnitOperationsWrapper

# Parses and executes the given command
def ExecuteCommand(sCommand, pUnitOperationsWrapper, pSystemModel, pHardwareComm):
    try:
        # Ignore empty commands
        if sCommand == "":
            return

        # Strip off the trailing parenthesis from the command and split into the function name and parameters
        pCommandComponents = sCommand.strip(")").split("(")
        sFunctionName = pCommandComponents[0]

        # Make sure the function name exists on either the unit operations wrapper or the hardware layer
        if hasattr(UnitOperationsWrapper, sFunctionName):
            bHardwareComm = False
            Object = UnitOperationsWrapper
            pObject = pUnitOperationsWrapper
        elif hasattr(HardwareComm, sFunctionName):
            bHardwareComm = True
            Object = HardwareComm
            pObject = pHardwareComm
        else:
            raise Exception("Unknown function " + sFunctionName)

        # Make sure the function name maps to a callable object
        pFunction = getattr(Object, sFunctionName)
        if not callable(pFunction):
            raise Exception(sFunctionName + " is not a function")

        # Make sure we have the correct number of arguments
        pParameters = pCommandComponents[1].split(",")
        nParameters = len(pParameters)
        if (nParameters == 1) and (pParameters[0] == ""):
            nParameters = 0
        pFunctionParameters = inspect.getargspec(pFunction).args
        if (nParameters + 1) != len(pFunctionParameters):
            raise Exception("Incorrect number of arguments for " + sFunctionName)

        # Prepare each function parameter
        for nIndex in range(0, nParameters):
            # Strip any quotes and whitespace
            pParameters[nIndex] = pParameters[nIndex].strip('"')
            pParameters[nIndex] = pParameters[nIndex].strip("'")
            pParameters[nIndex] = pParameters[nIndex].strip()
            
            # Interpret any integers as such
            try:
                pParameters[nIndex] = int(pParameters[nIndex])
                continue;
            except ValueError:
                pass

            # Interpret any floats as such
            try:
                pParameters[nIndex] = float(pParameters[nIndex])
                continue;
            except ValueError:
                pass

        # Call the function
        if nParameters == 0:
            pReturn = pFunction(pObject)
        elif nParameters == 1:
            pReturn = pFunction(pObject, pParameters[0])
        elif nParameters == 2:
            pReturn = pFunction(pObject, pParameters[0], pParameters[1])
        elif nParameters == 3:
            pReturn = pFunction(pObject, pParameters[0], pParameters[1], pParameters[2])
        elif nParameters == 4:
            pReturn = pFunction(pObject, pParameters[0], pParameters[1], pParameters[2], pParameters[3])
        elif nParameters == 5:
            pReturn = pFunction(pObject, pParameters[0], pParameters[1], pParameters[2], pParameters[3], pParameters[4])
        elif nParameters == 6:
            pReturn = pFunction(pObject, pParameters[0], pParameters[1], pParameters[2], pParameters[3], pParameters[4], pParameters[5])
        elif nParameters == 7:
            pReturn = pFunction(pObject, pParameters[0], pParameters[1], pParameters[2], pParameters[3], pParameters[4], pParameters[5], pParameters[6])
        else:
            raise Exception("Too many arguments");
        
        # Remember the unit operation objects
        if not bHardwareComm:
            pSystemModel.SetUnitOperation(pReturn)
            
    except Exception as ex:
        # Display the error
        print "Failed to execute command: " + str(ex)

# Parses and sends the raw command
def SendCommand(sCommand, pHardwareComm):
    # Extract the command and send it as a raw packet
    pCommandComponents = sCommand.split(" ")
    pHardwareComm._HardwareComm__SendRawCommand(pCommandComponents[1])

# Main CLI function
if __name__ == "__main__":
    # Create the hardware layer
    pHardwareComm = HardwareComm("../hardware/")
    pHardwareComm.StartUp()
  
    # Create the system model
    pSystemModel = SystemModel(pHardwareComm)
    pSystemModel.StartUp()
    
    # Create an RPC connection to the state monitoring window
    try:
        pStateMonitor = rpyc.connect("localhost", 18861)
        pSystemModel.SetStateMonitor(pStateMonitor)
    except socket.error, ex:
        print "Warning: failed to connect to state monitor, no output will be displayed"
    
    # Create the unit operations wrapper
    pUnitOperationsWrapper = UnitOperationsWrapper(pSystemModel)

    # CLI loop
    print "Elixys Command Line Interface"
    print "Type help for available commands."
    while True:
        # Get input and strip newlines
        sCommand = raw_input(">>> ").strip("\r\n")

        # Handle commands
        if sCommand == "exit":
            break
        elif sCommand == "help":
            print "Recognized commands:"
            print "  help unit operations   Lists available unit operation functions"
            print "  help hardware          Lists available hardware functions"
            print "  help send              Display a brief description of the PLC command format" 
            print "  get state              Displays the current state of the system"
            print "  send [command]         Send the raw command to the PLC"
        elif sCommand == "help unit operations":
            # List the recognized unit operations
            print "Recognized unit operations:"
            print "  React"
            print "  Not implemented: Add"
            print "  Not implemented: Evaporate"
            print "  Not implemented: Install"
            print "  Not implemented: TransferToHPLC"
            print "  Not implemented: TransferElute"
            print "  Not implemented: Transfer"
            print "  Not implemented: UserInput"
            print "  Not implemented: DetectRadiation"
            print "For additional information on each operation:"
            print "  help [unit operation name]"
        elif sCommand == "help React":
            # React unit operation
            print "Heat the given reactor to a specific temperature, holds for a set length of"
            print "time, cools the reactor to the final temperature, stirs throughout."
            print ""
            print "  React(nReactor,                 'Reactor1','Reactor2','Reactor3'"
            print "        nReactionTemperature,     Celsius"
            print "        nReactionTime,            Seconds"
            print "        nFinalTemperature,        Celsius"
            print "        nReactPosition,           'React1','React2'"
            print "        nStirSpeed)               Suggested 500"
        elif sCommand == "help Add":
            # Add unit operation
            print "Adds the specified reagent to the reactor"
            print ""
            print "  Add(nReactor,                   Reactor where the reagent will be"
            print "                                  added ('Reactor1','Reactor2','Reactor3')"
            print "      nReagentReactor,            Reactor of the cassette where the reagent"
            print "                                  resides ('Reactor1','Reactor2','Reactor3')"
            print "      nReagentPosition,           1-10 (?)"
            print "      nReagentDeliveryPosition    1-2 (?)"
        elif sCommand == "help Evaporate":
            # Evaporate unit operation
            print "Evaporates the contents of a reactor using a combination of heating, "
            print "stirring, nitrogen flow and vacuum."
            print ""
            print "  Evaporate(nReactor,             'Reactor1','Reactor2','Reactor3'"
            print "            nEvaporationTemperature,  Celsius"
            print "            nEvaporationTime,     Seconds"
            print "            nFinalTemperature,    Celsius"
            print "            nStirSpeed)           Suggested 500"
        elif sCommand == "help Install":
            # Install unit operation
            print "Moves a reactor to the installation position for easier access"
            print ""
            print "  Install(nReactor)               'Reactor1','Reactor2','Reactor3'"
        elif sCommand == "help TransferToHPLC":
            # TransferToHPLC unit operation
            print "Todo:  TransferToHPLC(nReactor, nStopcockPosition)"
        elif sCommand == "help TransferElute":
            # TransferElute unit operation
            print "Todo: TransferElute(self, nReactor, nStopcockPosition)"
        elif sCommand == "help Transfer":
            # Transfer unit operation
            print "Todo:  Transfer(nReactor, nStopcockPosition, nTransferReactorID)"
        elif sCommand == "help UserInput":
            # UserInput unit operation
            print "Todo: UserInput(sUserMessage, bIsCheckBox, sDescription)"
        elif sCommand == "help DetectRadiation":
            # Detect radiation unit operation
            print "Todo: DetectRadiation()"
        elif sCommand == "help hardware":
            # Yes, it's a wall of text.  We could use introspection for the function names but it gets even messier that way because we
            # don't want to list all of our functions
            print "Recognized hardware functions:"
            print "  * CoolingSystemOn()   * CoolingSystemOff()"
            print "  * SetPressureRegulator(nPressureRegulator, nPressure)"
            print "  * MoveRobotToReagent(nReactor, nReagent)   * MoveRobotToHome()"
            print "  * MoveRobotToDelivery(nReactor, nPosition)"
            print "  * GripperUp()      * GripperDown()   * GripperOpen()     * GripperClose()"
            print "  * LoadF18Start()   * LoadF18Stop()   * EluteF18Start()   * EluteF18Stop()"
            print "  * LoadHPLCStart()  * LoadHPLCStop()"
            print "  * MoveReactor(nReactor, sPositionName)"
            print "  * ReactorUp(nReactor)               * ReactorDown(nReactor)"
            print "  * ReactorEvaporateStart(nReactor)   * ReactorEvaporateStop(nReactor)"
            print "  * ReactorTransferStart(nReactor)    * ReactorTransferStop(nReactor)"
            print "  * ReactorReagentTransferStart(nReactor, nPosition)"
            print "  * ReactorReagentTransferStop(nReactor, nPosition)"
            print "  * ReactorStopcockPosition(nReactor, nStopcock, nPosition)"
            print "  * HeaterOn(nReactor)   * HeaterOff(nReactor)"
            print "  * SetHeater(nReactor, fSetPoint)   * SetMotorSpeed(nReactor, nMotorSpeed)"
            print "  * HomeRobots()   * DisableRobots()   * EnableRobots()"
            print "  * DisableReactorRobot(nReactor)   * EnableReactorRobot(nReactor)"
            print "All values are numbers except sPositionName which is one of the following:"
            print "      Install, Transfer, React1, Add, React2, Evaporate, Radiation"
        elif sCommand == "help send":
            # Display a brief description of the PLC command format
            print "Command format:"
            print "    [cccc][xx][xxxxxx][xxxx]"
            print "  Where [cccc] can be:"
            print "    0101 - Read Memory Area" 
            print "    0102 - Write Memory Area"
            print "    0402 - STOP - puts system in program mode"
            print "    0501 - Controller Read Data"
            print "    0601 - Controller Read Status"
            print "    0701 - Controller Read Clock"
            print "  Example:"
            print "    0101800000020001"
        elif sCommand == "get state":
            # Dump the state to standard out
            print pSystemModel.DumpStateToString()
        elif sCommand.startswith("send "):
            # Attempt to send the command
            SendCommand(sCommand, pHardwareComm)

            # Sleep a bit to give the PLC a chance to response before we display the input prompt
            time.sleep(0.25)
        else:
            # Attempt to execute the command
            ExecuteCommand(sCommand, pUnitOperationsWrapper, pSystemModel, pHardwareComm)

            # Sleep a bit to give the PLC a chance to response before we display the input prompt
            time.sleep(0.25)

    # Clean up
    pSystemModel.ShutDown()
    pHardwareComm.ShutDown()
