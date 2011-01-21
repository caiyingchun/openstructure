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

#include <ost/platform.hh>
#include <ost/gfx/map_slab.hh>
#include <ost/gfx/scene.hh>
#include <ost/gfx/map_iso.hh>

#include <ost/gui/gosty_app.hh>
#include <ost/gui/scene_selection.hh>

#include "map_tool.hh"

#include <QDir>
namespace ost { namespace gui {

MapTool::MapTool():
  Tool("Map Tool")
{}

void MapTool::MouseMove(const MouseEvent& event)
{
  int active_node_count = SceneSelection::Instance()->GetActiveNodeCount();
  if(active_node_count > 0){
    for(int i = 0; i<active_node_count;i++){
      gfx::GfxNodeP np=SceneSelection::Instance()->GetActiveNode(i);
      if(np) {
        if(gfx::MapIso* mi = dynamic_cast<gfx::MapIso*>(np.get())) {
          if(event.GetButtons()==MouseEvent::LeftButton) {
            if (event.IsShiftPressed()) {
              gfx::Scene& scene=gfx::Scene::Instance();
              
              geom::Vec3 p1(-event.GetLastPos().x(), 
                            event.GetLastPos().y(), 0);
              geom::Vec3 p2(-event.GetPos().x(), 
                             event.GetPos().y(), 0);
              geom::Vec3 delta=scene.UnProject(p1)-scene.UnProject(p2);
              img::ImageHandle the_map=mi->GetMap();
              img::Extent vis=mi->GetVisibleExtent();
              img::Extent new_vis(vis.GetStart()+img::Point(delta), 
                                  vis.GetEnd()+img::Point(delta));
              mi->SetVisibleExtent(new_vis);
            } else {
              float level = mi->GetLevel();
              float std = mi->GetStdDev();
              if(std::abs(event.GetDelta().x())>std::abs(event.GetDelta().y())) {
                level+=0.01*std*static_cast<Real>(event.GetDelta().x());
              } else {
                level+=0.001*std*static_cast<Real>(event.GetDelta().y());
              }
              mi->SetLevel(level);              
            }
            gfx::Scene::Instance().StatusMessage("");
          }
          if (event.GetButtons()==MouseEvent::MiddleButton) {
            if (event.GetDelta().x()==0) continue;
            int delta=event.GetDelta().x() < 0 ? -2 : 2;
            img::Extent ext=mi->GetVisibleExtent();
            img::Extent new_ext(img::Point(ext.GetStart()[0]+delta, 
                                           ext.GetStart()[1], ext.GetStart()[2]),
                                img::Point(ext.GetEnd()[0]+delta, 
                                           ext.GetEnd()[1], ext.GetEnd()[2]));
            mi->SetVisibleExtent(new_ext);
          }
        } else if(gfx::MapSlab* ms = dynamic_cast<gfx::MapSlab*>(np.get())) {
          mol::Transform tf = gfx::Scene::Instance().GetTransform();
          geom::Plane plane = ms->GetPlane();
          if(event.GetButtons()==MouseEvent::LeftButton) {
            if (event.IsShiftPressed()) {
              geom::Vec3 transl = tf.GetTrans();
              double mm[]={1,0,0,0,
                           0,1,0,0,
                           0,0,1,0,
                           transl[0],transl[1],transl[2],1};
              double pm[16];
              glGetDoublev(GL_PROJECTION_MATRIX,pm);
              GLint vp[4];
              glGetIntegerv(GL_VIEWPORT,vp);
              double wx,wy,wz;
              gluProject(0.0,0.0,0.0,mm,pm,vp,&wx,&wy,&wz);
              double ox,oy,oz;
              gluUnProject(wx+2.0,wy+2.0,wz,mm,pm,vp,&ox,&oy,&oz);
              geom::Vec2 fxy = geom::Vec2(ox,oy);

              geom::Vec3 trans(event.GetDelta().x()*fxy[0],
                               -event.GetDelta().y()*fxy[1],
                               0.0);
              plane.SetOrigin(plane.GetOrigin()+geom::Transpose(tf.GetRot())*trans);
              ms->SetPlane(plane);
            } else {
              plane.SetNormal(tf.GetXAxisRotation(static_cast<Real>(event.GetDelta().y())*0.5)*tf.GetYAxisRotation(static_cast<Real>(event.GetDelta().x())*0.5)*plane.GetNormal());
              ms->SetPlane(plane);
            }
          }
        }
      }
    }
  }
}

bool MapTool::CanOperateOn(gfx::NodePtrList nodes)
{
  if(nodes.size() == 1){
  for(unsigned int i=0; i < nodes.size(); i++){
    if(!dynamic_cast<gfx::MapIso*>(nodes[i].get())){
      return false;
    }
  }
  return true;
  }
  return false;
}

QIcon MapTool::GetIcon() const
{
  QDir icon_path(GetSharedDataPath().c_str());
  icon_path.cd("gui");
  icon_path.cd("icons");
  QIcon icon = QIcon(icon_path.absolutePath()+QDir::separator()+QString("map_icon.png"));
  return icon;
}

}} // ns
