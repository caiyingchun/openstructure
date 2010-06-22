//------------------------------------------------------------------------------
// This file is part of the OpenStructure project <www.openstructure.org>
//
// Copyright (C) 2008-2010 by the OpenStructure authors
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
#ifndef OST_GUI_TABBED_PANEL_BAR
#define OST_GUI_TABBED_PANEL_BAR

#include <QHBoxLayout>
#include <QWidget>
#include <QString>
#include <QAction>
#include <QTabWidget>

#include <ost/gui/module_config.hh>
#include <ost/gui/widget_pool.hh>
#include <ost/gui/widget.hh>

#include "panel_widget_container.hh"
#include "button_box.hh"

namespace ost { namespace gui {

/// \brief tabbed bottom Bar
class DLLEXPORT_OST_GUI TabbedPanelBar : public PanelWidgetContainer {
  Q_OBJECT
public:
  TabbedPanelBar(PanelBar* parent);
  ~TabbedPanelBar();

  virtual bool Save(const QString& prefix);
  virtual bool Restore(const QString& prefix);

  void WidgetMoved(Widget* widget, int position);
  QString GetName();
private:
  virtual void ShowWidget(Widget* widget, int pos, bool show);
  QHBoxLayout* layout_;
  QTabWidget* tabWidget_;
};

}}

#endif