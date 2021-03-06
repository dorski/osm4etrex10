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

'''Grmin subfile formats.
'''

import TRE, RGN, DEM, LBL, TYP, SRT, NET, NOD, MDR
import MPS
from Generic import TDBBlock

SUBFILE_TYPES = {
        'TRE': TRE.TRE,
        'RGN': RGN.RGN,
        'DEM': DEM.DEM,
        'MPS': MPS.MPS,
        'LBL': LBL.LBL,
        'TYP': TYP.TYP,
        'SRT': SRT.SRT,
        'NET': NET.NET,
        'NOD': NOD.NOD,
        'MDR': MDR.MDR,
}

