@echo off
REM ===================================================================
REM  derle.bat <harita> -- CoD2 SP derleme: cod2map -> cod2rad.
REM  VIS YOK: oyun SP'de vis'li bsp'yi reddediyor (olculdu, hata kutusu:
REM  "In single player, do not compile the bsp with visibility").
REM  Log: sidirezegh_tools\log\   CALISIRKEN BU DOSYA DUZENLENMEZ.
REM ===================================================================
setlocal
set R=F:\Activision\Call of Duty 2
set T=%R%\bin
set M=%~1
if "%M%"=="" set M=sidirezegh
set B=%R%\main\maps\
set L=%R%\sidirezegh_tools\log
if not exist "%L%" mkdir "%L%"
if not exist "%B%" mkdir "%B%"
copy /y "%R%\map_source\%M%.map" "%B%%M%.map" >nul
cd /d "%T%"
echo [1/2] cod2map
"%T%\cod2map.exe" -platform pc "%B%%M%" > "%L%\%M%_bsp.log" 2>&1
if errorlevel 1 (echo HATA: cod2map & goto son)
echo [2/2] cod2rad
if exist "%B%%M%.map" del "%B%%M%.map"
"%T%\cod2rad.exe" -platform pc "%B%%M%" > "%L%\%M%_rad.log" 2>&1
if errorlevel 1 (echo HATA: cod2rad & goto son)
echo TAMAM
:son
if exist "%B%%M%.map" del "%B%%M%.map"
if exist "%B%%M%.d3dpoly" del "%B%%M%.d3dpoly"
endlocal
