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

#include "image_layer.hh"
#include "graphics_image_item.hh"


namespace ost { namespace img { namespace gui {

ImageLayer::ImageLayer(QGraphicsItem* parent):
  QGraphicsItem(parent),
  images_()
{
}

GraphicsImageItem* ImageLayer::AddImage( const Data& data)
{
  GraphicsImageItem* image=new GraphicsImageItem(data,this);
  images_.insert(image);
  return image;
}

void ImageLayer::CenterOn(const QPointF& p)
{
}

QRectF ImageLayer::boundingRect() const
{
  return childrenBoundingRect();
}


void 	ImageLayer::paint( QPainter * painter, const QStyleOptionGraphicsItem * option, QWidget * widget)
{
}

QPointF ImageLayer::GetCenteringPosition()
{
  QRectF rect;
  foreach (GraphicsImageItem* image, images_){
    if(image->HasSelection()){
      Point center=image->GetSelection().GetCenter();
      return QPointF(center[0],center[1]);
    }else{
      rect|=image->boundingRect();
    }
  }
  return rect.center();
}

}}} //ns
