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

import logging, struct

class TDBBlock(object):
    '''Base class for all sorts of TDB blocks.

    Provides a common data interface and common functions for parsing the header.
    '''


    def __init__(self, raw_data):
        '''
        '''
        self.logger = logging.getLogger(str(self.__class__))
        self.logger.debug('overall block size: %i bytes', len(raw_data))
        self.header = {}
        self.raw_data = raw_data
        self.data = raw_data


    def map_units_to_degrees(self, map_units):
        '''Convert Garmin map units to degrees.
        '''
        return 360.0 * map_units / 2**32


    def _get_zstring(self, field_name):
        '''Extract a NUL-terminated string at the beginning of the block data.

        Adjusts the internally stored block data by removing the parsed header part.

        Variable length NUL-terminated strings are not supported by struct,
        thus this helper function is needed.
        '''

        parts = self.data.split('\0', 1)
        self.data = self.data[len(parts[0]) : ].lstrip('\0')
        self.header[field_name] = parts[0]


    def _parse_header(self, header_structure):
        '''Parse a block's header from internally stored block data.

        Adjusts the internally stored block data by removing the parsed header part.
        '''
        
        header_format = '<' + ''.join( fmt for name, fmt in header_structure )
        header_format_length = struct.calcsize(header_format)

        raw_header = struct.unpack(header_format,
                self.data[ : header_format_length])
        self.data = self.data[header_format_length : ]

        for index, (name, _) in enumerate(header_structure):
            self.header[name] = raw_header[index]



class Subfile(object):
    '''Base class for Garmin IMG subfiles.
    '''

    HEADER = (
            ('header length',   'H'),
            ('signature',       '10s'),
            ('unknown1',        'B'), # fixed 0x01?
            ('lock',            'B'), # 0x00 -- not locked, 0x80 -- locked
            ('creation year',   'H'),
            ('creation month',  'B'),
            ('creation day',    'B'),
            ('creation hour',   'B'),
            ('creation minute', 'B'),
            ('creation second', 'B'),
    )
    HEADER_FORMAT = '<' + ''.join( f[1] for f in HEADER )


    def __init__(self, img_file, block_size):
        '''
        '''
        
        self.logger = logging.getLogger(str(self.__class__))

        self.img_file = img_file
        self.block_size = block_size
        self.name = None
        self.type = None
        self.offset = None
        self.block_id_list = []
        self.common_header = {}
        self.header = {}


    def update(self, FAT_metadata):        
        '''
        '''

        if self.name is None:
            # first update
            self.name = FAT_metadata['name']
            self.type = FAT_metadata['type']
            self.offset = self.block_size * min(FAT_metadata['blocks'])
            self.parse_common_header()
            self.parse_specific_header()
        else:
            # subsequent updates
            
            # sanity checks
            if min(FAT_metadata['blocks']) < min(self.block_id_list):
                self.logger.critical('out of order datablocks (this should never happen)')

        self.block_id_list.extend(FAT_metadata['blocks'])

    
    def parse_specific_header(self):
        raise NotImplementedError, 'This must be implemented in child classes.'


    def parse_common_header(self):
        '''
        '''

        # jump to the common header, read and jump back
        offset = self.img_file.tell()
        self.img_file.seek(self.offset)
        raw_header = self.img_file.read(struct.calcsize(self.HEADER_FORMAT))
        self.img_file.seek(offset)

        parsed_header = struct.unpack(self.HEADER_FORMAT, raw_header)
        for index, (name, _) in enumerate(self.HEADER):
            self.common_header[name] = parsed_header[index]

        # sanity checks:
        if not self.common_header['signature'] == self.signature:
            self.logger.warning('Unexpected signature: %s', repr(self.common_header['signature']))
        else:
            self.logger.debug('found %s subfile @0x%06x', self.common_header['signature'], self.offset)
            self.logger.debug('creation date/time: %(creation year)i-%(creation month)02i-%(creation day)02i, %(creation hour)02i:%(creation minute)02i:%(creation second)02i' % self.common_header)
            self.logger.debug('header length: %i bytes', self.common_header['header length'])

    
    def __str__(self):
        return '%s: "%s", %i block(s) (~%i kb)' % (self.__class__, self.name, len(self.block_id_list), len(self.block_id_list)*self.block_size/1024)
