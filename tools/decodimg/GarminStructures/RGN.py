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

class RGN(Generic.Subfile):
    '''Garmin RGN subfile.
    '''

    signature = 'GARMIN RGN'

    # Even though the RGN header here is rather small,
    # typically the data only starts after 125 bytes
    # (including the common header).
    # Looking at original Garmin IMGs it appears
    # that indead there is more data in this header.

    RGN_HEADER = (
        ('data offset', 'I'),
        ('data length', 'I'),
    )
    RGN_HEADER_FORMAT = '<' + ''.join( f[1] for f in RGN_HEADER )


    def __init__(self, img_file, block_size):
        super(RGN, self).__init__(img_file, block_size)
        pass


    def parse_specific_header(self):
        '''
        '''
        pass
