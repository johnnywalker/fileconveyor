from fileconveyor.transport_notifier import TransportNotifier_Base
from Foundation import *
from CoreFoundation import CFRunLoopStop
from Queue import Queue, Empty
from threading import current_thread

class TransportNotifier_Darwin(TransportNotifier_Base):
    def __init__(self, logger):
        super(TransportNotifier_Darwin, self).__init__(logger)
        self.notification_queue = Queue()

    def run(self):
        self.logger.warning('Started Transport Notifier.')
        self.logger.warning('Init NSAutoreleasePool for thread %d' % \
            current_thread().ident)
        pool = NSAutoreleasePool.alloc().init()
        target = NotifierDelegate.alloc().initWithQueue_(self.notification_queue)
     
        self.dying = False

        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_( \
            0.5, target, 'timerFire:', None, True)

        resolution = 5.0
        is_running = True
        while not self.dying and is_running:
            until = NSDate.dateWithTimeIntervalSinceNow_(resolution)
            is_running = NSRunLoop.currentRunLoop().runMode_beforeDate_( \
                NSDefaultRunLoopMode, until)
            del pool
            pool = NSAutoreleasePool.alloc().init()

        self.logger.warning('Destroying NSAutoreleasePool for thread %d' % \
            current_thread().ident)
        del pool

        return 0

    def stop(self):
        self.dying = True
        CFRunLoopStop(NSRunLoop.currentRunLoop().getCFRunLoop())

    def _send_started(self):
        self.notification_queue.put(True)

    def _send_finished(self):
        self.notification_queue.put(False)

class NotifierDelegate(NSObject):
    def initWithQueue_(self, queue):
        self = self.init()
        self.queue = queue
        self.thread = NSThread.currentThread()
        self.dnc = NSDistributedNotificationCenter.defaultCenter()
        return self

    def timerFire_(self, timer):
        try:
            while True:
                n = self.queue.get_nowait()
                if n == True:
                    sel = 'sendWorkStartedNotification:'
                else:
                    sel = 'sendWorkFinishedNotification:'
                self.performSelector_onThread_withObject_waitUntilDone_( \
                    sel, self.thread, self, False)
        except Empty:
            pass

    def sendWorkStartedNotification_(self, sender):
        self.dnc.postNotificationName_object_('arbitratorWorkStarted', None)
        
    def sendWorkFinishedNotification_(self, sender):
        self.dnc.postNotificationName_object_('arbitratorWorkFinished', None)
