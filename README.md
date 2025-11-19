# DaVinci_Script_Proxy_Generator

This script, written in Python for DaVinci Resolve, automates the process of importing video footage and generating proxies. It categorizes the footage based on the video aspect ratio, then transcodes it to an approximate resolution of 1920x1080 using custom DaVinci Resolve render presets. 

This preset is configured for Full High Definition (FHD) video with H.265 encoding, 4:2:0 chroma subsampling, 8-bit color depth, and a video bitrate of 5Mbps. These settings are optimized for hardware decoding and systems with low I/O performance. Reduced file size is also better for transfer and storage.

Due to an issue of Adobe Premiere, which cannot use hardware decoding for 4:2:0 8-bit H.265 with 8 audio tracks (Sony XAVC-I codec), this script automatically selects the codec based on the number of audio channels in the video file:

      
      audio channels > 4 → ProRes Proxy
      audio channels ≤ 4 → 4:2:0 8-bit H.265
       

Ensure you have a davinci render preset named 'FHD_h.265_420_8bit_5Mbps' and 'FHD_prores_proxy'. Alternatively, you can create your own preset and update its name in Proxy_generator.py on line 372 and line 396.

The script automatically applies source clip name and source timecode overlay burn-ins to the generated proxies by default. This feature uses a custom data burn-in preset titled 'Burn-in' and can be disabled manually if needed.

Ensure you have a data burn-in preset named 'Burn-in'. Alternatively, you can create your own preset and update its name in Proxy_generator.py on line 215.    

## Prerequisites
Python >= 3.6 64-bit  
DaVinci Resolve >= 19.1.4


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
**The industray standard footage folder structure is outlined below. Please ensure that the date-specific folders (e.g., 'Shooting_Day_1', 'Shooting_Day_2') are situated directly beneath the 'Footage' folder.**
- 📁 Production
  - 📁 Footage
    - 📁 Shooting_Day_1
      - 📁 A001_0210Z9
      - 📁 B001_029AC3
    - 📁 Shooting_Day_2
      - 📁 A002_0210Z9

  
In our workflow,We place the Proxy folder alongside the Footage folder, feel free to put it wherever you like
- 📁 Production
  - 📁 Proxy
  - 📁 Footage
    - 📁 Shooting_Day_1
      - 📁 A001_0210Z9
      - 📁 B001_029AC3
    - 📁 Shooting_Day_2
      - 📁 A002_0210Z9


## Examples

This script supports two modes:
1. **Directory Mode**: Process footage folders within a directory tree with automatic bin organization
2. **JSON Mode**: Re-generate missing or incomplete proxies based on [File_Compare](https://github.com/UserProjekt/File_Compare) results from a JSON file

The script creates organized bin structures in DaVinci Resolve based on your folder hierarchy,
imports footage, and sets up proxy paths automatically. It uses depth-based organization to
preserve your folder structure at specified levels.

**Positional arguments:**
- `args` - Positional arguments for backward compatibility

**Mode selection (mutually exclusive):**
- `-f, --footage FOOTAGE` - Footage folder path (Directory mode)
- `-j, --json JSON` - Path to JSON file containing folder list (JSON mode)

**Required arguments:**
- `-p, --proxy PROXY` - Proxy folder path

**Depth control:**
- `-i, --in-depth IN_DEPTH` - Directory depth to start from (default: 4, typically Shooting day folder)
- `-o, --out-depth OUT_DEPTH` - Directory depth to include up to (default: 4, typically Shooting day folder)

**Folder selection (mutually exclusive):**
- `-s, --select` - Interactively select which folders to process at input depth
- `--filter FILTER` - Comma-separated list of folder names to process

**Optional arguments:**
- `-d, --dataset {1,2}` - Select dataset: 1 for files_only_in_group1, 2 for files_only_in_group2 (JSON mode only)
- `-c, --clean-image` - Generate clean proxies without burn-in overlays
- `-C, --codec {auto,prores,h265,hevc,265}` - Override render preset:
                             'prores' → FHD_prores_proxy
                             'h265/hevc/265' → FHD_h.265_420_8bit_5Mbps
                             default: auto(automatically selects the codec based on the number of audio channels in the video file)
- `-h, --help` - Show help message and exit

**Directory Mode:**
```zsh
# Process single depth level (depth 4 only)
proxy_generator.py -f /volume/Production/Footage/ -p /path/to/proxy -i 4 -o 4

# Process multiple depth levels (depth 4-5)
proxy_generator.py -f /volume/Production/Footage/ -p /path/to/proxy -i 4 -o 5
```

**JSON Mode:**
```zsh
# Process folders listed in JSON file at depth 4
proxy_generator.py -j comparison.json -d 1 -p /path/to/proxy -i 4 -o 4

# Process with unlimited depth
proxy_generator.py -j folders.json -p /path/to/proxy -i 3 -o 0
```

**Interactive Selection:**
```zsh
# Select specific folders interactively
proxy_generator.py -f /volume/Production/Footage/ -p /proxy -i 4 -o 5 --select

# Will display:
# 1. Shooting_Day_1 (150 files)
# 2. Shooting_Day_2 (200 files)
# 3. Shooting_Day_3 (180 files)
# 4. Shooting_Day_4 (220 files)
# 5. Shooting_Day_5 (190 files)
# Enter: 2-4  (selects Shooting_Day_2, Shooting_Day_3, Shooting_Day_4)
```

**Direct Filtering:**
```zsh
# Process specific folders by name
proxy_generator.py -f /volume/Production/Footage/ -p /proxy -i 4 -o 5 --filter "Shooting_Day_2,Shooting_Day_3"
```

**Clean Proxies (without burn-in):**
```zsh
# Generate clean proxies without overlays
proxy_generator.py -f /volume/Production/Footage/ -p /proxy -i 4 -o 5 -c
```

**Backward Compatibility (positional arguments):**
```zsh
# Old format still supported
proxy_generator.py /path/to/footage /path/to/proxy          # Directory mode, depth=4 (default)
proxy_generator.py comparison.json 1 /path/to/proxy         # JSON mode, dataset=1, depth=4
```

### Recovery from Crashes

If DaVinci Resolve crashes during rendering, simply reopen project and restart rendering. The script automatically saves the project before rendering, so your progress is preserved.
