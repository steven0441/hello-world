; <COMPILER: v1.1.30.03>
#NoEnv
#Warn
SendMode Input
SetWorkingDir %A_ScriptDir%
global FOLDERNAME := A_Args[2]
global OFFSET := ""
global LINE_ARRAY := ""
global HOLE_CONTENTS := ""
global FOUND_HOLES := 0
global FILE_CONTENTS := ""
global PROJECT_NUMBER := ""
global PART_NAME := ""
global PART_TYPE := ""
global PART_GRADE := ""
global PLATE_PART_GRADE := ""
global ADJ_SLOT_FLAG := ""
global ADJ_VERT_SLOT_FLAG := ""
global PLATE_HAS_SLOT := ""
global ROUND_PLATE := ""
global MACHINE_TYPE := ""
global PLATE_MACHINE := ""
global FLANGE_WIDTH := ""
global PART_WIDTH := ""
global PART_LENGTH := ""
global PART_HEIGHT := ""
global PARTFILEPATH := ""
global GSD_LIBRARY_LOC := "H:\PROGRAMMING\Standards\GSD Library\Shapes Library\"
global JOKER := ""
global COUNT := ""
GSD_UI:
if FOLDERNAME =
FileSelectFolder, FOLDERNAME, P:\, 3
if FOLDERNAME =
MsgBox, You didn't select a folder.
else
{
MsgBox, 4,, You have selected %FOLDERNAME%`n`nIs this correct?
IfMsgBox, YES
{
StartTime := A_TickCount
MainLoop()
EndTime := A_TickCount
ElapsedSeconds := (EndTime - StartTime)/1000.0
msgbox, Done! [%ElapsedSeconds% seconds]
}
IfMsgBox, NO
{
FOLDERNAME :=
gosub GSD_UI
}
}
MainLoop()
{
Loop, Files, %FOLDERNAME%\*.nc1
{
ReadFile()
CheckOffset()
GetGeometry()
FindPartGrade()
FindPartType()
ShapesLibrary()
FixWT()
FixJobNumber()
FixPartName()
IsItBar()
Find_Holes()
HoleFunctions()
AddOrRemoveScribe()
SaveNewFileContents()
}
}
ReadFile()
{
FileRead, FILE_CONTENTS, %A_LoopFileFullPath%
LINE_ARRAY := StrSplit(FILE_CONTENTS, "`n")
}
CheckOffset()
{
FOUND_HOLES := 0
OFFSET := 0
PLATE_HAS_SLOT := 0
ROUND_PLATE := 0
ADJ_SLOT_FLAG := 0
ADJ_VERT_SLOT_FLAG := 0
for line_index, line in LINE_ARRAY
{
if (line_index < 2)
{
continue
}
trimmed_line := Trim(line)
if (SubStr(trimmed_line, 1, 2) = "**")
{
OFFSET++
}
else
{
break
}
}
}
GetGeometry()
{
PART_LENGTH := ReadLine(10)
PART_WIDTH := ReadLine(11)
FLANGE_WIDTH := ReadLine(12)
PART_HEIGHT := ReadLine(14)
}
FixJobNumber()
{
project_line := OFFSET
project_line += 2
JOKER := ReadLine(2)
GetProjectNumber()
SpaceCount()
JOKER := ""
spaces := Replicate(" ", COUNT)
COUNT := ""
new_text := spaces . PROJECT_NUMBER
LINE_ARRAY[project_line] := new_text
}
FixPartName()
{
SplitPath, A_LoopFileName, ,,,Part_Name,
part_name_line := OFFSET
part_name_line += 5
JOKER := ReadLine(5)
SpaceCount()
JOKER := ""
spaces := Replicate(" ", COUNT)
COUNT := ""
new_text := spaces . Part_Name
LINE_ARRAY[part_name_line] := new_text
PART_NAME := Part_Name
}
SpaceCount()
{
COUNT := 0
Loop, Parse, JOKER
{
if (A_LoopField = " ")
{
COUNT++
}
}
}
SaveNewFileContents()
{
CreateDestinationFolder()
new_file_contents := ""
new_file_contents2 := ""
hole_export := ""
for line_index, line in LINE_ARRAY
{
new_file_contents .= line . "`n"
}
if (PLATE_HAS_SLOT = 1) and (ADJ_SLOT_FLAG = 1)
{
if (ADJ_VERT_SLOT_FLAG) = 0
FolderPath := FolderName . "\Completed\" . PART_TYPE . " With Adjusted Slots (NEEDS CUSTOMER APPROVAL)\" . PART_GRADE . "\Horizontal\"
else if (ADJ_VERT_SLOT_FLAG) = 1
FolderPath := FolderName . "\Completed\" . PART_TYPE . " With Adjusted Slots (NEEDS CUSTOMER APPROVAL)\" . PART_GRADE . "\Vertical\"
else
FolderPath := FolderName . "\Completed\" . PART_TYPE . " With Slotted Holes (2013)\" . PLATE_PART_GRADE . "\"
}
else if ROUND_PLATE = 1
FolderPath := FolderName . "\Completed\" . "Round " . PART_TYPE . " (Hulk Jr)\" . PLATE_PART_GRADE . "\"
else
FolderPath := FolderName . "\Completed\" . PART_TYPE . "\" . PLATE_PART_GRADE . "\"
IfNotExist, %FolderPath%
FileCreateDir, %FolderPath%
FileAppend, %new_file_contents%, %FolderPath%\%PART_NAME%.nc1
ifExist, %FolderPath%\%PART_NAME% Holes.txt
{
FileRead, hole_import, %FolderPath%\%PART_NAME% Holes.txt
foundEnd := false
Loop, Parse, hole_import, `n
{
currentLine := Trim(A_LoopField)
if (RegExMatch(currentLine, "^[A-Za-z0-9]") && !foundEnd)
{
if InStr(currentLine, "BO")
hole_export .= currentLine . "`n"
else
hole_export .=  "  " . currentLine . "`n"
}
else
{
foundEnd := true
}
}
FileAppend, %hole_export%, %FolderPath%\%PART_NAME%.nc1
sleep 250
FileDelete, %FolderPath%\%PART_NAME% Holes.txt
}
sleep 250
FileAppend, EN, %FolderPath%\%PART_NAME%.nc1
IfNotExist, %FOLDERNAME%\Backup
FileCreateDir, %FOLDERNAME%\Backup
FileMove, %A_LoopFileFullPath%, %FOLDERNAME%\Backup
}
CreateDestinationFolder()
{
short_project_number := SubStr(PROJECT_NUMBER, 1, 3)
if PART_TYPE = Plate
{
filedestination := "H:\SDS ARCHIVES\" . short_project_number . "\" . PROJECT_NUMBER . "\Structural\" . PART_TYPE
}
else if (PART_TYPE = "Angle") or (PART_TYPE = "Bar")
{
filedestination := "H:\SDS ARCHIVES\" . short_project_number . "\" . PROJECT_NUMBER . "\Structural\Anglemaster\" . PART_TYPE
}
else if (PART_TYPE = "Beam") or (PART_TYPE = "Channel") or (PART_TYPE = "Tube") or (PART_TYPE = "WT")
{
filedestination := "H:\PCD Line\" . short_project_number . "\" . PROJECT_NUMBER . "\Structural\" . PART_TYPE
}
else
{
return
}
IfNotExist, %filedestination%
FileCreateDir, %filedestination%
}
GetProjectNumber()
{
FP:= A_LoopFileFullPath
IF inStr(FP, "jestex")
PROJECT_NUMBER:= SubStr(FP, 11, 4)
else PROJECT_NUMBER:= SubStr(FP, 8, 6)
}
PartTypeLookup1(str)
{
part_codes1 := { "PI" : "Pipe", "RB" : "Rod", "PL" : "Plate", "HSS" : "Tube", "FL" : "Plate", "TS" : "Tube", "SB" : "Plate"}
for key, value in part_codes1
{
if (InStr(str, "RPL"))
{
ROUND_PLATE := 1
}
if (InStr(str, key))
{
PART_TYPE := part_codes1[key]
if PART_TYPE = Plate
FindPlateMachine()
return value
}
}
return ""
}
PartTypeLookup2(str)
{
part_codes2 := { "I" : "Beam", "U" : "Channel", "L" : "Angle", "T" : "WT", "SO" : "Other" , "RU" : "Other" }
for key, value in part_codes2
{
if (InStr(str, key))
{
PART_TYPE := part_codes2[key]
if PART_TYPE = Beam
{
beam_size := ReadLine(8)
beam_size := RegExReplace(beam_size, "\s+")
}
return value
}
}
return ""
}
FindPartType()
{
str := ReadLine(8)
part_type := PartTypeLookup1(str)
if (part_type = "")
{
str := ReadLine(9)
part_type := PartTypeLookup2(str)
if (part_type = "")
PART_TYPE := "TYPE NOT FOUND"
}
FindMachine(PART_TYPE)
}
FindPartGrade()
{
PART_GRADE := ReadLine(6)
PART_GRADE := RegExReplace(PART_GRADE, "[^A-Za-z\d_-]+", "")
PLATE_PART_GRADE := PART_GRADE
}
FixGrade()
{
grade_line := OFFSET
grade_line += 6
if instr(LINE_ARRAY[grade_line], "300W")
{
JOKER := ReadLine(6)
SpaceCount()
JOKER := ""
spaces := Replicate(" ", COUNT)
COUNT := ""
new_text := spaces . "A36"
PART_GRADE := "A36"
LINE_ARRAY[grade_line] := new_text
}
if instr(LINE_ARRAY[grade_line], "316SS")
{
JOKER := ReadLine(6)
SpaceCount()
JOKER := ""
spaces := Replicate(" ", COUNT)
COUNT := ""
new_text := spaces . "A36"
PART_GRADE := "A36"
LINE_ARRAY[grade_line] := new_text
}
if instr(LINE_ARRAY[grade_line], "SS-316")
{
JOKER := ReadLine(6)
SpaceCount()
JOKER := ""
spaces := Replicate(" ", COUNT)
COUNT := ""
new_text := spaces . "A36"
PART_GRADE := "A36"
LINE_ARRAY[grade_line] := new_text
}
if instr(LINE_ARRAY[grade_line], "50")
{
JOKER := ReadLine(6)
SpaceCount()
JOKER := ""
spaces := Replicate(" ", COUNT)
COUNT := ""
new_text := spaces . "A572-50"
PART_GRADE := "A572-50"
LINE_ARRAY[grade_line] := new_text
}
}
FindMachine(str)
{
machine := { "Plate" : "Plate Machine", "Angle" : "Anglemaster", "Bar" : "Anglemaster", "Beam" : "Beamline", "Channel" : "Beamline", "Tube" : "Beamline" , "Pipe" : "Saw" , "Rod" : "Saw" , "WT" : "Beamline" }
for key, value in machine
{
key_no_spaces := StrReplace(key, " ", "")
if (InStr(str, key_no_spaces))
{
MACHINE_TYPE := machine[key]
}
}
}
AddOrRemoveScribe()
{
Delete_Scribe()
RemoveEN()
if (MACHINE_TYPE = "Beamline") and (PART_TYPE != "Channel")
New_Scribe()
if (MACHINE_TYPE = "Anglemaster")
New_Angle_Scribe()
if (PART_TYPE = "Bar") or (PART_TYPE = "Plate")
Plate_Scribe()
}
Delete_Scribe()
{
FoundSI := false
StartIndex := 0
StopIndex := 0
new_lines := ""
Loop, % LINE_ARRAY.Length()
{
if (FoundSI = false) and (InStr(LINE_ARRAY[A_Index], "SI") > 0)
{
FoundSI := true
StartIndex := A_Index
}
if (FoundSI = true) and (A_Index > StartIndex)
{
new_lines := RegExReplace(LINE_ARRAY[A_Index], "\s+")
}
if (FoundSI = true) and (StrLen(new_lines) = 2)
{
StopIndex := A_Index - 1
break
}
}
if (StartIndex > 0) and (StopIndex > 0)
{
Loop, % StopIndex - StartIndex + 1
{
LINE_ARRAY.Delete(StartIndex)
StartIndex ++
}
Delete_Scribe()
}
}
New_Scribe()
{
BeamCenter := ""
BeamCenter := Round((FLANGE_WIDTH / 2) + 6.35, 2)
line1 := "SI"
IfLess PART_LENGTH, 152.4
line2 := "  o   25.40o  " . BeamCenter . "	0.00  13  " . PART_NAME
else IfLess PART_LENGTH, 304.8
line2 := "  o   25.40o  " . BeamCenter . "	0.00  13  " . PROJECT_NUMBER . "-" . PART_NAME
else IfLess PART_LENGTH, 6096
line2 := "  o   50.80o  " . BeamCenter . "	0.00  13  " . PROJECT_NUMBER . "-" . PART_NAME
else
line2 := "  o   914.40o " . BeamCenter . "	0.00  13  " . PROJECT_NUMBER . "-" . PART_NAME
StringReplace, line2, line2,_,-,All
LINE_ARRAY.Push(line1)
LINE_ARRAY.Push(line2)
}
New_Angle_Scribe()
{
BeamCenter := 25.4
ScribeStart := ""
IfLess PART_LENGTH, 304.8
ScribeStart := Round(PART_LENGTH - 25.40)
else IfLess PART_LENGTH, 6096
ScribeStart := Round(PART_LENGTH - 50)
else
ScribeStart := Round(PART_LENGTH - 914.4)
line1 := "SI"
IfLess PART_LENGTH, 152.4
line2 := "  h   " . ScribeStart . "u  " . BeamCenter . "	180.00  13  " . PART_NAME
else IfLess PART_LENGTH, 304.8
line2 := "  h   " . ScribeStart . "u  " . BeamCenter . "	180.00  13  " . PROJECT_NUMBER . "-" . PART_NAME
else IfLess PART_LENGTH, 6096
line2 := "  h   " . ScribeStart . "u  " . BeamCenter . "	180.00  13  " . PROJECT_NUMBER . "-" . PART_NAME
else
line2 := "  h   " . ScribeStart . "u  " . BeamCenter . "	180.00  13  " . PROJECT_NUMBER . "-" . PART_NAME
StringReplace, line2, line2,_,-,All
LINE_ARRAY.Push(line1)
LINE_ARRAY.Push(line2)
}
Plate_Scribe()
{
BeamCenter := ""
BeamCenter := Round((PART_WIDTH / 2) - 6.35, 2)
line1 := "SI"
IfLess PART_LENGTH, 152.4
line2 := "  v   25.40o  " . BeamCenter . "	0.00  13  " . PART_NAME
else IfLess PART_LENGTH, 304.8
line2 := "  v   25.40o  " . BeamCenter . "	0.00  13  " . PROJECT_NUMBER . "-" . PART_NAME
else IfLess PART_LENGTH, 6096
line2 := "  v   50.80o  " . BeamCenter . "	0.00  13  " . PROJECT_NUMBER . "-" . PART_NAME
else
line2 := "  v   914.40o " . BeamCenter . "	0.00  13  " . PROJECT_NUMBER . "-" . PART_NAME
StringReplace, line2, line2,_,-,All
LINE_ARRAY.Push(line1)
LINE_ARRAY.Push(line2)
}
FindPlateMachine()
{
FixGrade()
if PART_HEIGHT < 6.35
if PLATE_PART_GRADE = 316SS
{
PART_HEIGHT := "  6.35"
LINE_ARRAY[14] := PART_HEIGHT
}
else
PLATE_MACHINE := "Error"
else if PART_HEIGHT > 50.8
PLATE_MACHINE := "Error"
}
Find_Holes()
{
FoundBO := false
StartIndex := 0
StopIndex := 0
new_lines := ""
Loop, % LINE_ARRAY.Length()
{
if (FoundBO = false) and (InStr(LINE_ARRAY[A_Index], "BO") > 0)
{
FoundBO := true
StartIndex := A_Index
FOUND_HOLES := 1
}
if (FoundBO = true) and (A_Index > StartIndex)
{
new_lines := RegExReplace(LINE_ARRAY[A_Index], "\s+")
}
if (FoundBO = true) and (StrLen(new_lines) = 2)
{
StopIndex := A_Index - 1
break
}
}
StartIndex2 := StartIndex + 1
StopIndex2 := StopIndex
if (StartIndex2 > 0) and (StopIndex2 > 0)
{
Loop, % StopIndex2 - StartIndex2 + 1
{
HOLE_CONTENTS .= LINE_ARRAY[StartIndex2] . "`n"
StartIndex2 ++
}
}
if (StartIndex > 0) and (StopIndex > 0)
{
Loop, % StopIndex - StartIndex + 1
{
LINE_ARRAY.Delete(StartIndex)
StartIndex ++
}
Find_Holes()
}
}
ManageHoles(action)
{
if (PLATE_HAS_SLOT = 1) and (ADJ_SLOT_FLAG = 1)
{
if (ADJ_VERT_SLOT_FLAG) = 0
FolderPath := FolderName . "\Completed\" . PART_TYPE . " With Adjusted Slots (NEEDS CUSTOMER APPROVAL)\" . PART_GRADE . "\Horizontal\"
else if (ADJ_VERT_SLOT_FLAG) = 1
FolderPath := FolderName . "\Completed\" . PART_TYPE . " With Adjusted Slots (NEEDS CUSTOMER APPROVAL)\" . PART_GRADE . "\Vertical\"
else
FolderPath := FolderName . "\Completed\" . PART_TYPE . " With Slotted Holes (2013)\" . PLATE_PART_GRADE . "\"
}
else if ROUND_PLATE = 1
FolderPath := FolderName . "\Completed\" . "Round " . PART_TYPE . " (Hulk Jr)\" . PLATE_PART_GRADE . "\"
else
FolderPath := FolderName . "\Completed\" . PART_TYPE . "\" . PLATE_PART_GRADE . "\"
if (action = "clear")
HOLE_CONTENTS := ""
if (action = "save")
{
IfNotExist, %FolderPath%
FileCreateDir, %FolderPath%
if FOUND_HOLES = 1
{
FileAppend, BO, %FolderPath%\%PART_NAME% Holes.txt
sleep 50
FileAppend, `n, %FolderPath%\%PART_NAME% Holes.txt
sleep 50
FileAppend, %HOLE_CONTENTS%, %FolderPath%\%PART_NAME% Holes.txt
sleep 250
}
}
else if (action = "delete")
{
FileDelete, %FolderPath%\%PART_NAME% Holes.txt
}
}
HoleFunctions()
{
Check_Holes()
ManageHoles("save")
ManageHoles("clear")
}
Check_Holes()
{
lines := HOLE_CONTENTS
output := "  "
hole_location := ""
pop_mark := ""
columns := []
Loop, Parse, lines, `n
{
hole_error := 0
pop_mark := 0
sleep 50
line := StrReplace(A_LoopField, "`r", "")
result1 := DefineColumn(1, line)
result2 := DefineColumn(2, line)
result3 := DefineColumn(3, line)
result4 := DefineColumn(4, line)
result5 := DefineColumn(5, line)
result6 := DefineColumn(6, line)
result7 := DefineColumn(7, line)
result8 := DefineColumn(8, line)
result9 := DefineColumn(9, line)
if StrLen(line) < 4
return
col1 := SubStr(line, result1.start, result1.length)
col2 := SubStr(line, result2.start, result2.length)
col3 := SubStr(line, result3.start, result3.length)
col4 := SubStr(line, result4.start, result4.length)
col5 := SubStr(line, result5.start, result5.length)
col6 := SubStr(line, result6.start, result6.length)
col7 := SubStr(line, result7.start, result7.length)
col8 := SubStr(line, result8.start, result8.length)
col9 := SubStr(line, result9.start, result9.length)
col3 := StrReplace(col3, "m", "")
if (PART_TYPE = "WT")
{
col1 := StrReplace(col1, "h", "Q")
col1 := StrReplace(col1, "o", "h")
col1 := StrReplace(col1, "Q", "o")
col1 := StrReplace(col1, "v", "o")
if InStr(col1, "h")
{
JOKER := col3
SpaceCount()
JOKER := ""
spaces := Replicate(" ", COUNT)
COUNT := ""
col3_ns := StrReplace(col3, " ", "")
col3 := PART_WIDTH - col3_ns
col3 := round(col3, 2)
new_text := spaces . col3
col3 := new_text
}
}
col1_nospaces := StrReplace(col1, " ", "")
col2_nospaces := StrReplace(col2, " ", "")
col3_nospaces := StrReplace(col3, " ", "")
col4_nospaces := StrReplace(col4, " ", "")
col5_nospaces := StrReplace(col5, " ", "")
col6_nospaces := StrReplace(col6, " ", "")
col7_nospaces := StrReplace(col7, " ", "")
col8_nospaces := StrReplace(col8, " ", "")
col9_nospaces := StrReplace(col9, " ", "")
if (col6_nospaces > 0)
PLATE_HAS_SLOT := 1
if (col4_nospaces <= 0) and (col5_nospaces <= 0)
{
if (PART_TYPE = "Plate") or (PART_TYPE = "Bar")
hole_error := 1
else
pop_mark := 1
}
if (col4_nospaces = "20.64")
{
spaces := RegExReplace(col4, "(\s+)(20\.64)", "$1")
col4 := spaces . "22.23"
}
hole_x := RegExReplace(col2_nospaces, "[^0-9\.]", "")
hole_y := RegExReplace(col3_nospaces, "[^0-9\.]", "")
abs_hole_x := Abs(hole_x)
abs_hole_y := Abs(hole_y)
if (col1_nospaces = "u")
hole_location := "bottom"
if (col1_nospaces = "o")
hole_location := "top"
if (col1_nospaces = "v") or (col1_nospaces = "h")
hole_location := "web"
if (PART_TYPE = "Beam") or (PART_TYPE = "Channel") or (PART_TYPE = "WT")
{
if (hole_location = "web")
{
top_boundary := PART_WIDTH
btm_boundary := 0
hole_buffer := col4_nospaces
top_boundary -= hole_buffer
btm_boundary += hole_buffer
start_barrier := hole_buffer
stop_barrier := PART_LENGTH
stop_barrier -= hole_buffer
if (hole_y < btm_boundary) or (hole_y > top_boundary)
hole_error := 1
if (hole_x < start_barrier) or (hole_x > stop_barrier)
{
hole_error := 1
}
}
}
if (PART_TYPE = "Beam") or (PART_TYPE = "WT")
{
if (hole_location = "top") or (hole_location = "bottom")
{
flange_middle := FLANGE_WIDTH
flange_middle /= 2
hole_buffer := col4_nospaces
mid_barrier1 := flange_middle + hole_buffer
mid_barrier2 := flange_middle - hole_buffer
if (abs_hole_y < mid_barrier1) and (abs_hole_y > mid_barrier2)
hole_error := 1
}
}
if (PART_TYPE = "Angle")
{
col1 := StrReplace(col1, "h", "v")
col1 := StrReplace(col1, "u", "o")
if (abs_hole_y <= (col4_nospaces * 1.25))
hole_error := 1
}
if (PART_TYPE != "Plate")
{
if (hole_location = "top") or (hole_location = "bottom")
{
flange_stop := PART_LENGTH
hole_buffer := col4_nospaces
start_barrier := hole_buffer
stop_barrier := flange_stop
stop_barrier -= hole_buffer
flange_top := FLANGE_WIDTH
top_barrier := flange_top
top_barrier -= hole_buffer
btm_barrier := hole_buffer
if (hole_y < btm_barrier) or ((hole_y > top_barrier) and (PART_TYPE != "Channel") and (PART_TYPE != "Angle"))
{
hole_error := 1
}
if (hole_x < start_barrier) or (hole_x > stop_barrier)
{
hole_error := 1
}
}
if (PART_TYPE = "Plate")
{
if (col4_nospaces < 12.7)
{
hole_error := 1
}
}
}
if pop_mark = 1
{
InputBox, userInput, Enter Hole Diameter, No Hole Diameter found on %PART_NAME% on %hole_location%. Please enter the hole diameter in fractional inches.
if ErrorLevel
return
JOKER := col4
SpaceCount()
JOKER := ""
spaces := Replicate(" ", COUNT)
COUNT := ""
col4 := spaces . FractionToMm(userInput)
col5 := ""
col6 := ""
col7 := ""
col8 := ""
col9 := ""
}
if (col6_nospaces > 0) and (MACHINE_TYPE = "Beamline")
{
slot_rotation := col8_nospaces
if (slot_rotation = 0.00)
{
test_case := col4_nospaces + 1.5875
if (col6_nospaces < test_case) AND (slot_rotation = 0.00)
{
ADJ_SLOT_FLAG := 1
col6_old := col6_nospaces
col6_nospaces := col4_nospaces + 1.59
col6_nospaces := round(col6_nospaces, 2)
true_x := col2_nospaces
true_x += col6_old / 2
col2_nospaces := true_x - (col6_nospaces / 2)
col2_nospaces := Round(col2_nospaces, 2)
JOKER := col2
SpaceCount()
JOKER := ""
spaces := Replicate(" ", COUNT)
COUNT := ""
col2 := spaces . col2_nospaces
JOKER := col6
SpaceCount()
JOKER := ""
spaces := Replicate(" ", COUNT)
COUNT := ""
col6 := spaces . col6_nospaces
}
else
{
}
}
else
{
test_case := col4_nospaces + 1.5875
if (col6_nospaces < test_case) AND (slot_rotation = 90.00)
{
ADJ_SLOT_FLAG := 1
ADJ_VERT_SLOT_FLAG := 1
col6_old := col6_nospaces
col6_nospaces := col4_nospaces + 1.59
col6_nospaces := round(col6_nospaces, 2)
true_x := col3_nospaces
true_x += col6_old / 2
col3_nospaces := true_x - (col6_nospaces / 2)
col3_nospaces := Round(col3_nospaces, 2)
JOKER := col3
SpaceCount()
JOKER := ""
spaces := Replicate(" ", COUNT)
COUNT := ""
col3 := spaces . col3_nospaces
JOKER := col6
SpaceCount()
JOKER := ""
spaces := Replicate(" ", COUNT)
COUNT := ""
col6 := spaces . col6_nospaces
}
else
{
Msgbox % PART_NAME " flagged a slot that needed fixing but did not know how to fix it. Please investigate."
}
}
}
if (hole_error = "0") or (pop_mark = "1")
output .= col1 col2 col3 col4 col5 col6 col7 col8 col9 "`n"
HOLE_CONTENTS := output
}
}
IsItBar()
{
if PART_TYPE = Plate
{
mod_height := PART_HEIGHT
mod_height /= 25.4
mod_height := Round(mod_height, 2)
mod_width := PART_WIDTH
mod_width /= 25.4
mod_width := Round(mod_width, 2)
check_width := mod_width
check_width *= 4
mod_length := PART_LENGTH
mod_length /= 25.4
mod_length := Round(mod_length, 2)
if (mod_width > 6)
PART_TYPE := "Plate"
else if (mod_height = mod_width)
PART_TYPE := "Bar"
else if ((Mod(mod_width, 1) != 0) and (Mod(mod_width, 0.5) = 0) and (mod_length > 48) and (mod_height <= 0.5))
PART_TYPE := "Bar"
else if (Mod(mod_width, 1) = 0) and (mod_length > 18) and (mod_height <= 0.5) and (mod_length > check_width)
PART_TYPE := "Bar"
else if (mod_height <= 0.375) and (mod_length > 60)
PART_TYPE := "Bar"
}
}
CheckRoundPlate()
{
FoundAK := false
StartIndex := 0
StopIndex := 0
Loop, % LINE_ARRAY.Length()
{
if (FoundAK = false) and (InStr(LINE_ARRAY[A_Index], "AK") > 0)
{
FoundAK := true
StartIndex := A_Index
}
if (FoundAK = true) and (A_Index > StartIndex)
{
currentLine := Trim(LINE_ARRAY[A_Index])
if (StrLen(currentLine) = 2) or (currentLine = "")
{
StopIndex := A_Index - 1
break
}
}
}
if (FoundAK = true)
{
AK_Length := StopIndex - StartIndex
if AK_Length < 4
{
ROUND_PLATE := 1
}
}
}
Replicate( Str, Count )
{
VarSetCapacity( S, Count * ( A_IsUnicode ? 2:1 ), 1 )
StringReplace, S, S, % SubStr( S,1,1 ), %Str%, All
Return SubStr( S, 1, Count * StrLen(Str) )
}
RemoveEN()
{
for i, line in LINE_ARRAY
{
if (InStr(LINE_ARRAY[i], "EN"))
{
LINE_ARRAY.RemoveAt(i)
RemoveEN()
}
}
}
ReadLine(target_line)
{
target_line += OFFSET
for line_index, line in LINE_ARRAY
{
if (line_index = target_line)
{
value := LINE_ARRAY[target_line]
if InStr(value, ",")
{
myArray := StrSplit(value, ",")
value := myArray[1]
}
value := RegExReplace(value, "\R")
return value
}
}
}
ReadWTLine(target_line)
{
FileRead, beamfile, %PARTFILEPATH%
wtcontents := StrSplit(beamfile, "`n")
for line_index, line in wtcontents
{
if (line_index = target_line)
{
value := wtcontents[target_line]
if InStr(value, ",")
{
myArray := StrSplit(value, ",")
value := myArray[1]
}
value := RegExReplace(value, "\R")
return value
}
}
}
count_numbers_beam(string, ByRef count_between_letters, ByRef count_after_x)
{
pattern_between_letters := "([A-Za-z])(\d+)[A-Za-z]"
pattern_after_x := "X(\d+(\.\d+)?)"
count_between_letters := 0
count_after_x := 0
if (RegExMatch(string, pattern_between_letters, match_between_letters))
{
number_between_letters := match_between_letters2
count_between_letters := StrLen(number_between_letters)
}
if (RegExMatch(string, pattern_after_x, match_after_x))
{
number_after_x := match_after_x1
count_after_x := StrLen(number_after_x)
}
}
SplitPartString(string)
{
parts := []
start := 1
len := StrLen(string)
singleDelimiters := ["MC", "WT"]
delimiters := ""
if (singleDelimiters.Length() > 0)
{
Loop % singleDelimiters.Length()
{
delimiter := singleDelimiters[A_Index]
if (InStr(string, delimiter))
{
delimiters := "X" . delimiter
break
}
}
}
if (delimiters = "")
delimiters := "LXWC"
Loop % len
{
char := SubStr(string, A_Index, 1)
if (InStr(delimiters, char))
{
if (start < A_Index)
{
part := SubStr(string, start, A_Index - start)
parts.Push(part)
}
start := A_Index + 1
}
}
part := SubStr(string, start)
parts.Push(part)
return parts
}
GetPartAbbreviation(string)
{
len := StrLen(string)
singleDelimiters := ["MC", "WT", "HSS"]
partAbbreviation := ""
if (singleDelimiters.Length() > 0)
{
Loop % singleDelimiters.Length()
{
delimiter := singleDelimiters[A_Index]
if (InStr(string, delimiter))
{
partAbbreviation := delimiter
break
}
}
}
if (partAbbreviation = "")
{
Loop % len
{
char := SubStr(string, A_Index, 1)
if (RegExMatch(char, "[A-Za-z]"))
{
partAbbreviation := char
break
}
}
}
return partAbbreviation
}
FractionToDecimal(Fraction, Unit := false)
{
has_neg := ""
has_feet := ""
has_inches := ""
Has_Fraction := ""
FormatFloat := A_FormatFloat
SetFormat, FloatFast, 0.15
Num := {}
N := 0
D := 1
if RegExMatch(Fraction, "^\s*-")
Has_Neg := true
if RegExMatch(Fraction, "i)feet|foot|ft|'")
Has_Feet := true
if RegExMatch(Fraction, "i)inch|in|""")
Has_Inches := true
if RegExMatch(Fraction, "i)/|of|div")
Has_Fraction := true
Output := Trim(Fraction,"""'")
if Output is number
{
SetFormat, FloatFast, %FormatFloat%
return Output (Unit ? (Has_Feet ? "'":(Has_Inches ? """":"")) : "")
}
RegExMatch(Fraction,"^[^\d\.]*([\d\.]*)[^\d\.]*([\d\.]*)[^\d\.]*([\d\.]*)[^\d\.]*([\d\.]*)",Match)
Loop 4
if !(Match%A_Index% = "")
Num.Insert(Match%A_Index%)
if Has_Fraction
{
N := Num[Num.MaxIndex()-1]
D := Num[Num.MaxIndex()]
}
Output := (Num.MaxIndex() = 2 ? N / D : (Num[1]) + N / D)
if (Has_Feet &  Has_Inches)
if (Num.MaxIndex() = 2)
Output := Num[1] + Num[2] /12
else
Output := Num[1] + ((Num.MaxIndex() = 3 ? 0:Num[2]) + N / D) / 12
Output := (Has_Neg ? "-":"") (Output ~= "." ? RTrim(RTrim(Output,"0"),".") : Output) (Unit ? (Has_Feet ? "'":(Has_Inches ? """":"")) : "")
SetFormat, FloatFast, %FormatFloat%
return Output
}
FractionToMm(fraction) {
if (InStr(fraction, "/")) {
StringSplit, parts, fraction, /
result := parts1 / parts2
} else {
result := fraction
}
return Round(result * 25.4, 2)
}
TruncateToHundredth(number) {
decimalPos := InStr(number, ".")
if (decimalPos > 0) {
if (decimalPos + 2 < StrLen(number)) {
return SubStr(number, 1, decimalPos + 2)
}
}
return number
}
RoundNumbersToHundredth(line) {
words := StrSplit(line, " ")
result := ""
for index, word in words {
if (word ~= "^\d+\.\d{3,}$") {
word := TruncateToHundredth(word)
}
result .= (index > 1 ? " " : "") . word
}
return result
}
DefineColumn(columnNumber, line)
{
column_found := false
col_num := 0
total_char := 0
prev_char := ""
column_contents := ""
Loop, Parse, line
{
total_char++
char := A_LoopField
if (char = " ") and (prev_char != " ")
col_num++
if (col_num = columnNumber) and (column_found = false)
{
column_found := true
column_start := total_char
}
else if (col_num != columnNumber)
column_found := false
if (column_found = true)
column_contents .= char
prev_char := char
}
col_length := StrLen(column_contents)
if (col_length = 0)
column_start := 0
return {start: column_start, length: col_length, content: column_contents}
}
FixWT()
{
if PART_TYPE = WT
FilePath := FindWTConvert()
else
return
if FilePath =
PART_TYPE := "NEW WT SIZE"
else if PART_TYPE = WT
{
wtline := ""
str := ReadLine(8)
str := RegExReplace(str, "\s")
target_line1 := 8
target_line2 := 9
target_line3 := 11
target_line4 := 12
target_line5 := 13
target_line6 := 14
target_line7 := 15
target_line8 := 16
variables := [target_line1, target_line2, target_line3, target_line4, target_line5, target_line6, target_line7, target_line8]
for index, variable in variables
{
wtline += 1
JOKER := ReadLine(variable)
error_check := ReadLine(variable)
SpaceCount()
JOKER := ""
spaces := Replicate(" ", COUNT)
COUNT := ""
error_check := StrReplace(error_check, " ", "")
text := ReadWTLine(wtline)
if variable = 12
{
if (error_check - text) != 0
{
temp_hold := FLANGE_WIDTH
FLANGE_WIDTH := PART_WIDTH
PART_WIDTH := temp_hold
line_1 := 11
line_1 += OFFSET
line_2 := 12
line_2 += OFFSET
text := ReadWTLine(wtline)
new_text := spaces . text
variable += OFFSET
LINE_ARRAY[variable] := new_text
variable += 1
}
}
else
{
variable += OFFSET
new_text := spaces . text
LINE_ARRAY[variable] := new_text
variable += 1
}
}
}
GetGeometry()
}
FindWTConvert()
{
wt_size := ReadLine(8)
wt_size := RegExReplace(wt_size, "\s+")
wt_size := RegExReplace(wt_size, "x", "X")
c1 := 0
c2 := 0
count_numbers_beam(wt_size, c1, c2)
col1 := SubStr(wt_size, 1, 1)
col2 := SubStr(wt_size, 3, c1)
col3 := SubStr(wt_size, c1 + 4, c2)
col1_nospaces := StrReplace(col1, " ", "")
col2_nospaces := StrReplace(col2, " ", "")
col3_nospaces := StrReplace(col3, " ", "")
wt_depth := col2_nospaces
wt_weight := col3_nospaces
beam_letter := col1_nospaces
beam_depth := wt_depth
beam_depth *= 2
if (beam_depth - Floor(beam_depth) <> 0)
{
beam_depth := Round(beam_depth, 1)
}
else
{
beam_depth := Round(beam_depth)
}
beam_weight := wt_weight
beam_weight *= 2
if (beam_weight - Floor(beam_weight) <> 0)
{
beam_weight := Round(beam_weight, 1)
}
else
{
beam_weight := Round(beam_weight)
}
FolderPath := GSD_LIBRARY_LOC . "Beam\" . beam_letter . "\" . beam_depth . "\"
PARTFILEPATH := FolderPath . beam_letter . beam_depth . "X" . beam_weight . ".txt"
ifExist, %PARTFILEPATH%
return PARTFILEPATH
else
return ""
}
ShapesLibrary()
{
if ((MACHINE_TYPE = "Beamline") or (MACHINE_TYPE = "Anglemaster") or (PART_TYPE = "Plate")) and ((PART_TYPE != "WT") and (PART_TYPE != "Bar") and (PART_TYPE != "Other"))
{
if (PART_TYPE = "Plate")
{
read_part := ReadLine(8)
read_part := RegExReplace(read_part, "(.*?)X.*", "$1")
}
else
{
read_part := ReadLine(8)
}
read_part := RegExReplace(read_part, "x", "X")
string := Trim(read_part)
parts := SplitPartString(string)
c1 := (parts.Length() >= 1) ? parts[1] : ""
c2 := (parts.Length() >= 2) ? parts[2] : ""
c3 := (parts.Length() >= 3) ? parts[3] : ""
c1 := Trim(c1)
c2 := Trim(c2)
c3 := Trim(c3)
c1 := FractionToDecimal(c1)
c2 := FractiontoDecimal(c2)
c3 := FractiontoDecimal(c3)
partAbbreviation := GetPartAbbreviation(string)
partAbbreviation := Trim(partAbbreviation)
if (RegExMatch(c3, "[A-Za-z0-9]"))
{
FolderPath := GSD_LIBRARY_LOC PART_TYPE . "\" . partAbbreviation . "\" . c1 . "\" . c2 . "\"
PARTFILEPATH := FolderPath . partAbbreviation . c1 . "X" . c2 . "X" . c3 . ".txt"
}
else
{
FolderPath := GSD_LIBRARY_LOC . PART_TYPE . "\" . partAbbreviation . "\" . c1 . "\"
PARTFILEPATH := FolderPath . partAbbreviation . c1 . "X" . c2 . ".txt"
}
IfNotExist, %FolderPath%
FileCreateDir, %FolderPath%
ifNotExist, %PARTFILEPATH%
{
target_line1 := 8
target_line2 := 9
target_line3 := 11
target_line4 := 12
target_line5 := 13
target_line6 := 14
target_line7 := 15
target_line8 := 16
variables := [target_line1, target_line2, target_line3, target_line4, target_line5, target_line6, target_line7, target_line8]
for index, variable in variables
{
text := ReadLine(variable)
text := Trim(text)
FileAppend, %text%`n, %PARTFILEPATH%
}
CreateSummaryFile(partFilePath)
}
}
}
CreateSummaryFile(partFilePath)
{
SummaryFilePath := GSD_LIBRARY_LOC . "New Shapes Summary.txt"
IfNotExist, %SummaryFilePath%
{
FileAppend,, %SummaryFilePath%
FormatTime, CurrentDateTime,, yyyy-MM-dd HH:mm:ss
FileAppend, Summary created on %CurrentDateTime% `n`n, %SummaryFilePath%
}
part_created := ReadLine(8)
part_created := Trim(part_created)
FileGetTime, FileDateTime, %partFilePath%, M
FormatTime, FileDateTime,, MM-dd-yyyy HH:mm:ss
partFileName := SubStr(partFilePath, InStr(partFilePath, "\") + 1)
FileAppend, %part_created% - %FileDateTime% `n, %SummaryFilePath%
}