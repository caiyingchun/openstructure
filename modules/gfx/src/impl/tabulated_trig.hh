//------------------------------------------------------------------------------
// This file is part of the OpenStructure project <www.openstructure.org>
//
// Copyright (C) 2008-2020 by the OpenStructure authors
//
// This library is free software; you can redistribute it and/or modify it under
// the terms of the GNU Lesser General Public License as published by the Free
// Software Foundation; either version 3.0 of the License, or (at your option)
// any later version.
// This library is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
// FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
// details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with this library; if not, write to the Free Software Foundation, Inc.,
// 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
//------------------------------------------------------------------------------
#ifndef OST_GFX_IMPL_TABULATED_TRIG_HH
#define OST_GFX_IMPL_TABULATED_TRIG_HH

#include <ost/gfx/module_config.hh>
/*
   Author: Marco Biasini
 */
namespace ost { namespace gfx { namespace impl {

/// \brief calculate cosine of angle in radians using tabulated values
float TabCos(float angle);

/// \brief calculate sine of angle in radians using tabulated values
float TabSin(float angle);

}}}

#endif
