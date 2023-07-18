# DaVinci_Script_Proxy_generator

This is a DaVinci Resolve script and written in Python, automates the process of importing video footage. Additionally, it categorizes the footage based on the video aspect ratio and subsequently transcodes it into an approximate resolution of 1920x1080 using the H.265 4:2:0 codec

Original footage, especially when captured in high-resolution formats such as 4K, 6K, or 8K, is aimed at achieving the best possible image quality. These formats offer greater detail, higher dynamic range, and more flexibility for visual effects, color grading, cropping, and other post-production processes. High-resolution footage can also future-proof a project, allowing it to maintain its quality as display technologies improve over time.

However, the high data rate and larger file sizes of these formats can make the footage difficult to work with during the editing process, particularly on a system with weak I/O performance. It can slow down the editing software, make playback choppy or unresponsive, and consume significant storage space.

This is why a proxy workflow is often used. The editor can work with lower-resolution proxy files that are easier and faster to handle during the editing process, while the high-resolution original footage is used for the final render.
  
## Prerequisites and Usage
Excerpted from the "Blackmagic Design/DaVinci Resolve/Developer/Scripting/README.txt”


### Prerequisites
-------------
DaVinci Resolve scripting requires one of the following to be installed (for all users):

    Lua 5.1
    Python 2.7 64-bit
    Python >= 3.6 64-bit


### Using a script
--------------
DaVinci Resolve needs to be running for a script to be invoked.

For a Resolve script to be executed from an external folder, the script needs to know of the API location. 
You may need to set the these environment variables to allow for your Python installation to pick up the appropriate dependencies as shown below:

    Mac OS X:
    RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
    RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
    PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"

    Windows:
    RESOLVE_SCRIPT_API="%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
    RESOLVE_SCRIPT_LIB="C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
    PYTHONPATH="%PYTHONPATH%;%RESOLVE_SCRIPT_API%\Modules\"

    Linux:
    RESOLVE_SCRIPT_API="/opt/resolve/Developer/Scripting"
    RESOLVE_SCRIPT_LIB="/opt/resolve/libs/Fusion/fusionscript.so"
    PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"
    (Note: For standard ISO Linux installations, the path above may need to be modified to refer to /home/resolve instead of /opt/resolve)



### Folder Structure
--------------
Common Footage folder structure like this
- 📁 Production
  - 📁 Footage
    - 📁 Shooting Day 1
      - 📁 A001_0210Z9
      - 📁 B001_029AC3
    - 📁 Shooting Day 2
      - 📁 A002_0210Z9

  
In our Adobe PremierePro-based workflow，We place the Proxy folder alongside the Footage folder
- 📁 Production
  - 📁 Proxy
  - 📁 Footage
    - 📁 Shooting Day 1
      - 📁 A001_0210Z9
      - 📁 B001_029AC3
    - 📁 Shooting Day 2
      - 📁 A002_0210Z9


--------------
Upon invocation of this script, the terminal prompts the user to provide the paths for the footage folder and the proxy folder.
<img width="682" alt="Screenshot 2023-07-18 at 22 15 33" src="https://github.com/UserProjekt/DaVinciScript-ProxyTranscoder/assets/78477492/14de004d-6fe1-4ad0-910d-56007d9cc395">

After the paths are inputted, DaVinci Resolve initiates the process of importing video files, categorizing Clips and creating timelines based on aspect ratios. Subsequently, the script re-establishes the date-based folder structure within the Proxy folder, This then serves as the target location for the ensuing transcoding.
<img width="1556" alt="Screenshot 2023-07-18 at 23 16 58" src="https://github.com/UserProjekt/DaVinciScript-ProxyTranscoder/assets/78477492/dee01bb2-9adb-4e06-99f6-2d580db51d8a">

