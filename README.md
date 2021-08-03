# Hydrogen Drumkit Generator

This script generates and install an Hydrogen Drumkit from a set of samples
separated by subdirectories (kick, snare, etc...).
It is particulary useful when you need to convert a drum kit found on the web to
the Hydrogen Drumkit format.

## Features

 - Name your pack
 - Automatic integration to Hydrogen
 - FLAC and WAV support (working with FLAC is recommended)
 - Format conversion (FLAC from/to WAVE)
 - Set the maximum number of layers for each instrument (useful for roundrobins)
   - If the number of layers is lower than the amount of available samples,
     the script will choose the right samples for you
 - Support of samples names ordered by natural order
 - Automatic layers interleaving computing for a more natural playing

## Usage

```
usage: hdg.py [-h] [--layers LAYERS] [--from {flac,wav}] [--to {flac,wav}] folder name

positional arguments:
  folder             folder containing the samples
  name               name of the drum kit

optional arguments:
  -h, --help         show this help message and exit
  --layers LAYERS    max layers per instrument (default: 16)
  --from {flac,wav}  file format to look for (default: wav)
  --to {flac,wav}    output file format (requires SoX)
```

## Important

1. Be careful when using a high amount of layers. It can take a lot of RAM
   memory and time to load. Working with a SSD disk and more than 4 Gb of RAM
   is **strongly** advised!

2. To use more than 16 layers, check that Hydrogen is configured to support
   as much layers (can be defined in the "General" settings panel).

## Credits

Developer: Cyriaque 'cisoun' Skrapits (drowned.ch)
