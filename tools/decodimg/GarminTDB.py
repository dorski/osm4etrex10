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

import logging, argparse, struct, copy, binascii
import GarminStructures


class GarminTDBHeaderBlock(GarminStructures.TDBBlock):
    '''
    '''

    BLOCK_HEADER1 = (
            ('product ID',      'H'),
            ('unknown1',        'H'),
            ('TDB version',     'H'),
    )

    BLOCK_HEADER2 = (
            ('product version', 'H'),
    )

    
    def __init__(self, raw_data):
        '''
        '''
        super(GarminTDBHeaderBlock, self).__init__(raw_data)
        
        self._parse_header(self.BLOCK_HEADER1)
        self._get_zstring('map series name')
        self._parse_header(self.BLOCK_HEADER2)
        self._get_zstring('map family name')

        self.header['TDB version'] = self.header['TDB version'] / 100.0
        self.logger.debug('TDB version: %0.2f', self.header['TDB version'])
        self.logger.debug('map series: %s', self.header['map series name'])
        self.logger.debug('map family: %s', self.header['map family name'])
        self.logger.debug('product ID: %i', self.header['product ID'])
        self.logger.debug('product version: %i', self.header['product version'])
        self.logger.debug('unknown1: 0x%04x', self.header['unknown1'])
        if self.data != '':
            self.logger.debug('trailing data: %s', repr(self.data))


class GarminTDBCopyrightBlock(GarminStructures.TDBBlock):
    '''
    '''

    BLOCK_HEADER = (
            ('copyright code',    'B'),
            ('where code',        'B'),
            ('extra properties',  'H'),
    )


    def __init__(self, raw_data):
        '''
        '''
        super(GarminTDBCopyrightBlock, self).__init__(raw_data)

        self.copyright_statements = []

        while len(self.data) > 0:
            self._parse_header(self.BLOCK_HEADER)
            self._get_zstring('copyright string')
            self.logger.debug('copright code: 0x%02x', self.header['copyright code'])
            self.logger.debug('where code: 0x%02x', self.header['where code'])
            self.logger.debug('extra properties: 0x%04x', self.header['extra properties'])
            self.logger.debug('copyright string: %s', self.header['copyright string'])
            self.copyright_statements.append(copy.copy(self.header))
        

class GarminTDBOverviewMapBlock(GarminStructures.TDBBlock):
    '''
    '''

    BLOCK_HEADER = (
            ('map number',         'I'),
            ('parent map number',  'I'),
            ('N limit',            'i'),
            ('E limit',            'i'),
            ('S limit',            'i'),
            ('W limit',            'i'),
    )

    def __init__(self, raw_data):
        '''
        '''
        super(GarminTDBOverviewMapBlock, self).__init__(raw_data)

        self._parse_header(self.BLOCK_HEADER)

        self.logger.debug('map number: %i', self.header['map number'])
        self.logger.debug('parent map number: %i', self.header['parent map number'])
        self.logger.debug('map area: %s%0.1f--%s%0.1f, %s%0.1f--%s%03.1f',
                'N' if self.header['N limit'] >=0 else 'S',
                self.map_units_to_degrees(self.header['N limit']),
                'N' if self.header['N limit'] >=0 else 'S',
                self.map_units_to_degrees(self.header['S limit']),
                'E' if self.header['E limit'] >=0 else 'W',
                self.map_units_to_degrees(self.header['W limit']),
                'E' if self.header['E limit'] >=0 else 'W',
                self.map_units_to_degrees(self.header['E limit']),
        )

        self._get_zstring('description')
        self.logger.debug('map description: %s', self.header['description'])
        if self.data != '':
            self.logger.debug('trailing data: %s', repr(self.data))


class GarminTDBDetailMapBlock(GarminStructures.TDBBlock):
    '''
    '''

    BLOCK_HEADER1 = (
            ('map number',         'I'),
            ('parent map number',  'I'),
            ('N limit',            'i'),
            ('E limit',            'i'),
            ('S limit',            'i'),
            ('W limit',            'i'),
    )
    
    BLOCK_HEADER2 = (
            ('unknown1',           'H'),
            ('unknown2',           'H'),
            ('RGN data length',    'I'),
            ('TRE data length',    'I'),
            ('LBL data length',    'I'),
            ('unknown3',           'B'),
    )


    def __init__(self, raw_data):
        '''
        '''
        super(GarminTDBDetailMapBlock, self).__init__(raw_data)
        
        self._parse_header(self.BLOCK_HEADER1)
        
        self.logger.debug('map number: %i (parent map number: %i)',
                self.header['map number'],
                self.header['parent map number']
        )
        self.logger.debug('map area: %s%0.1f--%s%0.1f, %s%0.1f--%s%03.1f',
                'N' if self.header['N limit'] >=0 else 'S',
                self.map_units_to_degrees(self.header['N limit']),
                'N' if self.header['N limit'] >=0 else 'S',
                self.map_units_to_degrees(self.header['S limit']),
                'E' if self.header['E limit'] >=0 else 'W',
                self.map_units_to_degrees(self.header['W limit']),
                'E' if self.header['E limit'] >=0 else 'W',
                self.map_units_to_degrees(self.header['E limit']),
        )

        self._get_zstring('description')
        self.logger.debug('map description: %s',
                self.header['description'])

        self._parse_header(self.BLOCK_HEADER2)
        self.logger.debug('unknown1=0x%04x, unknown2=0x%04x, unknown3=0x%02x',
            self.header['unknown1'],
            self.header['unknown2'],
            self.header['unknown3'],
        )
        self.logger.debug('RGN data length: %i', self.header['RGN data length'])
        self.logger.debug('TRE data length: %i', self.header['TRE data length'])
        self.logger.debug('LBL data length: %i', self.header['LBL data length'])

        if self.data != '':
            self.logger.debug('trailing data: %s', repr(self.data))

        

class GarminTDBChecksumBlock(GarminStructures.TDBBlock):
    '''
    '''

    BLOCK_HEADER = (
            ('crc32 byte 1',  'B'),
            ('crc32 byte 2',  'B'),
            ('crc32 byte 3',  'B'),
            ('crc32 byte 4',  'B'),
    )

    def __init__(self, raw_data):
        '''
        '''
        super(GarminTDBChecksumBlock, self).__init__(raw_data)

        self._parse_header(self.BLOCK_HEADER)
        self.logger.debug('CRC32: 0x%02x%02x%02x%02x',
                self.header['crc32 byte 1'],
                self.header['crc32 byte 2'],
                self.header['crc32 byte 3'],
                self.header['crc32 byte 4'],
        )
        if self.data != '':
            self.logger.debug('trailing data: %s', repr(self.data))

        

class GarminTDBUnknownBlock(GarminStructures.TDBBlock):
    '''No idea what that could be.

    The mkgmap created blocks contain "Test preview map" strings.
    '''

    BLOCK_HEADER = (
        ('unknown1',    'B'),
    )

    def __init__(self, raw_data):
        '''
        '''
        super(GarminTDBUnknownBlock, self).__init__(raw_data)
        self._parse_header(self.BLOCK_HEADER)
        self._get_zstring('description')
        self.logger.debug('unknown1: 0x%02x', self.header['unknown1'])
        self.logger.debug('description: %s', self.header['description'])
        if self.data != '':
            self.logger.debug('trailing data: %s', repr(self.data))
        

class GarminTDB(object):
    '''
    '''

    GENERAL_HEADER = (
            ('block ID',     'B'),
            ('block length', 'H'),
    )
    GENERAL_HEADER_FORMAT = '<' + ''.join( f[1] for f in GENERAL_HEADER )

    BLOCK_TYPES = {
            0x42: GarminTDBOverviewMapBlock,
            0x44: GarminTDBCopyrightBlock,
            0x4c: GarminTDBDetailMapBlock,
            0x50: GarminTDBHeaderBlock,
            0x52: GarminTDBUnknownBlock,
            0x54: GarminTDBChecksumBlock,
    }


    def __init__(self, tdb_file):
        '''
        '''

        self.logger = logging.getLogger(str(self.__class__))
        self.tdb_file = tdb_file
        self.blocks = []

        for block_type, data in self.get_block_data():
            self.blocks.append(self.BLOCK_TYPES[block_type](data))

        # CRC32 check
        self.tdb_file.seek(0)
        raw_data = self.tdb_file.read()[ : -len(self.blocks[-1].raw_data)]
        crc = binascii.crc32(raw_data) & 0xffffffff
        self.logger.debug('CRC32, computed: 0x%08x', crc)
        self.logger.debug(len(raw_data))


    def get_block_data(self):
        '''
        '''

        header = self.tdb_file.read(3)
        
        while len(header) == 3:
            parsed_header = struct.unpack(self.GENERAL_HEADER_FORMAT, header)
            metadata = {}
            for index, (name, _) in enumerate(self.GENERAL_HEADER):
                metadata[name] = parsed_header[index]
            data = self.tdb_file.read(metadata['block length'])
            header = self.tdb_file.read(3)
            yield metadata['block ID'], data

        raise StopIteration
        


if __name__ == '__main__':

    ap = argparse.ArgumentParser(description='Analyze and manipulate Garmin TDB files.')
    ap.add_argument('tdb_file', metavar='FILE', nargs=1, help='TDB file name')
    ap.add_argument('-d', '--debug', action='store_true', help='enable debug messages', default=False, required=False)

    args = ap.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    with open(args.tdb_file[0], 'rb') as tdb_file:
        tdb = GarminTDB(tdb_file)
