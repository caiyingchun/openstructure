'''
Unit tests for Table class

Author: Tobias Schmidt
'''

import os
import unittest
from ost.table import *
import ost

HAS_NUMPY=True
HAS_MPL=True
try:
  import numpy as np
except ImportError:
  HAS_NUMPY=False

try:
  import matplotlib
  matplotlib.use('Agg')
except ImportError:
  HAS_MPL=False

class TestTable(unittest.TestCase):
  
  def setUp(self):
    ost.PushVerbosityLevel(3)

  def CreateTestTable(self):
    '''
    creates a table with some test data
    
      first  second  third 
    ----------------------
     x            3     NA
     foo         NA  2.200
     NA           9  3.300

    '''
    tab = Table()
    tab.AddCol('first', 'string')
    tab.AddCol('second', 'int')
    tab.AddCol('third', 'float', 3.141)
    self.CompareColCount(tab, 3)
    self.CompareRowCount(tab, 0)
    self.CompareColTypes(tab, ['first','second', 'third'], 'sif')
    tab.AddRow(['x',3, None], merge=None)
    tab.AddRow(['foo',None, 2.2], merge=None)
    tab.AddRow([None,9, 3.3], merge=None)
    return tab

  def CompareRowCount(self, t, row_count):
    '''
    Compare the number of rows
    '''
    self.assertEqual(len(t.rows),
                     row_count,
                     "row count (%i) different from expected value (%i)" \
                     %(len(t.rows), row_count))
  
  def CompareColCount(self, t, col_count):
    '''
    Compare the number of columns
    '''
    self.assertEqual(len(t.col_names),
                     col_count,
                     "column count (%i) different from expected value (%i)" \
                     %(len(t.col_names), col_count))
  
  def CompareColNames(self, t, col_names):
    '''
    Compare all column names of the table with a list of reference col names
    '''
    self.CompareColCount(t, len(col_names))
    for i, (col_name, ref_name) in enumerate(zip(t.col_names, col_names)):
        self.assertEqual(col_name,
                         ref_name,
                         "column name (%s) different from expected name (%s) at col %i" \
                         %(col_name, ref_name, i))
  
  def CompareDataFromDict(self, t, data_dict):
    '''
    Compare all values of a table with reference values given in the form of a
    dictionary containing a list of values for each column.
    '''
    self.CompareColCount(t, len(data_dict))
    for k, v in data_dict.iteritems():
      self.CompareDataForCol(t, k, v)
      
  def CompareDataForCol(self, t, col_name, ref_data):
    '''
    Compare the values of each row of ONE column specified by its name with
    the reference values specified as a list of values for this column.
    '''
    self.CompareRowCount(t, len(ref_data))
    idx = t.GetColIndex(col_name)
    for i, (row, ref) in enumerate(zip(t.rows, ref_data)):
      self.assertEqual(row[idx],
                       ref,
                       "data (%s) in col (%s), row (%i) different from expected value (%s)" \
                       %(row[idx], col_name, i, ref))
              
  def CompareColTypes(self, t, col_names, ref_types):
    '''
    Compare the types of n columns specified by their names with reference
    values specified either as a string consisting of the short type names 
    (e.g 'sfb') or a list of strings consisting of the long type names
    (e.g. ['string','float','bool'])
    '''
    if type(ref_types)==str:
      trans = {'s' : 'string', 'i': 'int', 'b' : 'bool', 'f' : 'float'}
      ref_types = [trans[rt] for rt in ref_types]
    if type(col_names)==str:
      col_names = [col_names]
    self.assertEqual(len(col_names),
                     len(ref_types),
                     "number of col names (%i) different from number of reference col types (%i)" \
                     %(len(col_names), len(ref_types)))
    idxs = [t.GetColIndex(x) for x in col_names]
    for idx, ref_type in zip(idxs, ref_types):
      self.assertEqual(t.col_types[idx],
                       ref_type,
                       "column type (%s) at column %i, different from reference col type (%s)" \
                       %(t.col_types[idx], idx, ref_type))

  def testTableInitEmpty(self):
    '''
    empty table
    '''
    tab = Table()
    self.CompareColCount(tab, 0)
    self.CompareRowCount(tab, 0)
    self.assertRaises(ValueError, tab.GetColIndex, 'a')
    
  def testTableInitSingleColEmpty(self):
    '''
    empty table with one float column:
    
     x 
    ---
    
    '''
    tab = Table(['x'], 'f')
    self.CompareColCount(tab, 1)
    self.CompareRowCount(tab, 0)
    self.CompareColNames(tab, ['x'])
    self.CompareColTypes(tab, 'x', 'f')
    
  def testTableInitMultiColEmpty(self):
    '''
    empty table with multiple column with different types:
    
     x  y  z  a 
    ------------
    
    '''
    tab = Table(['x','y','z','a'], 'sfbi')
    self.CompareColCount(tab, 4)
    self.CompareRowCount(tab, 0)
    self.CompareColNames(tab, ['x','y','z','a'])
    self.CompareColTypes(tab, ['x','y','z','a'], 'sfbi')
    self.CompareColTypes(tab, ['x','y','z','a'], ['string','float','bool','int'])
      
  def testTableInitSingleColSingleValueNonEmpty(self):
    '''
    table with one column and one row:
    
       x   
    -------
      5.000

    '''
    tab = Table(['x'], 'f', x=5)
    self.CompareColCount(tab, 1)
    self.CompareRowCount(tab, 1)
    self.CompareColNames(tab, ['x'])
    self.CompareColTypes(tab, 'x', 'f')
    
  def testTableInitMultiColSingleValueNonEmpty(self):
    '''
    table with three columns and one row:
    
       x      a      z   
    ---------------------
      5.000 False   1.425
    
    '''
    tab = Table(['x','a','z'], 'fbf', x=5, z=1.425, a=False)
    self.CompareColCount(tab, 3)
    self.CompareRowCount(tab, 1)
    self.CompareColNames(tab, ['x','a','z'])
    self.CompareColTypes(tab, ['z','x','a'], 'ffb')
    self.CompareDataFromDict(tab, {'x': [5], 'z': [1.425], 'a': [False]})
    
  def testTableInitMultiColSingleValueAndNoneNonEmpty(self):
    '''
    table with three columns and one row with two None values:
    
       x    a1  zzz 
    ----------------
      5.000 NA   NA 
    '''
    tab = Table(['x','a1','zzz'], 'fbf', x=5)
    self.CompareColCount(tab, 3)
    self.CompareRowCount(tab, 1)
    self.CompareColNames(tab, ['x','a1','zzz'])
    self.CompareColTypes(tab, ['zzz','x','a1'], 'ffb')
    self.CompareDataFromDict(tab, {'x': [5], 'zzz': [None], 'a1': [None]})
  
  def testTableInitSingleColMultiValueNonEmpty(self):
    '''
    table with one column and five row:
    
       x   
    -------
      0.000
      1.000
      2.000
      3.000
      4.000

    '''
    tab = Table(['x'], 'f', x=range(5))
    self.CompareColCount(tab, 1)
    self.CompareRowCount(tab, 5)
    self.CompareColNames(tab, ['x'])
    self.CompareColTypes(tab, 'x', 'f')
    
  def testTableInitMultiColMultiValueNonEmpty(self):
    '''
    table with two column and four rows:
    
      foo     bar
    ---------------
      i         10
      love      11
      unit      12
      tests     13

    '''
    
    tab = Table(['foo', 'bar'], 'si', bar=range(10,14), foo=['i','love','unit','tests'])
    self.CompareColCount(tab, 2)
    self.CompareRowCount(tab, 4)
    self.CompareColNames(tab, ['foo','bar'])
    self.CompareColTypes(tab, ['foo', 'bar'], 'si')
    self.CompareDataFromDict(tab, {'bar': [10,11,12,13], 'foo': ['i','love','unit','tests']})
    
  def testTableInitMultiColMissingMultiValue(self):
    '''
    test if error is raised when creating rows with missing data
    '''
    
    self.assertRaises(ValueError, Table, ['foo', 'bar'], 'si',
                      bar=range(10,14), foo=['i','love','tests'])
    
    
  def testTableInitMultiColMultiValueAndNoneNonEmpty(self):
    '''
    table with two column and four rows with None values:
    
      foo     bar
    ---------------
      i         NA
      love      NA
      unit      NA
      tests     NA

    '''
    tab = Table(['foo', 'bar'], 'si', foo=['i','love','unit','tests'])
    self.CompareColCount(tab, 2)
    self.CompareRowCount(tab, 4)
    self.CompareColNames(tab, ['foo','bar'])
    self.CompareColTypes(tab, ['foo', 'bar'], 'si')
    self.CompareDataFromDict(tab, {'bar': [None,None,None,None], 'foo': ['i','love','unit','tests']})
  
  def testTableAddSingleCol(self):
    '''
    init empty table, add one empty column:
    
     first 
    -------
    
    '''
    tab = Table()
    self.CompareColCount(tab, 0)
    self.CompareRowCount(tab, 0)
    tab.AddCol('first', 'string', 'AB C')
    self.CompareColCount(tab, 1)
    self.CompareRowCount(tab, 0)
    self.CompareColNames(tab, ['first'])
    self.CompareColTypes(tab, 'first', 's')
    
  def testTableAddSingleRow(self):
    '''
    init table with one col, add one row:
    
     first 
    -------
          2
    '''
    tab = Table(['first'],'i')
    self.CompareColCount(tab, 1)
    self.CompareRowCount(tab, 0)
    tab.AddRow([2], merge=None)
    self.CompareColCount(tab, 1)
    self.CompareRowCount(tab, 1)
    self.CompareColNames(tab, ['first'])
    self.CompareColTypes(tab, 'first', 'i')
    self.CompareDataFromDict(tab, {'first': [2]})
    
  def testTableAddSingleColSingleRow(self):
    '''
    init empty table, add one col, add one row:
    
     first 
    -------
          2
    '''
    tab = Table()
    tab.AddCol('first', 'int')
    self.CompareColCount(tab, 1)
    self.CompareRowCount(tab, 0)
    tab.AddRow([2], merge=None)
    self.CompareColCount(tab, 1)
    self.CompareRowCount(tab, 1)
    self.CompareColNames(tab, ['first'])
    self.CompareColTypes(tab, 'first', 'i')
    self.CompareDataFromDict(tab, {'first': [2]})
  
  def testTableAddSingleColWithRow(self):
    '''
    init table with two cols, add row with data, add third column:
    
     first  second  third 
    ----------------------
     x            3  3.141

    '''
    tab = Table(['first','second'],'si')
    self.CompareColCount(tab, 2)
    self.CompareRowCount(tab, 0)
    self.CompareColTypes(tab, ['first','second'], 'si')
    tab.AddRow(['x',3], merge=None)
    self.CompareColCount(tab, 2)
    self.CompareRowCount(tab, 1)
    tab.AddCol('third', 'float', 3.141)
    self.CompareColCount(tab, 3)
    self.CompareRowCount(tab, 1)
    self.CompareColTypes(tab, ['first','third','second'], 'sfi')
    self.CompareDataFromDict(tab, {'second': [3], 'first': ['x'], 'third': [3.141]})
    
  def testTableAddMultiColMultiRow(self):
    '''
    init empty table add three cols, add three rows with data:
    
      first  second  third 
    ----------------------
     x            3  1.000
     foo          6  2.200
     bar          9  3.300

    '''
    tab = Table()
    tab.AddCol('first', 'string')
    tab.AddCol('second', 'int')
    tab.AddCol('third', 'float', 3.141)
    self.CompareColCount(tab, 3)
    self.CompareRowCount(tab, 0)
    self.CompareColTypes(tab, ['first','second', 'third'], 'sif')
    tab.AddRow(['x',3, 1.0], merge=None)
    tab.AddRow(['foo',6, 2.2], merge=None)
    tab.AddRow(['bar',9, 3.3], merge=None)
    self.CompareColCount(tab, 3)
    self.CompareRowCount(tab, 3)
    self.CompareDataFromDict(tab, {'second': [3,6,9], 'first': ['x','foo','bar'], 'third': [1,2.2,3.3]})

  def testTableAddMultiColMultiRowFromDict(self):
    '''
    init empty table add three cols, add three rows with data:
    
      first  second  third 
    ----------------------
     x            3  1.000
     foo          6  2.200
     bar          9  3.300

    '''
    tab = Table()
    tab.AddCol('first', 'string')
    tab.AddCol('second', 'int')
    tab.AddCol('aaa', 'float', 3.141)
    self.CompareColCount(tab, 3)
    self.CompareRowCount(tab, 0)
    self.CompareColTypes(tab, ['first','second', 'aaa'], 'sif')
    tab.AddRow({'first':'x','second':3, 'aaa':1.0}, merge=None)
    tab.AddRow({'aaa':2.2, 'second':6, 'first':'foo'}, merge=None)
    tab.AddRow({'second':9, 'aaa':3.3, 'first':'bar'}, merge=None)
    self.CompareColCount(tab, 3)
    self.CompareRowCount(tab, 3)
    self.CompareDataFromDict(tab, {'second': [3,6,9], 'first': ['x','foo','bar'], 'aaa': [1,2.2,3.3]})
    
  def testTableAddMultiRowMultiCol(self):
    '''
    init empty table add one col, add three rows with data,
    add one col without data, add one col with data:
    
      first  second  third 
    ----------------------
     x        NA     3.141
     foo      NA     3.141
     bar      NA     3.141

    '''
    tab = Table()
    tab.AddCol('first', 'string')
    self.CompareColCount(tab, 1)
    self.CompareRowCount(tab, 0)
    self.CompareColTypes(tab, ['first'], 's')
    tab.AddRow(['x'], merge=None)
    tab.AddRow(['foo'], merge=None)
    tab.AddRow(['bar'], merge=None)
    tab.AddCol('second', 'int')
    tab.AddCol('third', 'float', 3.141)
    self.CompareColCount(tab, 3)
    self.CompareRowCount(tab, 3)
    self.CompareDataFromDict(tab, {'second': [None,None,None],
                                   'first': ['x','foo','bar'],
                                   'third': [3.141, 3.141, 3.141]})

  def testAddRowFromDictWithMerge(self):
    '''
    add rows from dictionary with merge (i.e. overwrite third row with additional data)
    
      x     foo   bar 
    ------------------
     row1  True      1
     row2    NA      2
     row3  False     3
     
    '''
    tab = Table()
    tab.AddCol('x', 'string')
    tab.AddCol('foo', 'bool')
    tab.AddCol('bar', 'int')
    tab.AddRow(['row1',True, 1])
    tab.AddRow(['row2',None, 2])
    tab.AddRow(['row3',False, None])
    self.CompareDataFromDict(tab, {'x': ['row1', 'row2', 'row3'],
                                   'foo': [True, None, False],
                                   'bar': [1, 2, None]})
    tab.AddRow({'x':'row3', 'bar':3}, merge='x')
    self.CompareDataFromDict(tab, {'x': ['row1', 'row2', 'row3'],
                                   'foo': [True, None, False],
                                   'bar': [1, 2, 3]})
    
  def testAddRowFromListWithMerge(self):
    '''
    add rows from list with merge (i.e. overwrite third row with additional data)
    
      x     foo   bar 
    ------------------
     row1  True      1
     row2    NA      2
     row3  True      3
     
    '''
    
    tab = Table()
    tab.AddCol('x', 'string')
    tab.AddCol('foo', 'bool')
    tab.AddCol('bar', 'int')
    tab.AddRow(['row1',True, 1])
    tab.AddRow(['row2',None, 2])
    tab.AddRow(['row3',False, None])
    self.CompareDataFromDict(tab, {'x': ['row1', 'row2', 'row3'],
                                   'foo': [True, None, False],
                                   'bar': [1, 2, None]})
    tab.AddRow(['row3', True, 3], merge='x')
    self.CompareDataFromDict(tab, {'x': ['row1', 'row2', 'row3'],
                                   'foo': [True, None, True],
                                   'bar': [1, 2, 3]})


  def testRaiseErrorOnWrongColumnTypes(self):
    # wrong columns types in init
    self.assertRaises(ValueError, Table, ['bla','bli'], 'ab')
    
    # wrong column types in Coerce
    tab = Table()
    self.assertRaises(ValueError, tab._Coerce, 'bla', 'a')

    # wrong column types in AddCol
    self.assertRaises(ValueError, tab.AddCol, 'bla', 'a')
    
  def testParseColumnTypes(self):
    types = Table._ParseColTypes(['i','f','s','b'])
    self.assertEquals(types, ['int','float','string','bool'])
    
    types = Table._ParseColTypes(['int','float','string','bool'])
    self.assertEquals(types, ['int','float','string','bool'])
    
    types = Table._ParseColTypes(['i','float','s','bool'])
    self.assertEquals(types, ['int','float','string','bool'])

    types = Table._ParseColTypes(['i','fLOAT','S','bool'])
    self.assertEquals(types, ['int','float','string','bool'])
    
    types = Table._ParseColTypes('ifsb')
    self.assertEquals(types, ['int','float','string','bool'])
    
    types = Table._ParseColTypes('int,float,string,bool')
    self.assertEquals(types, ['int','float','string','bool'])
    
    types = Table._ParseColTypes('int,f,s,bool')
    self.assertEquals(types, ['int','float','string','bool'])
    
    types = Table._ParseColTypes('INT,F,s,bOOL')
    self.assertEquals(types, ['int','float','string','bool'])

    types = Table._ParseColTypes('boOl')
    self.assertEquals(types, ['bool'])
    
    types = Table._ParseColTypes('S')
    self.assertEquals(types, ['string'])
    
    types = Table._ParseColTypes(['i'])
    self.assertEquals(types, ['int'])
    
    types = Table._ParseColTypes(['FLOAT'])
    self.assertEquals(types, ['float'])

    self.assertRaises(ValueError, Table._ParseColTypes, 'bfstring')
    self.assertRaises(ValueError, Table._ParseColTypes, ['b,f,string'])
    self.assertRaises(ValueError, Table._ParseColTypes, 'bi2')
    self.assertRaises(ValueError, Table._ParseColTypes, ['b',2,'string'])
    self.assertRaises(ValueError, Table._ParseColTypes, [['b'],['f','string']])
    self.assertRaises(ValueError, Table._ParseColTypes, 'a')
    self.assertRaises(ValueError, Table._ParseColTypes, 'foo')
    self.assertRaises(ValueError, Table._ParseColTypes, ['a'])
    self.assertRaises(ValueError, Table._ParseColTypes, ['foo'])
  
  def testShortLongColumnTypes(self):
    tab = Table(['x','y','z','a'],['i','f','s','b'])
    self.CompareColTypes(tab, ['x','y','z','a'], 'ifsb')
    
    tab = Table(['x','y','z','a'],['int','float','string','bool'])
    self.CompareColTypes(tab, ['x','y','z','a'], 'ifsb')
    
    tab = Table(['x','y','z','a'],['i','float','s','bool'])
    self.CompareColTypes(tab, ['x','y','z','a'], 'ifsb')
    
    tab = Table(['x','y','z','a'],['i','fLOAT','S','bool'])
    self.CompareColTypes(tab, ['x','y','z','a'], 'ifsb')
    
    tab = Table(['x','y','z','a'],'ifsb')
    self.CompareColTypes(tab, ['x','y','z','a'], 'ifsb')
    
    tab = Table(['x','y','z','a'],'int,float,string,bool')
    self.CompareColTypes(tab, ['x','y','z','a'], 'ifsb')
    
    tab = Table(['x','y','z','a'],'int,f,s,bool')
    self.CompareColTypes(tab, ['x','y','z','a'], 'ifsb')
    
    tab = Table(['x','y','z','a'],'INT,F,s,bOOL')
    self.CompareColTypes(tab, ['x','y','z','a'], 'ifsb')
    
    tab = Table(['x'], 'boOl')
    self.CompareColTypes(tab, ['x'], 'b')
    tab = Table(['x'], 'B')
    self.CompareColTypes(tab, ['x'], 'b')
    tab = Table(['x'], ['b'])
    self.CompareColTypes(tab, ['x'], 'b')
    tab = Table(['x'], ['Bool'])
    self.CompareColTypes(tab, ['x'], 'b')
    
    self.assertRaises(ValueError, Table, ['x','y','z'], 'bfstring')
    self.assertRaises(ValueError, Table, ['x','y','z'], ['b,f,string'])
    self.assertRaises(ValueError, Table, ['x','y','z'], 'bi2')
    self.assertRaises(ValueError, Table, ['x','y','z'], ['b',2,'string'])
    self.assertRaises(ValueError, Table, ['x','y','z'], [['b'],['f','string']])
    self.assertRaises(ValueError, Table, ['x'], 'a')
    self.assertRaises(ValueError, Table, ['x'], 'foo')
    self.assertRaises(ValueError, Table, ['x'], ['a'])
    self.assertRaises(ValueError, Table, ['x'], ['foo'])
    
  def testCoerce(self):
    tab = Table()
    
    # None values
    self.assertEquals(tab._Coerce('NA', 'x'), None)
    self.assertEquals(tab._Coerce(None, 'x'), None)
    
    # int type
    self.assertTrue(isinstance(tab._Coerce(2 ,'int'), int))
    self.assertEquals(tab._Coerce(2 ,'int'), 2)
    self.assertTrue(isinstance(tab._Coerce(2.2 ,'int'), int))
    self.assertEquals(tab._Coerce(2.2 ,'int'), 2)
    self.assertEquals(tab._Coerce(True ,'int'), 1)
    self.assertEquals(tab._Coerce(False ,'int'), 0)
    self.assertRaises(ValueError, tab._Coerce, "foo" , 'int')
    
    # float type
    self.assertTrue(isinstance(tab._Coerce(2 ,'float'), float))
    self.assertEquals(tab._Coerce(2 ,'float'), 2.000)
    self.assertTrue(isinstance(tab._Coerce(3.141 ,'float'), float))
    self.assertEquals(tab._Coerce(3.141 ,'float'), 3.141)
    self.assertRaises(ValueError, tab._Coerce, "foo" , 'float')
    
    # string type
    self.assertTrue(isinstance(tab._Coerce('foo' ,'string'), str))
    self.assertTrue(isinstance(tab._Coerce('this is a longer string' ,'string'), str))
    self.assertTrue(isinstance(tab._Coerce(2.2 ,'string'), str))
    self.assertTrue(isinstance(tab._Coerce(2 ,'string'), str))
    self.assertTrue(isinstance(tab._Coerce(True ,'string'), str))
    self.assertTrue(isinstance(tab._Coerce(False ,'string'), str))
    
    # bool type
    self.assertEquals(tab._Coerce(True ,'bool'), True)
    self.assertEquals(tab._Coerce(False ,'bool'), False)
    self.assertEquals(tab._Coerce('falSE' ,'bool'), False)
    self.assertEquals(tab._Coerce('no' ,'bool'), False)
    self.assertEquals(tab._Coerce('not false and not no','bool'), True)
    self.assertEquals(tab._Coerce(0, 'bool'), False)
    self.assertEquals(tab._Coerce(1, 'bool'), True)
    
    # unknown type
    self.assertRaises(ValueError, tab._Coerce, 'bla', 'abc')
    
  def testRemoveCol(self):
    tab = self.CreateTestTable()
    self.CompareDataFromDict(tab, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
    tab.RemoveCol("second")
    self.CompareDataFromDict(tab, {'first': ['x','foo',None], 'third': [None,2.2,3.3]})
    
    # raise error when column is unknown
    tab = self.CreateTestTable()
    self.assertRaises(ValueError, tab.RemoveCol, "unknown col")
    
  def testSortTable(self):
    tab = self.CreateTestTable()
    self.CompareDataFromDict(tab, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
    tab.Sort('first', '-')
    self.CompareDataFromDict(tab, {'first': [None,'foo','x'], 'second': [9,None,3], 'third': [3.3,2.2,None]})
    tab.Sort('first', '+')
    self.CompareDataFromDict(tab, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
    tab.Sort('third', '+')
    self.CompareDataFromDict(tab, {'first': [None,'foo','x'], 'second': [9,None,3], 'third': [3.3,2.2,None]})

  def testSaveLoadTable(self):
    tab = self.CreateTestTable()
    self.CompareDataFromDict(tab, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
    
    # write to disc
    tab.Save("saveloadtable_filename_out.csv")
    out_stream = open("saveloadtable_stream_out.csv", 'w')
    tab.Save(out_stream)
    out_stream.close()
    
    # read from disc
    in_stream = open("saveloadtable_stream_out.csv", 'r')
    tab_loaded_stream = Table.Load(in_stream)
    in_stream.close()
    tab_loaded_fname = Table.Load('saveloadtable_filename_out.csv')
    
    # check content
    self.CompareDataFromDict(tab_loaded_stream, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
    self.CompareDataFromDict(tab_loaded_fname, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
    
    # check Errors for empty/non existing files
    self.assertRaises(IOError, Table.Load, 'nonexisting.file')
    self.assertRaises(IOError, Table.Load, os.path.join('testfiles','emptytable.csv'))
    in_stream = open(os.path.join('testfiles','emptytable.csv'), 'r')
    self.assertRaises(IOError, Table.Load, in_stream)
    
  def testMergeTable(self):
    '''
    Merge the following two tables:
    
    x     y           x     u   
    -------           -------
    1 |  10           1 | 100
    2 |  15           3 | 200
    3 |  20           4 | 400  
    
    to get (only_matching=False):
    
    x      y     u
    ---------------
    1 |   10 |  100
    2 |   15 |   NA
    3 |   20 |  200
    4 |   NA |  400
    
    or (only_matching=True):
    
    x      y     u
    ---------------
    1 |   10 |  100
    3 |   20 |  200
    
    '''
    tab1 = Table(['x','y'],['int','int'])
    tab1.AddRow([1,10])
    tab1.AddRow([2,15])
    tab1.AddRow([3,20])
    
    tab2 = Table(['x','u'],['int','int'])
    tab2.AddRow([1,100])
    tab2.AddRow([3,200])
    tab2.AddRow([4,400])
    
    tab_merged = Merge(tab1, tab2, 'x', only_matching=False)
    tab_merged.Sort('x', order='-')
    self.CompareDataFromDict(tab_merged, {'x': [1,2,3,4], 'y': [10,15,20,None], 'u': [100,None,200,400]})
    
    tab_merged = Merge(tab1, tab2, 'x', only_matching=True)
    tab_merged.Sort('x', order='-')
    self.CompareDataFromDict(tab_merged, {'x': [1,3], 'y': [10,20], 'u': [100,200]})
    
  def testFilterTable(self):
    tab = self.CreateTestTable()
    tab.AddRow(['foo',1,5.15])
    tab.AddRow(['foo',0,1])
    tab.AddRow(['foo',1,12])
    
    # filter on one column
    tab_filtered = tab.Filter(first='foo')
    self.CompareDataFromDict(tab_filtered, {'first':['foo','foo','foo','foo'],
                                            'second':[None,1,0,1],
                                            'third':[2.2,5.15,1.0,12.0]})
    
    # filter on multiple columns
    tab_filtered = tab.Filter(first='foo',second=1)
    self.CompareDataFromDict(tab_filtered, {'first':['foo','foo'],
                                            'second':[1,1],
                                            'third':[5.15,12.0]})
    
    # raise Error when using non existing column name for filtering
    self.assertRaises(ValueError,tab.Filter,first='foo',nonexisting=1)
    
  def testMinTable(self):
    tab = self.CreateTestTable()
    tab.AddCol('fourth','bool',[True,True,False])

    self.assertEquals(tab.Min('first'),'foo')
    self.assertEquals(tab.Min('second'),3)
    self.assertAlmostEquals(tab.Min('third'),2.2)
    self.assertEquals(tab.Min('fourth'),False)
    self.assertRaises(ValueError,tab.Min,'fifth')
    
    self.assertEquals(tab.MinIdx('first'),1)
    self.assertEquals(tab.MinIdx('second'),0)
    self.assertAlmostEquals(tab.MinIdx('third'),1)
    self.assertEquals(tab.MinIdx('fourth'),2)
    self.assertRaises(ValueError,tab.MinIdx,'fifth')
    
    self.assertEquals(tab.MinRow('first'),['foo', None, 2.20, True])
    self.assertEquals(tab.MinRow('second'),['x', 3, None, True])
    self.assertEquals(tab.MinRow('third'),['foo', None, 2.20, True])
    self.assertEquals(tab.MinRow('fourth'),[None, 9, 3.3, False])
    self.assertRaises(ValueError,tab.MinRow,'fifth')
    
  def testMaxTable(self):
    tab = self.CreateTestTable()
    tab.AddCol('fourth','bool',[False,True,True])
    
    self.assertEquals(tab.Max('first'),'x')
    self.assertEquals(tab.Max('second'),9)
    self.assertAlmostEquals(tab.Max('third'),3.3)
    self.assertEquals(tab.Max('fourth'),True)
    self.assertRaises(ValueError,tab.Max,'fifth')
    
    self.assertEquals(tab.MaxIdx('first'),0)
    self.assertEquals(tab.MaxIdx('second'),2)
    self.assertAlmostEquals(tab.MaxIdx('third'),2)
    self.assertEquals(tab.MaxIdx('fourth'),1)
    self.assertRaises(ValueError,tab.MaxIdx,'fifth')
    
    self.assertEquals(tab.MaxRow('first'),['x', 3, None, False])
    self.assertEquals(tab.MaxRow('second'),[None, 9, 3.3, True])
    self.assertEquals(tab.MaxRow('third'),[None, 9, 3.3, True])
    self.assertEquals(tab.MaxRow('fourth'),['foo', None, 2.2, True])
    self.assertRaises(ValueError,tab.MaxRow,'fifth')
    
  def testSumTable(self):
    tab = self.CreateTestTable()
    tab.AddCol('fourth','bool',[False,True,False])
    
    self.assertRaises(TypeError,tab.Sum,'first')
    self.assertEquals(tab.Sum('second'),12)
    self.assertAlmostEquals(tab.Sum('third'),5.5)
    self.assertRaises(TypeError,tab.Sum,'fourth')
    self.assertRaises(ValueError,tab.Sum,'fifth')
    
  def testMedianTable(self):
    tab = self.CreateTestTable()
    tab.AddCol('fourth','bool',[False,True,False])
    
    self.assertRaises(TypeError,tab.Median,'first')
    self.assertEquals(tab.Median('second'),6.0)
    self.assertAlmostEquals(tab.Median('third'),2.75)
    self.assertRaises(TypeError,tab.Median,'fourth')
    self.assertRaises(ValueError,tab.Median,'fifth')
    
  def testMeanTable(self):
    tab = self.CreateTestTable()
    tab.AddCol('fourth','bool',[False,True,False])
    
    self.assertRaises(TypeError,tab.Mean,'first')
    self.assertAlmostEquals(tab.Mean('second'),6.0)
    self.assertAlmostEquals(tab.Mean('third'),2.75)
    self.assertRaises(TypeError,tab.Mean,'fourth')
    self.assertRaises(ValueError,tab.Mean,'fifth')
    
  def testStdDevTable(self):
    tab = self.CreateTestTable()
    tab.AddCol('fourth','bool',[False,True,False])
    
    self.assertRaises(TypeError,tab.StdDev,'first')
    self.assertAlmostEquals(tab.StdDev('second'),3.0)
    self.assertAlmostEquals(tab.StdDev('third'),0.55)
    self.assertRaises(TypeError,tab.StdDev,'fourth')
    self.assertRaises(ValueError,tab.StdDev,'fifth')
    
  def testCountTable(self):
    tab = self.CreateTestTable()
    tab.AddCol('fourth','bool',[False,True,False])
    
    self.assertEquals(tab.Count('first'),2)
    self.assertEquals(tab.Count('second'),2)
    self.assertEquals(tab.Count('third'),2)
    self.assertEquals(tab.Count('fourth'),3)
    self.assertEquals(tab.Count('first', ignore_nan=False),3)
    self.assertEquals(tab.Count('second', ignore_nan=False),3)
    self.assertEquals(tab.Count('third', ignore_nan=False),3)
    self.assertEquals(tab.Count('fourth', ignore_nan=False),3)
    self.assertRaises(ValueError,tab.Count,'fifth')
    
  def testCalcEnrichment(self):
    enrx_ref = [0.0, 0.041666666666666664, 0.083333333333333329, 0.125, 0.16666666666666666, 0.20833333333333334, 0.25, 0.29166666666666669, 0.33333333333333331, 0.375, 0.41666666666666669, 0.45833333333333331, 0.5, 0.54166666666666663, 0.58333333333333337, 0.625, 0.66666666666666663, 0.70833333333333337, 0.75, 0.79166666666666663, 0.83333333333333337, 0.875, 0.91666666666666663, 0.95833333333333337, 1.0]
    enry_ref = [0.0, 0.16666666666666666, 0.33333333333333331, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.66666666666666663, 0.66666666666666663, 0.83333333333333337, 0.83333333333333337, 0.83333333333333337, 0.83333333333333337, 0.83333333333333337, 0.83333333333333337, 0.83333333333333337, 1.0, 1.0, 1.0, 1.0]
    
    tab = Table(['score', 'rmsd', 'classific'], 'ffb',
                score=[2.64,1.11,2.17,0.45,0.15,0.85,1.13,2.90,0.50,1.03,1.46,2.83,1.15,2.04,0.67,1.27,2.22,1.90,0.68,0.36,1.04,2.46,0.91,0.60],
                rmsd=[9.58,1.61,7.48,0.29,1.68,3.52,3.34,8.17,4.31,2.85,6.28,8.78,0.41,6.29,4.89,7.30,4.26,3.51,3.38,0.04,2.21,0.24,7.58,8.40],
                classific=[False,True,False,True,True,False,False,False,False,False,False,False,True,False,False,False,False,False,False,True,False,True,False,False])
    
    enrx,enry = tab.ComputeEnrichment(score_col='score', score_dir='-',
                                      class_col='rmsd', class_cutoff=2.0,
                                      class_dir='-')
    
    for x,y,refx,refy in zip(enrx,enry,enrx_ref,enry_ref):
      self.assertAlmostEquals(x,refx)
      self.assertAlmostEquals(y,refy)
    
    enrx,enry = tab.ComputeEnrichment(score_col='score', score_dir='-',
                                      class_col='classific')
    
    for x,y,refx,refy in zip(enrx,enry,enrx_ref,enry_ref):
      self.assertAlmostEquals(x,refx)
      self.assertAlmostEquals(y,refy)
    
    tab.AddCol('bad','string','col')
    
    self.assertRaises(TypeError, tab.ComputeEnrichment, score_col='classific',
                      score_dir='-', class_col='rmsd', class_cutoff=2.0,
                      class_dir='-')
    
    self.assertRaises(TypeError, tab.ComputeEnrichment, score_col='bad',
                      score_dir='-', class_col='rmsd', class_cutoff=2.0,
                      class_dir='-')
    
    self.assertRaises(TypeError, tab.ComputeEnrichment, score_col='score',
                      score_dir='-', class_col='bad', class_cutoff=2.0,
                      class_dir='-')
    
    self.assertRaises(ValueError, tab.ComputeEnrichment, score_col='score',
                      score_dir='x', class_col='rmsd', class_cutoff=2.0,
                      class_dir='-')
    
    self.assertRaises(ValueError, tab.ComputeEnrichment, score_col='score',
                      score_dir='+', class_col='rmsd', class_cutoff=2.0,
                      class_dir='y')
    
  def testPlotEnrichment(self):
    if not HAS_MPL:
      return
    tab = Table(['score', 'rmsd', 'classific'], 'ffb',
                score=[2.64,1.11,2.17,0.45,0.15,0.85,1.13,2.90,0.50,1.03,1.46,2.83,1.15,2.04,0.67,1.27,2.22,1.90,0.68,0.36,1.04,2.46,0.91,0.60],
                rmsd=[9.58,1.61,7.48,0.29,1.68,3.52,3.34,8.17,4.31,2.85,6.28,8.78,0.41,6.29,4.89,7.30,4.26,3.51,3.38,0.04,2.21,0.24,7.58,8.40],
                classific=[False,True,False,True,True,False,False,False,False,False,False,False,True,False,False,False,False,False,False,True,False,True,False,False])
 
    pl = tab.PlotEnrichment(score_col='score', score_dir='-',
                            class_col='rmsd', class_cutoff=2.0,
                            class_dir='-')
    #pl.show()
    
  def testCalcEnrichmentAUC(self):
    if not HAS_NUMPY:
      return
    auc_ref = 0.65277777777777779
    tab = Table(['score', 'rmsd', 'classific'], 'ffb',
                score=[2.64,1.11,2.17,0.45,0.15,0.85,1.13,2.90,0.50,1.03,1.46,2.83,1.15,2.04,0.67,1.27,2.22,1.90,0.68,0.36,1.04,2.46,0.91,0.60],
                rmsd=[9.58,1.61,7.48,0.29,1.68,3.52,3.34,8.17,4.31,2.85,6.28,8.78,0.41,6.29,4.89,7.30,4.26,3.51,3.38,0.04,2.21,0.24,7.58,8.40],
                classific=[False,True,False,True,True,False,False,False,False,False,False,False,True,False,False,False,False,False,False,True,False,True,False,False])
 
    auc = tab.ComputeEnrichmentAUC(score_col='score', score_dir='-',
                                   class_col='rmsd', class_cutoff=2.0,
                                   class_dir='-')
    
    self.assertAlmostEquals(auc, auc_ref)
  
  def testTableAsNumpyMatrix(self):

    '''
    checks numpy matrix 
    
      first  second  third  fourth
    -------------------------------
     x            3     NA  True
     foo         NA  2.200  False
     NA           9  3.300  False
    '''
    
    tab = self.CreateTestTable()
    tab.AddCol('fourth','b',[True, False, False])
    m = tab.GetNumpyMatrix('second')
    mc = np.matrix([[3],[None],[9]])
    self.assertTrue(np.all(m==mc))
    mc = np.matrix([[3],[None],[10]])
    self.assertFalse(np.all(m==mc))
    m = tab.GetNumpyMatrix('third')
    mc = np.matrix([[None],[2.200],[3.300]])
    self.assertTrue(np.all(m==mc))
    m = tab.GetNumpyMatrix('second','third')
    mc = np.matrix([[3, None],[None, 2.200],[9, 3.300]])
    self.assertTrue(np.all(m==mc))
    m = tab.GetNumpyMatrix('third','second')
    mc = np.matrix([[None, 3],[2.200, None],[3.300, 9]])
    self.assertTrue(np.all(m==mc))

    self.assertRaises(TypeError, tab.GetNumpyMatrix, 'fourth')
    self.assertRaises(TypeError, tab.GetNumpyMatrix, 'first')
    self.assertRaises(RuntimeError, tab.GetNumpyMatrix)
    
  def testOptimalPrefactors(self):
    if not HAS_NUMPY:
      return
    tab = Table(['a','b','c','d','e','f'],
                'ffffff',
                a=[1,2,3,4,5,6,7,8,9],
                b=[2,3,4,5,6,7,8,9,10],
                c=[1,3,2,4,5,6,8,7,9],
                d=[0.1,0.1,0.1,0.2,0.3,0.3,0.4,0.5,0.8],
                e=[1,1,1,1,1,1,1,1,1],
                f=[9,9,9,9,9,9,9,9,9])
    
    pref = tab.GetOptimalPrefactors('c','a','b')
    self.assertAlmostEquals(pref[0],0.799999999)
    self.assertAlmostEquals(pref[1],0.166666666666)
    
    pref = tab.GetOptimalPrefactors('c','b','a')
    self.assertAlmostEquals(pref[0],0.166666666666)
    self.assertAlmostEquals(pref[1],0.799999999)
    
    pref = tab.GetOptimalPrefactors('c','b','a',weights='e')
    self.assertAlmostEquals(pref[0],0.166666666666)
    self.assertAlmostEquals(pref[1],0.799999999)
    
    pref = tab.GetOptimalPrefactors('c','b','a',weights='f')
    self.assertAlmostEquals(pref[0],0.166666666666)
    self.assertAlmostEquals(pref[1],0.799999999)
    
    pref = tab.GetOptimalPrefactors('c','a','b',weights='d')
    self.assertAlmostEquals(pref[0],0.6078825445851)
    self.assertAlmostEquals(pref[1],0.3394613806088)
    
    self.assertRaises(RuntimeError, tab.GetOptimalPrefactors, 'c','a','b',weight='d')
    self.assertRaises(RuntimeError, tab.GetOptimalPrefactors, 'c',weights='d')
    
  def testIsEmpty(self):
    tab = Table()
    self.assertTrue(tab.IsEmpty())
    self.assertTrue(tab.IsEmpty(ignore_nan=False))
    self.assertRaises(ValueError, tab.IsEmpty, 'a')
    
    # empty table
    tab = Table(['a','b','c'], 'fff')
    self.assertTrue(tab.IsEmpty())
    self.assertTrue(tab.IsEmpty('a'))
    self.assertTrue(tab.IsEmpty('b'))
    self.assertTrue(tab.IsEmpty('c'))
    self.assertTrue(tab.IsEmpty(ignore_nan=False))
    self.assertTrue(tab.IsEmpty('a', ignore_nan=False))
    self.assertTrue(tab.IsEmpty('b', ignore_nan=False))
    self.assertTrue(tab.IsEmpty('c', ignore_nan=False))
    self.assertRaises(ValueError, tab.IsEmpty, 'd')
    
    # fill row with NAN values
    tab.AddRow([None,None,None])
    self.assertTrue(tab.IsEmpty())
    self.assertTrue(tab.IsEmpty('a'))
    self.assertTrue(tab.IsEmpty('b'))
    self.assertTrue(tab.IsEmpty('c'))
    self.assertFalse(tab.IsEmpty(ignore_nan=False))
    self.assertFalse(tab.IsEmpty('a', ignore_nan=False))
    self.assertFalse(tab.IsEmpty('b', ignore_nan=False))
    self.assertFalse(tab.IsEmpty('c', ignore_nan=False))
    
    # fill some values into column 'c' only
    tab.AddRow([None,None,1.0])
    self.assertFalse(tab.IsEmpty())
    self.assertTrue(tab.IsEmpty('a'))
    self.assertTrue(tab.IsEmpty('b'))
    self.assertFalse(tab.IsEmpty('c'))
    self.assertFalse(tab.IsEmpty('a', ignore_nan=False))
    self.assertFalse(tab.IsEmpty('b', ignore_nan=False))
    self.assertFalse(tab.IsEmpty('c', ignore_nan=False))
    
    # fill some values into all columns
    tab.AddRow([2.0,3.0,1.0])
    self.assertFalse(tab.IsEmpty())
    self.assertFalse(tab.IsEmpty('a'))
    self.assertFalse(tab.IsEmpty('b'))
    self.assertFalse(tab.IsEmpty('c'))
    self.assertFalse(tab.IsEmpty('a', ignore_nan=False))
    self.assertFalse(tab.IsEmpty('b', ignore_nan=False))
    self.assertFalse(tab.IsEmpty('c', ignore_nan=False))
      
if __name__ == "__main__":
  try:
    unittest.main()
  except Exception, e:
    print e