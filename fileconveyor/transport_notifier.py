import platform
from threading import Lock, Thread

def get_notifier(logger):
    system = platform.system()
    if system == 'Darwin':
        from fileconveyor.transport_notifier_darwin import TransportNotifier_Darwin
        return TransportNotifier_Darwin(logger)
    else:
        return TransportNotifier_Base(logger)
    
class TransportNotifier_Base(Thread):
    def __init__(self, logger):
        super(TransportNotifier_Base, self).__init__()

        self.logger = logger
        self._status = False

        self._transporters = []
        self._transporters_lock = Lock()
    
    def run(self):
        # do nothing for base class
        raise NotImplemented

    def stop(self):
        # do nothing for base class
        raise NotImplemented

    def _send_started():
        # do nothing for base class
        pass
    
    def _send_finished():
        # do nothing for base class
        pass

    def _update_status(self):
        new_status = True in self._transporters

        if new_status > self._status:
            self._send_started()
        if new_status < self._status:
            self._send_finished()
        self._status = new_status

    def register_transporter(self):
        """
        Register transporter for thread
        """
        with self._transporters_lock:
            idx = len(self._transporters)
            self._transporters.append(False)

        def _set_transporter_busy():
            with self._transporters_lock:
                if not self._transporters[idx]:
                    self._transporters[idx] = True
                    self._update_status()
        def _set_transporter_idle():
            with self._transporters_lock:
                if self._transporters[idx]:
                    self._transporters[idx] = False
                    self._update_status()

        return (_set_transporter_busy, _set_transporter_idle)

