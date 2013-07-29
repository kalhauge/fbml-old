import unittest

from fbml.structure import *

class StructureTester (unittest.TestCase):

    """
    def test_id_from_string(self):
        root = RootPackage(['/directory'])
        name1 = root.make('name1',lambda label: Package)
        name2 = name1.make('name2',Package)
        name_id = Label.from_string('name1.name2',root) 
        self.assertEqual(name_id.get(),name2)
        self.assertListEqual(name_id.get_name_list(),['name1','name2'])
    """

