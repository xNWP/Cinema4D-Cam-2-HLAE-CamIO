@ECHO OFF
ECHO Deleting existing archives...
DEL /P *.7z *.zip
ECHO Done.

SET sevzip="C:\Program Files\7-Zip\7z.exe"
SET filelist=c4dcam2hlaecamio INSTALLATION.txt

SET /P versionMajor="Major Version: "
SET /P versionMinor="Minor Version: "
SET archName="C4D-Cam-2-HLAE-CamIO_%versionMajor%_%versionMinor%"

%sevzip% a -t7z %archname%.7z %filelist%
%sevzip% a -tzip %archname%.zip %filelist%

ECHO.
ECHO Packaged.