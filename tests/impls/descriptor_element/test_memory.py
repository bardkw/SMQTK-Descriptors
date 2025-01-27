from io import BytesIO
import pickle
import unittest

import numpy

from smqtk_core.configuration import configuration_test_helper
from smqtk_descriptors.impls.descriptor_element.memory import DescriptorMemoryElement


class TestDescriptorMemoryElement (unittest.TestCase):

    def test_configuration(self) -> None:
        """ Test instance standard configuration """
        inst = DescriptorMemoryElement('abcd')
        for i in configuration_test_helper(inst, {'uuid'},
                                           ('abcd',)):  # type: DescriptorMemoryElement
            assert i.uuid() == 'abcd'

    def test_pickle_dump_load(self) -> None:
        # Make a couple descriptors
        v1 = numpy.array([1, 2, 3])
        d1 = DescriptorMemoryElement(0)
        d1.set_vector(v1)

        v2 = numpy.array([4, 5, 6])
        d2 = DescriptorMemoryElement(1)
        d2.set_vector(v2)

        d1_s = pickle.dumps(d1)
        d2_s = pickle.dumps(d2)

        # Attempt reconstitution
        d1_r = pickle.loads(d1_s)
        d2_r = pickle.loads(d2_s)

        numpy.testing.assert_array_equal(v1, d1_r.vector())
        numpy.testing.assert_array_equal(v2, d2_r.vector())

    def test_set_state_version_1(self) -> None:
        # Test support of older state version
        expected_uid = 'test-uid'
        expected_v = numpy.array([1, 2, 3])
        expected_v_b = BytesIO()
        # noinspection PyTypeChecker
        numpy.save(expected_v_b, expected_v)
        expected_v_dump = expected_v_b.getvalue()

        # noinspection PyTypeChecker
        # - Using dummy data in constructor for testing __setstate__.
        e = DescriptorMemoryElement('unexpected-uid')
        e.__setstate__((expected_uid, expected_v_dump))
        self.assertEqual(e.uuid(), expected_uid)
        numpy.testing.assert_array_equal(e.vector(), expected_v)

    def test_input_immutability(self) -> None:
        # make sure that data stored is not susceptible to shifts in the
        # originating data matrix they were pulled from.

        #
        # Testing this with a single vector
        #
        v = numpy.random.rand(16)
        t = tuple(v.copy())
        d = DescriptorMemoryElement(0)
        d.set_vector(v)
        v[:] = 0
        self.assertTrue((v == 0).all())
        self.assertFalse(sum(t) == 0.)
        numpy.testing.assert_equal(d.vector(), t)

        #
        # Testing with matrix
        #
        m = numpy.random.rand(20, 16)

        v1 = m[3]
        v2 = m[15]
        v3 = m[19]

        # Save truth values of arrays as immutable tuples (copies)
        t1 = tuple(v1.copy())
        t2 = tuple(v2.copy())
        t3 = tuple(v3.copy())

        d1 = DescriptorMemoryElement(1)
        d1.set_vector(v1)
        d2 = DescriptorMemoryElement(2)
        d2.set_vector(v2)
        d3 = DescriptorMemoryElement(3)
        d3.set_vector(v3)

        numpy.testing.assert_equal(v1, d1.vector())
        numpy.testing.assert_equal(v2, d2.vector())
        numpy.testing.assert_equal(v3, d3.vector())

        # Changing the source should not change stored vectors
        m[:, :] = 0.
        self.assertTrue((v1 == 0).all())
        self.assertTrue((v2 == 0).all())
        self.assertTrue((v3 == 0).all())
        self.assertFalse(sum(t1) == 0.)
        self.assertFalse(sum(t2) == 0.)
        self.assertFalse(sum(t3) == 0.)
        numpy.testing.assert_equal(d1.vector(), t1)
        numpy.testing.assert_equal(d2.vector(), t2)
        numpy.testing.assert_equal(d3.vector(), t3)

    def test_output_immutability(self) -> None:
        # make sure that data stored is not susceptible to modifications after
        # extraction
        v = numpy.ones(16)
        d = DescriptorMemoryElement(0)
        self.assertFalse(d.has_vector())
        d.set_vector(v)
        r = d.vector()
        assert r is not None
        r[:] = 0
        self.assertEqual(r.sum(), 0)
        r_again = d.vector()
        assert r_again is not None
        self.assertEqual(r_again.sum(), 16)

    def test_none_set(self) -> None:
        d = DescriptorMemoryElement(0)
        self.assertFalse(d.has_vector())

        d.set_vector(numpy.ones(16))
        self.assertTrue(d.has_vector())
        numpy.testing.assert_equal(d.vector(), numpy.ones(16))

        d.set_vector(None)
        self.assertFalse(d.has_vector())
        self.assertIs(d.vector(), None)
