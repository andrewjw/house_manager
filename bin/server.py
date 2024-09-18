import os
import threading
from typing import List
import sys

import sentry_sdk

from house_manager import get_arguments, connect, serve


def main(argv: List[str]) -> None:
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        traces_sample_rate=0.0,
        profiles_sample_rate=0.0,
    )

    args = get_arguments(argv[1:])

    threading.Thread(target=connect,
                     args=(args, ),
                     daemon=True).start()

    serve(args)


if __name__ == "__main__":
    main(sys.argv)
