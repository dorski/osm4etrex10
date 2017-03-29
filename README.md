# osm4etrex10

`osm4etrex10` is a small framework around mkgmap that allows you to create OSM based maps for the rather limited eTrex 10 GPS receivers made by Garmin.

There are other frameworks and howto documents on this topic:

* another `mkgmap` map style optimized for the eTrex 10 at http://gps.maroufi.net/etrex10map.shtml (in German)
* 


## Basic requirements

For compiling small binary map images you will need

1. **OpenStreetMap data**: You can use data in either OSM/XML or OSM/PBF formats. There is a handy export functionality on the website at https://www.openstreetmap.org/ that allows retrieving data for relatively small areas directly. Alternatively, you can use OSM dumps and cut the needed data with `osmosis` (http://wiki.openstreetmap.org/wiki/Osmosis). Instead of using the whole planet file you can use country based pre-cut extracts hosted e. g. at http://download.geofabrik.de/.
1. **mkgmap** map compiler: The `mkgmap` project at http://www.mkgmap.org.uk/ automatically publishes daily builds after a series of technical tests. Generally it is save and advisable to use the latest build. Daily snapshots are named after their revision number (XXXX): `mkgmap-rXXXX.zip`. Unzip the snapshot file in the `osm4etrex10/lib/` lib directory. This will create a fully workable `mkgmap` installation.

Create a generic symlink within the `osm4etrex10/lib/` pointing to the snapshot:

```
user@host$ cd lib/
user@host$ ln -s mkgmap-rXXXX mkgmap
```
The wrapper calling the `mkgmap` binary relies on this symlink. You can install many different `mkgmap` snapshots under `lib/` allowing you to test their impact on map image size.


## Compiling the map

To compile a map within the `osm4etrex10` framework you call the `bin/mkgmap` wrapper. It expects the data extract in the OSM/XML or OSM/PBF format as a parameter:
```
user@host$ ./bin/mkgmap osm-data.pbf
Time started: Fri Oct 16 10:39:34 CEST 2015
Number of MapFailedExceptions: 0
Number of ExitExceptions: 0
Time finished: Fri Oct 16 10:40:15 CEST 2015
Total time taken: 41028ms
```
The compiled map is stored as `img-output/osmmap.img`. For use of the map with certain applications (such as `QLandkarteGT`) there is also a TDB file `img-output/osmmap.tdb` created.

To use the compiled map on the eTrex device, copy it to your handheld under it's `Garmin` directory, renaming it to `gmapbmap.img` (asuming the device is mounted under `/media/etrex/`):
```
user@host$ cp img-output/osmmap.img /media/etrex/Garmin/gmapbmap.img
```

## Technical Background

### Device limitations on the Etrex 10

eTrex 10 device have quite a few technical characteristic that make it difficult to use maps on those devices, most notably the display resolution, the memory limitations and different constraints by the device's firmware:

- **display limitations**:  The device comes equipped with a 2.2" (5.6&#160;mm) greyscale display showing 176×220 pixels. This is considerably coarser then the resolution of other devices from the new eTrex series that have the same physical dimensions but show 240×320 pixels. In the map style (TYP file), this is catered for by drastically restricting the width of lines to typically one pixel, effectively resulting in a wireframe representation of streets.
- **memory size**: The device has built in permanent memory of 10&#160;MB with no possibility for extension, e.&#160;g. by (Micro-)SD cards. A part of the memory is used for device configuration files, stored waypoint and track data (if track recording is enabled), or geocache descriptions (if your into geo-games). Effectively you can expect no more than about X&#160;MB for maps if you restrict the use of the device to displaying the map.
- **software specific limitations**: (data structures, access modes)

### Map size optimizations

There is a range of techniques and tricks that allows for a size reduction in `mkgmap` created maps:

- **Whitelisting map features** is the general principle of work for `mkgmap` styles. In the style descriptions, a mapping from OpenStreetMap map features to Garmin data entities (e.&#160;g. roads, POIs) is defined where only the explicitly mapped features end up in the compiled map image.
- Map images may contain several separate individual maps which are optimized for display at specific zoom levels. Depending on the zoom level, accuracy of the location information varies. On higher zoom levels, location information is stored with increasing precision, which implies a bigger number of bits per location information. This tradeoff between higher precision and smaller storage space per location information can be shifted in favour of the latter by **using lower zoom levels** for map images. Lower precision of the map's stored coordinates will generally lead to coarser maps and even disconnected streets after zooming into the map.
- **Abbreviating geographical names** also helps to reduze the size of map images, although the impact is less significant than can be achived with the other strategies. In OpenStreetMap, the policy for naming map features in general is to provide the unabriviated name. Regular expressions are exploited in the map style definition to shorten (parts of) geographical names to common abbreviations, such as (German) *Straße* to *Str*, (Dutch) *Plein* to *Pl*, or (Spanish) *Avenida* to *Av*.
- **Restricting index creation** (tbd.)

### Little helpers

- `tools/decodimg/GarminIMG.py` is a small tool that parses Garmin image files and prepares an overview of the embedded blocks together with their sizes. This is a useful debug utility that helps assess the impact of configuration changes or different version of `mkgmap`.
