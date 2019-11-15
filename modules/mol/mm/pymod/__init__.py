#------------------------------------------------------------------------------
# This file is part of the OpenStructure project <www.openstructure.org>
#
# Copyright (C) 2008-2016 by the OpenStructure authors
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#------------------------------------------------------------------------------

import os.path
from ._ost_mol_mm import *
from . import antechamber
import ost

def LoadAMBERForcefield():
  return Forcefield.Load(os.path.join(ost.GetSharedDataPath(),'forcefields','AMBER03.dat'))

def LoadCHARMMForcefield():
  return Forcefield.Load(os.path.join(ost.GetSharedDataPath(),'forcefields','CHARMM27.dat'))
