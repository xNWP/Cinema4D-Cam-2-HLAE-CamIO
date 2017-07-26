ECHO OFF
cls

SET "ProjDir="C:\xCode\C4D_Cam_To_HLAE_CamIO""
SET "PluginFolder=c4dcam2hlaecamio"
SET "Cinema4DPluginDir="C:\Program Files\MAXON\CINEMA 4D R17\plugins\%PluginFolder%""

CD %ProjDir%

RMDIR /S /Q %Cinema4DPluginDir%

MKDIR %Cinema4DPluginDir%
cls

XCOPY /S %PluginFolder% %Cinema4DPluginDir%

ECHO.
ECHO Plugin Pushed.
pause > nul