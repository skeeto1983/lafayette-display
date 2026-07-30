from mpd import MPDClient

client = MPDClient()
client.timeout = 10
client.idletimeout = None

client.connect("localhost", 6600)

status = client.status()
song = client.currentsong()

print("=== Status ===")
for key, value in status.items():
    print(f"{key:15}: {value}")

print("\n=== Current Song ===")
for key, value in song.items():
    print(f"{key:15}: {value}")

client.close()
client.disconnect()
