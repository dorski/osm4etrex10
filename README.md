# osm4etrex10
Create OSM based maps for eTrex 10 GPS receivers.

The documentation is still a stub.

## Basic requirements

OpenStreetMap data (OSM/XML or OSM/PBF): https://www.openstreetmap.org/ – either via the export function or using osmosis on the planet file, or any other suitable dump, e. g. from http://download.geofabrik.de/

mkgmap: http://www.mkgmap.org.uk/ – unzip the mkgmap-rXXXX.zip file in lib/ thus creating a directory lib/mkgmap-rXXXX/ with a workable mkgmap installation

## Compiling the map

using bin/mkgmap-wrapper

## Technical Background

### Device limitations on the Etrex 10

display

memory

software specific limitations (data structures, access modes)

### Map size optimizations

whitelisting map features

number of levels

resolution of levels

abbreviations for geographical names

### Little helpers

tools/decodimg/ for inspecting block sizes of the Garmin IMG files
