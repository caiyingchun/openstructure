#------------------------------------------------------------------------------
# This file is part of the OpenStructure project <www.openstructure.org>
#
# Copyright (C) 2008-2016 by the OpenStructure authors
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#------------------------------------------------------------------------------

# Functions to use Antechamber (from AmberTools) to automatically generate force
# field parameters. Allows the execution of Antechamber and the parsing of files
# generated by it.

import _ost_mol_mm as mm
import ost
from ost import settings, mol, geom
import os, subprocess, math

###############################################################################
# helper functions
def _GetInteraction(functype, atoms, params):
  """Get an mm.Interaction with the given func-type and params for the given
  atoms (name and types extracted from there)."""
  interaction = mm.Interaction(functype)
  interaction.SetNames([a.name for a in atoms])
  interaction.SetTypes([a.GetStringProp('type') for a in atoms])
  interaction.SetParam(params)
  return interaction

def _MakeComponentBuildingBlock(eh, ff_dict):
  """Take EntityHandle eh (from ParseModifiedPDB) and ff_dict (from 
  ParseAmberForceField) and return BuildingBlock."""
  # converters: length: A -> nm, angles: deg -> rad, energy: kcal -> kJ
  dist_scale = 1./10.0
  angle_scale = math.pi/180.
  # bond strength in OpenMM needs a factor of 2 compared to Amber
  bond_k_scale = 418.4*2.
  angle_k_scale = 4.184
  
  # get atom typing (dictionary listing all atoms of a certain type)
  atype_dict = {}
  for a in eh.atoms:
    atype = a.GetStringProp('type')
    if not atype in atype_dict:
      atype_dict[atype] = [a.handle]
    else:
      atype_dict[atype].append(a.handle)
  
  # set masses in entity handle (charges and types set in ParseModifiedPDB)
  for atype, mass in ff_dict['MASS']:
    for a in atype_dict[atype]: a.SetMass(mass)
  
  # start by adding atoms
  bb = mm.BuildingBlock()
  for a in eh.atoms:
    bb.AddAtom(a.name, a.GetStringProp('type'), a.GetCharge(), a.GetMass())
  
  # add bonds: first all bonds from the entity, then force-field params
  bl = eh.GetBondList()
  for b in bl:
    a1 = b.GetFirst()
    a2 = b.GetSecond()
    bond = mm.Interaction(mm.FuncType.HarmonicBond)
    bond.SetNames([a1.name, a2.name])
    bond.SetTypes([a1.GetStringProp('type'), a2.GetStringProp('type')])
    bb.AddBond(bond)
  added_bonds = []
  for atype1, atype2, d0, k in ff_dict['BOND']:
    for a1 in atype_dict[atype1]:
      for a2 in atype_dict[atype2]:
        # check connectivity and uniqueness of bond
        if not mol.BondExists(a1, a2): continue
        if [a1, a2] in added_bonds or [a2, a1] in added_bonds: continue
        added_bonds.append([a1,a2])
        params = [d0*dist_scale, k*bond_k_scale]
        bond = _GetInteraction(mm.FuncType.HarmonicBond, [a1, a2], params)
        bb.AddBond(bond, replace_existing=True)
  
  # add angles
  added_angles = []
  for atype1, atype2, atype3, a0, k in ff_dict['ANGL']:
    # a2 is the central atom
    for a2 in atype_dict[atype2]:
      for a1 in atype_dict[atype1]:
        if not mol.BondExists(a1, a2): continue
        for a3 in atype_dict[atype3]:
          # check connectivity and uniqueness of angle
          if not mol.BondExists(a2, a3): continue
          if a1 == a3: continue
          if [a1, a2, a3] in added_angles or [a3, a2, a1] in added_angles:
            continue
          added_angles.append([a1, a2, a3])
          angle = _GetInteraction(mm.FuncType.HarmonicAngle, [a1, a2, a3],
                                  [a0*angle_scale, k*angle_k_scale*2])
          bb.AddAngle(angle)
  
  # add dihedrals
  for atype1, atype2, atype3, atype4, idiv, period, phase, k in ff_dict['DIHE']:
    # there can be multiple ones for the same set of types!
    added_dihedrals = []
    for a1 in atype_dict[atype1]:
      for a2 in atype_dict[atype2]:
        if not mol.BondExists(a1, a2): continue
        for a3 in atype_dict[atype3]:
          if not mol.BondExists(a2, a3): continue
          if a1 == a3: continue
          for a4 in atype_dict[atype4]:
            # check connectivity and uniqueness of dihedral (can be mirrored)
            if not mol.BondExists(a3, a4): continue
            if a2 == a4: continue
            if [a1, a2, a3, a4] in added_dihedrals or \
               [a4, a3, a2, a1] in added_dihedrals: continue
            added_dihedrals.append([a1, a2, a3, a4])
            dihe = _GetInteraction(mm.FuncType.PeriodicDihedral, [a1, a2, a3, a4],
                                   [period, phase*angle_scale, k*angle_k_scale])
            bb.AddDihedral(dihe)
  
  # add impropers
  added_impropers = []
  for atype1, atype2, atype3, atype4, period, phase, k in ff_dict['IMPR']:
    # third atom is the central atom in amber force-field
    for ac in atype_dict[atype3]:
      for a1 in atype_dict[atype1]:
        if not mol.BondExists(ac, a1): continue
        for a2 in atype_dict[atype2]:
          if not mol.BondExists(ac, a2): continue
          if a1 == a2: continue
          for a4 in atype_dict[atype4]:
            # check connectivity and uniqueness of impr. (same central)
            if not mol.BondExists(ac, a4): continue
            if a2 == a4 or a1 == a4: continue
            if [ac, a1, a2, a4] in added_impropers or \
               [ac, a1, a4, a2] in added_impropers or \
               [ac, a2, a1, a4] in added_impropers or \
               [ac, a2, a4, a1] in added_impropers or \
               [ac, a4, a1, a2] in added_impropers or \
               [ac, a4, a2, a1] in added_impropers: continue
            added_impropers.append([ac, a1, a2, a4])
            impr = _GetInteraction(mm.FuncType.PeriodicImproper, [a1, a2, ac, a4],
                                   [period, phase*angle_scale, k*angle_k_scale])
            bb.AddImproper(impr)  
  return bb

def _ParseModifiedPDB(filename):
  """Read mpdb file produced by antechamber and return tuple of:
  - EntityHandle with connectivity, atom types (property 'type') and charges
  - Residue name as extracted from the mpdb file
  A RuntimeError is raised if the file can contains multiple residues.
  """
  eh = mol.CreateEntity()
  rname = ''
  edi = eh.EditXCS(mol.BUFFERED_EDIT)
  chain = edi.InsertChain('A')
  bond_list = []
  # get all atoms and bonds from file
  with open(filename, 'r') as in_file:
    for line in in_file:
      # atom or connectivity
      # -> fixed column format assumed for both
      if line.startswith('ATOM'):
        aname = line[12:17].strip()
        # extract res. name and ensure uniqueness
        if not rname:
          rname = line[17:20].strip()
          r = edi.AppendResidue(chain, rname)
        elif rname != line[17:20].strip():
          raise RuntimeError("More than one residue in file " + filename +\
                             ". Cannot parse!")
        # extract and store type and charge
        charge = float(line[54:66])
        atype = line[78:80].strip()
        a = edi.InsertAtom(r, aname, geom.Vec3())
        a.SetStringProp('type', atype)
        a.SetCharge(charge)
      elif line.startswith('CONECT'):
        ai1 = int(line[6:11])
        # max. 4 bond partners...
        for i in range(4):
          try:
            j = 11 + 5*i
            ai2 = int(line[j:j+5])
            # only unique bonds added to list
            s = set([ai1, ai2])
            if not s in bond_list: bond_list.append(s)
          except:
            # exception thrown for empty strings or non-integers
            # -> skip
            continue
  # set all bonds in entity
  for indices in bond_list:
    indices = list(indices)
    a1 = r.atoms[indices[0]-1]
    a2 = r.atoms[indices[1]-1]
    edi.Connect(a1, a2)
  # finalize
  edi.UpdateICS()
  return eh, rname

def _ParseAmberForceField(filename):
  """Read frcmod file produced by parmchk2 and return dictionary with all
  entries for masses, bonds, angles, dihedrals, impropers and non-bonded (LJ)
  interactions. Stored as key/list-of-value pairs:
  - 'MASS': [atype, mass]
  - 'BOND': [atype1, atype2, d0, k]
  - 'ANGL': [atype1, atype2, atype3, a0, k]
  - 'DIHE': [atype1, atype2, atype3, atype4, idiv, period, phase, k/idiv]
  - 'IMPR': [atype1, atype2, atype3, atype4, period, phase, k]
  - 'NONB': [Rvdw, epsilon]
  """
  keywords = ['MASS', 'BOND', 'ANGL', 'DIHE', 'IMPR', 'NONB']
  with open(filename, 'r') as in_file:
    ff_dict = {}
    for line in in_file:
      # look for keywords
      keyword = line[:4]
      if not keyword in keywords: continue
      # loop until empty line found
      ff_dict[keyword] = []
      line = in_file.next()
      while len(line.strip()) > 0:
        # fixed column format -> extract entries dep. on current keyword
        if keyword == 'MASS':
          atype = line[0:2].strip()
          s = line[2:].split()
          mass = float(s[0])
          ff_dict[keyword].append([atype, mass])
        elif keyword == 'BOND':
          atype1 = line[:2].strip()
          atype2 = line[3:5].strip()
          s = line[5:].split()
          k = float(s[0])
          d0 = float(s[1])
          ff_dict[keyword].append([atype1, atype2, d0, k])
        elif keyword == 'ANGL':
          atype1 = line[:2].strip()
          atype2 = line[3:5].strip()
          atype3 = line[6:8].strip()
          s = line[8:].split()
          k = float(s[0])
          a0 = float(s[1])
          ff_dict[keyword].append([atype1, atype2, atype3, a0, k])
        elif keyword == 'DIHE':
          atype1 = line[:2].strip()
          atype2 = line[3:5].strip()
          atype3 = line[6:8].strip()
          atype4 = line[9:11].strip()
          s = line[11:].split()
          idiv = float(s[0])
          k = float(s[1])
          phase = float(s[2])
          # negative periods = there is more than one term for that dihedral
          # -> no need to do anything special about that here...
          period = abs(float(s[3]))
          ff_dict[keyword].append([atype1, atype2, atype3, atype4, idiv,
                                   period, phase, k/float(idiv)])
        elif keyword == 'IMPR':
          atype1 = line[:2].strip()
          atype2 = line[3:5].strip()
          atype3 = line[6:8].strip()
          atype4 = line[9:11].strip()
          s = line[11:].split()
          k = float(s[0])
          phase = float(s[1])
          period = float(s[2])
          ff_dict[keyword].append([atype1, atype2, atype3, atype4, period,
                                   phase, k])
        elif keyword == 'NONB':
          line = line.strip()
          atype = line[0:2].strip()
          s = line[2:].split()
          Rvdw = float(s[0])
          epsilon = float(s[1])
          ff_dict[keyword].append([atype, Rvdw, epsilon])
        # next...
        line = in_file.next()
  return ff_dict
###############################################################################

def RunAntechamber(res_name, filename, format='ccif', amberhome=None,
                   base_out_dir=None):
  """Run Antechamber to guess force field parameters for a given residue name.

  This requires an installation of AmberTools (tested with AmberTools15) with
  binaries ``antechamber`` and ``parmchk2``.

  This has the same restrictions as Antechamber itself and we assume the input
  to be uncharged. Note that Antechamber cannot deal with metal ions and other
  non-organic elements.

  The results are stored in a separate folder named `res_name` within
  `base_out_dir` (if given, otherwise the current working directory). The main
  output files are ``frcmod`` and ``out.mpdb``. The former contains force field
  parameters and masses. The latter maps atom names to atom types and defines
  the partial charges. The same output could be obtained as follows:

  .. code-block:: console

     $ antechamber -i <FILENAME> -fi <FORMAT> -bk '<RES_NAME>' -o out.mol2 -fo mol2 -c bcc -pf yes
     $ parmchk2 -i out.mol2 -f mol2 -o frcmod -a Y
     $ antechamber -i out.mol2 -fi mol2 -o out.mpdb -fo mpdb -pf yes

  The force field parameters can be manually modified if needed. It can for
  instance happen that some parameters cannot be identified. Those lines will
  be marked with a comment "ATTN, need revision".

  :param res_name: Residue name for which we desire force field parameters.
  :type res_name:  :class:`str`
  :param filename: Path to a file which contains the necessary information for
                   `res_name`. It must include all hydrogens.
  :type filename:  :class:`str`
  :param format: Format of file given with `filename`. Common formats are 'ccif'
                 for PDB's component dictionary or 'pdb' for a PDB file
                 containing the desired residue with all hydrogens.
  :type format:  :class:`str`
  :param amberhome: Base path of your AmberTools installation. If not None,
                    we look for ``antechamber`` and ``parmchk2`` within
                    ``AMBERHOME/bin`` additionally to the system's ``PATH``.
  :type amberhome:  :class:`str`
  :param base_out_dir: Path to a base path, where the output will be stored.
                       If None, the current working directory is used.
  :type base_out_dir:  :class:`str`
  """
  # find antechamber binaries
  if amberhome is None:
    search_paths = []
  else:
    search_paths = [os.path.join(amberhome, 'bin')]
  try:
    antechamber = settings.Locate('antechamber', search_paths=search_paths)
    parmchk2 = settings.Locate('parmchk2', search_paths=search_paths)
  except settings.FileNotFound as ex:
    ost.LogError("Failed to find Antechamber binaries. Make sure you have "
                 "AmberTools installed!")
    raise ex
  
  # prepare path
  cwd = os.getcwd()
  if base_out_dir is None:
    base_out_dir = cwd
  out_dir = os.path.abspath(os.path.join(base_out_dir, res_name))
  if not os.path.exists(out_dir):
    # note: this creates intermediate folders too
    try:
      os.makedirs(out_dir)
    except Exception as ex:
      ost.LogError("Failed to create output directory " + out_dir + "!")
      raise ex
  
  # execute it
  os.chdir(out_dir)
  try:
    cmds = [antechamber + " -i " + filename + " -fi " + format + " -bk " \
            + res_name + " -o out.mol2 -fo mol2 -c bcc -pf yes",
            parmchk2 + " -i out.mol2 -f mol2 -o frcmod -a Y",
            antechamber + " -i out.mol2 -fi mol2 -o out.mpdb -fo mpdb -pf yes"]
    all_sout = "Generating force field parameters for " + res_name + "\n"
    all_serr = ""
    for cmd in cmds:
      all_sout += "-"*70 + "\n" + "Stdout of: " + cmd + "\n" + "-"*70 + "\n"
      all_serr += "-"*70 + "\n" + "Stderr of: " + cmd + "\n" + "-"*70 + "\n"
      job = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
      sout, serr = job.communicate()
      all_sout += sout
      all_serr += serr
      if job.returncode != 0:
        ost.LogError("Unsuccessful execution of " + cmd + ". Return code: "\
                     + str(job.returncode))
    # write command line outputs
    with open("console.stdout", "w") as txt_file:
      txt_file.write(all_sout)
    with open("console.stderr", "w") as txt_file:
      txt_file.write(all_serr)
  except Exception as ex:
    ost.LogError("Failed to excecute antechamber binaries!")
    raise ex
  
  # get back to original path
  os.chdir(cwd)

  # check result
  frcmod_filename = os.path.join(out_dir, 'frcmod')
  mpdb_filename = os.path.join(out_dir, 'out.mpdb')
  if not os.path.exists(frcmod_filename):
    raise RuntimeError("Failed to generate frcmod file with Antechamber!")
  if not os.path.exists(mpdb_filename):
    raise RuntimeError("Failed to generate out.mpdb file with Antechamber!")

def AddFromFiles(force_field, frcmod_filename, mpdb_filename):
  """Add data from a frcmod and an mpdb file to a force field.

  This will add a new :class:`~ost.mol.mm.BuildingBlock` to `force_field` for
  the residue defined in those files (residue name is extracted from the mpdb
  file which can only contain a single residue). Charges for each atom are
  extracted from the mpdb file. According to the frcmod file, an
  :class:`~ost.mol.mm.Interaction` is added for each bond, angle, dihedral and
  improper. Atom types with masses and non-bonded interactions are added to
  `force_field` as needed.

  :param force_field: A force field object to which the new parameters are
                      added.
  :type force_field:  :class:`~ost.mol.mm.Forcefield`
  :param frcmod_filename: Path to ``frcmod`` file as generated by ``parmchk2``.
  :type frcmod_filename:  :class:`str`
  :param mpdb_filename: Path to mpdb file as generated by ``antechamber``.
  :type mpdb_filename:  :class:`str`
  :return: The updated force field (same as `force_field`).
  :rtype:  :class:`~ost.mol.mm.Forcefield`
  """
  # check files
  if not os.path.exists(frcmod_filename):
    raise RuntimeError("Could not find frcmod file: " + frcmod_filename)
  if not os.path.exists(mpdb_filename):
    raise RuntimeError("Could not find mpdb file: " + mpdb_filename)
  # read in files
  try:
    eh, res_name = _ParseModifiedPDB(mpdb_filename)
  except Exception as ex:
    ost.LogError("Failed to parse mpdb file: " + mpdb_filename)
    raise ex
  try:
    ff_dict = _ParseAmberForceField(frcmod_filename)
  except Exception as ex:
    ost.LogError("Failed to parse frcmod file: " + frcmod_filename)
    raise ex
  ost.LogInfo("Adding force field for " + res_name)
  # add atoms to force field
  for aname, mass in ff_dict['MASS']:
    force_field.AddMass(aname, mass)
  # add LJs
  lj_sigma_scale = 2./10./2**(1./6.) # Rvdw to sigma in nm
  lj_epsilon_scale = 4.184           # kcal to kJ
  for aname, Rvdw, epsilon in ff_dict['NONB']:
    # fix 0,0 (from OpenMM's processAmberForceField.py)
    if Rvdw == 0 or epsilon == 0:
      Rvdw, epsilon = 1, 0
    lj = mm.Interaction(mm.FuncType.LJ)
    lj.SetTypes([aname])
    lj.SetParam([Rvdw*lj_sigma_scale, epsilon*lj_epsilon_scale])
    force_field.AddLJ(lj)
  # add building block
  bb = _MakeComponentBuildingBlock(eh, ff_dict)
  force_field.AddBuildingBlock(res_name, bb)

  return force_field

def AddFromPath(force_field, out_dir):
  """Add data from a directory created with :meth:`Run` to a force field.
  See :meth:`AddFromFiles` for details.

  :param force_field: A force field object to which the new parameters are
                      added.
  :type force_field:  :class:`~ost.mol.mm.Forcefield`
  :param out_dir: Output directory as created with :meth:`Run`. Must contain
                  files ``frcmod`` and ``out.mpdb``.
  :type out_dir:  :class:`str`
  :return: The updated force field (same as `force_field`).
  :rtype:  :class:`~ost.mol.mm.Forcefield`
  """
  frcmod_filename = os.path.join(out_dir, 'frcmod')
  mpdb_filename = os.path.join(out_dir, 'out.mpdb')
  return AddFromFiles(force_field, frcmod_filename, mpdb_filename)

def AddIon(force_field, res_name, atom_name, atom_mass, atom_charge, lj_sigma,
           lj_epsilon):
  """Add a single atom as an ion to a force field.

  Since Antechamber cannot deal with ions, you can add simple ones easily with
  this function. This adds a :class:`~ost.mol.mm.BuildingBlock` to `force_field`
  for the given residue name containing a single atom. The atom will have a type
  with the same name as the atom name and the given mass, charge and non-bonded
  (LJ) interaction parameters.

  :param force_field: A force field object to which the ion is added.
  :type force_field:  :class:`~ost.mol.mm.Forcefield`
  :param res_name: Residue name for the ion to be added.
  :type res_name:  :class:`str`
  :param atom_name: Atom name which is also used as atom type name.
  :type atom_name:  :class:`str`
  :param atom_mass: Mass of the atom.
  :type atom_mass:  :class:`float`
  :param atom_charge: Charge of the atom.
  :type atom_charge:  :class:`float`
  :param lj_sigma: The sigma parameter for the non-bonded LJ interaction.
  :type lj_sigma:  :class:`float` in nm
  :param lj_epsilon: The sigma parameter for the non-bonded LJ interaction.
  :type lj_epsilon:  :class:`float` in kJ/mol
  """
  # add mass (atom_type = atom_name)
  force_field.AddMass(atom_name, atom_mass)
  # add building block
  bb = mm.BuildingBlock()
  bb.AddAtom(atom_name, atom_name, atom_charge, atom_mass)
  force_field.AddBuildingBlock(res_name, bb)
  # add dummy LJ
  lj = mm.Interaction(mm.FuncType.LJ)
  lj.SetTypes([atom_name])
  lj.SetParam([lj_sigma, lj_epsilon])
  force_field.AddLJ(lj)

__all__ = ('RunAntechamber', 'AddFromFiles', 'AddFromPath', 'AddIon',)