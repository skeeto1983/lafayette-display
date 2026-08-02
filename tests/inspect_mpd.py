from pprint import pprint

from mpd import MPDClient


def main() -> None:
    client = MPDClient()
    client.timeout = 10
    client.idletimeout = None
    client.connect("localhost", 6600)

    try:
        print("\n=== STATUS ===")
        pprint(client.status())

        print("\n=== CURRENT SONG ===")
        pprint(client.currentsong())
    finally:
        try:
            client.close()
        except Exception:
            pass

        try:
            client.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    main()
