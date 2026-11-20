from itertools import product
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from round26_matrix_consistency import analytic_kernel,determinant_permutations,difference,encode,later_matrix,mm,mv
from matrix_experiments import determinant,inverse,transpose,MATRICES
from round26_source_audit import matrix_post_headers


class Round26Tests(unittest.TestCase):
    def test_two_independent_determinants_agree_and_inverse_multiplies_to_identity(self):
        for a in (MATRICES['old'],MATRICES['new'],[[1,1,1],[1,3,6],[1,1,4]]):
            self.assertEqual(determinant_permutations(a),determinant(a))
            for m in (25,26,29):
                inv=inverse(a,m)
                if inv is not None:self.assertEqual(mm(a,inv,m),[[int(i==j) for j in range(len(a))] for i in range(len(a))])

    def test_general_uncertain_cells_kernel_in_both_conventions(self):
        a=MATRICES['old']
        for x,y in ((-3,12),(2,7),(6,6)):
            d=difference(a,later_matrix(x,y))
            for m in (2,3,4):
                for orientation,operator in [('column',d),('row_as_transpose',transpose(d))]:
                    brute={v for v in product(range(m),repeat=4) if all(x==0 for x in mv(operator,v,m))}
                    self.assertEqual(brute,analytic_kernel(m,orientation,x,y))

    def test_uncertain_lower_count_changes_row_but_not_column_subspace(self):
        self.assertEqual(analytic_kernel(29,'column',6,5),analytic_kernel(29,'column',6,6))
        self.assertNotEqual(analytic_kernel(29,'row_as_transpose',6,5),analytic_kernel(29,'row_as_transpose',6,6))

    def test_even_modulus_extra_vector_and_odd_diagonal_images(self):
        a=MATRICES['old'];b=MATRICES['new']
        self.assertIn((13,0,0,0),analytic_kernel(26,'column'))
        self.assertEqual(mv(a,(13,0,0,0),26),mv(b,(13,0,0,0),26))
        for m in (25,29):
            outputs={mv(a,v,m) for v in analytic_kernel(m,'column')}
            self.assertEqual(outputs,{(t,t,t,t) for t in range(m)})

    def test_ciphertext_update_predicts_changed_ciphertext_and_rejects_unchanged_example(self):
        a=MATRICES['old'];b=MATRICES['new'];m=29;p=(1,2,3,4)
        cold=mv(a,p,m);cnew=mv(b,p,m);operator=mm(b,inverse(a,m),m)
        self.assertEqual(mv(operator,cold,m),cnew);self.assertNotEqual(cold,cnew)
        with self.assertRaises(ValueError):encode([1,2,3],a,m)

    def test_post_date_is_not_registration_date(self):
        source='<li class="postbitlegacy" id="post_123"><span class="date">08-05-2017,&nbsp;<span class="time">00:19</span></span><div>Registro02-12-2009</div>Aproveitei e passeei por hellgate</li>'
        out=matrix_post_headers(source)
        self.assertEqual(out[0]['displayed_post_timestamp'],'2017-05-08T00:19:00')


if __name__=='__main__':unittest.main()
