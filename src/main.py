import sys
import os

sys.path.append(os.path.dirname(__file__))

from streamer import Streamer

if __name__ == '__main__':
    Streamer().start_stream()