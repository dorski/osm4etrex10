#! /usr/bin/env python
'''
Copright 2015 by Dorski <geostuff@snafu.de>

This file is part of decodimg.

decodimg is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import argparse, logging, struct
import GarminStructures

class GarminIMG(object):
    '''
    '''

    # see http://wiki.openstreetmap.org/wiki/OSM_Map_On_Garmin/Format
    IMG_HEADER = (
        ('xor',                  'B'),
        ('padding1',             '9s'),
        ('update month',         'B'),
        ('update year',          'B'),
        ('padding2',             '3s'),
        ('checksum',             'B'),
        ('signature',            '7s'),
        ('unknown1',             's'), # fix?
        ('sectors',              'H'),
        ('heads',                'H'),
        ('cylinders',            'H'),
        ('unknown2',             '2s'),
        ('padding3',             '25s'), # NOT just padding
        ('creation year',        'H'),
        ('creation month',       'B'),
        ('creation day',         'B'),
        ('creation hour',        'B'),
        ('creation min',         'B'),
        ('creation sec',         'B'),
        ('unknown3',             's'), # NOT fix
        ('map file ident (fix)', '7s'),
        ('padding4',             '1s'),
        ('map description 1',    '20s'),
        ('heads2',               'H'), # ?? == heads
        ('sectors2',             'H'), # ?? == sectors
        ('block size exp. 1',    'B'),
        ('block size exp. 2',    'B'),
        ('block size',           'H'),
        ('map description 2',    '30s'),
        ('padding8',             's'),
        ('padding9',             '314s'), # there is something in the first bytes
        # partition table starts here
        ('boot(?)',              'B'),
        ('start head',           'B'), # ??
        ('start sector',         'B'), # ??
        ('start cylinder',       'B'), # ??
        ('system type(?)',       'B'),
        ('end head',             'B'), # ??
        ('end sector',           'B'), # ??
        ('end cylinder',         'B'), # ??
        ('rel sectors(?)',       'I'),
        ('number of sectors(?)', 'I'),
        ('padding5',             '48s'),
        ('BIOS boot signature',  '2s'),
        ('padding6',             '512s'),
        ('unknown4',             's'), # NOT fix
        ('unknown5',             '11s'), # NOT fix
        ('sub-file offset 1',    'I'), # 0 if none?
        ('unknown',              's'), # NOT fix
        ('padding7',             '15s'),
        ('raw block seq. nrs.',  '480s'),
        # partition table ends here
    )
    IMG_HEADER_FORMAT = '<' + ''.join( f[1] for f in IMG_HEADER )

    FAT_HEADER = (
        ('flag',         'B'),
        ('name',         '8s'),
        ('type',         '3s'),
        ('size',         'I'),
        ('part',         'H'),
        ('padding',      '14s'),
        ('raw block seq. nrs.', '480s'),
    )
    FAT_HEADER_FORMAT = '<' + ''.join( f[1] for f in FAT_HEADER )


    def __init__(self, img_file):
        '''
        '''
        self.logger = logging.getLogger(str(self.__class__))
        self.img_file = img_file
        self.header = {}
        self.subfiles = {}
        self.block_size = None
        self.data_blocks = []

        # determine the size of the input file
        self.img_file.seek(0, 2)
        self.img_file_length = self.img_file.tell()
        self.logger.debug('overall IMG size: %i bytes', self.img_file_length)
        self.img_file.seek(0)
        
        # get all metadata (header and FAT)
        # and simultaneously construct the subfile index
        self._parse_IMG_header()

        fat_table = self._parse_single_FAT_block()
        while fat_table is not None:

            subfile_id = (fat_table['name'], fat_table['type'])
            
            if not subfile_id in self.subfiles:
                self.subfiles[subfile_id] = GarminStructures.SUBFILE_TYPES[fat_table['type']](self.img_file, self.block_size)
            self.subfiles[subfile_id].update(fat_table)
            
            fat_table = self._parse_single_FAT_block(fat_table['next'])
        
        self.logger.debug('Number of data blocks: %i', len(self.data_blocks))

        # additional sanity checks
        if min(self.data_blocks) * self.block_size != self.header['sub-file offset 1']:
            self.logger.info('first subfile really starts at 0x%06x', min(self.data_blocks) * self.block_size)


    def _get_block_addresses(self, s):
        '''Extract block sequence numbers.

        Block sequence numbers are stored in 480 byte long strings as 0xFFFF padded short ints. This function parses the string and returns a list of the bock sequence numbers.
        '''
        return [ n for n in struct.unpack('<240H', s) if n != 0xffff ]


    def _parse_single_FAT_block(self, offset=0x600):
        '''
        '''
        self.img_file.seek(offset)
        raw_header = self.img_file.read(512)
        first_data_block = 0
        
        if raw_header == 512 * '\x00' and offset == 0x600:
            # for some files the FAT structure doesn't start at 0x600
            # but at 0x1200 -- no idea yet how to distinguish these
            # two variants based on the IMG header data
            offset = 0x1200
            self.img_file.seek(offset)
            self.logger.info('skipping to 0x%06x for FAT start', offset)
            raw_header = self.img_file.read(512)

        fat_structure = {}
        parsed_header = struct.unpack(self.FAT_HEADER_FORMAT,
                raw_header)
        
        for index, (name, _) in enumerate(self.FAT_HEADER):
            fat_structure[name] = parsed_header[index]

        if fat_structure['type'] in GarminStructures.SUBFILE_TYPES and (self.data_blocks == [] or offset < min(self.data_blocks) * self.block_size):
            fat_structure['blocks'] = self._get_block_addresses(fat_structure['raw block seq. nrs.'])
            self.data_blocks.extend(fat_structure['blocks'])
            fat_structure['block count'] = len(fat_structure['blocks'])
            fat_structure['offset'] = offset
            fat_structure['next'] = offset + 512
            self.logger.debug('FAT block: %(type)s ("%(name)s" @0x%(offset)06x, part #%(part)i, %(block count)i blocks' % fat_structure)
            return fat_structure
        else:
            return None


    def _parse_IMG_header(self):
        '''
        '''
        # xor != 0 is not handled
        self.img_file.seek(0)

        # read the header proper, the partition table,
        # the continued header, and the block sequence numbers
        raw_header = self.img_file.read(446+66+512+32+480)
        parsed_header = struct.unpack(self.IMG_HEADER_FORMAT, raw_header)
        
        for index, (field, _) in enumerate(self.IMG_HEADER):
            self.header[field] = parsed_header[index]

        # format adjustments, data derivations
        if self.header['update year'] < 99:
            self.header['update year'] += 2000
        else:
            self.header['update year'] += 1900

        self.header['map description'] = (self.header['map description 1'] + self.header['map description 2']).strip()

        self.header['block sequence numbers'] = self._get_block_addresses(self.header['raw block seq. nrs.'])
        
        self.header['calculated block size'] = self.header['heads'] * self.header['sectors'] * self.header['cylinders'] / (2 ** self.header['block size exp. 2'])

        # this seems to be the only reliable figure for block size
        self.header['real block size'] = 2 ** (9 + self.header['block size exp. 2'])
        self.block_size = self.header['real block size']

        # sanity checks
        if self.header['heads'] != self.header['heads2']:
            self.logger.info('heads != heads2')
        if self.header['sectors'] != self.header['sectors2']:
            self.logger.info('sectors != sectors2')
        if self.header['calculated block size'] != self.header['block size']:
            self.logger.info('block size != calculated value')
        if self.header['BIOS boot signature'] != '\x55\xAA':
            self.logger.info('strange BIOS boot signature: %s',
                    repr(self.header['BIOS boot signature']))
        if self.header['padding5'] != 48 * '\x00':
            self.logger.info('padding5 not empty: %s',
                    repr(self.header['padding5']))
        if self.header['padding6'] != 512 * '\x00':
            self.logger.info('padding6 not empty: %s',
                    repr(self.header['padding6']))
        if self.header['padding8'] != 1 * '\x00':
            self.logger.info('padding8 not empty: %s',
                    repr(self.header['padding8']))
        if self.header['padding9'] != 314 * '\x00':
            self.logger.info('padding9 not empty: %s (stripped)',
                    repr(self.header['padding9'].replace('\x00', '')))
        if len(self.header['block sequence numbers']) != len(set(self.header['block sequence numbers'])):
            self.logger.info('block sequence numbers in Garmin IMG not unique')

        if self.img_file_length % self.block_size != 0:
            self.logger.warning('IMG size not a multiple of real block size')



    def dump_header_information(self):
        '''
        '''
        print 'Map description:\t%(map description)s' % self.header
        print 'Creation date:\t%(creation year)i-%(creation month)02i-%(creation day)02i' % self.header
        print 'Update date:\t%(update year)i-%(update month)02i-XX' % self.header
        print 'Creation time:\t%(creation hour)02i:%(creation min)02i:%(creation sec)02i' % self.header
        print 'IMG geometry: cylinders=%(cylinders)i, heads=%(heads)i, sectors=%(sectors)i' % self.header
        print 'IMG geometry: heads2=%(heads2)i, sectors2=%(sectors2)i' % self.header
        print 'Block size exponents:\t E_1=%(block size exp. 1)s, E_2=%(block size exp. 2)s' % self.header
        print 'Block size: %(block size)i (calculated: %(calculated block size)i, real: %(real block size)i)' % self.header
        print 'Filesystem start: cylinder=%(start cylinder)i, head=%(start head)i, sector=%(start sector)i' % self.header
        print 'Filesystem end: cylinder=%(end cylinder)i, head=%(end head)i, sector=%(end sector)i' % self.header
        print 'XOR value:\t%(xor)#04x' % self.header
        print 'Checksum value:\t%(checksum)#04x' % self.header
        print 'First sub-file offset:\t0x%(sub-file offset 1)06x' % self.header
        #print 'Block sequence numbers:\t%(block sequence numbers)s' % self.header
        for subfile in self.subfiles.itervalues():
            print str(subfile)


    def checksum(self):
        '''Generate the checksum for the IMG.

        According to the 2005 Mechalas paper,
        "the checksum ... is calculated by summing all bytes,
        save for the checksum byte itself, in the map file
        and then multiplying by -1. The lowest byte in this product
        becomes the checksum byte ..."
        '''

        # is this checksum actually honoured in any piece of software?
        raise NotImplementedError



if __name__ == '__main__':

    ap = argparse.ArgumentParser(description='Decode Garmin IMG files.')
    ap.add_argument('img', metavar='IMG_FILE', nargs=1, help='IMG file name')
    ap.add_argument('-d', '--debug', action='store_true', help='enable debug messages', default=False, required=False)

    args = ap.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    with open(args.img[0], 'rb') as img_file:
        img = GarminIMG(img_file)
        img.dump_header_information()
