
-- ErdosAtlas/CirclePacking/Certificate.lean
-- Algebraic certificate connection: P18(d) minimal polynomial.
-- Formal level: L1 (statement only)

import ErdosAtlas.CirclePacking.Definitions
import Mathlib.Data.Real.Basic
import Mathlib.Algebra.Polynomial.Basic

namespace ErdosAtlas.CirclePacking.Certificate

open Polynomial

-- P18(d) minimal polynomial (integer coefficients)
-- Source: de Groot, Peikert, Wurtz (1990) / OEIS A281065
def p18Coeffs : List Int :=
  [ 1180129, -11436428, 98015844, -462103584, 1145811528
  , -1398966480, 227573920, 1526909568, -1038261808, -2960321792
  , 7803109440, -9722063488, 7918461504, -4564076288, 1899131648
  , -563649536, 114038784, -14172160, 819200 ]

theorem p18Coeffs_length : p18Coeffs.length = 19 := by decide

-- Leading coefficient: 1180129 = 827 * 1427
theorem p18_leading_factored : (827 : Int) * 1427 = 1180129 := by decide

-- Constant term: 819200 = 2^15 * 5^2
theorem p18_constant_factored : (2 : Int) ^ 15 * 5 ^ 2 = 819200 := by decide

end ErdosAtlas.CirclePacking.Certificate
