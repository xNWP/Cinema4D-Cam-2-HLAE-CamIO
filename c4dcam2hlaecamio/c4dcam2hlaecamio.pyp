"""		ID LAYOUT

0 - Primary UI
	50 - Header Image
	100 - Group (Program Information)
		101 - Version info
		102 - Description
		103 - Author
		104 - Website
	200 - Group (File Info)
		201 - No Frames
		202 - Framerate
		203 - Time in secs
	300 - Group (Export Options)
		300 - Group (Mode Group)
			300 - Mode Text
			301 - Mode
				302 - -Z Up (Maps)
				303 - +Y Up (default CamIO Import)
		325 - Group (buttons)
			326 - Export btn
			327 - Close btn

"""

# Imports
import c4d
from c4d import plugins
from c4d import documents
from c4d import gui
from c4d import storage

import math

# Global Vars
PLUGIN_VERSION = "v1.0"
PLUGIN_VERSION_FLOAT = 1.0
PLUGIN_NAME = "Cinema4D Camera 2 HLAE CamIO " + PLUGIN_VERSION
PLUGIN_DESCRIPTION = "Converts Cinema4D Camera Data to HLAE CamIO Camera Data."
PLUGIN_ID = 1039644  # Registered Plugin ID
PLUGIN_WEBPAGE = "http://github.com/xNWP"

def DoWork(MODE):
	
	c4d.StopAllThreads()
	
	# Select File Name/Loc
	filepath = storage.SaveDialog(c4d.FILESELECTTYPE_ANYTHING, "Save HLAE CamIO File... (*.cam)", force_suffix="cam")
	if(filepath == None): # catch cancel
		return False
	
	# Vars
	CurrentProj = documents.GetActiveDocument()
	FPS = CurrentProj.GetFps()
	LengthInSec = (CurrentProj.GetMaxTime() - CurrentProj.GetMinTime())
	StartFrame = (CurrentProj.GetMinTime()).GetFrame(FPS)
	NumberOfFrames = LengthInSec.GetFrame(FPS)
	LengthInSec = LengthInSec.Get()
	CAMERA = CurrentProj.GetActiveObject()
	
	# Console
	print "%s: Starting export with following settings." % (PLUGIN_NAME)
	print "~~ Camera: %s" % (CAMERA.GetName())
	print "~~ File: %s" % (filepath)
	print "~~ Frames: %s" % (NumberOfFrames)
	print "~~ Framerate: %s" % (FPS)
	print "~~ Length(s): %s" % (LengthInSec)
	
	# Init lists
	RawData = [None]*NumberOfFrames
	RawDataFov = [None]*NumberOfFrames
	
	# Define Rotation Matrix
	if(MODE == -1): # -Z Up (Rotate -90 P)
		off = c4d.Vector(0,0,0)
		v1 = c4d.Vector(1, 0, 0)
		v2 = c4d.Vector(0, 0, 1)
		v3 = c4d.Vector(0, -1, 0)
		RotMat = c4d.Matrix(off, v1, v2, v3)
	else:
		RotMat = c4d.Matrix() # Identity Matrix
	
	# Read every frame into a matrix
	i = 0
	for frame in RawData:
		c4d.StatusSetText("HLAE CamIO Export: Frame %s of %s" % (i, NumberOfFrames))
		c4d.StatusSetBar((i + 1.0) / NumberOfFrames * 100)
		CurrentProj.SetTime(c4d.BaseTime(StartFrame, FPS))
		CurrentProj.ExecutePasses(None, True, True, True, c4d.BUILDFLAGS_0)
		mat = RotMat * CAMERA.GetMg()
		RawData[i] = mat
		RawDataFov[i] = math.degrees(CAMERA[c4d.CAMERAOBJECT_FOV])
		i = i + 1
		StartFrame = StartFrame + 1
	
	c4d.StatusClear()
	c4d.StatusSetSpin()
	c4d.StatusSetText("HLAE CamIO Export: Writing File...")
	
	# Decompose the Matrix into the position's and rotations
	PosVec = []
	RotVec = []
	for frame in RawData:
		PosVec.append(frame.off)
		RadRotVec = c4d.utils.MatrixToHPB(frame)
		h = math.degrees(RadRotVec.x)
		p = math.degrees(RadRotVec.y)
		b = math.degrees(RadRotVec.z)
		tmpVec = c4d.Vector(h, p, b)
		RotVec.append(tmpVec)
		
		# Round Frames to 6 Digits	
	for index in range(NumberOfFrames):
		PosVec[index].x = round(PosVec[index].x, 6)
		PosVec[index].y = round(PosVec[index].y, 6)
		PosVec[index].z = round(PosVec[index].z, 6)
		RotVec[index].x = round(RotVec[index].x, 6)
		RotVec[index].y = round(RotVec[index].y, 6)
		RotVec[index].z = round(RotVec[index].z, 6)
		RawDataFov[index] = round(RawDataFov[index], 6)
	
	# Write The Data To The File
	file = open(filepath, "w")
	
	# Write our headers
	file.write("advancedfx Cam\n")
	file.write("version 1\n")
	file.write("scaleFov alienSwarm\n")
	file.write("channels time xPosition yPosition zPositon xRotation yRotation zRotation fov\n")
	file.write("DATA\n")
	
	# Write Frames to File
	for index in range(NumberOfFrames):
		
		if(MODE == -2): # +Y Up
			file.write(
		'%6f'%(index/float(FPS)) + " "
		+ '%6f'%(PosVec[index].z) + " "
		+ '%6f'%(-1*(PosVec[index].x)) + " "
		+ '%6f'%(PosVec[index].y) + " "
		+ '%6f'%(RotVec[index].z) + " "
		+ '%6f'%(-1*(RotVec[index].y)) + " "
		+ '%6f'%(RotVec[index].x) + " "
		+ '%6f'%(RawDataFov[index]) + "\n")
		
		if(MODE == -1): # -Z Up
			file.write(
		'%6f'%(index/float(FPS)) + " "
		+ '%6f'%(PosVec[index].x) + " "
		+ '%6f'%(PosVec[index].z) + " "
		+ '%6f'%(PosVec[index].y) + " "
		+ '%6f'%(RotVec[index].z) + " "
		+ '%6f'%(-1*(RotVec[index].y)) + " "
		+ '%6f'%(RotVec[index].x + 90) + " "
		+ '%6f'%(RawDataFov[index]) + "\n")
	
	file.close()
	c4d.StatusClear()
	
	gui.MessageDialog("Successfully exported %s frames to '%s'." % (NumberOfFrames, filepath))
	return True

# Banner Definition
class Banner(gui.GeUserArea):
	def GetMinSize(self):
		self.width = 350
		self.height = 100
		return (self.width, self.height)
	
	def DrawMsg(self, x1, y1, x2, y2, msg):
		bmp = c4d.bitmaps.BaseBitmap()
		path = __file__
		path = path.replace("c4dcam2hlaecamio.pyp", "") # remove plugin name
		path += "res\\banner.png"
		bmp.InitWith(path)
		
		self.DrawBitmap(bmp, 0, 0, bmp.GetBw(), bmp.GetBh(), 0, 0, bmp.GetBw(), bmp.GetBh(), c4d.BMP_NORMALSCALED)
	
	
# UI Definition
class PrimaryUI(gui.GeDialog):

	# BANNER
	TopBanner = Banner()

	# Layout Design
	def CreateLayout(self):
		CurrentProj = documents.GetActiveDocument()
		camera = CurrentProj.GetActiveObject()
		FPS = CurrentProj.GetFps()
		LengthInSec = (CurrentProj.GetMaxTime() - CurrentProj.GetMinTime())
		NumberOfFrames = LengthInSec.GetFrame(FPS)
		LengthInSec = LengthInSec.Get()
		
		# BANNER
		self.AddUserArea(50, c4d.BFH_CENTER, 350, 100)
		self.AttachUserArea(self.TopBanner, 50)
		self.TopBanner.LayoutChanged()
		self.TopBanner.Redraw()
	
		self.SetTitle(PLUGIN_NAME)
	
		self.GroupBegin(100, c4d.BFH_SCALE, 1, 4) # PROGRAM INFO GROUP
		
		self.AddStaticText(101, c4d.BFH_RIGHT, 0, 0, PLUGIN_VERSION)
		self.AddStaticText(102, c4d.BFH_CENTER, 0, 0, PLUGIN_DESCRIPTION)
		self.AddStaticText(103, c4d.BFH_CENTER, 0, 0, "Plugin by xNWP")
		self.AddStaticText(104, c4d.BFH_CENTER, 0, 0, PLUGIN_WEBPAGE)
		
		self.GroupEnd()
		
		self.AddStaticText(0, c4d.BFH_CENTER, 0, 3) # spacer
		self.AddSeparatorH(300, c4d.BFH_CENTER)
		self.AddStaticText(0, c4d.BFH_CENTER, 0, 3) # spacer
		
		self.GroupBegin(200, c4d.BFH_CENTER, 2, 3)
		self.GroupBorderNoTitle(c4d.BORDER_THIN_IN)
		self.GroupBorderSpace(20, 5, 20, 5)
		
		self.AddStaticText(201, c4d.BFH_RIGHT, 250, 0, "Number of Frames ->")
		self.AddStaticText(201, c4d.BFH_LEFT, 0, 0, NumberOfFrames)
		self.AddStaticText(202, c4d.BFH_RIGHT, 178, 0, "Framerate ->")
		self.AddStaticText(202, c4d.BFH_LEFT, 0, 0, FPS)
		self.AddStaticText(203, c4d.BFH_RIGHT, 250, 0, "Length in seconds ->")
		self.AddStaticText(203, c4d.BFH_LEFT, 0, 0, round(LengthInSec, 4))
		
		self.GroupEnd()
		
		self.AddStaticText(0, c4d.BFH_CENTER, 0, 4) # spacer
		
		self.GroupBegin(300, c4d.BFH_SCALE, 1, 3) # Mode and Buttons
		
		self.GroupBegin(300, c4d.BFH_SCALE, 2, 1) # Mode Combo & Text
		
		self.AddStaticText(300, c4d.BFH_CENTER, 0, 0, "Mode:")
		self.AddComboBox(301, c4d.BFH_CENTER, initw=300)
		self.AddChild(301, 302, "-Z Up (Most 3D Maps)")
		self.AddChild(301, 303, "+Y Up (Default CamIO Import Setting)")
		self.SetLong(301, 302)
		
		self.GroupEnd()
		
		self.AddStaticText(0, c4d.BFH_CENTER, 0, 4) # spacer
		
		self.GroupBegin(325, c4d.BFH_SCALE, 2, 1)
		
		self.AddButton(326, c4d.BFH_LEFT, 80, 16, "Export")
		self.AddButton(327, c4d.BFH_RIGHT, 80, 16, "Close")
		
		self.GroupEnd()
		self.GroupEnd()
		
		return True
	
	# USER CONTROL SECTION
	def Command(self, id, msg):
		
		if(id == 327): # Close Btn
			self.Close()
			return True
		
		if(id == 326): # Export Btn			
			if(self.GetLong(301) == 302): # -Z Up
				Mode = -1
			else:
				Mode = -2 # +Y Up
			
			if(DoWork(Mode)):
				self.Close()
				return True
			
			return False
		
		return True
		

# Plugin Definition
class C4DCam2HLAECamIO(plugins.CommandData):
	
	def Execute(self, BaseDocument):
	# defines what happens when the user clicks the plugin in the menu
		CurrentProj = documents.GetActiveDocument()
		obj = CurrentProj.GetActiveObject()
		
		if(type(obj) != c4d.CameraObject):
			print "%s: Bad Object Type." % (PLUGIN_NAME)
			gui.MessageDialog("Please select a Camera to export first.")
			return False
		else:		
			UI = PrimaryUI(gui.GeDialog)
			UI.Open(c4d.DLG_TYPE_MODAL, PLUGIN_ID, -1, -1, 400, 360, 0) # open ui		
		
		return True

# Main Definition
def main():
	# Icon
	icon = c4d.bitmaps.BaseBitmap()
	iconpath = __file__
	iconpath = iconpath.replace("c4dcam2hlaecamio.pyp", "") # remove plugin name
	iconpath += "res\\icon.png"
	icon.InitWith(iconpath)

	# Register the plugin
	plugins.RegisterCommandPlugin(PLUGIN_ID, PLUGIN_NAME, 0, icon, PLUGIN_DESCRIPTION, C4DCam2HLAECamIO())
	
	# Console confirmation
	print "Loaded %s" % (PLUGIN_NAME)

# Main Execution
main()