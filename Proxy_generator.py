#!/usr/bin/env python3
"""
DaVinci Script Proxy Generator
Automates proxy generation for DaVinci Resolve
"""

__version__ = "1.2.4"
__author__ = 'userprojekt'


import DaVinciResolveScript as dvr_script
resolve = dvr_script.scriptapp("Resolve")
import os
import sys
import argparse
import json

def counter():
    i = 0
    while True:
        i += 1
        yield i

c = counter()

def clean_path_input(path):
    # Replace escaped spaces
    path = path.replace("\\ ", " ")
    # Replace escaped hash symbols
    path = path.replace("\\#", "#")
    # Remove quotes around the path (if any)
    path = path.strip('" ').strip()
    return path

def get_parent_folders_at_levels(file_paths):
    """Extract unique parent folders at different levels from file paths"""
    level_folders = {}  # level -> set of folders
    max_depth = 0
    
    for file_path in file_paths:
        parts = file_path.split(os.sep)
        # Skip empty parts and the filename
        parts = [p for p in parts[:-1] if p]  
        max_depth = max(max_depth, len(parts))
        
        # Build paths at each level
        for i in range(len(parts)):
            level = i + 1
            if level not in level_folders:
                level_folders[level] = set()
            
            # Reconstruct path up to this level
            if os.sep == '/':  # Unix-like
                folder_path = '/' + os.path.join(*parts[:level])
            else:  # Windows
                folder_path = os.path.join(*parts[:level])
            
            level_folders[level].add((folder_path, parts[i]))
    
    return level_folders, max_depth

def select_footage_folder_level(level_folders):
    """Let user select which level represents the footage folder"""
    print("\nSelect footage folder level:")
    
    # Show examples from each level
    for level in sorted(level_folders.keys()):
        folders = list(level_folders[level])
        print(f"\nLevel {level}:")
        # Show up to 3 examples
        for i, (path, name) in enumerate(folders[:3]):
            print(f"  Example: {name} (full path: {path})")
        if len(folders) > 3:
            print(f"  ... and {len(folders) - 3} more folders")
    
    while True:
        try:
            level = int(input("\nEnter Footage folder level number: "))
            if level in level_folders:
                return level
            else:
                print(f"Invalid level. Please choose from: {sorted(level_folders.keys())}")
        except ValueError:
            print("Please enter a valid number.")

def select_subfolder_depth(footage_level, max_depth, file_paths):
    """Let user select how many subfolder levels to recreate in Media Pool"""
    print(f"\nYou selected footage folder at level {footage_level}")
    
    # Find example path to show structure
    example_file = file_paths[0]
    parts = [p for p in example_file.split(os.sep) if p]
    
    print("\nExample file structure:")
    for i in range(min(footage_level - 1, len(parts))):
        print(f"  {'  ' * i}└─ {parts[i]}")
    
    print(f"  {'  ' * (footage_level - 1)}└─ {parts[footage_level - 1]} ← Your footage folder")
    
    # Show available subfolder levels
    available_levels = []
    for i in range(footage_level, min(max_depth, len(parts))):
        print(f"  {'  ' * footage_level}{'  ' * (i - footage_level)}└─ {parts[i]} ← Level {i - footage_level + 1} subfolder")
        available_levels.append(i - footage_level + 1)
    
    if not available_levels:
        print("\nNo subfolders available. Will import directly into footage folder.")
        return 0
    
    print(f"\nHow many subfolder levels to recreate? (0-{max(available_levels)})")
    print("0 = Import directly into footage folder (output to proxy folder directly)")
    print("1 = Recreate first level subfolders (output to proxy/date/)")
    print("2 = Recreate two levels of subfolders (output to proxy/date/cam/)")
    print("\nNOTE: This will be used for both Media Pool structure AND output path!")
    
    while True:
        try:
            depth = int(input("\nEnter number of subfolder levels: "))
            if 0 <= depth <= max(available_levels):
                return depth
            else:
                print(f"Please enter a number between 0 and {max(available_levels)}")
        except ValueError:
            print("Please enter a valid number.")

def organize_files_by_structure(file_paths, footage_level, subfolder_depth):
    """Organize files by the selected folder structure"""
    organized_files = {}  # footage_folder_path -> subfolder_path -> list of files
    
    for file_path in file_paths:
        parts = file_path.split(os.sep)
        parts_clean = [p for p in parts if p]
        
        # Check if file is deep enough
        if len(parts_clean) <= footage_level - 1:
            continue
        
        # Reconstruct footage folder path
        if os.sep == '/':  # Unix-like
            footage_path = '/' + os.path.join(*parts_clean[:footage_level])
        else:  # Windows
            footage_path = os.path.join(*parts_clean[:footage_level])
        
        # Get subfolder path based on depth
        if subfolder_depth == 0:
            subfolder_key = ""  # No subfolders
        else:
            # Get the subfolder parts
            subfolder_parts = parts_clean[footage_level:footage_level + subfolder_depth]
            subfolder_key = os.sep.join(subfolder_parts) if subfolder_parts else ""
        
        if footage_path not in organized_files:
            organized_files[footage_path] = {}
        if subfolder_key not in organized_files[footage_path]:
            organized_files[footage_path][subfolder_key] = []
        
        organized_files[footage_path][subfolder_key].append(file_path)
    
    return organized_files

def select_footage_folders(organized_files):
    """Let user select which footage folders to process"""
    footage_list = sorted(organized_files.keys())
    
    print("\nAvailable footage folders:")
    for i, folder in enumerate(footage_list, 1):
        folder_name = os.path.basename(folder)
        total_files = sum(len(files) for files in organized_files[folder].values())
        subfolders = [sf for sf in organized_files[folder].keys() if sf]
        print(f"{i}. {folder_name} ({total_files} files in {len(organized_files[folder])} groups)")
        if subfolders:
            print(f"     Subfolders: {', '.join(subfolders[:3])}{'...' if len(subfolders) > 3 else ''}")
    
    selected = []
    print("\nEnter footage folder numbers to process (comma-separated, or 'all' for all folders):")
    choice = input().strip()
    
    if choice.lower() == 'all':
        return footage_list
    
    try:
        indices = [int(x.strip()) - 1 for x in choice.split(',')]
        selected = [footage_list[i] for i in indices if 0 <= i < len(footage_list)]
        return selected
    except:
        print("Invalid selection. Please try again.")
        return select_footage_folders(organized_files)

def process_files_in_resolve(organized_files, selected_footage_folders, proxy_folder_path, subfolder_depth, is_directory_mode=False, clean_image=False):
    """Process files in DaVinci Resolve"""
    # Create project with appropriate name based on mode
    ProjectManager = resolve.GetProjectManager()
    project_name = "proxy" if is_directory_mode else "proxy_redo"
    Project = ProjectManager.CreateProject(project_name)
    MediaStorage = resolve.GetMediaStorage()
    MediaPool = Project.GetMediaPool()
    RootFolder = MediaPool.GetRootFolder()
    
    # Only load burn-in preset if not in clean mode
    if not clean_image:
        Project.LoadBurnInPreset("burn-in")

    # Process each selected footage folder
    for footage_folder_path in selected_footage_folders:
        footage_folder_name = os.path.basename(footage_folder_path)
        subfolders_dict = organized_files[footage_folder_path]
        
        print(f"\nProcessing footage folder: {footage_folder_name}")
        
        # Create main folder in Media Pool
        main_folder = MediaPool.AddSubFolder(RootFolder, footage_folder_name)
        
        # Process each subfolder group
        for subfolder_path, items in sorted(subfolders_dict.items()):
            if subfolder_path:
                print(f"  Processing subfolder: {subfolder_path} ({len(items)} items)")
                
                # Split subfolder path for navigation
                subfolder_parts = subfolder_path.split(os.sep)
                
                # Create nested folder structure in Media Pool
                current_folder = main_folder
                for part in subfolder_parts:
                    # Check if subfolder exists
                    existing_folders = current_folder.GetSubFolderList()
                    existing_names = [f.GetName() for f in existing_folders]
                    
                    if part not in existing_names:
                        current_folder = MediaPool.AddSubFolder(current_folder, part)
                    else:
                        current_folder = next(f for f in existing_folders if f.GetName() == part)
                
                working_folder = current_folder
            else:
                print(f"  Processing items directly in footage folder ({len(items)} items)")
                working_folder = main_folder
                subfolder_parts = []
            
            # Import items (could be files or folders)
            try:
                # Filter to only existing items
                items_to_import = [item for item in items if os.path.exists(item)]
                
                if not items_to_import:
                    print(f"    No existing items found")
                    continue
                
                # Import items (files or folders - DaVinci will handle appropriately)
                uncat_clips = MediaStorage.AddItemListToMediaPool(items_to_import)
                
                if not uncat_clips:
                    print(f"    Failed to import items")
                    continue
                
                # Create resolution-based subfolders
                for uncat_clip in uncat_clips:
                    resolution = uncat_clip.GetClipProperty("Resolution")
                    clip_type = uncat_clip.GetClipProperty("Type")
                    
                    if clip_type != "Still":
                        resolution_folder_list = working_folder.GetSubFolderList()
                        resolution_folder_names = [f.GetName() for f in resolution_folder_list]
                        
                        if resolution not in resolution_folder_names:
                            resolution_folder = MediaPool.AddSubFolder(working_folder, resolution)
                        else:
                            resolution_folder = next(f for f in resolution_folder_list if f.GetName() == resolution)
                        
                        # Move clip to resolution folder
                        MediaPool.MoveClips([uncat_clip], resolution_folder)
                        MediaPool.SetCurrentFolder(working_folder)
                
                # Create timelines for each resolution
                resolution_folder_list = working_folder.GetSubFolderList()
                for resolution_folder in resolution_folder_list:
                    clips = resolution_folder.GetClipList()
                    if not clips:
                        continue
                    
                    resolution_folder_name = resolution_folder.GetName()
                    timeline_name = f"Video Resolution {resolution_folder_name}   #{next(c)}"
                    timeline = MediaPool.CreateTimelineFromClips(timeline_name, clips)
                    
                    # Set render settings
                    width, height = resolution_folder_name.split("x")
                    int_w = int(width)
                    int_h = int(height)
                    aspect = int_w / int_h
                    proxy_height = "1080"
                    int_proxy_width = round(int(proxy_height) * aspect)
                    if int_proxy_width % 2 == 1:
                        int_proxy_width += 1
                    proxy_width = str(int_proxy_width)
                    
                    timeline.SetSetting("useCustomSettings", "1")
                    timeline.SetSetting("timelineResolutionWidth", proxy_width)
                    timeline.SetSetting("timelineResolutionHeight", proxy_height)
                    
                    # Load render preset
                    Project.LoadRenderPreset('FHD_h.265_420_8bit_5Mbps')
                    
                    # Build target directory using the same subfolder structure
                    if subfolder_parts:
                        target_dir = os.path.join(proxy_folder_path, *subfolder_parts)
                    else:
                        target_dir = proxy_folder_path
                    
                    print(f"    Render target: {target_dir}")
                    
                    Project.SetRenderSettings({
                        "SelectAllFrames": True,
                        "FormatWidth": int(proxy_width),
                        "FormatHeight": int(proxy_height),
                        "TargetDir": target_dir,
                    })
                    
                    # Add render job
                    Project.AddRenderJob()
                    
            except Exception as e:
                print(f"    Error processing items: {e}")
                continue
    
    # Save project
    ProjectManager.SaveProject()
    
    # Ask if user wants to start rendering
    print("\nAll render jobs added. Start rendering now? (y/n)")
    if input().strip().lower() == 'y':
        Project.StartRendering()
        print("Rendering started...")
    else:
        print("Project saved. You can start rendering manually in DaVinci Resolve.")

def process_json_mode(json_path, proxy_path, dataset, level=None, clean_image=False):
    """Process using JSON file"""
    # Read JSON file
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            comparison_data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        sys.exit(1)
    
    # Get the selected file list
    if dataset == 1:
        file_list = comparison_data.get('files_only_in_group1', [])
    else:
        file_list = comparison_data.get('files_only_in_group2', [])
    
    if not file_list:
        print(f"No files found in group{dataset}")
        sys.exit(1)
    
    print(f"Found {len(file_list)} files in group{dataset}")
    
    # Get folders at different levels
    level_folders, max_depth = get_parent_folders_at_levels(file_list)
    
    # Let user select footage folder level
    footage_level = select_footage_folder_level(level_folders)
    
    # Use provided level or let user select subfolder depth
    if level is not None:
        subfolder_depth = level
        print(f"\nUsing specified subfolder depth: {subfolder_depth}")
    else:
        subfolder_depth = select_subfolder_depth(footage_level, max_depth, file_list)
    
    # Show configuration summary
    print("\n=== Configuration Summary ===")
    print(f"JSON file: {json_path}")
    print(f"Dataset: group{dataset}")
    print(f"Footage folder level: {footage_level}")
    print(f"Subfolder depth: {subfolder_depth}")
    if subfolder_depth == 0:
        print("Media Pool: Files imported directly into footage folder")
        print("Output path: Directly to proxy folder")
    else:
        print(f"Media Pool: {subfolder_depth} level(s) of subfolders will be recreated")
        print(f"Output path: Same {subfolder_depth} level(s) will be used in proxy folder")
    
    # Organize files by the selected structure
    organized_files = organize_files_by_structure(file_list, footage_level, subfolder_depth)
    
    # Let user select which footage folders to process
    selected_footage_folders = select_footage_folders(organized_files)
    
    if not selected_footage_folders:
        print("No footage folders selected.")
        sys.exit(1)
    
    # Process in Resolve
    process_files_in_resolve(organized_files, selected_footage_folders, proxy_path, subfolder_depth, is_directory_mode=False, clean_image=clean_image)

def process_directory_mode(footage_path, proxy_path, level, clean_image=False):
    """Process footage folder directly without JSON"""
    if not os.path.exists(footage_path):
        print(f"Error: Footage folder does not exist: {footage_path}")
        sys.exit(1)
    
    print(f"\nDirectory mode:")
    print(f"Footage folder: {footage_path}")
    print(f"Proxy folder: {proxy_path}")
    print(f"Subfolder levels: {level}")
    
    # Create a simple organized structure
    organized_files = {footage_path: {}}
    
    if level == 0:
        # Import the footage folder directly
        organized_files[footage_path][""] = [footage_path]
    else:
        # Get immediate subdirectories for level 1
        if level == 1:
            # Get immediate subdirectories only
            for item in os.listdir(footage_path):
                item_path = os.path.join(footage_path, item)
                if os.path.isdir(item_path):
                    # Each immediate subfolder becomes its own group
                    organized_files[footage_path][item] = [item_path]
        else:
            # For level > 1, walk through subdirectories
            for root, dirs, files in os.walk(footage_path):
                rel_path = os.path.relpath(root, footage_path)
                
                # Skip the root folder itself
                if rel_path == '.':
                    continue
                    
                path_parts = rel_path.split(os.sep)
                
                # Process directories at the specified level
                if len(path_parts) == level:
                    # Use parent folders as the key
                    subfolder_key = os.sep.join(path_parts[:-1]) if len(path_parts) > 1 else ""
                    if subfolder_key not in organized_files[footage_path]:
                        organized_files[footage_path][subfolder_key] = []
                    organized_files[footage_path][subfolder_key].append(root)
    
    # Debug print to see what we're importing
    print("\nFolders to import:")
    for key, folders in organized_files[footage_path].items():
        print(f"  Group '{key}': {folders}")
    
    # Process all folders
    process_files_in_resolve(organized_files, [footage_path], proxy_path, level, is_directory_mode=True, clean_image=clean_image)

def is_json_file(path):
    """Check if the path is likely a JSON file"""
    return path.lower().endswith('.json') or (os.path.isfile(path) and not os.path.isdir(path))

def main():
    parser = argparse.ArgumentParser(
        description='''DaVinci Resolve Proxy Generator

This script supports two modes:
1. Directory Mode: Generate proxies for footage folders with automatic bin organization
2. JSON Mode: Re-generate missing proxies based on file comparison results

The script creates organized bin structures in DaVinci Resolve based on your folder hierarchy,
imports footage, and sets up proxy paths automatically. It preserves your folder structure
up to the specified subfolder level.''',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Examples:
  Directory mode (positional arguments):
    %(prog)s /path/to/footage /path/to/proxy                   # Directory mode, level=1 (default)
    %(prog)s /path/to/footage /path/to/proxy 1                 # Directory mode, level=1
    %(prog)s /path/to/footage /path/to/proxy 2                 # Directory mode, level=2
    %(prog)s /path/to/footage /path/to/proxy 2 -c              # Directory mode, level=2, clean image (no burn-in)

  Directory Mode (using flags):
    %(prog)s -f /path/to/footage -p /path/to/proxy -l 1        # Directory mode, level=1
    %(prog)s -f /path/to/footage -p /path/to/proxy -l 2 -c     # Directory mode, level=2, clean image (no burn-in)

  JSON mode (positional arguments):
    %(prog)s comparison.json 1 /path/to/proxy                  # JSON mode, dataset=1, level=1 (default)
    %(prog)s comparison.json 1 /path/to/proxy 1                # JSON mode, dataset=1, level=1
    %(prog)s comparison.json 2 /path/to/proxy 2                # JSON mode, dataset=2, level=2

  JSON mode (using flags):
    %(prog)s -j comparison.json -d 1 -p /path/to/proxy -l 2    # JSON mode, dataset=1, level=2
    %(prog)s -j comparison.json -d 1 -p /path/to/proxy -l 2 -c # JSON mode, dataset=1, level=2, clean image (no burn-in)
'''
    )
    
    # Create mutually exclusive group for the two modes
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('-j', '--json', help='Path to JSON file from file_compare (JSON mode)')
    mode_group.add_argument('-f', '--footage', help='Footage folder path (Direct mode)')
    
    # Other arguments
    parser.add_argument('-p', '--proxy', help='Proxy folder path')
    parser.add_argument('-l', '--level', type=int, help='Subfolder levels to recreate')
    parser.add_argument('-d', '--dataset', type=int, choices=[1, 2], 
                        help='Select dataset: 1 for files_only_in_group1, 2 for files_only_in_group2 (JSON mode only)')
    parser.add_argument('-c', '--clean-image', action='store_true', 
                    help='Generate clean proxies without burn-in overlays')
    
    # Handle positional arguments for default mode
    parser.add_argument('args', nargs='*', help='Positional arguments for default mode')
    
    args = parser.parse_args()
    
    # Determine which mode we're in
    if args.json:
        # JSON mode with flags
        if not args.proxy:
            parser.error("JSON mode requires -p/--proxy")
        
        json_path = args.json
        proxy_path = clean_path_input(args.proxy)
        dataset = args.dataset if args.dataset else 1  # Default to 1
        level = args.level  # Can be None
        
        # Process JSON mode
        process_json_mode(json_path, proxy_path, dataset, level, args.clean_image)
        
    elif args.footage:
        # Directory mode with flags
        if not args.proxy:
            parser.error("Directory mode requires -p/--proxy")
        
        footage_path = clean_path_input(args.footage)
        proxy_path = clean_path_input(args.proxy)
        level = args.level if args.level is not None else 1  # Default to 1
        
        # Process directory mode
        process_directory_mode(footage_path, proxy_path, level, args.clean_image)
        
    elif len(args.args) >= 2:
        # Default mode - need to determine if first arg is JSON or footage folder
        first_arg = clean_path_input(args.args[0])
        
        if is_json_file(first_arg):
            # JSON mode: json_file dataset proxy [level]
            if len(args.args) < 3:
                parser.error("JSON mode requires: json_file dataset proxy_folder [level]")
            
            json_path = first_arg
            try:
                dataset = int(args.args[1])
                if dataset not in [1, 2]:
                    parser.error("Dataset must be 1 or 2")
            except ValueError:
                parser.error("Dataset must be 1 or 2")
            
            proxy_path = clean_path_input(args.args[2])
            
            # Optional level
            level = None
            if len(args.args) >= 4:
                try:
                    level = int(args.args[3])
                except ValueError:
                    parser.error("Level must be a number")
            
            # Process JSON mode
            process_json_mode(json_path, proxy_path, dataset, level, False)  # Default to False for positional
            
        else:
            # Directory mode: footage_folder proxy_folder [level]
            footage_path = first_arg
            proxy_path = clean_path_input(args.args[1])
            
            # Optional level, default to 1
            level = 1
            if len(args.args) >= 3:
                try:
                    level = int(args.args[2])
                except ValueError:
                    parser.error("Level must be a number")
            
            # Process directory mode
            process_directory_mode(footage_path, proxy_path, level, False)  # Default to False for positional
            
    else:
        parser.error("Usage:\n"
                    "  JSON mode:      script.py -j json_file -d dataset -p proxy_folder [-l level]\n"
                    "  Directory mode: script.py -f footage_folder -p proxy_folder [-l level]\n"
                    "  Default:        script.py json_file dataset proxy_folder [level]\n"
                    "                  script.py footage_folder proxy_folder [level]")

if __name__ == "__main__":
    main()