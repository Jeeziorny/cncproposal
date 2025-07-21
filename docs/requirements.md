# Quote for Creating an Application for Importing and Processing DXF Files and Generating CNC Machine Cutting Instructions

**Problem**

For a given DXF file, instructions must be generated for a CNC machine with an endless blade according to which the blade will be guided. The instructions should take into account the blade rotation range (from -360 to 360 degrees). The solution should allow the user to manually modify the instructions generated for the machine.

**Assumptions**

1. The solution implementation will be a desktop application.
2. The output parameter of the application is GCode (Attach GCode version specification that both parties agree on).
3. Graphics files needed to create the visual layer of the application will be provided by the development team.

**Selected Technologies**

After requirements specification

**Functional Requirements**

**File Import**

1. Importing files in DXF format.
2. Validation of imported DXF file:
    1. DXF file is grammatically correctly defined,
    2. DXF file contains one 2D figure,
    3. Figure in DXF file is "closed",
    4. Figure in DXF file has no intersecting lines.
    5. Figure has no overlapping lines (special case of line intersection)
    6. Figure has no redundant points
3. Translation of information from DXF file to GCode format.
4. Importing existing GCode file,

**Overwriting information imported from DXF file.**

1. Selecting cutting path start point,
2. Selecting cutting path end point,
3. User selection of blade rotation point,
4. Program suggestion of cutting rotation points,
5. Copying, cutting and pasting selected structures,
6. Adding, cloning and deleting selected structures,
7. Moving selected structures,
8. Rotation of selected structures by angle (range -360 to 360) degrees,
9. Mirror reflection of selected structures horizontally and vertically,
10. Mirror reflection of selected structures relative to selected point.
11. Reversing cutting direction (g0 x y -> g0 y z),
12. Presets with selected shapes.
13. Ability to select cutting start point.

**Creating programs using predefined models:**

1. Dialog window with ability to select model from available shapes. Each option has a graphic icon showing model thumbnail.
2. Ability to enter parameters required for given shape (side lengths, radius, etc.) - available parameters depend on selected shape.
3. Ability to specify number of pieces
4. Dialog window after selecting model offers legend with graphic representation of each parameter.
5. Window also offers special case of block dicing model
    1. For given parameters: plate height, plate width, block height, a model is generated that dices the block into rectangles touching each other
    2. Generated program should first cut rectangle being model frame and then cut subsequent model rows.

**Presentation of information contained in GCode**

1. Zooming in and out of perspective,
2. Fit to screen
3. Moving perspective,
4. Measuring length of selected structures,
5. Disable / Enable axis display,
6. Disable / Enable grid lines,
7. Setting grid line distance,
8. Disable / Enable margins,
9. Displaying cursor coordinates.

**Export resulting GCode to file**

1. Export GCode to file.

**Cutting simulation:**

1. Setting saw movement speed in cutting simulation in range 1-1000%
2. Displaying current blade rotation angle,
3. Pause, Stop, Repeat and Start for cutting simulation,
4. Settings of important CNC machine parameters for cutting simulation,
5. Simulation is performed on resulting GCode program. The purpose of simulation is to verify potential errors in model and translation to GCode.

**User Interface:**

1. Supporting Polish language,
2. Supporting English language,
3. Creating graphic files for application icons and widgets.
4. Recently opened files history - ability to quickly open recently used file
5. Ability to undo changes.

**Non-functional Requirements**

1. Protection against application copying,
2. Application should check if new updates are available.
3. Software signing.
4. Exporting logs from application.

**Implementation Quote**

**TBD**

**System Operating Costs**

1. Application signature maintenance costs:
    1. macOS $99/year,
    2. Windows ~$70/year. 