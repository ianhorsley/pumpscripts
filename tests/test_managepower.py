"""Unittests for src.get_schedule module"""
import unittest
import logging
import os

from managepower import compute_pump_curve

class Setup_Data:
    settings = Dict()

class TestPumpCurve(unittest.TestCase):
    def setUp(self):
        self.setup_data = Setup_Data()

        settings = {'maxrooms': 5,
                    'percperroom': 6,
                    'percforwater': 20,
                    'mincurve': 5,
                    'defaultcurve': 40,
                    'maxcurve': 70,
                    'warmingthres': 30,
                    'warmingmultiplier': 1.6,
                    'maxchangescale': 1.2,
                    }

        self.setup_data.settings['pumpcurveselection'] = settings

    def test_conpute_pump_curve(self):
        #compute_pump_curve(setup_data, return_temp, num_rooms, water_demand, pump_curve_previous)
        self.assertEqual(compute_pump_curve(self.setup_data, 30, 0, 0, 0), 5)


if __name__ == '__main__':
    unittest.main()