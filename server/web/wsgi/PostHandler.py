#!/usr/bin/python

# Imports
import json
import GetHandler
import sys
sys.path.append("/opt/elixys/core")
import SequenceManager
import Exceptions

class PostHandler:
    # Constructor
    def __init__(self, pCoreServer, pDatabase):
        # Remember the input references
        self.__pCoreServer = pCoreServer
        self.__pDatabase = pDatabase

        # Create the sequence manager
        self.__pSequenceManager = SequenceManager.SequenceManager(pDatabase)

        # Initialize server state
        self.__pServerState = None

    # Main entry point for handling all POST requests
    def HandleRequest(self, pClientState, sRemoteUser, sPath, pBody, nBodyLength):
        # Remember the request variables
        self.__pClientState = pClientState
        self.__sRemoteUser = sRemoteUser
        self.__sPath = sPath
        self.__pBody = pBody
        self.__nBodyLength = nBodyLength

        # Call the appropriate handler function
        if self.__sPath == "/HOME":
            return self.__HandlePostHome()
        elif self.__sPath == "/SELECT":
            return self.__HandlePostSelect()
        elif self.__sPath == "/VIEW":
            return self.__HandlePostView()
        elif self.__sPath == "/EDIT":
            return self.__HandlePostEdit()
        elif self.__sPath == "/RUN":
            return self.__HandlePostRun()
        elif self.__sPath == "/PROMPT":
            return self.__HandlePostPrompt()
        elif self.__sPath.startswith("/sequence/"):
            if self.__sPath.find("/component/") != -1:
                return self.__HandlePostComponent()
            elif self.__sPath.find("/reagent/") != -1:
                return self.__HandlePostReagent()
            else:
                return self.__HandlePostSequence()
        else:
            raise Exception("Unknown path: " + sPath)

    # Handle POST /HOME
    def __HandlePostHome(self):
        # Make sure we are on the home page
        if self.__pClientState["screen"] != "HOME":
            raise Exception("State misalignment");

        # Parse the JSON string in the body
        pJSON = json.loads(self.__pBody)

        # Check which option the user selected
        sActionType = str(pJSON["action"]["type"])
        sActionTargetID = str(pJSON["action"]["targetid"])
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "CREATE":
                # Switch states to Select Sequence
                self.__pClientState["screen"] = "SELECT_SAVEDSEQUENCES"
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "OBSERVE":
                # Switch to Run Sequence
                pServerState = self.__GetServerState()
                self.__pClientState["screen"] = "RUN"
                self.__pClientState["sequenceid"] = pServerState["runstate"]["sequenceid"]
                self.__pClientState["componentid"] = pServerState["runstate"]["componentid"]
                return self.__SaveClientStateAndReturn()

        # Unhandled use case
        raise Exception("State misalignment")

    # Handle POST /SELECT
    def __HandlePostSelect(self):
        # Make sure we are on Select Sequence
        if not self.__pClientState["screen"].startswith("SELECT"):
            raise Exception("State misalignment");

        # Parse the JSON string in the body
        pJSON = json.loads(self.__pBody)

        # Check which option the user selected
        sActionType = str(pJSON["action"]["type"])
        sActionTargetID = str(pJSON["action"]["targetid"])
        nSequenceID = pJSON["sequenceid"]
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "VIEW":
                # Switch states to View Sequence
                self.__pClientState["screen"] = "VIEW"
                self.__pClientState["sequenceid"] = nSequenceID
                self.__pClientState["componentid"] = 0
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "EDIT":
                # Switch states to Edit Sequence
                self.__pClientState["screen"] = "EDIT"
                self.__pClientState["sequenceid"] = nSequenceID
                self.__pClientState["componentid"] = 0
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "RUN":
                # Show the Run Sequence prompt
                return self.__ShowRunSequencePrompt(nSequenceID)
            elif sActionTargetID == "BACK":
                # Switch states to Home
                self.__pClientState["screen"] = "HOME"
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "CREATE":
                # Show the Create Sequence prompt
                self.__pClientState["prompt"]["screen"] = "PROMPT_CREATESEQUENCE"
                self.__pClientState["prompt"]["show"] = True
                self.__pClientState["prompt"]["title"] = "Create new sequence"
                self.__pClientState["prompt"]["text1"] = "Enter the name of the new sequence:"
                self.__pClientState["prompt"]["edit1"] = True
                self.__pClientState["prompt"]["edit1validation"] = "type=string; required=true"
                self.__pClientState["prompt"]["text2"] = "Enter optional sequence description:"
                self.__pClientState["prompt"]["edit2"] = True
                self.__pClientState["prompt"]["edit2validation"] = "type=string; required=false"
                self.__pClientState["prompt"]["buttons"] = [{"type":"button",
                    "text":"Cancel",
                    "id":"CANCEL"},
                    {"type":"button",
                    "text":"Create",
                    "id":"CREATE"}]
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "COPY":
                # Show the Copy Sequence prompt
                pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, nSequenceID, False)
                self.__pClientState["prompt"]["screen"] = "PROMPT_COPYSEQUENCE"
                self.__pClientState["prompt"]["show"] = True
                self.__pClientState["prompt"]["title"] = "Copy sequence"
                self.__pClientState["prompt"]["text1"] = "Enter the name of the new sequence:"
                self.__pClientState["prompt"]["edit1"] = True
                self.__pClientState["prompt"]["edit1default"] = pSequence["metadata"]["name"] + " Copy"
                self.__pClientState["prompt"]["edit1validation"] = "type=string; required=true"
                self.__pClientState["prompt"]["text2"] = "Enter an optional description of the new sequence:"
                self.__pClientState["prompt"]["edit2"] = True
                self.__pClientState["prompt"]["edit2default"] = pSequence["metadata"]["comment"]
                self.__pClientState["prompt"]["edit2validation"] = "type=string; required=false"
                self.__pClientState["prompt"]["buttons"] = [{"type":"button",
                    "text":"Cancel",
                    "id":"CANCEL"},
                    {"type":"button",
                    "text":"Copy",
                    "id":"COPY"}]
                self.__pClientState["sequenceid"] = nSequenceID
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "DELETE":
                # Show the Delete Sequence prompt
                pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, nSequenceID, False)
                self.__pClientState["prompt"]["screen"] = "PROMPT_DELETESEQUENCE"
                self.__pClientState["prompt"]["show"] = True
                self.__pClientState["prompt"]["title"] = "Delete sequence"
                self.__pClientState["prompt"]["text1"] = "Are you sure that you want to permanently delete sequence \"" + pSequence["metadata"]["name"] + "\"?"
                self.__pClientState["prompt"]["edit1"] = False
                self.__pClientState["prompt"]["text2"] = ""
                self.__pClientState["prompt"]["edit2"] = False
                self.__pClientState["prompt"]["buttons"] = [{"type":"button",
                    "text":"Cancel",
                    "id":"CANCEL"},
                    {"type":"button",
                    "text":"Delete",
                    "id":"DELETE"}]
                self.__pClientState["sequenceid"] = nSequenceID
                return self.__SaveClientStateAndReturn()
        elif sActionType == "TABCLICK":
            if sActionTargetID == "SAVEDSEQUENCES":
                # Switch states to the Saved Sequences tab
                self.__pClientState["screen"] = "SELECT_SAVEDSEQUENCES"
                self.__pClientState["sequenceid"] = nSequenceID
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "RUNHISTORY":
                # Switch states to the Run History tab
                self.__pClientState["screen"] = "SELECT_RUNHISTORY"
                self.__pClientState["sequenceid"] = nSequenceID
                return self.__SaveClientStateAndReturn()

        # Unhandled use case
        raise Exception("State misalignment")

    # Show the Run Sequence prompt
    def __ShowRunSequencePrompt(self, nSequenceID):
        # Load the sequence
        pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, nSequenceID, False)

        # Fill in the state
        self.__pClientState["prompt"]["screen"] = "PROMPT_RUNSEQUENCE"
        self.__pClientState["prompt"]["show"] = True
        self.__pClientState["prompt"]["title"] = "Confirm run"
        self.__pClientState["prompt"]["text1"] = "Would you like to run the sequence \"" + pSequence["metadata"]["name"] + "\"?"
        self.__pClientState["prompt"]["edit1"] = False
        self.__pClientState["prompt"]["text2"] = ""
        self.__pClientState["prompt"]["edit2"] = False
        self.__pClientState["prompt"]["buttons"] = [{"type":"button",
            "text":"No",
            "id":"NO"},
            {"type":"button",
            "text":"Yes",
            "id":"YES"}]
        self.__pClientState["sequenceid"] = nSequenceID
        return self.__SaveClientStateAndReturn()

    # Handle POST /VIEW
    def __HandlePostView(self):
        # Make sure we are on View Sequence
        if self.__pClientState["screen"] != "VIEW":
            raise Exception("State misalignment")

        # Parse the JSON string in the body and extract the action type and target
        pJSON = json.loads(self.__pBody)
        sActionType = str(pJSON["action"]["type"])
        sActionTargetID = str(pJSON["action"]["targetid"])

        # Call the base sequence POST handler first
        if self.__HandlePostBaseSequence(sActionType, sActionTargetID):
            return self.__SaveClientStateAndReturn()

        # Handle View Sequence specific requests
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "EDIT":
                # Switch states to Edit Sequence
                self.__pClientState["screen"] = "EDIT"
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "RUN":
                # Show the Run Sequence prompt
                return self.__ShowRunSequencePrompt(self.__pClientState["sequenceid"])

        # Unhandled use case
        raise Exception("State misalignment")

    # Handle POST /EDIT
    def __HandlePostEdit(self):
        # Make sure we are on Edit Sequence
        if self.__pClientState["screen"] != "EDIT":
            raise Exception("State misalignment")

        # Parse the JSON string in the body and extract the action type and target
        pJSON = json.loads(self.__pBody)
        sActionType = str(pJSON["action"]["type"])
        sActionTargetID = str(pJSON["action"]["targetid"])

        # Call the base sequence POST handler first
        if self.__HandlePostBaseSequence(sActionType, sActionTargetID):
            return self.__SaveClientStateAndReturn()

        # Handle Edit Sequence specific requests
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "RUN":
                # Show the Run Sequence prompt
                return self.__ShowRunSequencePrompt(self.__pClientState["sequenceid"])

        # Unhandled use case
        raise Exception("State misalignment")

    # Handle POST /RUN
    def __HandlePostRun(self):
        # Make sure we are on Run Sequence
        if self.__pClientState["screen"] != "RUN":
            raise Exception("State misalignment")

        # Parse the JSON string in the body and extract the action type and target
        pJSON = json.loads(self.__pBody)
        sActionType = str(pJSON["action"]["type"])
        sActionTargetID = str(pJSON["action"]["targetid"])

        # Check which button the user clicked
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "ABORT":
                # Switch states to Prompt (Abort sequence run)
                self.__pClientState["prompt"]["screen"] = "PROMPT_ABORTSEQUENCERUN"
                self.__pClientState["prompt"]["show"] = True
                self.__pClientState["prompt"]["title"] = "Abort run"
                self.__pClientState["prompt"]["text1"] = "Are you sure you want to abort the sequence run?\n\nThis operation cannot be undone."
                self.__pClientState["prompt"]["edit1"] = False
                self.__pClientState["prompt"]["text2"] = ""
                self.__pClientState["prompt"]["edit2"] = False
                self.__pClientState["prompt"]["buttons"] = [{"type":"button",
                    "text":"Yes",
                    "id":"YES"},
                    {"type":"button",
                    "text":"No",
                    "id":"NO"}]
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "BACK":
                # Switch states to Home
                self.__pClientState["screen"] = "HOME"
                return self.__SaveClientStateAndReturn()

        # Unhandled use case
        raise Exception("State misalignment")

    # Handle sequence POST requests
    def __HandlePostBaseSequence(self, sActionType, sActionTargetID):
        # Check which option the user selected
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "BACK":
                # Switch states to Select Sequence
                self.__pClientState["screen"] = "SELECT_SAVEDSEQUENCES"
                return True
            elif sActionTargetID == "PREVIOUS":
                # Move to the previous component
                pPreviousComponent = self.__pDatabase.GetPreviousComponent(self.__sRemoteUser, self.__pClientState["componentid"])
                if pPreviousComponent != None:
                    self.__pClientState["componentid"] = pPreviousComponent["id"]
                return True
            elif sActionTargetID == "NEXT":
                # Move to the next component
                pNextComponent = self.__pDatabase.GetNextComponent(self.__sRemoteUser, self.__pClientState["componentid"])
                if pNextComponent != None:
                    self.__pClientState["componentid"] = pNextComponent["id"]
                return True
            else:
                # Check if the target ID corresponds to one of our sequence components
                try:
                    # Cast the action target ID to an integer and fetch the corresponding component
                    nActionTargetID = int(sActionTargetID)
                    pComponent = self.__pDatabase.GetComponent(self.__sRemoteUser, nActionTargetID)

                    # Make sure the sequence IDs match
                    if pComponent["sequenceid"] != self.__pClientState["sequenceid"]:
                        return False

                    # Move to the component
                    self.__pClientState["componentid"] = pComponent["id"]
                    return True
                except ValueError:
                    # Action target ID is not an integer
                    pass
                except Exceptions.ComponentNotFoundException:
                    # Interger does not correspond to a component ID
                    pass


        # Tell the caller we didn't handle it
        return False

    # Handle POST /PROMPT
    def __HandlePostPrompt(self):
        # Make sure we are on Prompt
        if not self.__pClientState["prompt"]["show"] or not self.__pClientState["prompt"]["screen"].startswith("PROMPT"):
            raise Exception("State misalignment");

        # Parse the JSON string in the body
        pJSON = json.loads(self.__pBody)

        # Extract the post parameters
        sActionType = str(pJSON["action"]["type"])
        sActionTargetID = str(pJSON["action"]["targetid"])
        sEdit1 = str(pJSON["edit1"])
        sEdit2 = str(pJSON["edit2"])

        # The only recognized action from a prompt is a button click
        if sActionType != "BUTTONCLICK":
            raise Exception("State misalignment")

        # Interpret the response in context of the client state
        if self.__pClientState["prompt"]["screen"] == "PROMPT_CREATESEQUENCE":
            if sActionTargetID == "CREATE":
                # Sequence name is required
                if sEdit1 == "":
                    raise Exception("Sequence name is required")

                # Create the new sequence
                nSequenceID = self.__pDatabase.CreateSequence(self.__sRemoteUser, sEdit1, sEdit2, "Saved", 3, 10, 2)

                # Hide the prompt and move the client to the editing the new sequence
                self.__pClientState["prompt"]["show"] = False
                self.__pClientState["screen"] = "EDIT"
                self.__pClientState["sequenceid"] = nSequenceID
                return self.__SaveClientStateAndReturn()
            if sActionTargetID == "CANCEL":
                # Hide the prompt
                self.__pClientState["prompt"]["show"] = False
                return self.__SaveClientStateAndReturn()
        elif self.__pClientState["prompt"]["screen"] == "PROMPT_COPYSEQUENCE":
            if sActionTargetID == "COPY":
                # Sequence name is required
                if sEdit1 == "":
                    raise Exception("Sequence name is required")

                # Create a copy of the sequence in the database
                nNewSequenceID = self.__pSequenceManager.CopySequence(self.__sRemoteUser, self.__pClientState["sequenceid"], sEdit1, sEdit2)

                # Hide the prompt
                self.__pClientState["prompt"]["show"] = False
                return self.__SaveClientStateAndReturn()
            if sActionTargetID == "CANCEL":
                # Hide the prompt
                self.__pClientState["prompt"]["show"] = False
                return self.__SaveClientStateAndReturn()
        elif self.__pClientState["prompt"]["screen"] == "PROMPT_DELETESEQUENCE":
            if sActionTargetID == "DELETE":
                # Delete the sequence from the database
                self.__pDatabase.DeleteSequence(self.__sRemoteUser, self.__pClientState["sequenceid"])

                # Hide the prompt
                self.__pClientState["prompt"]["show"] = False
                return self.__SaveClientStateAndReturn()
            if sActionTargetID == "CANCEL":
                # Hide the prompt
                self.__pClientState["prompt"]["show"] = False
                return self.__SaveClientStateAndReturn()
        elif self.__pClientState["prompt"]["screen"] == "PROMPT_ABORTSEQUENCERUN":
            if sActionTargetID == "YES":
                # Abort the run and return to the home page
                self.__pCoreServer.EmergencyStop(self.__sRemoteUser)
                self.__pClientState["prompt"]["show"] = False
                self.__pClientState["screen"] = "HOME"
                return self.__SaveClientStateAndReturn()
            if sActionTargetID == "NO":
                # Hide the prompt
                self.__pClientState["prompt"]["show"] = False
                return self.__SaveClientStateAndReturn()
        elif self.__pClientState["prompt"]["screen"] == "PROMPT_RUNSEQUENCE":
            if sActionTargetID == "YES":
                # Run the sequence
                self.__pCoreServer.RunSequence(self.__sRemoteUser, self.__pClientState["sequenceid"])

                # Hide the prompt and switch states to Run Sequence
                self.__pClientState["prompt"]["show"] = False
                self.__pClientState["screen"] = "RUN"
                return self.__SaveClientStateAndReturn()
            if sActionTargetID == "NO":
                # Hide the prompt
                self.__pClientState["prompt"]["show"] = False
                return self.__SaveClientStateAndReturn()
        elif self.__pClientState["prompt"]["screen"] == "PROMPT_UNITOPERATION":
            if sActionTargetID == "OK":
                # Continue the sequence
                self.__pCoreServer.Continue(self.__sRemoteUser)
                self.__pClientState["prompt"]["show"] = False
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "BACK":
                # Switch states to Home
                self.__pClientState["screen"] = "HOME"
                self.__pClientState["prompt"]["show"] = False
                return self.__SaveClientStateAndReturn()

        # Unhandled use case
        raise Exception("State misalignment")

    # Handle POST /sequence/[sequenceid]
    def __HandlePostSequence(self):
        raise Exception("Implement post sequence")
        # There currently isn't any way in the UI to edit the sequence metadata

    # Handle POST /sequence/[sequenceid]/component/[componentid]
    def __HandlePostComponent(self):
        # Extract sequence and component IDs
        pPathComponents = self.__sPath.split("/")
        nSequenceID = int(pPathComponents[2])
        nComponentID = int(pPathComponents[4])
        nInsertionID = None
        if len(pPathComponents) == 6:
            nInsertionID = int(pPathComponents[5])

        # Parse the component JSON if present
        pComponent = None
        if self.__nBodyLength != 0:
            pComponent = json.loads(self.__pBody)

        # Are we working with an existing component?
        if nComponentID != 0:
            # Yes, so update the existing component
            self.__pSequenceManager.UpdateComponent(self.__sRemoteUser, nSequenceID, nComponentID, nInsertionID, pComponent)
        else:
            # No, so add a new component
            nComponentID = self.__pSequenceManager.AddComponent(self.__sRemoteUser, nSequenceID, nInsertionID, pComponent)

            # Update the client to show the new component
            self.__pClientState["componentid"] = nComponentID

        # Return the new state
        return self.__SaveClientStateAndReturn()

    # Handle POST /sequence/[sequenceid]/reagent/[reagentid]
    def __HandlePostReagent(self):
        # Extract sequence and reagent IDs
        pPathComponents = self.__sPath.split("/")
        nSequenceID = int(pPathComponents[2])
        nReagentID = int(pPathComponents[4])

        # Save the reagent
        pReagent = json.loads(self.__pBody)
        self.__pDatabase.UpdateReagent(self.__sRemoteUser, nReagentID, pReagent["available"], pReagent["name"], pReagent["description"])

        # Return the new state
        return self.__SaveClientStateAndReturn()

    # Save the client state and return
    def __SaveClientStateAndReturn(self):
        self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, self.__sRemoteUser, self.__pClientState)
        pGetHandler = GetHandler.GetHandler(self.__pCoreServer, self.__pDatabase)
        return pGetHandler.HandleRequest(self.__pClientState, self.__sRemoteUser, "/state", None, 0)

    # Initializes and/or returns the cached server state
    def __GetServerState(self):
        if self.__pServerState == None:
            self.__pServerState = self.__pCoreServer.GetServerState(self.__sRemoteUser)
        return self.__pServerState
