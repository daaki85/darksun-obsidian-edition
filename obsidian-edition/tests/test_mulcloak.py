"""The separate garment must span the back even over a fitted hood, belt or kilt."""
import unittest

from dsloader import classoutfits as co


class MulCloakTests(unittest.TestCase):
    def test_worn_cape_keeps_the_yoke_and_lower_back_continuous(self):
        # Native points in the missing shoulder blade and lower folds of the
        # three-quarter rear drawings, including the bow and all four steps.
        seams = {1: ((12, 10), (11, 15)), 7: ((7, 9), (7, 16)),
                 8: ((8, 9), (7, 16)), 9: ((8, 9), (8, 16)),
                 10: ((8, 9), (9, 15)), 18: ((6, 9), (7, 16)),
                 19: ((7, 9), (8, 16)), 20: ((8, 9), (11, 16)),
                 25: ((8, 12), (9, 18))}
        roles = co.MUL_ROLES.values()
        for role in roles:
            frames = co.frames(role, False, 2093) + co.frames(role, True, 2093)
            reference = co.frames("Fighter", False, 2093) + co.frames("Fighter", True, 2093)
            for pose, (frame, fighter) in enumerate(zip(frames, reference)):
                with self.subTest(role=role, pose=pose):
                    cape = {(x, y): color for x, y, color in frame.equipped_cape}
                    protected = set(frame.head)
                    for bit in (co.FOREARM, co.BOW, co.LEFT_FOOT, co.RIGHT_FOOT):
                        protected.update(frame.regions[bit])
                    self.assertTrue(cape.keys().isdisjoint(protected))
                    self.assertTrue(all(p in cape or p in protected for p in seams.get(pose, ())))
                    # Across outfits the same shoulder seam remains visible,
                    # except where that wearer's hood, toe or elbow crosses it.
                    for x, y, tone in fighter.equipped_cape:
                        if (x, y) not in protected:
                            self.assertEqual(cape.get((x, y)), tone)
