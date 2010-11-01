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
  Author: Andreas Schenk
*/

#include <QDebug>
#include <QPainter>
#include "widget_layer_item.hh"
#include <QGraphicsProxyWidget>

namespace ost { namespace img { namespace gui {

WidgetLayerItem::WidgetLayerItem(QGraphicsItem* parent):
  QGraphicsItem(parent)
{
}

void WidgetLayerItem::paint( QPainter * painter, const QStyleOptionGraphicsItem * option, QWidget * widget)
{
}

QRectF WidgetLayerItem::boundingRect() const
{
  return QRectF();
}

void WidgetLayerItem::AddWidget(QWidget* widget)
{
  QGraphicsProxyWidget* proxy=new QGraphicsProxyWidget(this,Qt::Tool);
  proxy->setWidget(widget);
  proxy->setFlag(QGraphicsItem::ItemIsMovable);
  proxy->setOpacity(0.9);
  proxy->setPos(30,30);
}
void WidgetLayerItem::AddWidget(QGraphicsWidget* widget)
{
  widget->setParentItem(this);
  widget->setFlag(QGraphicsItem::ItemIsMovable);
  widget->setOpacity(0.9);
  widget->setPos(30,30);
}

}}} //ns
