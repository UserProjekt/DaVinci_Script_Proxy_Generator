# DaVinci_Script_Proxy_Generator

This script, written in Python for DaVinci Resolve, automates the process of importing video footage and generating proxies. It categorizes the footage based on the video aspect ratio, then transcodes it to an approximate resolution of 1920x1080 using a custom DaVinci Resolve render preset titled 'FHD_h.265_420_8bit_5Mbps'. 

This preset is configured for Full High Definition (FHD) video with H.265 encoding, 4:2:0 chroma subsampling, 8-bit color depth, and a video bitrate of 5Mbps. These settings are optimized for hardware decoding and systems with low I/O performance. Reduced file size is also better for transfer and storage.

Ensure you have a render preset named 'FHD_h.265_420_8bit_5Mbps'. Alternatively, you can create your own preset and update its name in Proxy_generator.py on line 290:

      
      Project.LoadRenderPreset('FHD_h.265_420_8bit_5Mbps')
      

The script automatically applies source clip name and source timecode overlay burn-ins to the generated proxies by default. This feature uses a custom data burn-in preset titled 'Burn-in' and can be disabled manually if needed.

Ensure you have a data burn-in preset named 'Burn-in'. Alternatively, you can create your own preset and update its name in Proxy_generator.py on line 191:
  
    
      Project.LoadBurnInPreset("burn-in")
    

## Prerequisites
Python >= 3.6 64-bit  
DaVinci Resolve >= 18.6.5


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

For DaVinci Resolve installed via the Apple App Store:

    RESOLVE_SCRIPT_API="/Applications/DaVinci Resolve Studio.app/Contents/Resources/Developer/Scripting"
    RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve Studio.app/Contents/Libraries/Fusion/fusionscript.so"
    PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"


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


## Examples

**Important:** Ensure no project named 'Proxy' exists in the DaVinci Resolve Project Manager before running the script.

The script supports two modes:

1. **Direct Mode:** Generate proxies directly from footage folders with automatic bin organization
2. **JSON Mode:** Re-generate missing proxies based on file comparison results from a JSON file

The script automatically creates organized bin structures in DaVinci Resolve that mirror your folder hierarchy, imports footage, and configures proxy paths. Your folder structure is preserved up to the specified subfolder level.

**Positional arguments:**
- `args` - Positional arguments for default mode

**Optional arguments:**
- `-h, --help` - Show help message and exit
- `-j JSON, --json JSON` - Path to JSON file from file_compare (JSON mode)
- `-f FOOTAGE, --footage FOOTAGE` - Footage folder path (Direct mode)
- `-p PROXY, --proxy PROXY` - Proxy folder path
- `-l LEVEL, --level LEVEL` - Subfolder levels to recreate (default: 1)
- `-d {1,2}, --dataset {1,2}` - Select dataset for JSON mode:1 for files_only_in_group1, 2 for files_only_in_group2 (JSON mode only)

**Direct Mode (using positional arguments):**
```bash
proxy_generator.py /path/to/footage /path/to/proxy          # Direct mode, level=1 (default)
proxy_generator.py /path/to/footage /path/to/proxy 1        # Direct mode, level=1
proxy_generator.py /path/to/footage /path/to/proxy 2        # Direct mode, level=2
```

**Direct Mode (using flags):**
```bash
proxy_generator.py -f /path/to/footage -p /path/to/proxy -l 2 # Direct mode, level=2
```

**JSON Mode (using positional arguments):**
```bash
proxy_generator.py comparison.json 1 /path/to/proxy         # JSON mode, dataset=1, level=1
proxy_generator.py comparison.json 1 /path/to/proxy 1       # JSON mode, dataset=1, level=1
proxy_generator.py comparison.json 2 /path/to/proxy 2       # JSON mode, dataset=2, level=2
```

**JSON Mode (using flags):**
```bash
proxy_generator.py -j comparison.json -d 1 -p /path/to/proxy -l 2 # JSON mode, dataset=1, level=2
```

### Recovery from Crashes

If DaVinci Resolve crashes during rendering, you can resume unfinished jobs by:
1. Reopening the 'Proxy' project in DaVinci Resolve
2. Restarting the rendering process

The script automatically saves the project before starting the rendering process, ensuring your progress is preserved.


## Update

### New in v1.1.0:
- JSON input support

### New in v1.2.0:
- Burn-in preset support

### New in v1.2.1:
- Correct resolution handling for DCI 4K & 2K footage

