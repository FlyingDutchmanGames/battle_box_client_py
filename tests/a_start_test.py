import unittest
from battle_box_client import a_star


def make_adjacent_locations(width, height):
    def adjacent_locations(location):
        (x, y) = location
        adjacent_locations = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return [
                location for location
                in adjacent_locations
                if 0 <= location[0] < width
                and 0 <= location[1] < height
                ]

    return adjacent_locations


class AStarTest(unittest.TestCase):
    def test_start_same_as_end(self):
        loc = (1, 2)
        (path, cost) = a_star(loc, loc, make_adjacent_locations(1, 1))
        self.assertEqual(cost, 0)
        self.assertEqual(path, [(1, 2)])

    def test_path_on_a_1_x_4_board(self):
        (path, cost) = a_star((0, 0), (0, 4), make_adjacent_locations(1, 4))
        self.assertEqual(cost, 0)
        self.assertEqual(path, [(1, 2)])

    def test_with_no_neighbors(self):
        result = a_star((0,0), (1,1), neighbors=(lambda node: []))
        self.assertEqual(result, None)
