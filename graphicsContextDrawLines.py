# Adapted from WxPython Demo.
# I plan to use this file to overexplain things so that I can quickly glance over it
# to relearn wxPython and GraphicsContext basics as necessary in the future.
# (wxPython's DC or device context objects draw raster graphics, GraphicsContext objects
#  draw using primitives via vector graphics and can be antialiased)

import wx, colorsys
from math import cos, sin, radians

assertMode = wx.PYAPP_ASSERT_DIALOG # assert statements pop up in dialog boxes

# Constants:
BASE  = 80.0    # sizes used in shapes drawn below (appear to be pixels?)
BASE2 = BASE/2
BASE4 = BASE/4
USE_BUFFER = ('wxMSW' in wx.PlatformInfo) # use buffered drawing on Windows

class RunDemoApp(wx.App):  # A wx.App does the work of setting up wxPython and some basic windowing stuff.
                           # It is the object that "has" everything else: panels, frames, etc.
    def __init__(self):
        wx.App.__init__(self) #redirect=False

    def OnInit(self):
        self.SetAssertMode(assertMode) # see variable definition

        frame = wx.Frame(None, -1, "Drawing Stuff", pos=(50,50), size=(200,100),
                        style=wx.DEFAULT_FRAME_STYLE, name="insignificant")
        """From wxWidgets documentation:
            A frame is a window whose size and position can (usually) be changed by the user. It usually has 
            thick borders and a title bar, and can optionally contain a menu bar, toolbar and status bar. A 
            frame can contain any window that is not a frame or dialog. A frame that has a status bar and toolbar, 
            created via the CreateStatusBar() and CreateToolBar() functions, manages these windows and adjusts 
            the value returned by GetClientSize() to reflect the remaining size available to application windows.
            Remarks:
                An application should normally define an wxCloseEvent handler for the frame to respond to 
                system close events, for example so that related data and subwindows can be cleaned up."""

        menuBar = wx.MenuBar() # Pretty self explanatory.
        
        menu = wx.Menu()
        # From wxWidgets documentation:
        # A menu is a popup (or pull down) list of items, one of which may be selected before the menu goes away 
        # (clicking elsewhere dismisses the menu). Menus may be used to construct either menu bars or popup menus.
        
        item = menu.Append(-1, "E&xit\tCtrl-Q", "Exit demo") # Adding items to a menu
        
        self.Bind(wx.EVT_MENU, self.OnExitApp, item) # Binding an event to a method and a menu item
        # Some details on event binding can be found at http://wiki.wxpython.org/self.Bind%20vs.%20self.button.Bind
        
        menuBar.Append(menu, "&File")

        frame.SetMenuBar(menuBar)
        frame.Show(True)
        #frame.Bind(wx.EVT_CLOSE, self.OnCloseFrame) 
        # wx.EVT_CLOSE is what happens when you try to close something, useful if you want to
        # throw a dialog box for confirmation or do something first. I got rid of the OnCloseFrame function.
        # To do something when an even happens and then let it continue to do it's thing, use event.Skip()

        win = TestPanel(frame) # Our TestPanel class, which derives from wx.Panel
        # A panel is a window on which controls are placed. It is usually placed within a frame (wxWidgets documentation).

        frame.SetSize((280, 240)) # Self-explanatory
        
        win.SetFocus() # Sets the focus to this window, allowing it to receive keyboard input (wxWidgets documentation).
        
        self.window = win   # It's helpful if these things are "owned" by their parent so that 
                            # they can be accessed in its other methods. See self.frame below.
        
        frect = frame.GetRect() # Returns the rectangle that the sizer item should occupy (wxWidgets documentation).

        self.SetTopWindow(frame) # Relatively self-explanatory.
        
        self.frame = frame

        return True

    def OnExitApp(self, evt):
        self.frame.Close(True)
    
# end class RunDemoApp

class TestPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1) # create the panel
        self.Bind(wx.EVT_PAINT, self.OnPaint) # Things get repainted often, such as when windows are resized
        if USE_BUFFER:
            self.Bind(wx.EVT_SIZE, self.OnSize) # When we get resized, do some shit.

    def OnSize(self, evt):
        self.InitBuffer() # set up the buffer (see below)
        evt.Skip() # let everyone else handle the resize event, too!
        
    def OnPaint(self, evt):
        if USE_BUFFER:
            # The buffer already contains our drawing, so no need to
            # do anything else but create the buffered DC.  When this
            # method exits and dc is collected then the buffer will be
            # blitted to the paint DC automagically
            dc = wx.BufferedPaintDC(self, self._buffer)
        else:
            # Otherwise we need to draw our content to the paint DC at
            # this time.
            dc = wx.PaintDC(self) # Creates a PaintDC, these are used for paint events
            gc = wx.GraphicsContext.Create(dc) # Make a GraphicsContext from the DC (device context)
            self.Draw(gc)  # Draw all our shit (see below)

    def InitBuffer(self):
        sz = self.GetClientSize()
        # Returns the size of the window 'client area' in pixels. The client area is the area 
        # which may be drawn on by the programmer, excluding title bar, border, scrollbars, etc
        
        sz.width = max(1, sz.width)
        sz.height = max(1, sz.height)
        # These can be set, we are making sure they are at least 1
        
        self._buffer = wx.EmptyBitmap(sz.width, sz.height, 32) # Create empty bitmap for initialization

        dc = wx.MemoryDC(self._buffer) # Create a MemoryDC and initialize it with the empty bitmap
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        # SetBackground: Sets the current background brush for the DC.
        # wx.Brush: A brush is a drawing tool for filling in areas. It is used for painting the background 
        #           of rectangles, ellipses, etc. when drawing on a wx.DC. It has a colour and a style.
        # GetBackGroundColour: Returns the background colour of the window. (this could vary by window & platform)
        # All info from wxWidgets reference.
        
        dc.Clear() # Clears the device context using the current background brush (from wxWidgets reference).
        gc = wx.GraphicsContext.Create(dc) # Make a GraphicsContext from the DC (device context)
        self.Draw(gc)  # Draw all our shit (see below)
        
    def Draw(self, gc):  # All the interesting drawing stuff.
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.BOLD)
        gc.SetFont(font)
        # All pretty self-explanatory

        gc.PushState()             # save current translation/scale/other state ("state" refers to the transformation matrix)

        gc.SetPen(wx.Pen("navy", 1)) # Pens are for drawing line-type things, and have a color, width and style.
        gc.SetBrush(wx.Brush("pink")) # Brushes are for filling areas, explained above, have color and style.

        # My section    
        gc.Translate(BASE, BASE)  # move basis of relative coordinates ("Translates the current transformation matrix. ")
        # The transformation matrix maps a Cartesian coordinate input to the screen through some method involving possible
        # translations, rotations, and scalings. By translating it, we move our reference point around the screen.
        
        somePoints = [(-BASE2,BASE2),(BASE2,BASE2),(BASE2,-BASE2),(-BASE2,-BASE2),(-BASE2,BASE2)]
        w, h = gc.GetTextExtent("Draw some lines")
        gc.DrawText("Draw some lines", -w/2, -BASE2-h-4)
        gc.StrokeLines(somePoints) # draw lines from a list of points
        # /My section
        
        gc.PopState()  # restore state/transformation matrix
        
    # end def Draw
# end class TestPanel

if __name__ == '__main__':
    app = RunDemoApp()
    app.MainLoop()