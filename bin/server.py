import threading
from typing import List
import sys

from house_manager import get_arguments, connect, glow_msg, serve


def main(argv: List[str]) -> None:
    args = get_arguments(argv[1:])

    threading.Thread(target=connect,
                     args=(args, glow_msg),
                     daemon=True).start()

    serve(args)


if __name__ == "__main__":
    main(sys.argv)
