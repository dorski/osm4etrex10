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

class LBL(Generic.Subfile):
    '''Garmin LBL subfile.

    This subfile type contains textual labels for points, lines, and polygons.
    '''

    signature = 'GARMIN LBL'

    def __init__(self, img_file, block_size):
        super(LBL, self).__init__(img_file, block_size)
        pass


    def parse_specific_header(self):
        '''
        '''
        pass
