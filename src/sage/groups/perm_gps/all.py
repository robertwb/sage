import permgroup as pg

from permgroup_named import (SymmetricGroup, AlternatingGroup,
                       DihedralGroup, CyclicPermutationGroup,
                       DiCyclicGroup, TransitiveGroup, PGL, PSL, PSp,PSU,PGU,
                       MathieuGroup, KleinFourGroup, QuaternionGroup,
                       SuzukiGroup, TransitiveGroups)

from permgroup import  PermutationGroup, PermutationGroup_generic, PermutationGroup_subgroup, direct_product_permgroups

from permgroup_element import PermutationGroupElement,is_PermutationGroupElement

from permgroup_morphism import (is_PermutationGroupMorphism,
                                PermutationGroupMorphism as PermutationGroupMap,
                                PermutationGroupMorphism_im_gens,
                                PermutationGroupMorphism_id)
PermutationGroupMorphism = PermutationGroupMorphism_im_gens

from cubegroup import CubeGroup, RubiksCube
