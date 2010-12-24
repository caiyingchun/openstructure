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
#ifndef OST_ENTITY_HANDLE_HH
#define OST_ENTITY_HANDLE_HH

#include <ost/mol/module_config.hh>
#include <ost/mol/transform.hh>

#include "impl/entity_impl_fw.hh"
#include "entity_visitor_fw.hh"
#include "query.hh"
#include "entity_observer_fw.hh"
#include "residue_prop.hh"
#include "entity_view.hh"
#include "chain_handle.hh"
#include "handle_type_fw.hh"
#include "iterator_fw.hh"


#include "editor_type_fw.hh"

namespace ost { namespace mol {

/// \brief create entity
/// \relates EntityHandle
DLLEXPORT_OST_MOL EntityHandle CreateEntity();

/// \brief Protein or molecule
///
/// Molecules such as proteins and ligands are all represented as entities
/// in OpenStructure. To work with subsets of atoms, residues, chains and bonds, 
/// refer to EntityView
///
/// Entities consist of zero or more chains of residues. The interface of
/// entities is tailored to proteins, but is not limited to that. An entity may 
/// also represent a ligand or a collection of water molecules - hence the rather
/// generic name. 
/// A new, empty entity is created with CreateEntity(). Atoms, residues, chains 
/// and bonds are added,removed or manipulated via \ref editors "editors".
class DLLEXPORT_OST_MOL EntityHandle : public EntityBase {
public:
  friend class XCSEditor;
  friend class ICSEditor;
  
  /// internally used ctor
  EntityHandle(const impl::EntityImplPtr&);

  /// default ctor. creates invalid handle.
  EntityHandle();
  
  
  /// \name Handle validity
  //@{
  /// \brief check validity of handle
  /// 
  /// check, whether the entity handle points to a valid entity.
  /// \note It is an error to use any method other than #IsValid, #Impl and 
  ///       #operator bool() when the handle is invalid. An InvalidHandle
  ///       exception will be thrown.
  operator bool() const { return this->IsValid(); }
  /// \brief check validity of handle
  /// \sa #operator bool()
  bool IsValid() const { return Impl().get()!=0; }
  //@}
  /// \brief copy entity, effectively duplicating the whole data structure
  /// 
  /// Alternative atom positions are not handled at all!
  EntityHandle Copy() const;
  


  /// \name Center, Mass and Extent
  //@{
  /// \brief Get entity's center of atoms (not mass weighted)
  ///
  /// Returns the center of all the atoms in an entity. This is
  /// similar to GetCenterOfMass(), but the atoms are not mass weighted
  geom::Vec3 GetCenterOfAtoms() const;
  
  /// \brief Get entity's mass
  Real GetMass() const;
  
  /// \brief Get entity's center of mass (mass weighted)
  geom::Vec3 GetCenterOfMass() const;  

  geom::AlignedCuboid GetBounds() const;
  //@}
  
  /// \brief
  /// swaps implementations on the entity handle level
  void Swap(EntityHandle& eh);

  /// deep swaps the implementations, effectively affecting
  /// _all_ entity handles that point to either
  void DeepSwap(EntityHandle& eh);

  /// \name Observer interface
  //@{
  /// \brief attach observer
  void AttachObserver(const EntityObserverPtr&);
  
  
  /// \brief remove observer
  void DetachObserver(const EntityObserverPtr&);
  //@}


  /// \brief visitor interface
  void Apply(EntityVisitor& v);


  /// \brief Search a specific torsion
  ///
  /// The order of atoms is important. For the torsion to exist, it must have been
  /// added before via AddTorsion.
  /// \return the torsion or an invalid torsion handle if the torsion could not be
  ///      found
  /// \sa DihedralAngle, SetDihedralAngle
  TorsionHandle FindTorsion(const AtomHandle& a1, const AtomHandle& a2,
                            const AtomHandle& a3, const AtomHandle& a4) const;

  /// \brief  Get list of chains
  ChainHandleList GetChainList() const;

  /// \brief Iterator pointing to the beginning of the residues.
  ///
  /// The residues are first ordered by chain and then ascending residue number.
  /// \note The residue range is not fail-safe. If residues are removed or
  ///      the iterators become invalid and the behaviour undefined.
  ResidueHandleIter ResiduesBegin() const;

  /// \brief Iterator pointing to the end of th residues
  ///
  /// The two iterators returned by ResiduesBegin() and ResiduesEnd() form a
  /// half-closed range. It is cheaper to cache the iterator returned by
  /// ResiduesEnd() than to call ResiduesEnd() after very loop, i.e. like
  /// \code
  /// // e is an instance of EntityHandle
  /// for (ResidueHandleIter i=e.ResiduesBegin(), x=e.ResiduesEnd(); i!=x; ++i) {
  ///  . . .
  /// }
  /// \endcode
  ResidueHandleIter ResiduesEnd() const;

  /// \brief Iterator pointing to the beginning of the chains
  ChainHandleIter ChainsBegin() const;

  /// \brief Iterator pointing to the end of the chains
  ChainHandleIter ChainsEnd() const;

  /// \brief Iterator pointing to the beginning of atoms
  AtomHandleIter AtomsBegin() const;

  /// \brief Iterator pointing to the end of atoms
  AtomHandleIter AtomsEnd() const;

  ///\name Single item addressing
  //@{
  /// \brief Find chain by name.
  ///
  /// Find chain within this entity with given name.
  /// \sa      #IsValid, #FindResidue, #FindAtom
  /// \return  The found chain, or an invalid chain handle if no such chain
  ///          exists
  ChainHandle FindChain(const String& name) const;

  /// \brief Find residue by chain and residue number
  ///
  /// Find residue that belongs to the chain with \var name and has \var
  /// number.
  ///
  /// \note    This is identical to writing
  /// \code
  /// ChainHandle chain=entity.FindChain("A");
  /// if (chain.IsValid()) {
  ///   ResidueHandle r=chain.FindResidue(ResNum(120,'A'))
  /// }
  /// \endcode
  /// \sa      #IsValid, #FindChain, #FindAtom
  /// \return  The found residue, or an invalid residue handle if no such
  ///          residue exists.
  ResidueHandle FindResidue(const String& chain_name,
                            const ResNum& number) const;

  /// \brief Find atom by chain name, residue number and atom name
  ///
  /// Find atom with \var atom_name that belongs to the chain with
  /// \var chain_name and residue number \var number.
  ///
  /// \sa      #IsValid, #FindChain, #FindResidue
  /// \return  The found atom, or an invalid atom handle if no such atom exists.
  AtomHandle FindAtom(const String& chain_name,
                      const ResNum& number,
                      const String& atom_name) const;
  //@}

  /// \brief use atom hash to perform fast within lookup
  AtomHandleList FindWithin(const geom::Vec3& pos, Real radius) const;

  /// \brief return view based on a query object
  /// \sa Query
  EntityView Select(const Query& q, QueryFlags flags=0) const;

  /// \brief return view based on query String.
  /// \sa Query
  EntityView Select(const String& query_string, QueryFlags flags=0) const;

  /// \brief return a (new) full view of this entity
  EntityView CreateFullView() const;

  /// \brief return a (new) empty view of this entity
  EntityView CreateEmptyView() const;

  /// \brief   Get number of atoms of this entity.
  ///
  /// To count the atoms of a specific chain or residue, use the respective
  /// method of ChainHandle and ResidueHandle.
  /// \sa ResidueHandle::GetAtomCount, ChainHandle::GetAtomCount, #GetResidueCount
  int GetAtomCount() const;

  /// \brief   Get number of residues of this entity.
  ///
  /// To count the atoms of a chain, use the \c GetResidueCount() of
  /// \c ChainHandle.
  /// \sa #GetAtomCount, ChainHandle::GetResidueCount
  int GetResidueCount() const;

  /// \brief Get number of chains of this entity
  int GetChainCount() const;

  /// \brief  Get number of bonds
  int GetBondCount() const;

  /// \brief Get list of bonds
  mol::BondHandleList GetBondList() const;


  /// \brief  Get angle in radians between bonds a1-a2 and a2-a3
  Real GetAngle(const AtomHandle& a1, const AtomHandle& a2,
                const AtomHandle& a3) const;

  /// \brief  Get angle in radians between bonds a1-a2 and a2-a3
  Real GetAngle(const AtomView& a1, const AtomView& a2,
                const AtomView& a3) const;

  const geom::Mat4& GetTransformationMatrix() const;


  const geom::Mat4& GetInvTransformationMatrix() const;

  bool IsTransformationIdentity() const;

  /// \brief get complete list of residues
  /// \sa #ResiduesBegin, #ResiduesEnd
  ResidueHandleList GetResidueList() const;
  
  /// \brief get complete list of atoms
  /// \sa #AtomsBegin, #AtomsEnd
  AtomHandleList GetAtomList() const;
  
  /// \brief Get editor for external coordinate system to manipulate atom 
  ///     positions
  /// \sa editors
  XCSEditor EditXCS(EditMode mode=UNBUFFERED_EDIT) const;
  
  /// \brief Get editor for the internal coordinate system to manipulate 
  ///    torsions bond lengths and angles between bonds
  /// \sa editors
  ICSEditor EditICS(EditMode mode=UNBUFFERED_EDIT) const;  
  
  /// \brief get this handle
  /// 
  /// Useful for templated code and duck-typing in Python
  EntityHandle GetHandle() const;
  bool operator==(const EntityHandle& ref) const;
  bool operator!=(const EntityHandle& ref) const;
};

}}

#endif // OST_ENTITY_HANDLE_HH

