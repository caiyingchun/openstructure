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
#include <boost/python.hpp>
using namespace boost::python;

#include <ost/gfx/entity.hh>
using namespace ost;
using namespace ost::gfx;

#include "color_by_def.hh"

namespace {

void color_by_01(Entity* e,
                 const String& prop, 
                 const Gradient& gradient,
                 float minv,float maxv,
                 mol::Prop::Level hint)
{
  e->ColorBy(prop,gradient,minv,maxv,hint);
}

void color_by_02(Entity* e,
                 const String& prop, 
                 const Gradient& gradient,
                 float minv,float maxv)
{
  e->ColorBy(prop,gradient,minv,maxv);
}

void color_by_03(Entity* e,
                 const String& prop, 
                 const Gradient& gradient,
                 mol::Prop::Level hint)
{
  e->ColorBy(prop,gradient,hint);
}

void color_by_04(Entity* e,
                 const String& prop, 
                 const Gradient& gradient)
{
  e->ColorBy(prop,gradient);
}

void color_by_05(Entity* e,
                 const String& prop, 
                 const Color& c1, const Color& c2,
                 float minv,float maxv,
                 mol::Prop::Level hint)
{
  e->ColorBy(prop,c1,c2,minv,maxv,hint);
}

void color_by_06(Entity* e,
                 const String& prop, 
                 const Color& c1, const Color& c2,
                 float minv,float maxv)
{
  e->ColorBy(prop,c1,c2,minv,maxv);
}

void color_by_07(Entity* e,
                 const String& prop, 
                 const Color& c1, const Color& c2,
                 mol::Prop::Level hint)
{
  e->ColorBy(prop,c1,c2,hint);
}

void color_by_08(Entity* e,
                 const String& prop, 
                 const Color& c1, const Color& c2)
{
  e->ColorBy(prop,c1,c2);
}

void radius_by_01(Entity* e,
                  const String& prop, 
                  float rmin,float rmax,
                  float minv,float maxv,
                  mol::Prop::Level hint)
{
  e->RadiusBy(prop,rmin,rmax,minv,maxv,hint);
}

void radius_by_02(Entity* e,
                  const String& prop, 
                  float rmin,float rmax,
                  float minv,float maxv)
{
  e->RadiusBy(prop,rmin,rmax,minv,maxv);
}

void radius_by_03(Entity* e,
                  const String& prop, 
                  float rmin,float rmax,
                  mol::Prop::Level hint)
{
  e->RadiusBy(prop,rmin,rmax,hint);
}

void radius_by_04(Entity* e,
                  const String& prop, 
                  float rmin,float rmax)
{
  e->RadiusBy(prop,rmin,rmax);
}


void ent_set_color1(Entity* e, const Color& c) {
  e->SetColor(c);
}
void ent_set_color2(Entity* e, const Color& c, const String& s) {
  e->SetColor(c,s);
}


void ent_apply_11(Entity* e, UniformColorOp& uco, bool store){
  e->Apply(uco,store);
}
void ent_apply_12(Entity* e, UniformColorOp& uco){
  e->Apply(uco);
}

void ent_apply_21(Entity* e, ByElementColorOp& beco, bool store){
  e->Apply(beco,store);
}
void ent_apply_22(Entity* e, ByElementColorOp& beco){
  e->Apply(beco);
}

void ent_apply_41(Entity* e, EntityViewColorOp& evco, bool store){
  e->Apply(evco,store);
}
void ent_apply_42(Entity* e, EntityViewColorOp& evco){
  e->Apply(evco);
}

void ent_apply_51(Entity* e, GradientLevelColorOp& glco, bool store){
  e->Apply(glco,store);
}
void ent_apply_52(Entity* e, GradientLevelColorOp& glco){
  e->Apply(glco);
}

#if OST_IMG_ENABLED
void ent_apply_61(Entity* e, MapHandleColorOp& mhco, bool store){
  e->Apply(mhco,store);
}
void ent_apply_62(Entity* e, MapHandleColorOp& mhco){
  e->Apply(mhco);
}
#endif //OST_IMG_ENABLED

template<class T1, class T2>
struct PairToTupleConverter {
  static PyObject* convert(const std::pair<T1, T2>& pair) {
    tuple t=boost::python::make_tuple<T1,T2>(pair.first,pair.second);
    return incref(t.ptr());
  }
};


RenderOptionsPtr ent_sline_opts(Entity* ent)
{
  return ent->GetOptions(RenderMode::SLINE);
}
void (Entity::*set_rm1)(RenderMode::Type, const mol::EntityView&, bool)=&Entity::SetRenderMode;
void (Entity::*set_rm2)(RenderMode::Type)=&Entity::SetRenderMode;
RenderOptionsPtr ent_trace_opts(Entity* ent)
{
  return ent->GetOptions(RenderMode::LINE_TRACE);
}

RenderOptionsPtr ent_simple_opts(Entity* ent)
{
  return ent->GetOptions(RenderMode::SIMPLE);
}

RenderOptionsPtr ent_custom_opts(Entity* ent)
{
  return ent->GetOptions(RenderMode::CUSTOM);
}

RenderOptionsPtr ent_tube_opts(Entity* ent)
{
  return ent->GetOptions(RenderMode::TUBE);
}

RenderOptionsPtr ent_hsc_opts(Entity* ent)
{
  return ent->GetOptions(RenderMode::HSC);
}

RenderOptionsPtr ent_cpk_opts(Entity* ent)
{
  return ent->GetOptions(RenderMode::CPK);
}

}

void export_Entity()
{
  class_<Entity, boost::shared_ptr<Entity>, bases<GfxObj>, boost::noncopyable>("Entity", init<const String&, const mol:: EntityHandle&, optional<const mol:: Query&> >())
    .def(init<const String&, RenderMode::Type, const mol::EntityHandle&, optional<const mol::Query&> >())
    .def(init<const String&, const mol::EntityView&>())
    .def(init<const String&, RenderMode::Type, const mol::EntityView&>())
    .def("SetColor",ent_set_color1)
    .def("SetColor",ent_set_color2)
    .def("SetDetailColor", &Entity::SetDetailColor, arg("sel")=String(""))
    .def("SetColorForAtom", &Entity::SetColorForAtom)
    .def("Rebuild", &Entity::Rebuild)
    .def("UpdatePositions",&Entity::UpdatePositions)
    .def("BlurSnapshot", &Entity::BlurSnapshot)
    .def("SetBlurFactors",&Entity::SetBlurFactors)
    .def("SetBlur",&Entity::SetBlur)
    .def("SetSelection",&Entity::SetSelection)
    .def("GetSelection",&Entity::GetSelection)    
    .add_property("selection", &Entity::GetSelection, 
                  &Entity::SetSelection)
    .def("GetView", &Entity::GetView)
    .def("SetRenderMode", set_rm1, arg("keep")=false)
    .def("SetRenderMode", set_rm2)
    .add_property("view", &Entity::GetView)
    .def("SetVisible", &Entity::SetVisible)
    .def("ColorBy", color_by_01)
    .def("ColorBy", color_by_02)
    .def("ColorBy", color_by_03)
    .def("ColorBy", color_by_04)
    .def("ColorBy", color_by_05)
    .def("ColorBy", color_by_06)
    .def("ColorBy", color_by_07)
    .def("ColorBy", color_by_08)
    COLOR_BY_DEF()
    .def("RadiusBy", radius_by_01)
    .def("RadiusBy", radius_by_02)
    .def("RadiusBy", radius_by_03)
    .def("RadiusBy", radius_by_04)
    .def("ResetRadiusBy", &Entity::ResetRadiusBy)

    .def("ColorByElement",&Entity::ColorByElement)
    .def("CleanColorOps", &Entity::CleanColorOps)
    .def("ReapplyColorOps", &Entity::ReapplyColorOps)
    .def("GetOptions", &Entity::GetOptions)
    .add_property("sline_options", &ent_sline_opts)
    .add_property("simple_options", &ent_simple_opts)    
    .add_property("tube_options", &ent_sline_opts)
    .add_property("custom_options", &ent_custom_opts)
    .add_property("cartoon_options", &ent_hsc_opts)    
    .add_property("cpk_options", &ent_cpk_opts)
    .add_property("trace_options", &ent_trace_opts)
    .def("ApplyRenderOptions", &Entity::ApplyRenderOptions)
    .def("SetOptions", &Entity::SetOptions)
    .def("Apply",&ent_apply_11)
    .def("Apply",&ent_apply_12)
    .def("Apply",&ent_apply_21)
    .def("Apply",&ent_apply_22)
    .def("Apply",&ent_apply_41)
    .def("Apply",&ent_apply_42)
    .def("Apply",&ent_apply_51)
    .def("Apply",&ent_apply_52)
#if OST_IMG_ENABLED
    .def("Apply",&ent_apply_61)
    .def("Apply",&ent_apply_62)
#endif //OST_IMG_ENABLED
  ;
  //register_ptr_to_python<EntityP>();
  
  to_python_converter<std::pair<GfxObjP, mol::AtomHandle>, 
                      PairToTupleConverter<GfxObjP, mol::AtomHandle> >();

}
