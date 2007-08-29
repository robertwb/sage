#########################################################################
#       Copyright (C) 2004--2006 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#########################################################################

from constructor import ModularForms, CuspForms, EisensteinForms

from eis_series import eisenstein_series_qexp

from half_integral import half_integral_weight_modform_basis

from theta import theta_qexp, theta2_qexp

from j_invariant import j_invariant_qexp

from vm_basis import victor_miller_basis, delta_qexp

from hecke_operator_on_qexp import (hecke_operator_on_qexp,
                                    hecke_operator_on_basis)
from numerical import NumericalEigenforms as numerical_eigenforms

from element import is_ModularFormElement

#from find_generators import ModularFormsRing, span_of_series, modform_generators
