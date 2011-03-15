//------------------------------------------------------------------------------
// This file is part of the OpenStructure project <www.openstructure.org>
//
// Copyright (C) 2008-2011 by the OpenStructure authors
// Copyright (C) 2003-2010 by the IPLT authors
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
#ifndef OST_IO_MAP_IO_MRC_HANDLER_HH
#define OST_IO_MAP_IO_MRC_HANDLER_HH

#include <ost/unit_cell.hh>

#include "map_io_handler.hh"

namespace ost { namespace io {

class DLLEXPORT_OST_IO MRC: public ImageFormatBase
{
 public:

  MRC(bool normalize_on_save = false, Subformat subformat = MRC_AUTO_FORMAT ,Endianess endianness_on_save = OST_LOCAL_ENDIAN);

  Endianess GetEndianessOnSave() const;
  void SetEndianessOnSave(Endianess end);

  bool GetNormalizeOnSave() const;
  void SetNormalizeOnSave(bool normalize_on_save);

  Subformat GetSubformat() const;
  void SetSubformat(Subformat subformat);

  static String FORMAT_STRING;

    
 private:
  Subformat subformat_;
  bool normalize_on_save_;
  Endianess endianess_on_save_;
};

class DLLEXPORT_OST_IO CCP4: public MRC
{
 public:
  CCP4(bool normalize_on_save = false, Endianess endianness_on_save = OST_LOCAL_ENDIAN);
};

typedef CCP4 MAP;

class MapIOMrcHandler: public MapIOHandler {
public:

  MapIOMrcHandler():
   is_file_(false),
   filename_("") {}

  /// \brief Map IO handler to read/write mrc and ccp4 map files
  ///
  /// This map IO handler reads and writes MRC formatted map files, as
  /// generated by the MRC electron crystallography processing package
  virtual void Import(img::MapHandle& sh, const boost::filesystem::path& loc,
                      const ImageFormatBase& formatstruct);
  virtual void Import(img::MapHandle& sh, std::istream& loc, const ImageFormatBase& formatstruct);
  virtual void Export(const img::MapHandle& sh, const boost::filesystem::path& loc, const ImageFormatBase& formatstruct) const;
  virtual void Export(const img::MapHandle& sh, std::ostream& loc,const ImageFormatBase& formatstruct) const;
  static bool MatchContent(unsigned char* header);
  static bool MatchType(const ImageFormatBase& type);
  static bool MatchSuffix(const String& loc);
  static String GetFormatName() { return String("Mrc"); };
  static String GetFormatDescription() { return String("Format used by the MRC software package"); };

  const img::Size& GetUnitCellSize() const { return unit_cell_size_; }  
  const UnitCell& GetUnitCell() const { return unit_cell_; }
private:

  mutable bool   is_file_;
  mutable String filename_;
  char           header_[256];
  UnitCell       unit_cell_;
  img::Size      unit_cell_size_;
};

typedef MapIOHandlerFactory<MapIOMrcHandler> MapIOMrcHandlerFactory;

}}


#endif
