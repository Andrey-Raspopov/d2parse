import argparse
import threading

from DemoParser import DemoParser


def main():
    parser = argparse.ArgumentParser(description="Dota 2 demo parser")
    parser.add_argument("demo", help="The .dem file to parse")
    parser.add_argument(
        "--verbosity",
        dest="verbosity",
        default=3,
        type=int,
        help="how verbose [1-5] (optional)",
    )
    parser.add_argument(
        "--frames",
        dest="frames",
        default=None,
        type=int,
        help="maximum number of frames to parse (optional)",
    )

    args = parser.parse_args()

    threads = []

    r = DemoParser(args.demo, verbosity=args.verbosity, frames=args.frames)

    r.parse()
    #parse_thread = threading.Thread(target=r.parse, daemon=True, args=())
    #threads.append(parse_thread)

    #for thread in threads:
        #thread.start()

    #for thread in threads:
    #    thread.join()


if __name__ == "__main__":
    main()
