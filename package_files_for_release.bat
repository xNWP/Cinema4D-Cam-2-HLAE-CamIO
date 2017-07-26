ECHO OFF
CLS

DEL /P *.7z *.zip
CLS

SET "sevzip="C:\Program Files\7-Zip\7z.exe""
SET "version=v1"
SET "filelist=c4dcam2hlaecamio INSTALLATION.txt"

%sevzip% a -t7z C4D_Cam_2_HLAE_CamIO_%version%.7z %filelist%
%sevzip% a -tzip C4D_Cam_2_HLAE_CamIO_%version%.zip %filelist%

ECHO.
ECHO Packaged.
PAUSE > nul