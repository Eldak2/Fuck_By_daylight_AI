Dim objShell
Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = "C:\Users\aleks\Documents\Projects\Fuck_By_Daylight_AI"
objShell.Run "start_all.bat", 0, False
Set objShell = Nothing