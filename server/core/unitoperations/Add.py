# Add unit operation

# Imports
from UnitOperation import *
import urllib

# Component type
componentType = "ADD"

# Create a unit operation from a component object
def createFromComponent(nSequenceID, pComponent, username, database, systemModel):
  pParams = {}
  pParams["ReactorID"] = "Reactor" + str(pComponent["reactor"])
  pParams["ReagentReactorID"] = "Reactor0"   #We'll get the actual value once we initialize the component
  pParams["ReagentPosition"] = 0             #Ditto
  pParams["reagentLoadPosition"] = pComponent["deliveryposition"]
  pParams["duration"] = pComponent["deliverytime"]
  pParams["pressure"] = pComponent["deliverypressure"]
  pAdd = Add(systemModel, pParams, username, nSequenceID, pComponent["id"], database)
  pAdd.initializeComponent(pComponent)
  if pComponent["reagent"].has_key("position"):
    pAdd.reagentPosition = int(pComponent["reagent"]["position"])
    pAdd.reagentName = pComponent["reagent"]["name"]
  if pComponent["reagent"].has_key("reagentid"):
    pAdd.ReagentReactorID = "Reactor" + str(database.GetReagentCassette(username, nSequenceID, pComponent["reagent"]["reagentid"]))
  pAdd.setDescription()
  return pAdd

# Updates a component object based on a unit operation
def updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel):
  pComponent["deliverytime"] = int(pUnitOperation.duration)

# Add class
class Add(UnitOperation):
  def __init__(self,systemModel,params,username = "",sequenceID = 0, componentID = 0, database = None):
    UnitOperation.__init__(self,systemModel,username,sequenceID,componentID,database)
    expectedParams = {REACTORID:STR,REAGENTREACTORID:STR,REAGENTPOSITION:INT,REAGENTLOADPOSITION:INT,PRESSURE:FLOAT,DURATION:INT}
    paramError = self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)
    self.reagentName = ""

  def setDescription(self):
    self.description = "Adding " + urllib.unquote(str(self.reagentName)) + " to reactor " + str(self.ReactorID[-1]) + " position " + str(self.reagentLoadPosition) + ".  Delivering with " + \
      str(self.pressure) + " psi nitrogen for " + str(self.duration) + " seconds.";

  def run(self):
    try:
      self.setStatus("Adjusting pressure")
      self.setPressureRegulator(1,self.pressure)
      self.setStatus("Moving reactor")
      self.setReactorPosition(ADDREAGENT)
      self.setStatus("Picking up vial")
      self.setGripperPlace(0)
      self.setStatus("Delivering reagent")
      self.startTimer(self.duration)
      self.duration = self.waitForTimer()
      self.setStatus("Returning vial")
      self.removeGripperPlace()
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(str(e), False)
  
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("reactorvalidation"):
      self.component.update({"reactorvalidation":""})
    if not self.component.has_key("reagentvalidation"):
      self.component.update({"reagentvalidation":""})
    if not self.component.has_key("deliverypositionvalidation"):
      self.component.update({"deliverypositionvalidation":""})
    if not self.component.has_key("deliverytimevalidation"):
      self.component.update({"deliverytimevalidation":""})
    if not self.component.has_key("deliverypressurevalidation"):
      self.component.update({"deliverypressurevalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["note"] = ""
    self.component["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["reagentvalidation"] = "type=enum-reagent; values=" + self.listReagents(pAvailableReagents) + "; required=true"
    self.component["deliverypositionvalidation"] = "type=enum-number; values=1,2; required=true"
    self.component["deliverytimevalidation"] = "type=number; min=0; max=90"
    self.component["deliverypressurevalidation"] = "type=number; min=0; max=15"

    #Look up the reagent we are adding and remove it from the list of available reagents
    if self.component["reagent"].has_key("reagentid"):
      pReagent = self.getReagentByID(self.component["reagent"]["reagentid"], pAvailableReagents, True)
      if pReagent != None:
        #Set the component note
        self.component["note"] = pReagent["name"]

    #Do a quick validation
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["reactor"], self.component["reactorvalidation"]) or \
       not self.validateComponentField(self.component["reagent"], self.component["reagentvalidation"]) or \
       not self.validateComponentField(self.component["deliveryposition"], self.component["deliverypositionvalidation"]) or \
       not self.validateComponentField(self.component["deliverytime"], self.component["deliverytimevalidation"]) or \
       not self.validateComponentField(self.component["deliverypressure"], self.component["deliverypressurevalidation"]):
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
    pDBComponent["reagentvalidation"] = self.component["reagentvalidation"]
    pDBComponent["deliverypositionvalidation"] = self.component["deliverypositionvalidation"]
    pDBComponent["deliverytimevalidation"] = self.component["deliverytimevalidation"]
    pDBComponent["deliverypressurevalidation"] = self.component["deliverypressurevalidation"]
    pDBComponent["deliverytime"] = self.component["deliverytime"]
    pDBComponent["deliverypressure"] = self.component["deliverypressure"]
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
    pAddReagent = {}
    if self.component["reagent"] != 0:
      pAddReagent = self.database.GetReagent(self.username, self.component["reagent"])

    # Replace the reagent
    del self.component["reagent"]
    self.component["reagent"] = pAddReagent

    # Set the default delivery time and pressure
    if self.component["deliverytime"] == 0:
      self.component["deliverytime"] = DEFAULT_ADD_DURATION
    if self.component["deliverypressure"] == 0:
      self.component["deliverypressure"]= DEFAULT_ADD_PRESSURE

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(self, pTargetComponent)

    # Update the fields we want to save
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
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["deliveryposition"] = self.component["deliveryposition"]
    pTargetComponent["deliverytime"] = self.component["deliverytime"]
    pTargetComponent["deliverypressure"] = self.component["deliverypressure"]

  def copyComponentImpl(self, nSourceSequenceID, nTargetSequenceID, pComponentCopy):
    """Performs unit-operation specific copying"""
    if self.component["reagent"] != None:
      nReagentCassette = self.database.GetReagentCassette(self.username, nSourceSequenceID, self.component["reagent"]["reagentid"])
      pNewReagent = self.database.GetReagentByPosition(self.username, nTargetSequenceID, nReagentCassette, self.component["reagent"]["position"])
      pComponentCopy["reagent"] = pNewReagent["reagentid"]
    else:
      pComponentCopy["reagent"] = 0

