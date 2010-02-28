//------------------------------------------------------------------------------
// This file is part of the OpenStructure project <www.openstructure.org>
//
// Copyright (C) 2008-2010 by the OpenStructure authors
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

/*
  Authors: Ansgar Philippsen, Andreas Schenk
*/

#ifndef IPLT_GUI_DATA_VIEWER_H
#define IPLT_GUI_DATA_VIEWER_H

#include <map>

#include <ost/base.hh>
#include <ost/img/data.hh>
#include <ost/img/data_observer.hh>
#include <ost/img/alg/norm.hh>   

#include <ost/gui/main_window.hh>

#include "overlay_base_fw.hh"
#include "overlay_manager_fw.hh"
#include "overlay_manager_gui.hh"
#include "argand.hh"
#include "info_panel.hh"
#include "fft_panel.hh"
#include <ost/gui/module_config.hh>

//fw decl
class QLabel;

namespace ost { 

namespace gui {
class GostyApp;
} //ns

namespace img { namespace gui {

//fw decl
class DataViewerPanel;

//! Data viewer
class DLLEXPORT_OST_GUI DataViewer: public ost::gui::MainWindow
{
  Q_OBJECT;

  friend class ost::gui::GostyApp; // for creation

public:
  virtual ~DataViewer();

  //! set new image or function to display
  void SetData(const Data& data);

  //! retrieve used normalizer
  NormalizerPtr GetNormalizer() const;

  //! re-apply normalization using current normalizer
  void Renormalize();

  void Recenter();

  //! return currently active selection
  Extent GetSelection() const;

  //! set the name, displayed as the window title
  void SetName(const String& name);

  //! add a new overlay
  int AddOverlay(const OverlayPtr& ov, bool make_active=true);

  //! remove all overlays
  void ClearOverlays();

  //! return the overlay manager for this viewer
  OverlayManagerPtr GetOverlayManager() const;

  //! internal use
  virtual void OnPanelMouseEvent(QMouseEvent* e);

  //! enable/disable antialiasing
  void SetAntialiasing(bool f);

  //! event filter for DataViewerPanel
  virtual bool eventFilter(QObject * object, QEvent *event);


public slots:
  //! update view
  void UpdateView();

  void OnSlabChange(int slab);
  void OnZoomChange(int zoomlevel);

 protected:
  //! initialize with data to view, plus a name
  DataViewer(QWidget* p, const Data& data, const QString& name="");

 private:
  // inhibit coping and assignement
  DataViewer(const DataViewer& v);

  DataViewer& operator=(const DataViewer& v) {return *this;}

  QString name_;
  DataViewerPanel* panel_;

  OverlayManagerPtr ov_manager_;
  OverlayManagerGUI* ov_manager_gui_;

  InfoPanel* info_;
  Argand* argand_;
  FFTPanel* fft_;
  
  QLabel* zoomlabel_;
  QLabel* slablabel_;
  QPoint lastmouse_;

  void build(const Data& data);

  void build_menu();
};

}}}  //ns

#endif
