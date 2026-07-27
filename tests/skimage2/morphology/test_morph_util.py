"""Tests for `_util`."""

import numpy as np
import pytest
from numpy.testing import assert_array_equal
from scipy import ndimage as ndi

from _skimage2._shared import testing
from _skimage2.morphology import _util


@pytest.mark.parametrize("connectivity", [None, 1, 2])
@pytest.mark.parametrize("ndim", [1, 2, 3])
def test_validate_connectivity_matches_resolve_neighborhood(connectivity, ndim):
    """Scalar/None connectivity shares footprint logic with `_resolve_neighborhood`."""
    conn = 1 if connectivity is None else connectivity
    if conn > ndim:
        pytest.skip("connectivity cannot exceed ndim")

    footprint, offset = _util._validate_connectivity(ndim, connectivity, None)
    expected = _util._resolve_neighborhood(None, conn, ndim)

    testing.assert_equal(footprint, expected)
    testing.assert_equal(offset, np.array(expected.shape) // 2)


def test_validate_connectivity_array_and_explicit_offset():
    footprint = np.ones((2, 2), dtype=bool)
    offset = np.array([0, 1])
    result, result_offset = _util._validate_connectivity(2, footprint, offset)

    testing.assert_equal(result, footprint)
    testing.assert_equal(result_offset, offset)


def test_validate_connectivity_even_shape_requires_offset():
    footprint = np.ones((2, 2), dtype=bool)
    with testing.raises(ValueError, match="unambiguous"):
        _util._validate_connectivity(2, footprint, None)


def test_validate_connectivity_wrong_ndim():
    footprint = np.ones((3, 3), dtype=bool)
    with testing.raises(ValueError, match="dimensions"):
        _util._validate_connectivity(3, footprint, None)


@pytest.mark.parametrize(
    "footprint,connectivity,ndim",
    [
        (None, 1, 2),
        (None, None, 3),
        (np.ones((3, 3), dtype=bool), None, 2),
    ],
)
def test_resolve_neighborhood_basic(footprint, connectivity, ndim):
    result = _util._resolve_neighborhood(footprint, connectivity, ndim)
    if footprint is None:
        conn = ndim if connectivity is None else connectivity
        expected = ndi.generate_binary_structure(ndim, conn)
    else:
        expected = footprint
    testing.assert_equal(result, expected)


def test_resolve_neighborhood_enforce_adjacency():
    footprint = np.ones((5, 5), dtype=bool)
    with testing.raises(ValueError, match="dimension size"):
        _util._resolve_neighborhood(footprint, None, 2, enforce_adjacency=True)

    result = _util._resolve_neighborhood(footprint, None, 2, enforce_adjacency=False)
    testing.assert_equal(result, footprint)


@pytest.mark.parametrize("image_shape", [(111,), (33, 44), (22, 55, 11), (6, 5, 4, 3)])
@pytest.mark.parametrize("order", ["C", "F"])
def test_offsets_to_raveled_neighbors_highest_connectivity(image_shape, order):
    """
    Check scenarios where footprint is always of the highest connectivity
    and all dimensions are > 2.
    """
    footprint = np.ones((3,) * len(image_shape), dtype=bool)
    center = (1,) * len(image_shape)
    offsets = _util._offsets_to_raveled_neighbors(image_shape, footprint, center, order)

    # Assert only neighbors are present, center was removed
    assert len(offsets) == footprint.sum() - 1
    assert 0 not in offsets
    # Assert uniqueness
    assert len(set(offsets)) == offsets.size
    # offsets form pairs of with same value but different signs
    # if footprint is symmetric around center
    assert all(-x in offsets for x in offsets)

    # Construct image whose values are the Manhattan distance to its center
    image_center = tuple(s // 2 for s in image_shape)
    coords = [
        np.abs(np.arange(s, dtype=np.intp) - c)
        for s, c in zip(image_shape, image_center)
    ]
    grid = np.meshgrid(*coords, indexing="ij")
    image = np.sum(grid, axis=0)

    image_raveled = image.ravel(order)
    image_center_raveled = np.ravel_multi_index(image_center, image_shape, order=order)

    # Sample raveled image around its center
    samples = []
    for offset in offsets:
        index = image_center_raveled + offset
        samples.append(image_raveled[index])

    # Assert that center with value 0 wasn't selected
    assert np.min(samples) == 1
    # Assert that only neighbors where selected
    # (highest value == connectivity)
    assert np.max(samples) == len(image_shape)
    # Assert that nearest neighbors are selected first
    assert list(sorted(samples)) == samples


@pytest.mark.parametrize(
    "image_shape", [(2,), (2, 2), (2, 1, 2), (2, 2, 1, 2), (0, 2, 1, 2)]
)
@pytest.mark.parametrize("order", ["C", "F"])
def test_offsets_to_raveled_neighbors_footprint_smaller_image(image_shape, order):
    """
    Test if a dimension indicated by `image_shape` is smaller than in
    `footprint`.
    """
    footprint = np.ones((3,) * len(image_shape), dtype=bool)
    center = (1,) * len(image_shape)
    offsets = _util._offsets_to_raveled_neighbors(image_shape, footprint, center, order)

    # Assert only neighbors are present, center and duplicates (possible
    # for this scenario) where removed
    assert len(offsets) <= footprint.sum() - 1
    assert 0 not in offsets
    # Assert uniqueness
    assert len(set(offsets)) == offsets.size
    # offsets form pairs of with same value but different signs
    # if footprint is symmetric around center
    assert all(-x in offsets for x in offsets)


def test_offsets_to_raveled_neighbors_explicit_0():
    """Check reviewed example."""
    image_shape = (100, 200, 3)
    footprint = np.ones((3, 3, 3), dtype=bool)
    center = (1, 1, 1)
    offsets = _util._offsets_to_raveled_neighbors(image_shape, footprint, center)

    desired = np.array(
        [
            -600,
            -3,
            -1,
            1,
            3,
            600,
            -603,
            -601,
            -599,
            -597,
            -4,
            -2,
            2,
            4,
            597,
            599,
            601,
            603,
            -604,
            -602,
            -598,
            -596,
            596,
            598,
            602,
            604,
        ]
    )
    assert_array_equal(offsets, desired)


def test_offsets_to_raveled_neighbors_explicit_1():
    """Check reviewed example where footprint is larger in last dimension."""
    image_shape = (10, 9, 8, 3)
    footprint = np.ones((3, 3, 3, 4), dtype=bool)
    center = (1, 1, 1, 1)
    offsets = _util._offsets_to_raveled_neighbors(image_shape, footprint, center)

    desired = np.array(
        [
            -216,
            -24,
            -3,
            -1,
            1,
            3,
            24,
            216,
            -240,
            -219,
            -217,
            -215,
            -213,
            -192,
            -27,
            -25,
            -23,
            -21,
            -4,
            -2,
            2,
            4,
            21,
            23,
            25,
            27,
            192,
            213,
            215,
            217,
            219,
            240,
            -243,
            -241,
            -239,
            -237,
            -220,
            -218,
            -214,
            -212,
            -195,
            -193,
            -191,
            -189,
            -28,
            -26,
            -22,
            -20,
            20,
            22,
            26,
            28,
            189,
            191,
            193,
            195,
            212,
            214,
            218,
            220,
            237,
            239,
            241,
            243,
            -244,
            -242,
            -238,
            -236,
            -196,
            -194,
            -190,
            -188,
            188,
            190,
            194,
            196,
            236,
            238,
            242,
            244,
            5,
            -211,
            -19,
            29,
            221,
            -235,
            -187,
            197,
            245,
        ]
    )
    assert_array_equal(offsets, desired)
