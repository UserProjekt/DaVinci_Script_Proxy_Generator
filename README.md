# DaVinci_Script_Proxy_Generator

This script, written in Python for DaVinci Resolve, automates the process of importing video footage and generating proxies. It categorizes the footage based on the video aspect ratio, then transcodes it to an approximate resolution of 1920x1080 using a custom DaVinci Resolve render preset titled 'FHD_h.265_420_8bit_5Mbps'. 

This preset is configured for Full High Definition (FHD) video with H.265 encoding, 4:2:0 chroma subsampling, 8-bit color depth, and a video bitrate of 5Mbps. These settings are optimized for hardware decoding and systems with low I/O performance. Reduced file size is also better for transfer and storage.

Ensure you have a preset named 'FHD_h.265_420_8bit_5Mbps'. Alternatively, you can create your own preset and update its name in Proxy_generator.py on line 98:

	
  		Project.LoadRenderPreset('FHD_h.265_420_8bit_5Mbps')
    
## Prerequisites
The Python version requirements for DaVinci Resolve depend on the version of the software you are using. This is because older versions of DaVinci Resolve rely on the `imp` module for importing Python modules, which is [removed](https://docs.python.org/3.11/library/imp.html) in Python 3.12. To address this, starting from version 18.6.5, DaVinci Resolve has switched to using the `importlib` module instead.

Here are the specific Python version requirements based on your DaVinci Resolve version:

1. If your DaVinci Resolve version is 18.6.5 or higher:
   - Your Python version should be greater than or equal to 3.6 (Python >= 3.6).

2. If you are using an older version of DaVinci Resolve (lower than 18.6.5):
   - Your Python version should be between 3.6 and 3.11, inclusive (3.6 <= Python <= 3.11).
   - Older versions of DaVinci Resolve are not compatible with Python versions higher than 3.11 due to the deprecation of the `imp` module.

To summarize:

	- For DaVinci Resolve version 18.6.5 and above: Python >= 3.6
	- For DaVinci Resolve versions below 18.6.5: 3.6 <= Python <= 3.11


## Using a script
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



## Folder Structure
**The industray standard footage folder structure is outlined below. Please ensure that the date-specific folders (e.g., 'Shooting Day 1', 'Shooting Day 2') are situated directly beneath the 'Footage' folder.**
- 📁 Production
  - 📁 Footage
    - 📁 Shooting Day 1
      - 📁 A001_0210Z9
      - 📁 B001_029AC3
    - 📁 Shooting Day 2
      - 📁 A002_0210Z9

  
In our workflow,We place the Proxy folder alongside the Footage folder, feel free to put it wherever you like
- 📁 Production
  - 📁 Proxy
  - 📁 Footage
    - 📁 Shooting Day 1
      - 📁 A001_0210Z9
      - 📁 B001_029AC3
    - 📁 Shooting Day 2
      - 📁 A002_0210Z9


## Example
**Please ensure that no project titled 'Proxy' exists within the DaVinci Resolve Project Manager.**

Upon running of this script, the terminal prompts the user to provide the paths for the footage folder and the proxy folder.
<img width="682" alt="Screenshot 2023-07-31 at 04 23 59" src="https://github.com/UserProjekt/DaVinci_Script_Proxy_Generator/assets/78477492/9172c6b3-3171-43cf-8c2a-88c082de7ac8">


After the paths are inputted, DaVinci Resolve initiates the process of importing video files, categorizing Clips and creating timelines based on aspect ratios. Subsequently, the script recreate the date-based folder structure within the Proxy folder, This then serves as the target location for the ensuing transcoding.
<img width="1556" alt="Screenshot 2023-07-18 at 23 16 58" src="https://github.com/UserProjekt/DaVinci_Script_Proxy_generator/assets/78477492/fcf8034d-01ec-423a-8b07-626cc620eb6c">

If DaVinci Resolve crashes during the rendering process, you can resume the unfinished jobs by reopening the 'Proxy' Project and restarting the rendering. Because the script makes sure to save the project before it starts the automatic rendering.

You can disable automatic rendering by commenting out the last line of Proxy_generator.py.
