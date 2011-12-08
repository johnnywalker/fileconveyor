from os import dup2, dup
import sys
stdout_bak = dup(sys.stdout.fileno())
stderr_bak = dup(sys.stderr.fileno())

import objc
dup2(stdout_bak, sys.stdout.fileno())
dup2(stderr_bak, sys.stderr.fileno())
from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper
#import ctypes
import os
from os import path
#from os import pipe, fork, dup2, read, close, kill, waitpid, setsid, path
import sys
from shutil import copyfile

FLT_MAX = sys.float_info.max

class FileConveyorApp(NSApplication):
    status = False
    animated = False
    task = None

    def finishLaunching(self):
        # Take care of Bridge Support
        f = open('Foundation.bridgesupport')
        objc.parseBridgeSupport(f.read(), globals(), 'Foundation')
        f.close()

        self.appSupportDir = self.applicationSupportDirectory()

        # Make statusbar item
        statusbar = NSStatusBar.systemStatusBar()
        self.statusitem = statusbar.statusItemWithLength_(NSSquareStatusItemLength)
        self.statusitem.setHighlightMode_(True);
        self.icons = (
            NSImage.alloc().initByReferencingFile_('icons/sync_0.png'),
            NSImage.alloc().initByReferencingFile_('icons/sync_1.png'),
            NSImage.alloc().initByReferencingFile_('icons/sync_2.png'),
            NSImage.alloc().initByReferencingFile_('icons/sync_3.png'),
            NSImage.alloc().initByReferencingFile_('icons/sync_4.png'),
            NSImage.alloc().initByReferencingFile_('icons/sync_5.png'),
            NSImage.alloc().initByReferencingFile_('icons/sync_6.png'),
            NSImage.alloc().initByReferencingFile_('icons/sync_7.png'),
            NSImage.alloc().initByReferencingFile_('icons/sync_8.png'),
            NSImage.alloc().initByReferencingFile_('icons/sync_9.png'),
            NSImage.alloc().initByReferencingFile_('icons/sync_10.png'),
            NSImage.alloc().initByReferencingFile_('icons/sync_11.png'),
            NSImage.alloc().initByReferencingFile_('icons/sync_12.png'),
            )
        for i in self.icons:
            i.setScalesWhenResized_(True)
            i.setSize_((20, 20))
        self.statusitem.setImage_(self.icons[0])

        appIcon = NSImage.alloc().initByReferencingFile_('icons/sync_1.png')
        appIcon.setScalesWhenResized_(True)
        self.setApplicationIconImage_(appIcon)

        #make the menu
        self.menubarMenu = NSMenu.alloc().init()

        self.start = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_( \
            'Start', 'startArbitrator:', '')
        self.menubarMenu.addItem_(self.start)
        self.stop = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_( \
            'Stop', 'stopArbitrator:', '')

        self.showOutput = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_( \
            'Show Output', 'showOutput:', '')
        self.menubarMenu.addItem_(self.showOutput)
        self.hideOutput = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_( \
            'Hide Output', 'hideOutput:', '')
        
        self.quit = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_( \
            'Quit', 'terminateApp:', '')
        self.menubarMenu.addItem_(self.quit)

        #add menu to statusitem
        self.statusitem.setMenu_(self.menubarMenu)
        self.statusitem.setToolTip_('File Conveyor (not running)')

        tc = NSTextContainer.alloc().init()
        ts = NSTextStorage.alloc().init()
        lm = NSLayoutManager.alloc().init()

        #tc.setHeightTracksTextView_(True)
        tc.setWidthTracksTextView_(True)
        ts.addLayoutManager_(lm)
        lm.addTextContainer_(tc)

        self.outputPanel = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_( \
            ((400, 400), (600, 400)), NSTitledWindowMask | NSClosableWindowMask | NSResizableWindowMask,
            NSBackingStoreBuffered, True)
        self.outputPanel.setContentView_(MyView.alloc().initWithWindow_(self.outputPanel))

        self.outputPanel.setReleasedWhenClosed_(False)
        self.outputPanel.setTitle_('File Conveyor Output')
        cv = self.outputPanel.contentView()

        sv = NSScrollView.alloc().initWithFrame_(cv.bounds())
        sv.setHasVerticalScroller_(True)
        sv.setHasHorizontalScroller_(False)
        sv.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)
        sv.setBorderType_(NSNoBorder)
        sv.setAutohidesScrollers_(True)
        self.scrollView = sv
        
        cs = sv.contentSize()
        tc.setContainerSize_(NSMakeSize(cs.width, FLT_MAX))
        tv = NSTextView.alloc().initWithFrame_textContainer_( \
            (NSZeroPoint, cs), tc)
        tv.setMinSize_(NSMakeSize(0, cs.height))
        tv.setMaxSize_(NSMakeSize(FLT_MAX, FLT_MAX))
        tv.setAutoresizingMask_(NSViewWidthSizable)
        tv.setVerticallyResizable_(True)
        tv.setHorizontallyResizable_(False)
        tv.setEditable_(False)
        #tv.setTypingAttributes_(None)
        tv.setTextContainerInset_((8, 12))

        self.textAttrs = NSMutableDictionary.alloc().init()
        self.textAttrs.setObject_forKey_(NSFont.fontWithName_size_('Menlo', 11), NSFontAttributeName)

        sv.setDocumentView_(tv)
        cv.addSubview_(sv)
    
        self.outputPanel.makeFirstResponder_(tv)

        self.outputStorage = ts
        self.outputView = tv
        
    def showOutput_(self, notification):
        self.activateIgnoringOtherApps_(True)
        self.outputPanel.makeKeyAndOrderFront_(self)
        self.menubarMenu.insertItem_atIndex_(self.hideOutput, 1)
        self.menubarMenu.removeItemAtIndex_(2)

    def hideOutput_(self, notification):
        self.outputPanel.close()
        self.menubarMenu.insertItem_atIndex_(self.showOutput, 1)
        self.menubarMenu.removeItemAtIndex_(2)


    def toggleStatus(self):
        if self.status:
            self.statusitem.setToolTip_('File Conveyor (not running)')
            self.statusitem.setImage_(self.icons[0])
            self.menubarMenu.insertItem_atIndex_(self.start, 0)
            self.menubarMenu.removeItemAtIndex_(1)
        else:
            self.statusitem.setToolTip_('File Conveyor (running - pid: %d)' % \
                self.task.processIdentifier())
            self.statusitem.setImage_(self.icons[1])
            self.menubarMenu.insertItem_atIndex_(self.stop, 0)
            self.menubarMenu.removeItemAtIndex_(1)
        self.status ^= True
        self.animated = False

    def toggleAnimation_(self, notification):
        if self.animated:
            if self.timer:
                self.timer.invalidate()
                self.timer = None
                self.statusitem.setImage_(self.icons[1])
        else:
            self.icon_idx = 1
            self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(0.1, self, 'rotateAnimation:', None, True)
        self.animated ^= True

    def rotateAnimation_(self, timer):
        self.icon_idx += 1
        if self.icon_idx == 13:
            self.icon_idx = 1
        self.statusitem.setImage_(self.icons[self.icon_idx])

    def startArbitrator_(self, unused):
        if self.task:
            return

        length = self.outputStorage.length()
        self.outputStorage.beginEditing()
        self.outputStorage.replaceCharactersInRange_withString_( \
            NSMakeRange(0, length), '')
        self.outputStorage.endEditing()
        
        #self.outputPanel.contentView().setNeedsDisplay_(True)
        #self.scrollView.reflectScrolledClipView_(self.scrollView.documentView())
        
        t = NSTask.alloc().init()
        t.setLaunchPath_(sys.executable)
#        python_path = path.abspath(path.join(sys.executable, '../../Resources/lib/python' + sys.version[:3]))
#        t.setEnvironment_(dict(PYTHONPATH='%s:%s/lib-dynload' % (python_path, python_path)))
#        t.setArguments_(['-E', '-S', arbitrator.__file__,])
        t.setArguments_(['-E', '-S', '-c', 'import sys\nsys.path=' + repr(sys.path) + '\n'
            'from fileconveyor.arbitrator import run_file_conveyor\nrun_file_conveyor()\n'])
        p_out = NSPipe.pipe()
        p_in = NSPipe.pipe()
        t.setStandardInput_(p_in)
        t.setStandardOutput_(p_out)
        t.setStandardError_(p_out)
        
        def callback(task):
            self.arbitratorFinished_(task)

        t.setTerminationHandler_(callback)

        dnc = NSDistributedNotificationCenter.defaultCenter()
        dnc.addObserver_selector_name_object_(self, 'arbitratorWorkStarted:',
            'arbitratorWorkStarted', None)
        dnc.addObserver_selector_name_object_(self, 'arbitratorWorkFinished:',
            'arbitratorWorkFinished', None)

        NSThread.detachNewThreadSelector_toTarget_withObject_( \
            'catchArbitratorOutput:', self, p_out)
        
        t.launch()
        self.task = t
        self.toggleStatus()
        self.writeSettingsAndConfig_(p_in)

    def writeSettingsAndConfig_(self, p):
        fh = p.fileHandleForWriting()
        fd = fh.fileDescriptor()
        settings = """
import logging

class Settings(object):
    def __init__(self):
        self.PERSISTENT_DATA_DB = '${APPSUPPORTDIR}/persistent_data.db'
        self.SYNCED_FILES_DB = '${APPSUPPORTDIR}/synced_files.db'
        self.FSMONITOR_DB = '${APPSUPPORTDIR}/fsmonitor.db'
        self.WORKING_DIR = '/tmp/fileconveyor'
        self.MAX_FILES_IN_PIPELINE = 50
        self.MAX_SIMULTANEOUS_PROCESSORCHAINS = 1
        self.MAX_SIMULTANEOUS_TRANSPORTERS = 10
        self.MAX_TRANSPORTER_QUEUE_SIZE = 1
        self.QUEUE_PROCESS_BATCH_SIZE = 20
        self.CALLBACKS_CONSOLE_OUTPUT = False
        self.CONSOLE_LOGGER_LEVEL = logging.WARNING
        self.RETRY_INTERVAL = 30

settings = Settings()

"""
        settings = settings.replace('${APPSUPPORTDIR}', self.appSupportDir)
        os.write(fd, settings)
        os.write(fd, '\0')
        config_file = path.join(self.appSupportDir, 'config.xml')
        if not path.exists(config_file):
            copyfile('config.sample.xml', config_file)
        f_cfg = open(config_file, 'r')
        os.write(fd, f_cfg.read())
        f_cfg.close()
        fh.closeFile()
        del fh

    def stopArbitrator_(self, unused):
        if not self.task:
            return

        self.task.interrupt()

    def arbitratorFinished_(self, task):
        self.task = None
        dnc = NSDistributedNotificationCenter.defaultCenter()
        dnc.removeObserver_name_object_(self, None, None)
        if self.animated:
            self.toggleAnimation_(unused)
        self.toggleStatus()

    def appendStringToOutput_(self, data):
        outputAttributed = NSAttributedString.alloc().initWithString_attributes_( \
            data, self.textAttrs)
        length = self.outputStorage.length()
        self.outputStorage.beginEditing()
        self.outputStorage.appendAttributedString_(outputAttributed)
        self.outputStorage.endEditing()
        new_length = self.outputStorage.length()
        self.outputView.scrollRangeToVisible_(NSMakeRange(new_length, 0))
        self.scrollView.documentView().display()


    def catchArbitratorOutput_(self, pipe):
        if not pipe:
            NSThread.exit()
            return
        fh = pipe.fileHandleForReading()
        fd = fh.fileDescriptor()
        try:
            while True:
                output = os.read(fd, 1024)
                if len(output) == 0:
                    break
                self.performSelectorOnMainThread_withObject_waitUntilDone_('appendStringToOutput:', output, False)
        finally:
            fh.closeFile()
        NSThread.exit()

    def scrollToBottom(self):
        # assume that the scrollView is an existing variable
        if self.scrollView.documentView().isFlipped():
            newScrollOrigin = NSMakePoint(0.0,
                NSMaxY(self.scrollView.documentView().frame()) - \
                NSHeight(self.scrollView.contentView().bounds()))
        else:
            newScrollOrigin = NSMakePoint(0.0,0.0)
     
        self.scrollView.documentView().scrollPoint_(newScrollOrigin);

    def arbitratorWorkStarted_(self, notification):
        if not self.animated:
            self.performSelectorOnMainThread_withObject_waitUntilDone_('toggleAnimation:', None, True)

    def arbitratorWorkFinished_(self, notification):
        if self.animated:
            self.performSelectorOnMainThread_withObject_waitUntilDone_('toggleAnimation:', None, True)

    def terminateApp_(self, notification):
        if self.task:
            self.task.interrupt()
            self.task.waitUntilExit()
        self.terminate_(notification)

    def findOrCreateDirectory_inDomain_appendPathComponent_(self, searchPathDirectory, domainMask, appendComponent):
        # Search for the path
        paths = NSSearchPathForDirectoriesInDomains(
            searchPathDirectory,
            domainMask,
            True)
        if paths.count() == 0:
            # *** creation and return of error object omitted for space
            return None;
 
        # Normally only need the first path
        resolvedPath = paths.objectAtIndex_(0)
     
        if appendComponent:
            resolvedPath = resolvedPath. \
                stringByAppendingPathComponent_(appendComponent)
     
        # Create the path if it doesn't exist
        error = None
        success = NSFileManager.defaultManager().createDirectoryAtPath_withIntermediateDirectories_attributes_error_( \
            resolvedPath, True, None, error)
        if not success:
            return None;
     
        # If we've made it this far, we have a success
        return resolvedPath

    def applicationSupportDirectory(self):
        executableName = \
            NSBundle.mainBundle().infoDictionary().objectForKey_('CFBundleExecutable')
        result = self.findOrCreateDirectory_inDomain_appendPathComponent_( \
            NSApplicationSupportDirectory, NSUserDomainMask, executableName)
        return result;

class MyView(NSView):
    def initWithWindow_(self, window):
        f = window.contentView().bounds()
        return super(MyView, self).initWithFrame_(f)

    def performKeyEquivalent_(self, event):
        if event.type() == NSKeyDown:
            if event.charactersIgnoringModifiers() == 'w' and event.modifierFlags() & NSCommandKeyMask:
                NSApplication.sharedApplication().hideOutput_(None)
                return True
            elif event.charactersIgnoringModifiers() == 'q' and event.modifierFlags() & NSCommandKeyMask:
                NSApplication.sharedApplication().terminateApp_(None)
                return True
        return super(MyView, self).performKeyEquivalent_(event)

if __name__ == "__main__":
    app = FileConveyorApp.sharedApplication()
    AppHelper.runEventLoop()

