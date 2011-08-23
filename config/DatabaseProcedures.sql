/* Create the stored procedures */

-- Change the delimiter for this file
DELIMITER //

/****************************************************************************************************************************************************************
 ** Roles *******************************************************************************************************************************************************
 ***************************************************************************************************************************************************************/

/* Get a list of roles */
DROP PROCEDURE IF EXISTS GetAllRoles;
CREATE PROCEDURE GetAllRoles()
    BEGIN
        -- Fetch the roles
        SELECT * FROM Roles;
    END //

/* Get a specific role:
 *   IN Rolename - Name of the role
 */
DROP PROCEDURE IF EXISTS GetRole;
CREATE PROCEDURE GetRole(IN iRoleName VARCHAR(30))
    BEGIN
        DECLARE lRoleID INT UNSIGNED;

        -- Fetch the roles
        CALL Internal_GetRoleID(iRoleName, lRoleID);
        SELECT * FROM Roles WHERE RoleID = lRoleID;
    END //

/* Create a new role:
 *   IN Rolename - Name of the role
 *   IN Flags - Flags describing the role permissions
 */
DROP PROCEDURE IF EXISTS CreateRole;
CREATE PROCEDURE CreateRole(IN iRoleName VARCHAR(30), IN iFlags INT UNSIGNED)
    BEGIN
        -- Create the role
        INSERT INTO Roles VALUES (NULL, iRoleName, iFlags);
    END //

/* Updates an existing role:
 *   IN Rolename - Name of the existing role
 *   IN UpdatedRolename - Name of the updated role
 *   IN UpdatedFlags - Flags describing the updated role permissions
 */
DROP PROCEDURE IF EXISTS UpdateRole;
CREATE PROCEDURE UpdateRole(IN iRoleName VARCHAR(30), IN iUpdatedRoleName VARCHAR(30), IN iUpdatedFlags INT UNSIGNED)
    BEGIN
        DECLARE lRoleID INT UNSIGNED;

        -- Update the role
        CALL Internal_GetRoleID(iRoleName, lRoleID);
        UPDATE Roles SET RoleName = iUpdatedRoleName, Flags = iUpdatedFlags WHERE RoleID = lRoleID;
    END //

/* Deletes an existing role:
 *   IN Rolename - Name of the existing role
 */
DROP PROCEDURE IF EXISTS DeleteRole;
CREATE PROCEDURE DeleteRole(IN iRoleName VARCHAR(30))
    BEGIN
        DECLARE lRoleID INT UNSIGNED;

        -- Delete the role
        CALL Internal_GetRoleID(iRoleName, lRoleID);
        DELETE FROM Roles WHERE RoleID = lRoleID;
    END //

/****************************************************************************************************************************************************************
 ** Users *******************************************************************************************************************************************************
 ***************************************************************************************************************************************************************/

/* Gets information about all system users */
DROP PROCEDURE IF EXISTS GetAllUsers;
CREATE PROCEDURE GetAllUsers()
    BEGIN
        DECLARE lUsername VARCHAR(30);
        DECLARE lFirstName VARCHAR(20);
        DECLARE lLastName VARCHAR(20);
        DECLARE lRoleName VARCHAR(30);
        DECLARE lNoMoreRows BOOLEAN default FALSE;
        DECLARE lUsersCursor CURSOR FOR SELECT Username FROM Users;

        -- Declare exception handler
        DECLARE CONTINUE HANDLER FOR NOT FOUND
            SET lNoMoreRows = TRUE;

        -- Create a temporary table to hold the users
        DROP TEMPORARY TABLE IF EXISTS tmp_Users;
        CREATE TEMPORARY TABLE tmp_Users
        (
            Username VARCHAR(30) NOT NULL,
            FirstName VARCHAR(20) NOT NULL,
            LastName VARCHAR(20) NOT NULL,
            RoleName VARCHAR(30) NOT NULL
        ) ENGINE=Memory COMMENT="Temporary users.";

        -- Open the cursor and get the number of rows
        OPEN lUsersCursor;

        -- Iterate over the users and fill our temporary table
        UsersLoop: LOOP
            -- Get the next username
            FETCH lUsersCursor INTO lUsername;

            -- Break out of the loop if we failed to get a username
            IF lNoMoreRows THEN
                CLOSE lUsersCursor;
                LEAVE UsersLoop;
            END IF;

            -- Call the internal function and insert into the temporary table
            CALL Internal_GetUser(lUsername, lFirstName, lLastName, lRoleName);
            INSERT INTO tmp_Users VALUES (lUsername, lFirstName, lLastName, lRoleName);
        END LOOP UsersLoop;

        -- Return the result set
        SELECT * FROM tmp_Users;
    END //

/* Gets information about the specified user:
 *   IN Username - Name of the user
 */
DROP PROCEDURE IF EXISTS GetUser;
CREATE PROCEDURE GetUser(IN iUsername VARCHAR(30))
    BEGIN
        DECLARE lFirstName VARCHAR(20);
        DECLARE lLastName VARCHAR(20);
        DECLARE lRoleID INT UNSIGNED;
        DECLARE lRoleName VARCHAR(30);

        -- Create a temporary table to hold the user data
        DROP TEMPORARY TABLE IF EXISTS tmp_User;
        CREATE TEMPORARY TABLE tmp_User
        (
            Username VARCHAR(30) NOT NULL,
            FirstName VARCHAR(20) NOT NULL,
            LastName VARCHAR(20) NOT NULL,
            RoleName VARCHAR(30) NOT NULL
        ) ENGINE=Memory COMMENT="Temporary user data.";

        -- Call the internal function
        CALL Internal_GetUser(iUsername, lFirstName, lLastName, lRoleName);

        -- Fill and return the user result set
        INSERT INTO tmp_User VALUES (iUsername, lFirstName, lLastName, lRoleName);
        SELECT * FROM tmp_User WHERE Username = iUsername;
    END //

/* Creates a new user:
 *   
 *   IN Username - Username
 *   IN Password - Hash of the user's password
 *   IN FirstName - User's first name
 *   IN LastName - User's last name
 *   IN RoleName - User's role
 */
DROP PROCEDURE IF EXISTS CreateUser;
CREATE PROCEDURE CreateUser(IN iUsername VARCHAR(30), IN iPassword VARCHAR(30), IN iFirstName VARCHAR(20), IN iLastName VARCHAR(20), IN iRoleName VARCHAR(20))
    BEGIN
        DECLARE lRoleID INT UNSIGNED;

        -- Look up the role ID
        CALL Internal_GetRoleID(iRoleName, lRoleID);

        -- Create the user
        INSERT INTO Users VALUES (NULL, iUsername, iPassword, iFirstName, iLastName, lRoleID, "");
    END //

/* Updates an existing user:
 *   IN Username - Username of the user to update
 *   IN FirstName - User's first name
 *   IN LastName - User's last name
 *   IN RoleName - User's role
 */
DROP PROCEDURE IF EXISTS UpdateUser;
CREATE PROCEDURE UpdateUser(IN iUsername VARCHAR(30), IN iFirstName VARCHAR(20), IN iLastName VARCHAR(20), IN iRoleName VARCHAR(20))
    BEGIN
        DECLARE lRoleID INT UNSIGNED;

        -- Look up the role ID
        CALL Internal_GetRoleID(iRoleName, lRoleID);

        -- Update the user
        UPDATE Users SET FirstName = iFirstName, LastName = iLastName, RoleID = lRoleID WHERE Username = iUsername;
    END //
 
/* Updates a user's password:
 *   IN Username - Username of the user to update
 *   IN Password - Hash of the user's password
 */
DROP PROCEDURE IF EXISTS UpdateUserPassword;
CREATE PROCEDURE UpdateUserPassword(IN iUsername VARCHAR(30), IN iPassword VARCHAR(30))
    BEGIN
        -- Update the user
        UPDATE Users SET Password = iPassword WHERE Username = iUsername;
    END //

/* Deletes a user:
 *   IN Username - Username of the user to delete
 */
DROP PROCEDURE IF EXISTS DeleteUser;
CREATE PROCEDURE DeleteUser(IN iUsername VARCHAR(30))
    BEGIN
        -- Delete the user
        DELETE FROM Users WHERE Username = iUsername;
    END //

/* Returns the client state of a user:
 *   IN Username - Username
 */
DROP PROCEDURE IF EXISTS GetUserClientState;
CREATE PROCEDURE GetUserClientState(IN iUsername VARCHAR(30))
    BEGIN
        -- Return the user's client state
        SELECT ClientState FROM Users WHERE Username = iUsername;
    END //

/* Updates the client state of a user:
 *   IN Username - Username
 *   IN ClientState - String describing the state of the client
 */
DROP PROCEDURE IF EXISTS UpdateUserClientState;
CREATE PROCEDURE UpdateUserClientState(IN iUsername VARCHAR(30), IN iClientState VARCHAR(64))
    BEGIN
        -- Save the user's client state
        UPDATE Users SET ClientState = iClientState WHERE Username = iUsername;
    END //

/****************************************************************************************************************************************************************
 ** Sequences ***************************************************************************************************************************************************
 ***************************************************************************************************************************************************************/

/* Get a list of sequences:
 *   IN Type - Type of sequence to return (either "Saved" or "Manual")
 */
DROP PROCEDURE IF EXISTS GetAllSequences;
CREATE PROCEDURE GetAllSequences(IN iType VARCHAR(20))
    BEGIN
        -- Fetch the sequences
        SELECT * FROM Sequences WHERE Type = iType;
    END //

/* Get a sequence:
 *   IN SequenceID - ID of the sequence to get
 */
DROP PROCEDURE IF EXISTS GetSequence;
CREATE PROCEDURE GetSequence(IN iSequenceID INT UNSIGNED)
    BEGIN
        -- Fetch the sequence
        SELECT * FROM Sequences WHERE SequenceID = iSequenceID;
    END //

/* Create a new sequence:
 *   IN Name - Name of the new sequence
 *   IN Comment - Comment associated with the new sequence
 *   IN Type - Type of the sequence (either "Saved" or "Manual")
 *   IN Username - Username of the user creating the new sequence
 *   IN Cassettes - Number of cassettes in the new sequence
 *   IN Reagents - Number of reagents per cassette
 *   IN Columns - Number of columns per cassette
 *   OUT SequenceID - ID of the new sequence
 */
DROP PROCEDURE IF EXISTS CreateSequence;
CREATE PROCEDURE CreateSequence(IN iName VARCHAR(64), IN iComment VARCHAR(255), IN iType VARCHAR(20), IN iUsername VARCHAR(30), IN iCassettes INT UNSIGNED,
                                IN iReagents INT UNSIGNED, IN iColumns INT UNSIGNED, OUT oSequenceID INT UNSIGNED)
    BEGIN
        DECLARE lUserID INT UNSIGNED;
        DECLARE lSequenceID INT UNSIGNED;
        DECLARE lCassetteID INT UNSIGNED;
        DECLARE lReagentID INT UNSIGNED;
        DECLARE lCassette INT UNSIGNED default 0;
        DECLARE lReagent INT UNSIGNED;
        DECLARE lColumn INT UNSIGNED;
        DECLARE lCassetteJSON VARCHAR(1024);

        -- Look up the user ID
        SET lUserID = (SELECT UserID FROM Users WHERE Username = iUsername);

        -- Create the entry in the sequences table
        INSERT INTO Sequences VALUES (NULL, iName, iComment, iType, NULL, lUserID, 0);
        SET lSequenceID = LAST_INSERT_ID();

        -- Create each cassette
        WHILE lCassette < iCassettes DO
            -- Create the cassette
            CALL CreateComponent(lSequenceID, "Saved", "CASSETTE", "", lCassetteID);

            -- Update the sequence table reference if this is the first cassette
            IF lCassette = 0 THEN
                UPDATE Sequences SET FirstComponentID = lCassetteID WHERE SequenceID = lSequenceID;
            END IF;

            -- Start the cassette JSON string
            SET lCassetteJSON = CONCAT("{\"type\":\"CASSETTE\", \"reactor\":", lCassette + 1, ", \"available\":False, \"reagents\":[");

            -- Create the reagents
            SET lReagent = 0;
            WHILE lReagent < iReagents DO
                -- Create an entry in the reagents table
                INSERT INTO Reagents VALUES (NULL, lSequenceID, lCassetteID, lReagent + 1, False, "", "");
                SET lReagentID = LAST_INSERT_ID();

                -- Update the cassette JSON string
                IF lReagent = 0 THEN
                    SET lCassetteJSON = CONCAT(lCassetteJSON, lReagentID);
                ELSE
                    SET lCassetteJSON = CONCAT(lCassetteJSON, ", ", lReagentID);
                END IF;

                -- Increment the reagent counter
                SET lReagent = lReagent + 1;
            END WHILE;

            -- Create the columns
            SET lColumn = 0; 
            WHILE lColumn < iColumns DO
                -- Create an entry in the reagents table
                INSERT INTO Reagents VALUES (NULL, lSequenceID, lCassetteID, CHAR(ASCII('A') + lColumn), False, "", "");
                SET lReagentID = LAST_INSERT_ID();

                -- Update the cassette JSON string
                SET lCassetteJSON = CONCAT(lCassetteJSON, ", ", lReagentID);

                -- Increment the column counter
                SET lColumn = lColumn + 1;
            END WHILE;

            -- Finish the cassette JSON string
            SET lCassetteJSON = CONCAT(lCassetteJSON, "]}");

            -- Update the cassette JSON string
            UPDATE Components SET Details = lCassetteJSON WHERE ComponentID = lCassetteID;

            -- Increment the cassette counter
            SET lCassette = lCassette + 1;
        END WHILE;

        -- Return the sequence ID
        SET oSequenceID = lSequenceID;
    END //

/* Creates a copy of an existing sequence:
 *   IN SequenceID - ID of the sequence to copy
 *   IN Name - Name of the new sequence
 *   IN Comment - Comment associated with the new sequence
 *   IN Username - Username of the user creating the new sequence
 *   OUT SequenceID - ID of the new sequence
 */
DROP PROCEDURE IF EXISTS CopySequence;
CREATE PROCEDURE CopySequence(IN iSequenceID INT UNSIGNED, IN iName VARCHAR(64), IN iComment VARCHAR(255), IN iUsername VARCHAR(30), OUT oSequenceID INT UNSIGNED)
    BEGIN
    END //

/* Deletes a sequence:
 *   IN SequenceID - ID of the sequence to delete
 */
DROP PROCEDURE IF EXISTS DeleteSequence;
CREATE PROCEDURE DeleteSequence(IN iSequenceID INT UNSIGNED)
    BEGIN
        -- Delete the sequence reagents
        DELETE FROM Reagents WHERE SequenceID = iSequenceID;

        -- Delete the sequence components
        DELETE FROM Components WHERE SequenceID = iSequenceID;

        -- Delete the sequence
        DELETE FROM Sequences WHERE SequenceID = iSequenceID;
    END //

/****************************************************************************************************************************************************************
 ** Reagents ****************************************************************************************************************************************************
 ***************************************************************************************************************************************************************/

/* Gets a reagent:
 *   IN ReagentID - ID of the reagent
 */
DROP PROCEDURE IF EXISTS GetReagent;
CREATE PROCEDURE GetReagent(IN iReagentID INT UNSIGNED)
    BEGIN
        -- Look up the reagent
        SELECT * FROM Reagents WHERE ReagentID = iReagentID;
    END //

/* Gets all reagents in the sequence that match the given name:
 *   IN SequenceID - ID of the sequence
 *   IN Name - Reagent name
 */
DROP PROCEDURE IF EXISTS GetReagentsByName;
CREATE PROCEDURE GetReagentsByName(IN iSequenceID INT UNSIGNED, IN iName VARCHAR(64))
    BEGIN
        -- Look up the reagent
        SELECT * FROM Reagents WHERE SequenceID = iSequenceID AND Name = iName;
    END //

/* Gets all reserved reagents in the database that match the given name:
 *   IN Name - Reagent name
 */
DROP PROCEDURE IF EXISTS GetReservedReagentsByName;
CREATE PROCEDURE GetReservedReagentsByName(IN iName VARCHAR(64))
    BEGIN
        -- Look up the reagent
        SELECT * FROM Reagents WHERE SequenceID = 0 AND Name = iName;
    END //

/* Update an existing reagent:
 *   IN ReagentID - ID of the reagent
 *   IN Available - True if a reagent is in this position, False otherwise
 *   IN Name - Reagent name
 *   IN Description - ReagentDescription
 */
DROP PROCEDURE IF EXISTS UpdateReagent;
CREATE PROCEDURE UpdateReagent(IN iReagentID INT UNSIGNED, IN iAvailable BOOL, IN iName VARCHAR(64), IN iDescription VARCHAR(255))
    BEGIN
        -- Update the reagent
        UPDATE Reagents SET Available = iAvailable, Name = iName, Description = iDescription WHERE ReagentID = iReagentID;
    END //

/* Updates an existing reagent by position:
 *   IN SequenceID - Sequence ID of the reagent
 *   IN CassetteNumber - Cassette number of the reagent
 *   IN Position - Position of the reagent
 *   IN Available - True if a reagent is in this position, False otherwise
 *   IN Name - Reagent name
 *   IN Description - ReagentDescription
 */
DROP PROCEDURE IF EXISTS UpdateReagentByPosition;
CREATE PROCEDURE UpdateReagentByPosition(IN iSequenceID INT UNSIGNED, IN iCassetteNumber INT UNSIGNED, IN iPosition VARCHAR(2), IN iAvailable BOOL, IN iName VARCHAR(64),
                                         IN iDescription VARCHAR(255))
    BEGIN
        DECLARE lComponentID INT UNSIGNED;
        DECLARE lReagentID INT UNSIGNED;

        -- Look up the component ID of the cassette
        CALL Internal_GetComponentByOffset(iSequenceID, iCassetteNumber - 1, lComponentID);

        -- Look up the reagent ID by position
        SET lReagentID = (SELECT ReagentID FROM Reagents WHERE SequenceID = iSequenceID AND ComponentID = lComponentID AND Position = iPosition);

        -- Update the reagent by position
        CALL UpdateReagent(lReagentID, iAvailable, iName, iDescription);
    END //

/* Creates a reserved reagent:
 *   IN Name - Reagent name
 *   IN Description - Reagent description
 */
DROP PROCEDURE IF EXISTS CreateReservedReagent;
CREATE PROCEDURE CreateReservedReagent(IN iName VARCHAR(64), IN iDescription VARCHAR(255))
    BEGIN
        -- Add the reagent
        INSERT INTO Reagents VALUES (NULL, 0, 0, 0, False, iName, iDescription);
    END //

/****************************************************************************************************************************************************************
 ** Components **************************************************************************************************************************************************
 ***************************************************************************************************************************************************************/

/* Gets a component:
 *   IN ComponentID - ID of the component
 */
DROP PROCEDURE IF EXISTS GetComponent;
CREATE PROCEDURE GetComponent(IN iComponentID INT UNSIGNED)
    BEGIN
        -- Return the component
        SELECT * FROM Components WHERE ComponentID = iComponentID;
    END //

/* Gets all components associated with a sequence:
 *   IN SequenceID - ID of the sequence
 */
DROP PROCEDURE IF EXISTS GetSequenceComponents;
CREATE PROCEDURE GetSequenceComponents(IN iSequenceID INT UNSIGNED)
    BEGIN
        -- Return the components
        SELECT * FROM Components WHERE SequenceID = iSequenceID;
    END //

/* Creates a new component and inserts it at the end of a sequence:
 *   IN SequenceID - ID of the sequence
 *   IN Type - Type of the component
 *   IN Name - Name of the component
 *   IN Details - Component details
 *   OUT ComponentID - ID of the new component
 */
DROP PROCEDURE IF EXISTS CreateComponent;
CREATE PROCEDURE CreateComponent(IN iSequenceID INT UNSIGNED, IN iType VARCHAR(20), IN iName VARCHAR(20), IN iDetails VARCHAR(2048), OUT oComponentID INT UNSIGNED)
    BEGIN
        DECLARE lLastComponentID INT UNSIGNED;

        -- Get the ID of the last component in the sequence
        CALL Internal_GetLastComponent(iSequenceID, lLastComponentID);

        -- Insert the component
        CALL InsertComponent(iSequenceID, iType, iName, iDetails, lLastComponentID, oComponentID);
    END //

/* Creates a new component and inserts it at the desired location in a sequence:
 *   IN SequenceID - ID of the sequence
 *   IN Type - Type of the component
 *   IN Name - Name of the component
 *   IN Details - Component details
 *   IN InsertID - ID of the component to insert after
 *   OUT ComponentID - ID of the new component
 */
DROP PROCEDURE IF EXISTS InsertComponent;
CREATE PROCEDURE InsertComponent(IN iSequenceID INT UNSIGNED, IN iType VARCHAR(20), IN iName VARCHAR(20), IN iDetails VARCHAR(2048), IN iInsertID INT UNSIGNED, 
                                 OUT oComponentID INT UNSIGNED)
    BEGIN
        DECLARE lUserID INT UNSIGNED;
        DECLARE lNextComponentID INT UNSIGNED;

        -- Get the component after the insert position
        CALL Internal_GetNextComponent(iInsertID, lNextComponentID);
        IF lNextComponentID IS NULL THEN
            SET lNextComponentID = 0;
        END IF;

        -- Add the component
        INSERT INTO Components VALUES (NULL, iSequenceID, iInsertID, lNextComponentID, iType, iName, iDetails);
        SET oComponentID = LAST_INSERT_ID();

        -- Update the previous and next components
        UPDATE Components SET NextComponentID = oComponentID WHERE ComponentID = iInsertID;
        UPDATE Components SET PreviousComponentID = oComponentID WHERE ComponentID = lNextComponentID;
    END //

/* Updates an existing component:
 *   IN ComponentID - ID of the component to update
 *   IN Type - Type of the component
 *   IN Name - Name of the component
 *   IN Details - Component details
 */
DROP PROCEDURE IF EXISTS UpdateComponent;
CREATE PROCEDURE UpdateComponent(IN iComponentID INT UNSIGNED, IN iType VARCHAR(20), IN iName VARCHAR(20), IN iDetails VARCHAR(2048))
    BEGIN
        -- Update the component
        UPDATE Components SET Type = iType, Name = iName, Details = iDetails WHERE ComponentID = iComponentID;
    END //

/* Deletes the component and removes it from the sequence:
 *   IN ComponentID - ID of the component to delete
 */
DROP PROCEDURE IF EXISTS DeleteComponent;
CREATE PROCEDURE DeleteComponent(IN iComponentID INT UNSIGNED)
    BEGIN
        DECLARE lPreviousComponentID INT UNSIGNED;
        DECLARE lNextComponentID INT UNSIGNED;

        -- Find the previous and next component IDs
        CALL Internal_GetPreviousComponent(iComponentID, lPreviousComponentID);
        CALL Internal_GetNextComponent(iComponentID, lNextComponentID);

        -- Update the component references
        UPDATE Components SET NextComponentID = lNextComponentID WHERE ComponentID = lPreviousComponentID;
        UPDATE Components SET PreviousComponentID = lPreviousComponentID WHERE ComponentID = lNextComponentID;

        -- Delete the component
        DELETE FROM Components WHERE ComponentID = iComponentID;
    END //

/****************************************************************************************************************************************************************
 ** Internal procedures *****************************************************************************************************************************************
 ***************************************************************************************************************************************************************/

/* Gets information about the specified user */
DROP PROCEDURE IF EXISTS Internal_GetUser;
CREATE PROCEDURE Internal_GetUser(IN iUsername VARCHAR(30), OUT oFirstName VARCHAR(20), OUT oLastName VARCHAR(20), OUT oRoleName VARCHAR(30))
    BEGIN
        DECLARE lRoleID INT UNSIGNED;

        -- Fetch the user data
        SELECT FirstName FROM Users WHERE Username = iUsername INTO oFirstName;
        SELECT LastName FROM Users WHERE Username = iUsername INTO oLastName;
        SELECT RoleID FROM Users WHERE Username = iUsername INTO lRoleID;

        -- Look up the role name
        SELECT RoleName FROM Roles WHERE RoleID = lRoleID INTO oRoleName;
    END //

/* Maps a given role name to an ID */
DROP PROCEDURE IF EXISTS Internal_GetRoleID;
CREATE PROCEDURE Internal_GetRoleID(IN iRoleName VARCHAR(30), OUT oRoleID INT UNSIGNED)
    BEGIN
        -- Look up the role ID
        SELECT RoleID FROM Roles WHERE RoleName = iRoleName INTO oRoleID;
    END //

/* Returns the first component of a sequence:
 *   IN SequenceID - ID of the sequence
 *   OUT ComponentID - ID of the first component in the sequence
 */
DROP PROCEDURE IF EXISTS Internal_GetFirstComponent;
CREATE PROCEDURE Internal_GetFirstComponent(IN iSequenceID INT UNSIGNED, OUT oComponentID INT UNSIGNED)
    BEGIN
        -- Get the first component ID
        SET oComponentID = (SELECT FirstComponentID FROM Sequences WHERE SequenceID = iSequenceID);
    END //

/* Returns the previous component of a sequence:
 *   IN ComponentID - ID of the current component
 *   OUT ComponentID - ID of the previous component in the sequence
 */
DROP PROCEDURE IF EXISTS Internal_GetPreviousComponent;
CREATE PROCEDURE Internal_GetPreviousComponent(IN iComponentID INT UNSIGNED, OUT oComponentID INT UNSIGNED)
    BEGIN
        -- Get the previous component ID
        SET oComponentID = (SELECT PreviousComponentID FROM Components WHERE ComponentID = iComponentID);
    END //

/* Returns the next component of a sequence:
 *   IN ComponentID - ID of the current component
 *   OUT ComponentID - ID of the next component in the sequence
 */
DROP PROCEDURE IF EXISTS Internal_GetNextComponent;
CREATE PROCEDURE Internal_GetNextComponent(IN iComponentID INT UNSIGNED, OUT oComponentID INT UNSIGNED)
    BEGIN
        -- Get the next component ID
        SET oComponentID = (SELECT NextComponentID FROM Components WHERE ComponentID = iComponentID);
    END //

/* Returns the last component of a sequence:
 *   IN SequenceID - ID of the sequence
 *   OUT ComponentID - ID of the last component in the sequence
 */
DROP PROCEDURE IF EXISTS Internal_GetLastComponent;
CREATE PROCEDURE Internal_GetLastComponent(IN iSequenceID INT UNSIGNED, OUT oComponentID INT UNSIGNED)
    BEGIN
        DECLARE lComponentID INT UNSIGNED;
        DECLARE lNextComponentID INT UNSIGNED;

        -- Get the first and next component IDs
        CALL Internal_GetFirstComponent(iSequenceID, lComponentID);
        CALL Internal_GetNextComponent(lComponentID, lNextComponentID);

        -- Loop until we the next component ID is zero
        WHILE lNextComponentID > 0 DO
            -- Get the next component ID
            SET lComponentID = lNextComponentID;
            CALL Internal_GetNextComponent(lComponentID, lNextComponentID);
        END WHILE;

        -- Return the component ID
        SET oComponentID = lComponentID;
    END //

/* Returns the Nth component of a sequence:
 *   IN SequenceID - ID of the sequence
 *   IN ComponentOffset - Offset of the component
 *   OUT ComponentID - ID of the component
 */
DROP PROCEDURE IF EXISTS Internal_GetComponentByOffset;
CREATE PROCEDURE Internal_GetComponentByOffset(IN iSequenceID INT UNSIGNED, IN iComponentOffset INT UNSIGNED, OUT oComponentID INT UNSIGNED)
    BEGIN
        DECLARE lComponentID INT UNSIGNED default 0;
        DECLARE lComponentOffset INT UNSIGNED default 0;

        -- Loop until we reach the desired offset
        WHILE lComponentOffset <= iComponentOffset DO
            IF lComponentOffset = 0 THEN
                -- Get the first component ID
                CALL Internal_GetFirstComponent(iSequenceID, lComponentID);
            ELSE
                -- Get the next component ID
                CALL Internal_GetNextComponent(lComponentID, lComponentID);
            END IF;

            -- Increment the component counter
            SET lComponentOffset = lComponentOffset + 1;
        END WHILE;

        -- Set the return value
        SET oComponentID = lComponentID;
    END //

-- Restore the delimiter
DELIMITER ;
