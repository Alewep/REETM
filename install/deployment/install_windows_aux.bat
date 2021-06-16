setlocal EnableDelayedExpansion
@echo off
echo Administrative permissions required. Detecting permissions...


net session >nul 2>&1
if %errorLevel% == 0 (
   cd "%~dp0"
   echo Installing ffmpeg...
   if "%ffmpegInstalled%"=="1" (

         echo ffmpeg was already installed.

    ) else (
         tar -xf ffmpeg-4.4-essentials_build.zip
	 ren ffmpeg-4.4-essentials_build ffmpeg

         Xcopy  /y /e /i "ffmpeg" "C:\Program Files\ffmpeg"
         setx /m PATH "%PATH%;C:\Program Files\ffmpeg\bin"
         setx ffmpegInstalled 1

    )
     
   set anacondaPath=C:\Users\%USERNAME%\anaconda3

   set /p rep="Is anaconda in the default path : !anacondaPath! (y/n) ? "
   
   if "!rep!"=="n" (
      
      set /p anacondaPath="Anaconda path : "
   ) 

   echo Installing Anaconda environment...
   call "!anacondaPath!\Scripts\activate.bat" "!anacondaPath!"
   call conda env remove -n envReetm
   call conda env create -f reetmEnv.yml
   echo Installation succes, you can close this window.
) else (
    echo Failure: Current permissions inadequate.
)




