# DaVinci_Script_Proxy_generator

This script, written in Python for DaVinci Resolve, automates the process of importing video footage and generating proxies. It categorizes the footage based on the video aspect ratio and subsequently transcodes it to an approximate resolution of 1920x1080 using Render Presets. This script employs a custom preset titled 'FHD_h.265_420_8bit_5Mbps'. 

This preset corresponds to Full High Definition (FHD) video with H.265 encoding, 4:2:0 chroma subsampling, 8-bit color depth, and a bitrate of 5Mbps. These settings are optimized for hardware decoding and systems with low I/O performance, resulting in decreased storage space.
  
## Prerequisites and Usage
Excerpted from the:

Mac OS X:
 /Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/README.txt

Windows:
 C:\Program Files\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\README.txt

    


### Prerequisites
DaVinci Resolve scripting requires one of the following to be installed (for all users):

    Lua 5.1
    Python 2.7 64-bit
    Python >= 3.6 64-bit


### Using a script
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
The standard footage folder structure is outlined below. Please ensure that the date-specific folders (e.g., 'Shooting Day 1', 'Shooting Day 2') are situated directly beneath the 'Footage' folder.
- 📁 Production
  - 📁 Footage
    - 📁 Shooting Day 1
      - 📁 A001_0210Z9
      - 📁 B001_029AC3
    - 📁 Shooting Day 2
      - 📁 A002_0210Z9

  
In our workflow,We place the Proxy folder alongside the Footage folder,feel free to put it wherever you like
- 📁 Production
  - 📁 Proxy
  - 📁 Footage
    - 📁 Shooting Day 1
      - 📁 A001_0210Z9
      - 📁 B001_029AC3
    - 📁 Shooting Day 2
      - 📁 A002_0210Z9


### Example
Please ensure that no project titled 'Proxy' exists within the DaVinci Resolve Project Manager.

Upon invocation of this script, the terminal prompts the user to provide the paths for the footage folder and the proxy folder.
 <img width="682" alt="Screenshot 2023-07-18 at 22 15 33" src="https://github.com/UserProjekt/DaVinci_Script_Proxy_generator/assets/78477492/4abd475c-1fa2-42a0-baf9-8ebd42a5e136">


After the paths are inputted, DaVinci Resolve initiates the process of importing video files, categorizing Clips and creating timelines based on aspect ratios. Subsequently, the script re-establishes the date-based folder structure within the Proxy folder, This then serves as the target location for the ensuing transcoding.
<img width="1556" alt="Screenshot 2023-07-18 at 23 16 58" src="https://github.com/UserProjekt/DaVinci_Script_Proxy_generator/assets/78477492/fcf8034d-01ec-423a-8b07-626cc620eb6c">

If DaVinci Resolve crash during the rendering process, you can resume the unfinished jobs by reopening the 'Proxy' Project and restart the rendering. Because the script makes sure to save the project before it starts the automatic rendering.
