# Hydrogen Drumkit Generator

This script generates an Hydrogen Drumkit from a set of samples separated by
subdirectories (kick, snare, etc...).  
It is particulary useful when you need to convert a drumkit found on the web to
the Hydrogen Drumkit format.

## Features

 - Name selection of your pack
 - Automatic integration to Hydrogen
 - FLAC and WAV support (working with FLAC is recommended)
 - Format conversion (FLAC from/to WAVE)
 - Maximum number of layers for each instrument (useful for roundrobins)

## Usage

```
usage: hdg.py [-h] [--layers LAYERS] [--from {flac,wav}] [--to {flac,wav}] folder name

positional arguments:
  folder             folder containing the samples
  name               name of the drumkit

optional arguments:
  -h, --help         show this help message and exit
  --layers LAYERS    max layers per instrument (default: 16)
  --from {flac,wav}  file format to look for (default: wav)
  --to {flac,wav}    output file format (requires SoX)
```

## Important

Be careful when using a high amount of layers. It can take a lot of RAM memory
and time to load. Working with a SSD disk and more than 4 Gb of RAM is
**strongly** advised!

## Credits

Developer: Cyriaque 'cisoun' Skrapits (drowned.ch)
