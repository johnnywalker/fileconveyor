from fileconveyor.transporters.transporter import *
from storages.S3BotoStorage import *


TRANSPORTER_CLASS = "TransporterS3"


class TransporterS3(Transporter):


    name              = 'S3'
    valid_settings    = ImmutableSet(["access_key_id", "secret_access_key", "bucket_name", "bucket_prefix"])
    required_settings = ImmutableSet(["access_key_id", "secret_access_key", "bucket_name"])
    headers = {
        'Expires':       'Tue, 20 Jan 2037 03:00:00 GMT', # UNIX timestamps will stop working somewhere in 2038.
        'Cache-Control': 'max-age=315360000',             # Cache for 10 years.
        'Vary' :         'Accept-Encoding',               # Ensure S3 content can be accessed from behind proxies.
    }


    def __init__(self, settings, callback, error_callback, notifier, parent_logger=None):
        Transporter.__init__(self, settings, callback, error_callback, notifier, parent_logger)

        # Fill out defaults if necessary.
        configured_settings = Set(self.settings.keys())
        if not "bucket_prefix" in configured_settings:
            self.settings["bucket_prefix"] = ""

        # Map the settings to the format expected by S3Storage.
        try:
            self.storage = S3BotoStorage(
                self.settings["bucket_name"],
                self.settings["bucket_prefix"],
                self.settings["access_key_id"],
                self.settings["secret_access_key"],
                "public-read",
                self.__class__.headers
            )
        except Exception, e:            
            raise ConnectionError(e)
