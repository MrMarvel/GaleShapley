from unittest import TestCase

import numpy as np

import gali_shelli
import main


class TestGaliShelli(TestCase):
    def test_fit(self):
        g = gali_shelli.GaliShelli()
        X = [[2, 1, 3, 4],
             [4, 1, 2, 3],
             [1, 3, 2, 4],
             [2, 3, 1, 4]]
        X = np.array(np.array(X) - 1).tolist()
        Y = [[1, 3, 2, 4],
             [3, 4, 1, 2],
             [4, 2, 3, 1],
             [3, 2, 1, 4]]
        Y = np.array(np.array(Y) - 1).tolist()
        pairs = g.fit(X, Y)
        pairs_result = np.array(np.array(pairs) + 1).tolist()
        self.assertEqual([1, 4, 3, 2], pairs_result[0])


class TestShelliFormatter(TestCase):

    def test_fit2(self):
        g = gali_shelli.GaliShelli()
        X = [[0, 1, 2, 3],  # 123=1 0=0
             [1, 2, 3, 0],
             [1, 2, 3],
             [0]]
        Y = [[0, 2, 1],
             [3, 1, 2, 0],
             [3, 1, 2, 0],
             [3, 1, 2, 0]]
        res_base = g.fit(X, Y)
        X_2 = {'0': ['1', '2'],
               '1': ['2', '1'],
               '2': ['2'],
               '3': ['1']}

        Y_2 = {'1': ['0', '2', '1'],
               '2': ['3', '1', '2', '0']}
        Y2_places = {'1': 1, '2': 3}
        res = main.ShelliFormatter().fit(X_2, Y_2, Y2_places)
        self.assertIsInstance(res, tuple)
        self.assertEqual(2, len(res))
        self.assertTupleEqual((X, Y), res)

    def test_format_data(self):
        X = [[0, 1, 2, 3],
             [1, 2, 3, 0],
             [1, 2, 3],
             [0]]
        Y = [[0, 2, 1],
             [3, 1, 2, 0],
             [3, 1, 2, 0],
             [3, 1, 2, 0]]
        X_2 = {'0': ['1', '2'],
               '1': ['2', '1'],
               '55': ['2'],
               '3': ['1']}

        Y_2 = {'1': ['0', '55', '1'],
               '2': ['3', '1', '55', '0']}
        Y2_places = {'1': 1, '2': 3}
        res = main.ShelliFormatter().fit(X_2, Y_2, Y2_places)
        self.assertIsInstance(res, tuple)
        self.assertEqual(2, len(res))
        self.assertTupleEqual((X, Y), res)

    def test_format_data2(self):
        X = [[0, 1, 2, 3],
             [1, 2, 3, 0],
             [1, 2, 3],
             [0]]
        Y = [[0, 2, 1],
             [3, 1, 2, 0],
             [3, 1, 2, 0],
             [3, 1, 2, 0]]
        X_2 = {'0': ['1', '2'],
               '1': ['2', '1'],
               '55': ['2'],
               '3': ['1']}

        Y_2 = {'1': ['0', '55', '1'],
               '2': ['3', '1', '55', '0']}
        Y2_places = {'1': 1, '2': 3}
        f = main.ShelliFormatter()
        res = f.fit(X_2, Y_2, Y2_places)
        self.assertIsInstance(res, tuple)
        self.assertEqual(2, len(res))
        self.assertTupleEqual((X, Y), res)
        back_res = f.decode(*res)
        self.assertIsInstance(back_res, tuple)
        self.assertEqual(2, len(back_res))
        self.assertTupleEqual((X_2, Y_2), back_res)
        pass


class TestComplexGaleShapleyFormatter(TestCase):
    def test_process(self):
        g = main.GaliShelli()
        X = {'0': ['1', '2'],
             '1': ['2', '1'],
             '55': ['2'],
             '3': ['1']}

        Y = {'1': ['0', '55', '1'],
             '2': ['3', '1', '55', '0']}
        Y_places = {'1': 1, '2': 3}
        f = main.ShelliFormatter()
        X1, Y1 = f.fit(X, Y, Y_places)
        pairsX, pairsY = g.fit(X1, Y1)
        resX, resY = f.decode_result(pairsX, pairsY)
        pass
