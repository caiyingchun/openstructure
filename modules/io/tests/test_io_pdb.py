import unittest
from ost import *

class TestPDB(unittest.TestCase):
  def setUp(self):
    pass

  def test_compnd_parser(self):
    e=io.LoadPDB('testfiles/pdb/compnd.pdb', restrict_chains="A")
    self.assertEquals(e.GetChainCount(), 1)
    ch = e.FindChain("A");
    self.assertEquals(ch.GetIntProp("mol_id"), 1)

  def test_no_bond_feasibility(self):
    profiles=io.IOProfiles()
    profiles['NO_FEAS_CHECK']=io.IOProfile(bond_feasibility_check=False,
                                           processor=conop.HeuristicProcessor())
        
    e=io.LoadPDB('testfiles/pdb/simple_defective.pdb', restrict_chains="A", 
                 profile='NO_FEAS_CHECK')
    
    res=e.FindResidue('A',3)
        
    self.assertTrue(mol.BondExists(res.FindAtom("CA"),res.FindAtom("CB")))
    
if __name__== '__main__':
  from ost import testutils
  testutils.RunTests()


 
