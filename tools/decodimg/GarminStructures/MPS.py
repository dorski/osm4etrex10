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

import Generic

# FIXME: really inherit from Generic.Subfile?

class MPS(Generic.Subfile):
    '''Garmin MPS subfile.

    This subfile type doesn't follow the usual format (even no common header).
    (MapSource related?)
    '''

    signature = None
    # mkgmap and gmaptool seem to use '\x00\x00\x00\x00\x00\x17\x94\x7f\x00G'
    # another signature: '\x00\x06\x00\xd0\x07\xa9\xfd\xc4\x03O'
    # yet another: '\x00\x01\x00\xfcR`(D\x01O'

    def __init__(self, img_file, block_size):
        super(MPS, self).__init__(img_file, block_size)
        pass

    # TODO: override parse_common_header()


    def parse_specific_header(self):
        '''
        '''
        pass
