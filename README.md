# lafayette-display
A Raspberry Pi touchscreen "Now Playing" display inspired by 1970s Lafayette stereo equipment.

# Lafayette Display

A Raspberry Pi touchscreen "Now Playing" display for moOde Audio inspired by the classic Lafayette receivers of the 1970s.

## Features

- Album artwork
- Radio Paradise support
- Spotify Connect
- Vintage-inspired interface
- Home Assistant integration (planned)
- Analog VU meters (planned)

## Spotify Connect

Adjusted the default Spotify Connect volume:

```sql
UPDATE cfg_spotify
SET value='100'
WHERE param='initial_volume';
```

This prevents new Spotify Connect sessions from starting at 5% volume.
