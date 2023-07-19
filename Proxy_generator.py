#!/usr/bin/env python3

import DaVinciResolveScript as dvr_script
resolve = dvr_script.scriptapp("Resolve")
import os
def counter():
    i = 0
    while True:
        i += 1
        yield i

c = counter()

#create a Proxy project
ProjectManager = resolve.GetProjectManager()
Project = ProjectManager.CreateProject("Proxy")
MediaStorage = resolve.GetMediaStorage()
MediaPool = Project.GetMediaPool()
RootFolder = MediaPool.GetRootFolder()
DateFolderlist = RootFolder.GetSubFolderList()

#create folder base on date import videofiles
FootageFolderPath = input('"Footage"Dir:')
ProxyFolderPath = input('"Proxy"Dir:')
DateFolderPathList = MediaStorage.GetSubFolderList(FootageFolderPath)
DateFolderNameList = [DateFolderPath.split('/')[-1] for DateFolderPath in DateFolderPathList]
for DateFolderName, DateFolderPath in zip(DateFolderNameList, DateFolderPathList):
	DateFolder = MediaPool.AddSubFolder(RootFolder, DateFolderName)
	ResolutionFolderlist = DateFolder.GetSubFolderList()
	Uncat_Clips = MediaStorage.AddItemListToMediaPool(DateFolderPath)
	#create folder base on resolution
	for Uncat_Clip in Uncat_Clips:
		Resolution = Uncat_Clip.GetClipProperty("Resolution")
		Type = Uncat_Clip.GetClipProperty("Type")
		if Type != "Still":
			ResolutionFolderlist = DateFolder.GetSubFolderList()
			ReasolutionFolderNameList = [FolderObject.GetName() for FolderObject in ResolutionFolderlist]
			if Resolution not in ReasolutionFolderNameList:
				ResolutionFolder = MediaPool.AddSubFolder(DateFolder, Resolution) 
				#move videofiles to ResolutionFolder
				Uncat_Cliplist = [Uncat_Clip]
				MediaPool.MoveClips(Uncat_Cliplist, ResolutionFolder)
				MediaPool.SetCurrentFolder(DateFolder) 
			else:
				#To obtain the existing folder object
				ResolutionFolder = [ResolutionFolder_exist for ResolutionFolder_exist in ResolutionFolderlist if ResolutionFolder_exist.GetName() == Resolution][0]
				#move videofiles to ResolutionFolder
				Uncat_Cliplist = [Uncat_Clip]
				MediaPool.MoveClips(Uncat_Cliplist, ResolutionFolder)
				MediaPool.SetCurrentFolder(DateFolder)

	#create timelines base on resolution folder
	for ResolutionFolder in ResolutionFolderlist:
		Clips = ResolutionFolder.GetClipList()
		ResolutionFolderName = ResolutionFolder.GetName()
		TimelineName = "Video Resolution " + ResolutionFolderName + "   #" + str(next(c))
		Timeline = MediaPool.CreateTimelineFromClips(TimelineName, Clips) 
		#set render settings
		Width,Height = ResolutionFolderName.split("x")
		intW = int(Width)
		intH = int(Height)
		Aspect = intH / intW
		Proxy_Width = "1920"
		intProxy_Height = round(int(Proxy_Width)*Aspect)
		Proxy_Height = str(intProxy_Height)
		Timeline.SetSetting("useCustomSettings", "1")
		Timeline.SetSetting("timelineResolutionWidth", Proxy_Width)
		Timeline.SetSetting("timelineResolutionHeight", Proxy_Height)
		#chose DaVinci Resolve render Preset
		Project.LoadRenderPreset('FHD_h.265_420_8bit_5Mbps')
		TargetDir = os.path.join(ProxyFolderPath, DateFolderName)
		Project.SetRenderSettings({
		"SelectAllFrames": True,
		"TargetDir":str(ProxyFolderPath),
		"FormatWidth":int(Proxy_Width),
		"FormatHeight":int(Proxy_Height),
		"TargetDir":TargetDir
		})
		#add render job
		Project.AddRenderJob()

#save project
ProjectManager.SaveProject()


#start rendering
Project.StartRendering()
