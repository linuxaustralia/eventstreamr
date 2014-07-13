__author__ = 'Lee Symes'

from twisted.internet import reactor, task
from twisted.internet.protocol import Factory

from lib.json_helper import load_json
from lib.monitor import FilteredFileInFolderMonitor
from lib.manager.queue import EncoderQueue
from roles import SuperAMP

# Load the config as a dictionary from the JSON file.
manager_config = load_json("manager.json")

registered_stations = []


def configure_encoder_fs_watch():
    encode_config = manager_config["encode"]
    base_path = encode_config["base_path"]
    check_folder = base_path + "todo"
    file_pattern = encode_config["file_pattern"]
    l = task.LoopingCall(FilteredFileInFolderMonitor(check_folder, file_pattern, EncoderQueue(base_path)))
    l.start(10.0, now=False) # Call every minute. Wait a minute before starting.














def main():
    # FROM: http://twistedmatrix.com/documents/current/core/examples/ampserver.py

    pf = Factory()
    pf.noisy = True
    pf.protocol = SuperAMP

    configure_encoder_fs_watch()

    reactor.listenTCP(8888, pf)
    reactor.run()

if __name__ == "__main__":
    main()



