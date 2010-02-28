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
#include "file_loader.hh"

#include <QDir>
#include <QAction>
#include <QMenu>
#include <QFileInfo>
#include <QMessageBox>
#include <QMenuBar>


#include <ost/config.hh>
#include <ost/mol/mol.hh>
#include <ost/mol/surface.hh>

#include <ost/io/mol/pdb_reader.hh>
#include <ost/io/mol/load_entity.hh>
#include <ost/io/mol/load_surface.hh>

#include <ost/conop/conop.hh>

#include <ost/gfx/entity.hh>
#include <ost/gfx/surface.hh>
#include <ost/gfx/scene.hh>

#include <ost/gui/gosty_app.hh>
#include <ost/gui/perspective.hh>
#include <ost/gui/python_shell/python_interpreter.hh>
#include <ost/gui/main_area.hh>

#if OST_IMG_ENABLED
  #include <ost/io/img/load_map.hh>
  #include <ost/gfx/map_iso.hh>
  #include <ost/img/extent.hh>
#endif

namespace ost { namespace gui {

LoaderManagerPtr FileLoader::loader_manager_ = LoaderManagerPtr();

#if OST_IMG_ENABLED
  QList<img::ImageHandle> FileLoader::loaded_images_;
#endif

FileLoader::FileLoader(){}

void FileLoader::LoadObject(const QString& file_name)
{
  gfx::GfxObjP obj;
  if(file_name.endsWith(".py",Qt::CaseInsensitive)){
    FileLoader::RunScript(file_name);
  }
  else if(file_name.endsWith(".pdb",Qt::CaseInsensitive)||
      file_name.endsWith(".ent",Qt::CaseInsensitive)||
      file_name.endsWith(".pdb.gz",Qt::CaseInsensitive)||
      file_name.endsWith(".ent.gz",Qt::CaseInsensitive)){
    FileLoader::LoadPDB(file_name);
  }
  else{
    obj=FileLoader::TryLoadEntity(file_name);
    if (!obj)  {
      try{
        obj=FileLoader::TryLoadMap(file_name);
        if (!obj) return;
      } catch (io::IOException&) {
        obj = gfx::GfxObjP();
      }
    }
    if (!obj) {
      obj=FileLoader::TryLoadSurface(file_name);
    }
    if (!obj) {
      QMessageBox messageBox(QMessageBox::Warning, "Error while Loading Entity", 
                             "Could not Open file. No suitable io handler found!");
      messageBox.setStandardButtons( QMessageBox::Ok);
      messageBox.exec();
      return;
    }
    try{
      gfx::Scene::Instance().Add(obj);
    }
    catch (Message m) {
      HandleError(m, obj);
    }
    if (gfx::Scene::Instance().GetRootNode()->GetChildCount()==1) {
      gfx::Scene::Instance().SetCenter(obj->GetCenter());
    }
  }
}

void FileLoader::LoadFrom(const QString& id, const QString& site)
{
  if(!loader_manager_.get())
    loader_manager_ = LoaderManagerPtr(new LoaderManager());
  RemoteSiteLoader* remote_site = loader_manager_->GetRemoteSiteLoader(site);
  if(remote_site){
    remote_site->LoadById(id);
  }
  else{
    remote_site = loader_manager_->GetCurrentSiteLoader();
    if(remote_site){
      remote_site->LoadById(id);
    }
  }
}

LoaderManagerPtr FileLoader::GetLoaderManager()
{
  if(!loader_manager_.get())
    loader_manager_ = LoaderManagerPtr(new LoaderManager());
  return loader_manager_;
}

std::vector<String> FileLoader::GetSiteLoaderIdents()
{
  if(!loader_manager_.get())
    loader_manager_ = LoaderManagerPtr(new LoaderManager());
  return loader_manager_->GetSiteLoaderIdents();
}

void FileLoader::HandleError(Message m, gfx::GfxObjP obj){
  QMessageBox messageBox(QMessageBox::Warning,
      "Error while adding Node to Scene", m._mesg.c_str());
  //Todo Add Rename Button
  messageBox.setStandardButtons( QMessageBox::Yes | QMessageBox::Cancel);
  messageBox.setButtonText(QMessageBox::Yes, "Reload");
  int value = messageBox.exec();
  switch(value){
  case QMessageBox::Yes:
    gfx::Scene::Instance().Remove(obj->GetName());
    gfx::Scene::Instance().Add(obj);
    break;
  }
}

gfx::GfxObjP FileLoader::TryLoadEntity(const QString& filename)
{
  try {
    mol::EntityHandle ent=io::LoadEntity(filename.toStdString());
    QFileInfo file_info(filename);
    gfx::EntityP gfx_ent(new gfx::Entity(file_info.baseName().toStdString(),
                                         ent));
    return gfx_ent;
  } catch (io::IOException& e) {
    return gfx::GfxObjP();
  }
}

gfx::GfxObjP FileLoader::TryLoadMap(const QString& filename) throw(io::IOException)
{
//TODO IMPROVE CODE
#if OST_IMG_ENABLED
  img::ImageHandle map=io::LoadMap(filename.toStdString());
  ost::img::Extent ext = map.GetExtent();
  if(ext.GetSize().GetDepth()>1){
    QFileInfo file_info(filename);
    gfx::MapIsoP map_iso(new gfx::MapIso(file_info.baseName().toStdString(),
                                         map, 0.0));
    map_iso->SetLevel(map_iso->GetMean());
    return map_iso;
  }
  else if(ext.GetSize().GetDepth()==1){
    //FIXME ImageHandle should not be destroyed at the end of method
    //therefore hack with list
    loaded_images_.append(map);
    ost::img::gui::DataViewer* viewer = GostyApp::Instance()->CreateDataViewer(loaded_images_.last());
    gui::GostyApp::Instance()->GetPerspective()->GetMainArea()->AddWidget(filename,viewer);
  }
#else
  throw io::IOException("No IPLT Available");
#endif
  return gfx::GfxObjP();
}

gfx::GfxObjP FileLoader::TryLoadSurface(const QString& filename)
{
  try {
  QFileInfo fi(filename);
  QString path = fi.absolutePath().append(QDir::separator()).append(fi.completeBaseName());
  mol::EntityHandle ent = io::LoadEntity(path.toStdString() + ".pdb");
  mol::SurfaceHandle surf= io::LoadSurface(path.toStdString(),"msms");
  surf.Attach(ent,5.0);
  gfx::SurfaceP gfx_surf(new gfx::Surface(fi.baseName().toStdString(),surf));

  return gfx_surf;
  }catch (io::IOException&) {
    return gfx::GfxObjP();
  }

}

void FileLoader::RunScript(const QString& filename)
{
  PythonInterpreter& pi = PythonInterpreter::Instance();
  //HackerMode On
  //The following code lines are just temporary
  //TODO create class or function which can load any kind of files and execute scripts
  pi.RunCommand("_dir=os.getcwd()");
  pi.RunCommand("os.chdir('"+QFileInfo(filename).absolutePath()+"')");
  pi.RunCommand("execfile('"+QFileInfo(filename).fileName()+"')");
  pi.RunCommand("os.chdir(_dir)");
  //HackerMode Off
}

void FileLoader::LoadPDB(const QString& filename)
{
  io::PDBReader reader(filename.toStdString());
  QList<mol::EntityHandle> entities;
  conop::BuilderP builder=conop::Conopology::Instance().GetBuilder("DEFAULT");
  while (reader.HasNext()){
    mol::EntityHandle ent=mol::CreateEntity();
    reader.Import(ent);
    conop::Conopology::Instance().ConnectAll(builder,ent,0);
    entities.append(ent);
  }

  QFileInfo file_info(filename);
  if(entities.size()==1){
    gfx::EntityP gfx_ent(new gfx::Entity(file_info.baseName().toStdString(),entities.first()));
    try{
      gfx::Scene::Instance().Add(gfx_ent);
    }
    catch (Message m) {
      HandleError(m, gfx_ent);
    }
    if (gfx::Scene::Instance().GetRootNode()->GetChildCount()==1) {
      gfx::Scene::Instance().SetCenter(gfx_ent->GetCenter());
    }
  }
  else{
    try{
      for(int i = 0 ; i<entities.size(); i++){
        gfx::EntityP gfx_ent(new gfx::Entity(QString(file_info.baseName()+" ("+QString::number(i)+")").toStdString(),entities[i]));
        gfx::Scene::Instance().Add(gfx_ent);
      }
    }
    catch (Message m) {
      QMessageBox messageBox(QMessageBox::Warning,
            "Error while adding Nodes to Scene", m._mesg.c_str());
      messageBox.setStandardButtons( QMessageBox::Ok);
      messageBox.exec();
    }
  }
}

FileLoader::~FileLoader(){}

} }
