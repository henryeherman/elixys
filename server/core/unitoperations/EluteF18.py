# EluteF18 unit operation

# Imports
from UnitOperation import *
import urllib

# Component type
componentType = "ELUTEF18"

# Create a unit operation from a component object
def createFromComponent(nSequenceID, pComponent, username, database, systemModel):
  pParams = {}
  pParams["ReactorID"] =  "Reactor" + str(pComponent["reactor"])
  pParams["eluteTime"] = pComponent["elutetime"]
  pParams["elutePressure"] = pComponent["elutepressure"]
  pParams["ReagentReactorID"] = "Reactor0"   #We'll get the actual value once we initialize the component
  pParams["ReagentPosition"] = 0             #Ditto
  pEluteF18 = EluteF18(systemModel, pParams, username, nSequenceID, pComponent["id"], database)
  pEluteF18.initializeComponent(pComponent)
  if pComponent["reagent"].has_key("position"):
    pEluteF18.reagentPosition = int(pComponent["reagent"]["position"])
    pEluteF18.reagentName = pComponent["reagent"]["name"]
  if pComponent["reagent"].has_key("reagentid"):
    pEluteF18.ReagentReactorID = "Reactor" + str(database.GetReagentCassette(username, nSequenceID, pComponent["reagent"]["reagentid"]))
  pEluteF18.setDescription()
  return pEluteF18

# Updates a component object based on a unit operation
def updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel):
  pComponent["elutetime"] = int(pUnitOperation.eluteTime)

# EluteF18 class
class EluteF18(UnitOperation):
  def __init__(self,systemModel,params,username = "",sequenceID = 0, componentID = 0, database = None):
    UnitOperation.__init__(self,systemModel,username,sequenceID,componentID,database)
    expectedParams = {REACTORID:STR,ELUTETIME:INT,ELUTEPRESSURE:FLOAT,REAGENTREACTORID:STR,REAGENTPOSITION:INT}
    paramError = self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)
    self.reagentName = ""
    self.description = "Eluting F18 off the QMA attached to reactor " + str(self.ReactorID[-1]) + \
      " with the reagent in cassette " + str(self.ReagentReactorID[-1]) + " position " + str(self.reagentPosition) + \
      " for " + str(self.eluteTime) + " seconds using " + str(self.elutePressure) + " psi nitrogen.";

  def setDescription(self):
    self.description = "Eluting F18 off the QMA attached to reactor " + str(self.ReactorID[-1]) + " with " + \
      urllib.unquote(str(self.reagentName)) + " for " + str(self.eluteTime) + " seconds using " + \
      str(self.elutePressure) + " psi nitrogen.";

  def run(self):
    try:
      self.setStatus("Adjusting pressure")
      self.setPressureRegulator(1,0) #Vent pressure to avoid delivery issues
      self.setStatus("Moving reactor")
      self.setReactorPosition(ADDREAGENT)
      self.setStatus("Picking up vial")
      self.setStopcockPosition(F18ELUTE)
      self.setGripperPlace(1)
      self.setStatus("Eluting")
      self.timerShowInStatus = False
      self.setPressureRegulator(1,self.elutePressure,5)
      self.startTimer(self.eluteTime)
      self.eluteTime = self.waitForTimer()
      self.setStatus("Returning vial")
      self.removeGripperPlace()
      self.setStopcockPosition(F18DEFAULT)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(str(e), False)
      
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("reactorvalidation"):
      self.component.update({"reactorvalidation":""})
    if not self.component.has_key("elutepressurevalidation"):
      self.component.update({"elutepressurevalidation":""})
    if not self.component.has_key("elutetimevalidation"):
      self.component.update({"elutetimevalidation":""})
    if not self.component.has_key("reagentvalidation"):
      self.component.update({"reagentvalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["note"] = ""
    self.component["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["elutetimevalidation"] = "type=number; min=0; max=7200; required=true"
    self.component["elutepressurevalidation"] = "type=number; min=0; max=25"
    self.component["reagentvalidation"] = "type=enum-reagent; values=" + self.listReagents(pAvailableReagents) + "; required=true"

    #Look up the reagent we are adding and remove it from the list of available reagents
    if self.component["reagent"].has_key("reagentid"):
      pReagent = self.getReagentByID(self.component["reagent"]["reagentid"], pAvailableReagents, True)
      if pReagent != None:
        #Set the component name
        self.component["note"] = pReagent["name"]

    #Do a quick validation
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["reactor"], self.component["reactorvalidation"]) or \
       not self.validateComponentField(self.component["elutetime"], self.component["elutetimevalidation"]) or \
       not self.validateComponentField(self.component["elutepressure"], self.component["elutepressurevalidation"]) or \
       not self.validateComponentField(self.component["reagent"], self.component["reagentvalidation"]):
      bValidationError = True

    # Set the validation error field
    self.component.update({"validationerror":bValidationError})
    return not bValidationError

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["reactorvalidation"] = self.component["reactorvalidation"]
    pDBComponent["elutetimevalidation"] = self.component["elutetimevalidation"]
    pDBComponent["elutepressurevalidation"] = self.component["elutepressurevalidation"]
    pDBComponent["reagentvalidation"] = self.component["reagentvalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], self.component["note"], json.dumps(pDBComponent))

  def addComponentDetails(self):
    """Adds details to the component after retrieving it from the database and prior to sending it to the client"""
    # Skip if we've already updated the reagent
    try:
      int(self.component["reagent"])
    except TypeError:
      return

    # Look up the reagent we are adding
    pEluteReagent = {}
    if self.component["reagent"] != 0:
      pEluteReagent = self.database.GetReagent(self.username, self.component["reagent"])

    # Replace the reagent
    del self.component["reagent"]
    self.component["reagent"] = pEluteReagent

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(self, pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["elutetime"] = self.component["elutetime"]
    pTargetComponent["elutepressure"] = self.component["elutepressure"]
    pTargetComponent["reagent"] = self.component["reagent"]
    if self.isNumber(pTargetComponent["reagent"]):
      if pTargetComponent["reagent"] != 0:
        pReagent = self.database.GetReagent(self.username, pTargetComponent["reagent"])
        pTargetComponent.update({"note":pReagent["name"]})
      else:
        pTargetComponent.update({"note":""})
    else:
      if pTargetComponent["reagent"].has_key("name"):
        pTargetComponent.update({"note":pTargetComponent["reagent"]["name"]})
      else:
        pTargetComponent.update({"note":""})
      if pTargetComponent["reagent"].has_key("reagentid"):
        pTargetComponent["reagent"] = pTargetComponent["reagent"]["reagentid"]
      else:
        pTargetComponent["reagent"] = 0

  def copyComponentImpl(self, nSourceSequenceID, nTargetSequenceID, pComponentCopy):
    """Performs unit-operation specific copying"""
    if self.component["reagent"] != None:
      nReagentCassette = self.database.GetReagentCassette(self.username, nSourceSequenceID, self.component["reagent"]["reagentid"])
      pNewReagent = self.database.GetReagentByPosition(self.username, nTargetSequenceID, nReagentCassette, self.component["reagent"]["position"])
      pComponentCopy["reagent"] = pNewReagent["reagentid"]
    else:
      pComponentCopy["reagent"] = 0


