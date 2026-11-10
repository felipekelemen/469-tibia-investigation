import importlib.util,json,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('source_validation_inventory',ROOT/'scripts/source_validation_inventory.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class SourceValidationTests(unittest.TestCase):
    def test_transitive_groups_prevent_three_way_split(self):
        records=[{'id':'a','symbols':'ABCD'},{'id':'b','symbols':'CDEF'},{'id':'c','symbols':'EFGH'}]
        self.assertEqual(m.components(records,'symbols',2),[['a','b','c']])
    def test_book_boundaries_do_not_create_shared_context(self):
        books=[{'digits':'123'},{'digits':'456'}]
        self.assertEqual(m.coverage('345',books,3),0)
    def test_inherited_projection_requires_boundaries_and_unique_alignment(self):
        b={'id':'a','codes':['01','23','04'],'symbols':'ABC','digits':'1234','omitted_zero_code_indices':[0,2],'alignment_count_capped_2':1}
        hit=[{'book_id':'a','raw_start':1}]
        p=m.inherited_projections('23',[b],hit)
        self.assertEqual(p[0]['codes'],['23']);self.assertEqual(p[0]['symbols'],'B')
        self.assertEqual(m.inherited_projections('12',[b],[{'book_id':'a','raw_start':0}]),[])
        b['alignment_count_capped_2']=2
        self.assertEqual(m.inherited_projections('23',[b],hit),[])
    def test_chayenne_is_not_new_content(self):
        books=json.loads((ROOT/'data/normalized_books.json').read_text())
        for fragment,n in [('114514519485611451908304576512282177',11),('6612527570584',9)]:
            self.assertEqual(sum(len(list(m.occurrences(b['digits'],fragment))) for b in books),n)
            self.assertEqual(m.coverage(fragment,books,12),len(fragment))
if __name__=='__main__':unittest.main()
