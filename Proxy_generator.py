#!/usr/bin/env python3
"""
DaVinci Script Proxy Generator
Automates proxy generation for DaVinci Resolve
"""

__version__ = "1.3.2"
__author__ = 'userprojekt'


import DaVinciResolveScript as dvr_script
resolve = dvr_script.scriptapp("Resolve")
import os
import sys
import argparse
import json
from datetime import datetime

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

def organize_files_by_structure(file_paths, in_depth, out_depth):
    """Organize files based on input/output depth ranges"""
    organized_files = {}
    
    for file_path in file_paths:
        # Split path into parts
        parts = file_path.split(os.sep)
        parts_clean = [p for p in parts if p]
        
        # Skip files that don't have enough depth
        if len(parts_clean) <= in_depth:
            continue
        
        # Extract the key path (what we'll use as the main folder)
        # This is at in_depth level
        if os.sep == '/':  # Unix-like
            key_path = '/' + os.path.join(*parts_clean[:in_depth])
        else:  # Windows
            key_path = os.path.join(*parts_clean[:in_depth])
        
        # Extract subfolder structure between in_depth and out_depth
        if out_depth > in_depth:
            subfolder_parts = parts_clean[in_depth:out_depth]
            subfolder_key = os.sep.join(subfolder_parts) if subfolder_parts else ""
        else:
            subfolder_key = ""
        
        # Initialize structure
        if key_path not in organized_files:
            organized_files[key_path] = {}
        if subfolder_key not in organized_files[key_path]:
            organized_files[key_path][subfolder_key] = []
        
        organized_files[key_path][subfolder_key].append(file_path)
    
    return organized_files

def filter_folders_at_in_depth(organized_files, in_depth, filter_mode=None, filter_list=None):
    """Filter organized files based on folder selection at input depth"""
    
    if not filter_mode:
        return organized_files
    
    # Build a mapping of folder names to full paths
    folder_map = {}
    for key_path in organized_files.keys():
        folder_name = os.path.basename(key_path.rstrip(os.sep))
        folder_map[folder_name] = key_path
    
    if filter_mode == 'select':
        # Interactive selection
        print(f"\nFolders available at depth {in_depth}:")
        folder_list = sorted(folder_map.keys())
        
        # Show folder list with file counts
        for i, folder in enumerate(folder_list, 1):
            full_path = folder_map[folder]
            file_count = sum(len(files) for files in organized_files[full_path].values())
            print(f"{i}. {folder} ({file_count} files)")
        
        print("\nSelect folders to process:")
        print("Enter numbers (comma-separated), range (e.g., 2-4), or 'all':")
        choice = input().strip()
        
        if choice.lower() == 'all':
            return organized_files
        
        selected_indices = parse_selection(choice, len(folder_list))
        selected_folders = [folder_list[i] for i in selected_indices]
        
        # Filter the organized_files dict
        filtered = {}
        for folder_name in selected_folders:
            if folder_name in folder_map:
                full_path = folder_map[folder_name]
                filtered[full_path] = organized_files[full_path]
        
        return filtered
    
    elif filter_mode == 'filter' and filter_list:
        # Similar logic for filter mode...
        filter_names = [f.strip() for f in filter_list.split(',')]
        
        filtered = {}
        for folder_name in filter_names:
            if folder_name in folder_map:
                full_path = folder_map[folder_name]
                filtered[full_path] = organized_files[full_path]
        
        if not filtered:
            print(f"Warning: No matching folders found for filter: {filter_list}")
            print(f"Available folders: {', '.join(sorted(folder_map.keys()))}")
        else:
            print(f"Filtering to folders: {', '.join(filter_names)}")
        
        return filtered
    
    return organized_files

def parse_selection(choice, max_num):
    """Parse user selection like '1,3,5-7' into list of indices"""
    indices = []
    parts = choice.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            # Range like "2-4"
            try:
                start, end = part.split('-')
                start_idx = int(start) - 1
                end_idx = int(end) - 1
                indices.extend(range(start_idx, end_idx + 1))
            except:
                continue
        else:
            # Single number
            try:
                idx = int(part) - 1
                if 0 <= idx < max_num:
                    indices.append(idx)
            except:
                continue
    
    return sorted(set(indices))  # Remove duplicates and sort

def process_files_in_resolve(organized_files, selected_footage_folders, proxy_folder_path, subfolder_depth, is_directory_mode=False, clean_image=False):
    """Process files in DaVinci Resolve"""
    # Create project with appropriate name based on mode
    ProjectManager = resolve.GetProjectManager()

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create project name with timestamp
    base_name = "proxy" if is_directory_mode else "proxy_redo"
    project_name = f"{base_name}_{timestamp}"

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
                    footage_folder_name = os.path.basename(footage_folder_path)
                    if subfolder_parts:
                        target_dir = os.path.join(proxy_folder_path, footage_folder_name, *subfolder_parts)
                    else:
                        target_dir = os.path.join(proxy_folder_path, footage_folder_name)
                    
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

def process_json_mode(json_path, proxy_path, dataset, in_depth, out_depth, 
                      clean_image=False, filter_mode=None, filter_list=None):
    """Process using JSON file with input/output depth and folder filtering"""

    # Read JSON file
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            comparison_data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        sys.exit(1)
    
    # Validate dataset parameter
    if dataset not in [1, 2]:
        print(f"Error: Invalid dataset value '{dataset}'. Must be 1 or 2.")
        sys.exit(1)
    
    # Get the selected file list
    if dataset == 1:
        file_list = comparison_data.get('files_only_in_group1', [])
        # Add frame mismatch files from group 1 if they exist
        if 'frame_count_mismatches' in comparison_data:
            mismatch_files = [mismatch['path1'] for mismatch in comparison_data['frame_count_mismatches']]
            file_list.extend(mismatch_files)
            print(f"Added {len(mismatch_files)} files from frame count mismatches (group 1)")
    else:  # dataset == 2
        file_list = comparison_data.get('files_only_in_group2', [])
        # Add frame mismatch files from group 2 if they exist
        if 'frame_count_mismatches' in comparison_data:
            mismatch_files = [mismatch['path2'] for mismatch in comparison_data['frame_count_mismatches']]
            file_list.extend(mismatch_files)
            print(f"Added {len(mismatch_files)} files from frame count mismatches (group 2)")
    
    if not file_list:
        print(f"No files found in group{dataset}")
        sys.exit(1)
    
    print(f"Found {len(file_list)} files in group{dataset}")
    
    # Show configuration
    print("\n=== Configuration Summary ===")
    print(f"JSON file: {json_path}")
    print(f"Dataset: group{dataset}")
    print(f"Input depth: {in_depth} (start from level {in_depth})")
    print(f"Output depth: {out_depth} (include up to level {out_depth})")
    
    # Show example of what will be included
    if file_list:
        example = file_list[0]
        parts = [p for p in example.split(os.sep) if p]
        print(f"\nExample file: {example}")
        print(f"Will extract: {os.sep.join(parts[in_depth-1:out_depth])}")
    
    # Organize files
    organized_files = organize_files_by_structure(file_list, in_depth, out_depth)
    
    # Apply folder filtering if requested
    organized_files = filter_folders_at_in_depth(
        organized_files, in_depth, filter_mode, filter_list
    )
    
    if not organized_files:
        print("No folders to process after filtering.")
        sys.exit(1)
    
    # Process filtered folders
    selected_folders = list(organized_files.keys())
    subfolder_depth = out_depth - in_depth
    
    process_files_in_resolve(organized_files, selected_folders, proxy_path, 
                            subfolder_depth, is_directory_mode=False, clean_image=clean_image)

def process_directory_mode(footage_path, proxy_path, in_depth, out_depth, 
                          clean_image=False, filter_mode=None, filter_list=None):
    """Process footage folder with absolute input/output depths"""

    if not os.path.exists(footage_path):
        print(f"Error: Footage folder does not exist: {footage_path}")
        sys.exit(1)
    
    # Calculate the depth of the footage folder itself
    footage_parts = [p for p in footage_path.split(os.sep) if p]
    footage_depth = len(footage_parts)
    
    print(f"\nDirectory mode:")
    print(f"Footage folder: {footage_path} (depth: {footage_depth})")
    print(f"Proxy folder: {proxy_path}")
    print(f"Input depth: {in_depth} (absolute)")
    print(f"Output depth: {out_depth} (absolute)")
    
    # First, find all folders at the input depth level within the footage tree
    input_depth_folders = []
    for root, dirs, files in os.walk(footage_path):
        # Calculate absolute depth of current folder
        root_parts = [p for p in root.split(os.sep) if p]
        current_depth = len(root_parts)
        
        # Collect folders at exactly in_depth
        if current_depth == in_depth:
            input_depth_folders.append(root)
        
        # Don't go deeper than necessary
        if current_depth >= in_depth:
            dirs.clear()
    
    if not input_depth_folders:
        print(f"No folders found at depth {in_depth} within the footage tree")
        sys.exit(1)
    
    print(f"Found {len(input_depth_folders)} folders at depth {in_depth}")
    
    # Now for each input folder, find all folders at output depth OR max depth if less
    target_folders_by_input = {}
    folder_max_depths = {}
    
    for input_folder in input_depth_folders:
        target_folders = []
        max_depth_found = in_depth
        
        # Walk through this input folder to find folders at output depth or max depth
        for root, dirs, files in os.walk(input_folder):
            root_parts = [p for p in root.split(os.sep) if p]
            current_depth = len(root_parts)
            
            # Track the maximum depth found for this input folder
            if current_depth > max_depth_found:
                max_depth_found = current_depth
            
            # Collect folders at exactly out_depth
            if current_depth == out_depth:
                target_folders.append(root)
                dirs.clear()  # Don't go deeper
            elif current_depth > out_depth:
                dirs.clear()  # Don't go deeper than output depth
        
        # If no folders found at output depth, use folders at max depth found
        if not target_folders and max_depth_found < out_depth:
            # Re-walk to get folders at max depth
            for root, dirs, files in os.walk(input_folder):
                root_parts = [p for p in root.split(os.sep) if p]
                current_depth = len(root_parts)
                
                if current_depth == max_depth_found:
                    target_folders.append(root)
        
        # Store the results
        if target_folders:
            target_folders_by_input[input_folder] = target_folders
            folder_max_depths[input_folder] = max_depth_found
        else:
            # If input folder has no subfolders, include itself
            target_folders_by_input[input_folder] = [input_folder]
            folder_max_depths[input_folder] = in_depth
    
    # Apply filtering at input depth level
    if filter_mode == 'select':
        print(f"\nFolders available at depth {in_depth}:")
        folder_names = []
        folder_paths = []
        
        for input_folder, targets in target_folders_by_input.items():
            folder_name = os.path.basename(input_folder)
            actual_depth = folder_max_depths[input_folder]
            depth_info = f" (max depth: {actual_depth})" if actual_depth < out_depth else ""
            folder_names.append(f"{folder_name}{depth_info}")
            folder_paths.append(input_folder)
        
        for i, folder_name in enumerate(folder_names, 1):
            target_count = len(target_folders_by_input[folder_paths[i-1]])
            print(f"{i}. {folder_name} - {target_count} folders")
        
        print("\nSelect folders to process:")
        print("Enter numbers (comma-separated), range (e.g., 2-4), or 'all':")
        choice = input().strip()
        
        if choice.lower() != 'all':
            selected_indices = parse_selection(choice, len(folder_paths))
            selected_paths = [folder_paths[i] for i in selected_indices]
            
            # Filter the results
            filtered = {}
            for path in selected_paths:
                if path in target_folders_by_input:
                    filtered[path] = target_folders_by_input[path]
            target_folders_by_input = filtered
    
    elif filter_mode == 'filter' and filter_list:
        filter_names = [f.strip() for f in filter_list.split(',')]
        filtered = {}
        
        for input_folder, targets in target_folders_by_input.items():
            folder_name = os.path.basename(input_folder)
            if folder_name in filter_names:
                filtered[input_folder] = targets
        
        if not filtered:
            print(f"Warning: No matching folders found for filter: {filter_list}")
            available = [os.path.basename(f) for f in target_folders_by_input.keys()]
            print(f"Available folders: {', '.join(available)}")
            sys.exit(1)
        
        target_folders_by_input = filtered
    
    if not target_folders_by_input:
        print("No folders to process after filtering.")
        sys.exit(1)
    
    # Flatten all target folders for processing
    all_target_folders = []
    for targets in target_folders_by_input.values():
        all_target_folders.extend(targets)
    
    print(f"\nTotal folders to process: {len(all_target_folders)}")
    
    # Organize for processing
    organized_files = organize_files_by_structure(all_target_folders, in_depth, out_depth)
    
    if not organized_files:
        # Fallback for simple case
        organized_files = {footage_path: {"": all_target_folders}}
    
    # Process filtered folders
    selected_folders = list(organized_files.keys())
    subfolder_depth = out_depth - in_depth
    
    process_files_in_resolve(organized_files, selected_folders, proxy_path, subfolder_depth,
                            is_directory_mode=True, clean_image=clean_image)

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
  Directory mode:
    %(prog)s -f /volume/Production/Footage/ -p /path/to/proxy -i 4 -o 4   # Include depth 4 
    %(prog)s -f /volume/Production/Footage/ -p /path/to/proxy -i 4 -o 5   # Include depth 4-5
    
  JSON mode:
    %(prog)s -j comparison.json -d 1 -p /path/to/proxy -i 4 -o 4          # Include depth 4

  Interactive selection of Shooting day folders
    %(prog)s -f /volume/Production/Footage/ -p /proxy -i 4 -o 5 --select  # Include depth 4-5, selecting from depth 4
    # Will show:
    # 1. Shooting_Day_1 (150 files)
    # 2. Shooting_Day_2  (200 files)
    # 3. Shooting_Day_3  (180 files)
    # 4. Shooting_Day_4  (220 files)
    # 5. Shooting_Day_5  (190 files)
    # Enter: 2-4  (to select Shooting_Day_2, Shooting_Day_3, Shooting_Day_3)       # Selected Shooting day

  Direct filtering
    %(prog)s -f /volume/Production/Footage/ -p /proxy -i 4 -o 5 --filter "Shooting_Day_2,Shooting_Day_3"  # Specific Date
'''
    )
    
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('-f', '--footage', help='Footage folder path (Direct mode)')
    mode_group.add_argument('-j', '--json', help='Path to JSON file from file_compare (JSON mode)')
    parser.add_argument('-d', '--dataset', type=int, choices=[1, 2], 
                        help='Select dataset: 1 for files_only_in_group1, 2 for files_only_in_group2 (JSON mode only)')
    parser.add_argument('-p', '--proxy', help='Proxy folder path')
    parser.add_argument('-i', '--in-depth', type=int, default=4,
                       help='Directory depth to start from (default: 4, typically Shooting day folder)')
    parser.add_argument('-o', '--out-depth', type=int, default=4,
                       help='Directory depth to include up to (default: 4, typically Shooting day folder)')

    # Add folder selection options
    selection_group = parser.add_mutually_exclusive_group()
    selection_group.add_argument('--select', action='store_true',
                                help='Interactively select which folders to process at input depth')
    selection_group.add_argument('--filter', type=str,
                                help='Comma-separated list of folder names to process (e.g., "Shooting_Day_2,Shooting_Day_3,Shooting_Day_4")')
    
    # Add a switch for turn off burn-in
    parser.add_argument('-c', '--clean-image', action='store_true', 
                    help='Generate clean proxies without burn-in overlays')
    
    # Handle positional arguments for backward compatibility
    parser.add_argument('args', nargs='*', help='Positional arguments for default mode')

    args = parser.parse_args()

    if args.json:
        # JSON mode with flags
        if not args.proxy:
            parser.error("JSON mode requires -p/--proxy")
        
        json_path = args.json
        proxy_path = clean_path_input(args.proxy)
        dataset = args.dataset if args.dataset else 1
        in_depth = args.in_depth
        out_depth = args.out_depth
        
        # Validate depths
        if out_depth < in_depth:
            parser.error("Output depth must be >= input depth")
        
        # Determine filter mode
        filter_mode = None
        filter_list = None
        if args.select:
            filter_mode = 'select'
        elif args.filter:
            filter_mode = 'filter'
            filter_list = args.filter
        
        # Process JSON mode with filtering
        process_json_mode(json_path, proxy_path, dataset, in_depth, out_depth, 
                         args.clean_image, filter_mode, filter_list)

    elif args.footage:
        # Directory mode with flags
        if not args.proxy:
            parser.error("Directory mode requires -p/--proxy")
        
        footage_path = clean_path_input(args.footage)
        proxy_path = clean_path_input(args.proxy)
        in_depth = args.in_depth
        out_depth = args.out_depth
        
        # Validate depths
        if out_depth < in_depth:
            parser.error("Output depth must be >= input depth")

        # Determine filter mode
        filter_mode = None
        filter_list = None
        if args.select:
            filter_mode = 'select'
        elif args.filter:
            filter_mode = 'filter'
            filter_list = args.filter
        
        # Process directory mode with filtering
        process_directory_mode(footage_path, proxy_path, in_depth, out_depth, 
                             args.clean_image, filter_mode, filter_list)

    elif len(args.args) >= 2:
        # Positional arguments mode (backward compatibility)
        footage_path = clean_path_input(args.args[0])
        proxy_path = clean_path_input(args.args[1])
        in_depth = args.in_depth
        out_depth = args.out_depth
        
        # Validate depths
        if out_depth < in_depth:
            parser.error("Output depth must be >= input depth")
        
        # Determine filter mode
        filter_mode = None
        filter_list = None
        if args.select:
            filter_mode = 'select'
        elif args.filter:
            filter_mode = 'filter'
            filter_list = args.filter

        # Check if first arg is JSON file
        if is_json_file(footage_path):
            # JSON mode
            dataset = args.dataset if args.dataset else 1
            process_json_mode(footage_path, proxy_path, dataset, in_depth, out_depth,
                            args.clean_image, filter_mode, filter_list)
        else:
            # Directory mode
            process_directory_mode(footage_path, proxy_path, in_depth, out_depth,
                                 args.clean_image, filter_mode, filter_list)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()