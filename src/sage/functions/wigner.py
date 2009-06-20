r"""
Calculate Wigner 3j, 6j, 9j, Clebsch-Gordan, Racah and Gaunt
coefficients

Collection of functions for calculating Wigner 3j, 6j, 9j,
Clebsch-Gordan, Racah as well as Gaunt coefficients exactly, all
evaluating to a rational number times the square root of a rational
number [Rasch03].

Please see the description of the individual functions for further
details and examples.


REFERENCES:

- [Rasch03] 'Efficient Storage Scheme for Pre-calculated Wigner 3j, 6j
  and Gaunt Coefficients', J. Rasch and A. C. H. Yu, SIAM
  J. Sci. Comput. Volume 25, Issue 4, pp. 1416-1428 (2003)


AUTHORS:

- Jens Rasch (2009-03-24): initial version for Sage
- Jens Rasch (2009-05-31): updated to sage-4.0

"""

#***********************************************************************
#       Copyright (C) 2008 Jens Rasch <jyr2000@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#***********************************************************************

from sage.symbolic.constants import pi
from sage.rings.integer import Integer
from sage.rings.complex_number import ComplexNumber
from sage.rings.integer_mod import Mod

# This list of precomputed factorials is needed to massively
# accelerate future calculations of the various coefficients
_Factlist=[1]

def _calc_factlist(nn):
    r"""
    Function calculates a list of precomputed factorials in order to
    massively accelerate future calculations of the various
    coefficients.

    INPUT:

     - nn Highest factorial to be computed

    OUTPUT:

    integer list of factorials


    EXAMPLES:

    Calculate list of factorials:

        sage: from sage.functions.wigner import _calc_factlist
        sage: _calc_factlist(10)
        [1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880, 3628800]
    """
    if nn>=len(_Factlist):
        for ii in range(len(_Factlist),nn+1):
            _Factlist.append(_Factlist[ii-1]*ii)
            #_Factlist.append(factorial(ii))
    return _Factlist[:Integer(nn)+1]




def Wigner3j(j_1,j_2,j_3,m_1,m_2,m_3,prec=None):
    r"""
    Calculate the Wigner 3j symbol Wigner3j(j_1,j_2,j_3,m_1,m_2,m_3)


    NOTES:

    The Wigner 3j symbol obeys the following symmetry rules:

    - invariant under any permutation of the columns (with the
      exception of a sign change where $J:=j_1+j_2+j_3$):
      Wigner3j(j_1,j_2,j_3,m_1,m_2,m_3)
          =Wigner3j(j_3,j_1,j_2,m_3,m_1,m_2)
          =Wigner3j(j_2,j_3,j_1,m_2,m_3,m_1)
          =(-)^J Wigner3j(j_3,j_2,j_1,m_3,m_2,m_1)
          =(-)^J Wigner3j(j_1,j_3,j_2,m_1,m_3,m_2)
          =(-)^J Wigner3j(j_2,j_1,j_3,m_2,m_1,m_3)

    - invariant under space inflection, i. e.
      Wigner3j(j_1,j_2,j_3,m_1,m_2,m_3)
         =(-)^J Wigner3j(j_1,j_2,j_3,-m_1,-m_2,-m_3)

    - symmetric with respect to the 72 additional symmetries based on
      the work by [Regge58]

    - zero for $j_1$, $j_2$, $j_3$ not fulfilling triangle relation

    - zero for $m_1+m_2+m_3!= 0$

    - zero for violating any one of the conditions
      $j_1\ge|m_1|$,  $j_2\ge|m_2|$,  $j_3\ge|m_3|$


    ALGORITHM:

    This function uses the algorithm of [Edmonds74] to calculate the
    value of the 3j symbol exactly. Note that the formula contains
    alternating sums over large factorials and is therefore unsuitable
    for finite precision arithmetic and only useful for a computer
    algebra system [Rasch03].



    INPUT:

    j_1 - integer or half integer
    j_2 - integer or half integer
    j_3 - integer or half integer
    m_1 - integer or half integer
    m_2 - integer or half integer
    m_3 - integer or half integer
    prec - precision, default: None. Providing a precision can
           drastically speed up the calculation.


    OUTPUT:

    The result will be a rational number times the square root of a
    rational number, unless a precision is given.


    EXAMPLES:

    A couple of examples:

        sage: Wigner3j(2,6,4,0,0,0)
        sqrt(5/143)

        sage: Wigner3j(2,6,4,0,0,1)
        0

        sage: Wigner3j(0.5,0.5,1,0.5,-0.5,0)
        sqrt(1/6)

        sage: Wigner3j(40,100,60,-10,60,-50)
        95608/18702538494885*sqrt(21082735836735314343364163310/220491455010479533763)

        sage: Wigner3j(2500,2500,5000,2488,2400,-4888 ,prec=64)
        7.60424456883448589e-12


    It is an error to have arguments that are not integer or half
    integer values:

        sage: Wigner3j(2.1,6,4,0,0,0)
        Traceback (most recent call last):
        ...
        ValueError: j values must be integer or half integer

        sage: Wigner3j(2,6,4,1,0,-1.1)
        Traceback (most recent call last):
        ...
        ValueError: m values must be integer or half integer



    REFERENCES:

    - [Regge58] 'Symmetry Properties of Clebsch-Gordan Coefficients',
      T. Regge, Nuovo Cimento, Volume 10, pp. 544 (1958)

    - [Edmonds74] 'Angular Momentum in Quantum Mechanics',
      A. R. Edmonds, Princeton University Press (1974)

    - [Rasch03] 'Efficient Storage Scheme for Pre-calculated Wigner 3j,
      6j and Gaunt Coefficients', J. Rasch and A. C. H. Yu, SIAM
      J. Sci. Comput. Volume 25, Issue 4, pp. 1416-1428 (2003)


    AUTHORS:

    - Jens Rasch (2009-03-24): initial version

    """

    if int(j_1*2)!=j_1*2 or int(j_2*2)!=j_2*2 or int(j_3*2)!=j_3*2:
        raise ValueError("j values must be integer or half integer")
        #return 0
    if int(m_1*2)!=m_1*2 or int(m_2*2)!=m_2*2 or int(m_3*2)!=m_3*2:
        raise ValueError("m values must be integer or half integer")
        #return 0
    if (m_1+m_2+m_3<>0):
        return 0
    prefid=Integer((-1)**(int(j_1-j_2-m_3)))
    m_3=-m_3
    a1=j_1+j_2-j_3
    if (a1<0):
        return 0
    a2=j_1-j_2+j_3
    if (a2<0):
        return 0
    a3=-j_1+j_2+j_3
    if (a3<0):
        return 0
    if (abs(m_1)>j_1) or (abs(m_2)>j_2) or (abs(m_3)>j_3):
        return 0

    maxfact=max(j_1+j_2+j_3+1,j_1+abs(m_1),j_2+abs(m_2),j_3+abs(m_3))
    _calc_factlist(maxfact)

    #try:
    argsqrt=Integer(_Factlist[int(j_1+j_2-j_3)]\
                     *_Factlist[int(j_1-j_2+j_3)]\
             *_Factlist[int(-j_1+j_2+j_3)]\
             *_Factlist[int(j_1-m_1)]*_Factlist[int(j_1+m_1)]\
             *_Factlist[int(j_2-m_2)]*_Factlist[int(j_2+m_2)]\
             *_Factlist[int(j_3-m_3)]*_Factlist[j_3+m_3])\
             /_Factlist[int(j_1+j_2+j_3+1)]\
    #except:
    #    return 0

    ressqrt=argsqrt.sqrt(prec)
    if type(ressqrt) is ComplexNumber:
        ressqrt=ressqrt.real()

    imin=max(-j_3+j_1+m_2,-j_3+j_2-m_1,0)
    imax=min(j_2+m_2,j_1-m_1,j_1+j_2-j_3)
    sumres=0
    for ii in range(imin,imax+1):
        den=_Factlist[ii]*_Factlist[int(ii+j_3-j_1-m_2)]\
             *_Factlist[int(j_2+m_2-ii)]*_Factlist[int(j_1-ii-m_1)]\
             *_Factlist[int(ii+j_3-j_2+m_1)]\
             *_Factlist[int(j_1+j_2-j_3-ii)]
        sumres=sumres+Integer((-1)**ii)/den

    res=ressqrt*sumres*prefid
    return res


def ClebschGordan(j_1,j_2,j_3,m_1,m_2,m_3,prec=None):
    r"""
    Calculates the Clebsch-Gordan coefficient

    $< j_1 m_1 \; j_2 m_2 | j_3 m_3 >$


    NOTES:

    The Clebsch-Gordan coefficient will be evaluated via its relation
    to Wigner 3j symbols:
    < j_1 m_1 \; j_2 m_2 | j_3 m_3 >
        =(-1)^(j_1-j_2+m_3) \sqrt(2j_3+1) Wigner3j(j_1,j_2,j_3,m_1,m_2,-m_3)

    See also the documentation on Wigner 3j symbols which exhibit much
    higher symmetry relations that the Clebsch-Gordan coefficient.


    INPUT:

    j_1 - integer or half integer
    j_2 - integer or half integer
    j_3 - integer or half integer
    m_1 - integer or half integer
    m_2 - integer or half integer
    m_3 - integer or half integer
    prec - precision, default: None. Providing a precision can
           drastically speed up the calculation.


    OUTPUT:

    The result will be a rational number times the square root of a
    rational number, unless a precision is given.


    EXAMPLES:

    A couple of examples:

        sage: simplify(ClebschGordan(3/2,1/2,2, 3/2,1/2,2))
        1

        sage: ClebschGordan(1.5,0.5,1, 1.5,-0.5,1)
        1/2*sqrt(3)

        sage: ClebschGordan(3/2,1/2,1, -1/2,1/2,0)
        -sqrt(1/6)*sqrt(3)


    REFERENCES:

    - [Edmonds74] 'Angular Momentum in Quantum Mechanics',
      A. R. Edmonds, Princeton University Press (1974)

    - [Rasch03] 'Efficient Storage Scheme for Pre-calculated Wigner 3j,
      6j and Gaunt Coefficients', J. Rasch and A. C. H. Yu, SIAM
      J. Sci. Comput. Volume 25, Issue 4, pp. 1416-1428 (2003)


    AUTHORS:

    - Jens Rasch (2009-03-24): initial version

    """

    res=(-1)**(int(j_1-j_2+m_3))*(2*j_3+1).sqrt(prec)\
         *Wigner3j(j_1,j_2,j_3,m_1,m_2,-m_3,prec)
    return res





def _bigDeltacoeff(aa,bb,cc,prec=None):
    r"""
    Calculates the Delta coefficient of the 3 angular momenta for
    Racah symbols. Also checks that the differences are of integer
    value.

    INPUT:

     - aa - first angular momentum, integer or half integer
     - bb - second angular momentum, integer or half integer
     - cc - third angular momentum, integer or half integer
     - prec - precision of the sqrt() calculation

    OUTPUT:

    double - Value of the Delta coefficient


    EXAMPLES:

    Simple examples:

        sage: from sage.functions.wigner import _bigDeltacoeff
        sage: _bigDeltacoeff(1,1,1)
        1/2*sqrt(1/6)

    """

    if(int(aa+bb-cc)!=(aa+bb-cc)):
        raise ValueError("j values must be integer or half integer and fulfil the triangle relation")
        #return 0
    if(int(aa+cc-bb)!=(aa+cc-bb)):
        raise ValueError("j values must be integer or half integer and fulfil the triangle relation")
        #return 0
    if(int(bb+cc-aa)!=(bb+cc-aa)):
        raise ValueError("j values must be integer or half integer and fulfil the triangle relation")
        #return 0
    if(aa+bb-cc)<0:
        return 0
    if(aa+cc-bb)<0:
        return 0
    if(bb+cc-aa)<0:
        return 0

    maxfact=max(aa+bb-cc,aa+cc-bb,bb+cc-aa,aa+bb+cc+1)
    _calc_factlist(maxfact)

    argsqrt=Integer(_Factlist[int(aa+bb-cc)]*_Factlist[int(aa+cc-bb)]\
                    *_Factlist[int(bb+cc-aa)])\
                    /Integer(_Factlist[int(aa+bb+cc+1)])

    ressqrt=argsqrt.sqrt(prec)
    if type(ressqrt) is ComplexNumber:
        res=ressqrt.real()
    else:
        res=ressqrt
    return res




def Racah(aa,bb,cc,dd,ee,ff,prec=None):
    r"""
    Calculate the Racah symbol

    W(a,b,c,d;e,f)

    NOTES:

    The Racah symbol is related to the Wigner 6j symbol:
    Wigner6j(j_1,j_2,j_3,j_4,j_5,j_6)
        =(-1)^(j_1+j_2+j_4+j_5) W(j_1,j_2,j_5,j_4,j_3,j_6)

    Please see the 6j symbol for its much richer symmetries and for
    additional properties.


    ALGORITHM:

    This function uses the algorithm of [Edmonds74] to calculate the
    value of the 6j symbol exactly. Note that the formula contains
    alternating sums over large factorials and is therefore unsuitable
    for finite precision arithmetic and only useful for a computer
    algebra system [Rasch03].


    INPUT:

    a - integer or half integer
    b - integer or half integer
    c - integer or half integer
    d - integer or half integer
    e - integer or half integer
    f - integer or half integer
    prec - precision, default: None. Providing a precision can
           drastically speed up the calculation.


    OUTPUT:

    The result will be a rational number times the square root of a
    rational number, unless a precision is given.


    EXAMPLES:

    A couple of examples and test cases:

        sage: Racah(3,3,3,3,3,3)
        -1/14


    REFERENCES:

    - [Edmonds74] 'Angular Momentum in Quantum Mechanics',
      A. R. Edmonds, Princeton University Press (1974)

    - [Rasch03] 'Efficient Storage Scheme for Pre-calculated Wigner 3j,
      6j and Gaunt Coefficients', J. Rasch and A. C. H. Yu, SIAM
      J. Sci. Comput. Volume 25, Issue 4, pp. 1416-1428 (2003)


    AUTHORS:

    - Jens Rasch (2009-03-24): initial version

    """

    prefac=_bigDeltacoeff(aa,bb,ee,prec)*_bigDeltacoeff(cc,dd,ee,prec)\
            *_bigDeltacoeff(aa,cc,ff,prec)*_bigDeltacoeff(bb,dd,ff,prec)
    if prefac==0:
        return 0
    imin=max(aa+bb+ee,cc+dd+ee,aa+cc+ff,bb+dd+ff)
    imax=min(aa+bb+cc+dd,aa+dd+ee+ff,bb+cc+ee+ff)

    maxfact=max(imax+1,aa+bb+cc+dd,aa+dd+ee+ff,bb+cc+ee+ff)
    _calc_factlist(maxfact)

    sumres=0
    for kk in range(imin,imax+1):
        den=_Factlist[int(kk-aa-bb-ee)]*_Factlist[int(kk-cc-dd-ee)]\
            *_Factlist[int(kk-aa-cc-ff)]\
            *_Factlist[int(kk-bb-dd-ff)]*_Factlist[int(aa+bb+cc+dd-kk)]\
            *_Factlist[int(aa+dd+ee+ff-kk)]\
            *_Factlist[int(bb+cc+ee+ff-kk)]
        sumres=sumres+Integer((-1)**kk*_Factlist[kk+1])/den

    res=prefac*sumres*(-1)**(int(aa+bb+cc+dd))
    return res





def Wigner6j(j_1,j_2,j_3,j_4,j_5,j_6,prec=None):
    r"""
    Calculate the Wigner 6j symbol Wigner6j(j_1,j_2,j_3,j_4,j_5,j_6)


    NOTES:

    The Wigner 6j symbol is related to the Racah symbol but exhibits
    more symmetries as detailed below.
    Wigner6j(j_1,j_2,j_3,j_4,j_5,j_6)
        =(-1)^(j_1+j_2+j_4+j_5) W(j_1,j_2,j_5,j_4,j_3,j_6)

    The Wigner 6j symbol obeys the following symmetry rules:

    - Wigner $6j$ symbols are left invariant under any permutation of
      the columns:
      Wigner6j(j_1,j_2,j_3,j_4,j_5,j_6)
          =Wigner6j(j_3,j_1,j_2,j_6,j_4,j_5)
          =Wigner6j(j_2,j_3,j_1,j_5,j_6,j_4)
          =Wigner6j(j_3,j_2,j_1,j_6,j_5,j_4)
          =Wigner6j(j_1,j_3,j_2,j_4,j_6,j_5)
          =Wigner6j(j_2,j_1,j_3,j_5,j_4,j_6)

    - They are invariant under the exchange of the upper and lower
      arguments in each of any two columns, i. e.
      Wigner6j(j_1,j_2,j_3,j_4,j_5,j_6)
          =Wigner6j(j_1,j_5,j_6,j_4,j_2,j_3)
          =Wigner6j(j_4,j_2,j_6,j_1,j_5,j_3)
          =Wigner6j(j_4,j_5,j_3,j_1,j_2,j_6)

    - additional 6 symmetries [Regge59] giving rise to 144 symmetries
      in total

    - only non-zero if any triple of $j$'s fulfil a triangle relation


    ALGORITHM:

    This function uses the algorithm of [Edmonds74] to calculate the
    value of the 6j symbol exactly. Note that the formula contains
    alternating sums over large factorials and is therefore unsuitable
    for finite precision arithmetic and only useful for a computer
    algebra system [Rasch03].


    INPUT:

    j_1 - integer or half integer
    j_2 - integer or half integer
    j_3 - integer or half integer
    j_4 - integer or half integer
    j_5 - integer or half integer
    j_6 - integer or half integer
    prec - precision, default: None. Providing a precision can
           drastically speed up the calculation.


    OUTPUT:

    The result will be a rational number times the square root of a
    rational number, unless a precision is given.


    EXAMPLES:

    A couple of examples and test cases:

        sage: Wigner6j(3,3,3,3,3,3)
        -1/14

        sage: Wigner6j(5,5,5,5,5,5)
        1/52

        sage: Wigner6j(6,6,6,6,6,6)
        309/10868

        sage: Wigner6j(8,8,8,8,8,8)
        -12219/965770

        sage: Wigner6j(30,30,30,30,30,30)
        36082186869033479581/87954851694828981714124

        sage: Wigner6j(0.5,0.5,1,0.5,0.5,1)
        1/6

        sage: Wigner6j(200,200,200,200,200,200, prec=1000)*1.0
        0.000155903212413242


    It is an error to have arguments that are not integer or half
    integer values or do not fulfil the triangle relation:

        sage: Wigner6j(2.5,2.5,2.5,2.5,2.5,2.5)
        Traceback (most recent call last):
        ...
        ValueError: j values must be integer or half integer and fulfil the triangle relation

        sage: Wigner6j(0.5,0.5,1.1,0.5,0.5,1.1)
        Traceback (most recent call last):
        ...
        ValueError: j values must be integer or half integer and fulfil the triangle relation


    REFERENCES:

    - [Regge59] 'Symmetry Properties of Racah Coefficients',
      T. Regge, Nuovo Cimento, Volume 11, pp. 116 (1959)

    - [Edmonds74] 'Angular Momentum in Quantum Mechanics',
      A. R. Edmonds, Princeton University Press (1974)

    - [Rasch03] 'Efficient Storage Scheme for Pre-calculated Wigner 3j,
      6j and Gaunt Coefficients', J. Rasch and A. C. H. Yu, SIAM
      J. Sci. Comput. Volume 25, Issue 4, pp. 1416-1428 (2003)

    """

    res=(-1)**(int(j_1+j_2+j_4+j_5))*Racah(j_1,j_2,j_5,j_4,j_3,j_6,prec)
    return res




def Wigner9j(j_1,j_2,j_3,j_4,j_5,j_6,j_7,j_8,j_9,prec=None):
    r"""
    Calculate the Wigner 9j symbol
    Wigner9j(j_1,j_2,j_3,j_4,j_5,j_6,j_7,j_8,j_9)


    ALGORITHM:

    This function uses the algorithm of [Edmonds74] to calculate the
    value of the 3j symbol exactly. Note that the formula contains
    alternating sums over large factorials and is therefore unsuitable
    for finite precision arithmetic and only useful for a computer
    algebra system [Rasch03].


    INPUT:

    j_1 - integer or half integer
    j_2 - integer or half integer
    j_3 - integer or half integer
    j_4 - integer or half integer
    j_5 - integer or half integer
    j_6 - integer or half integer
    j_7 - integer or half integer
    j_8 - integer or half integer
    j_9 - integer or half integer
    prec - precision, default: None. Providing a precision can
           drastically speed up the calculation.


    OUTPUT:

    The result will be a rational number times the square root of a
    rational number, unless a precision is given.


    EXAMPLES:

    A couple of examples and test cases, note that for speed reasons a
    precision is given:

        sage: Wigner9j(1,1,1, 1,1,1, 1,1,0 ,prec=64) # ==1/18
        0.0555555555555555555

        sage: Wigner9j(1,1,1, 1,1,1, 1,1,1)
        0

        sage: Wigner9j(1,1,1, 1,1,1, 1,1,2 ,prec=64) # ==1/18
        0.0555555555555555556

        sage: Wigner9j(1,2,1, 2,2,2, 1,2,1 ,prec=64) # ==-1/150
        -0.00666666666666666667

        sage: Wigner9j(3,3,2, 2,2,2, 3,3,2 ,prec=64) # ==157/14700
        0.0106802721088435374

        sage: Wigner9j(3,3,2, 3,3,2, 3,3,2 ,prec=64) # ==3221*sqrt(70)/(246960*sqrt(105)) - 365/(3528*sqrt(70)*sqrt(105))
        0.00944247746651111739

        sage: Wigner9j(3,3,1, 3.5,3.5,2, 3.5,3.5,1 ,prec=64) # ==3221*sqrt(70)/(246960*sqrt(105)) - 365/(3528*sqrt(70)*sqrt(105))
        0.0110216678544351364

        sage: Wigner9j(100,80,50, 50,100,70, 60,50,100 ,prec=1000)*1.0
        1.05597798065761e-7

        sage: Wigner9j(30,30,10, 30.5,30.5,20, 30.5,30.5,10 ,prec=1000)*1.0 # ==(80944680186359968990/95103769817469)*sqrt(1/682288158959699477295)
        0.0000325841699408828

        sage: Wigner9j(64,62.5,114.5, 61.5,61,112.5, 113.5,110.5,60, prec=1000)*1.0
        -3.41407910055520e-39

        sage: Wigner9j(15,15,15, 15,3,15, 15,18,10, prec=1000)*1.0
        -0.0000778324615309539

        sage: Wigner9j(1.5,1,1.5, 1,1,1, 1.5,1,1.5)
        0


    It is an error to have arguments that are not integer or half
    integer values or do not fulfil the triangle relation:

        sage: Wigner9j(0.5,0.5,0.5, 0.5,0.5,0.5, 0.5,0.5,0.5,prec=64)
        Traceback (most recent call last):
        ...
        ValueError: j values must be integer or half integer and fulfil the triangle relation

        sage: Wigner9j(1,1,1, 0.5,1,1.5, 0.5,1,2.5,prec=64)
        Traceback (most recent call last):
        ...
        ValueError: j values must be integer or half integer and fulfil the triangle relation


    REFERENCES:

    - [Edmonds74] 'Angular Momentum in Quantum Mechanics',
      A. R. Edmonds, Princeton University Press (1974)

    - [Rasch03] 'Efficient Storage Scheme for Pre-calculated Wigner 3j,
      6j and Gaunt Coefficients', J. Rasch and A. C. H. Yu, SIAM
      J. Sci. Comput. Volume 25, Issue 4, pp. 1416-1428 (2003)

    """

    imin=0
    imax=min(j_1+j_9,j_2+j_6,j_4+j_8)

    sumres=0
    for kk in range(imin,imax+1):
        sumres=sumres+(2*kk+1)*Racah(j_1,j_2,j_9,j_6,j_3,kk,prec)\
                *Racah(j_4,j_6,j_8,j_2,j_5,kk,prec)\
                *Racah(j_1,j_4,j_9,j_8,j_7,kk,prec)
    return sumres




def Gaunt(l_1,l_2,l_3,m_1,m_2,m_3,prec=None):
    r"""
    Calculate the Gaunt coefficient which is defined as the integral
    over three spherical harmonics:

    Y(j_1,j_2,j_3,m_1,m_2,m_3)
        =\int Y_{l_1,m_1}(\Omega)
         Y_{l_2,m_2}(\Omega) Y_{l_3,m_3}(\Omega) d\Omega
        =\sqrt((2l_1+1)(2l_2+1)(2l_3+1)/(4\pi))
         Y(j_1,j_2,j_3,0,0,0) Y(j_1,j_2,j_3,m_1,m_2,m_3)


    NOTES:

    The Gaunt coefficient obeys the following symmetry rules:

    - invariant under any permutation of the columns
      Y(j_1,j_2,j_3,m_1,m_2,m_3)
          =Y(j_3,j_1,j_2,m_3,m_1,m_2)
          =Y(j_2,j_3,j_1,m_2,m_3,m_1)
          =Y(j_3,j_2,j_1,m_3,m_2,m_1)
          =Y(j_1,j_3,j_2,m_1,m_3,m_2)
          =Y(j_2,j_1,j_3,m_2,m_1,m_3)

    - invariant under space inflection, i.e.
      Y(j_1,j_2,j_3,m_1,m_2,m_3)
         =Y(j_1,j_2,j_3,-m_1,-m_2,-m_3)

    - symmetric with respect to the 72 Regge symmetries as inherited
      for the $3j$ symbols [Regge58]

    - zero for $l_1$, $l_2$, $l_3$ not fulfilling triangle relation

    - zero for violating any one of the conditions: $l_1\ge|m_1|$,
      $l_2\ge|m_2|$, $l_3\ge|m_3|

    - non-zero only for an even sum of the $l_i$, i. e.
      $J=l_1+l_2+l_3=2n$ for $n$ in $\mathbf{N}$


    ALGORITHM:

    This function uses the algorithm of [Liberatodebrito82] to
    calculate the value of the Gaunt coefficient exactly. Note that
    the formula contains alternating sums over large factorials and is
    therefore unsuitable for finite precision arithmetic and only
    useful for a computer algebra system [Rasch03].


    INPUT:

    j_1 - integer
    j_2 - integer
    j_3 - integer
    m_1 - integer
    m_2 - integer
    m_3 - integer
    prec - precision, default: None. Providing a precision can
           drastically speed up the calculation.


    OUTPUT:

    The result will be a rational number times the square root of a
    rational number, unless a precision is given.


    EXAMPLES:

        sage: Gaunt(1,0,1,1,0,-1)
        -1/2/sqrt(pi)

        sage: Gaunt(1,0,1,1,0,0)
        0

        sage: Gaunt(29,29,34,10,-5,-5)
        1821867940156/215552371055153321*sqrt(22134)/sqrt(pi)

        sage: Gaunt(20,20,40,1,-1,0)
        28384503878959800/74029560764440771/sqrt(pi)

        sage: Gaunt(12,15,5,2,3,-5)
        91/124062*sqrt(36890)/sqrt(pi)

        sage: Gaunt(10,10,12,9,3,-12)
        -98/62031*sqrt(6279)/sqrt(pi)

        sage: Gaunt(1000,1000,1200,9,3,-12).n(64)
        0.00689500421922113448


    It is an error to use non-integer values for $l$ and $m$:

        sage: Gaunt(1.2,0,1.2,0,0,0)
        Traceback (most recent call last):
        ...
        ValueError: l values must be integer

        sage: Gaunt(1,0,1,1.1,0,-1.1)
        Traceback (most recent call last):
        ...
        ValueError: m values must be integer



    REFERENCES:

    - [Regge58] 'Symmetry Properties of Clebsch-Gordan Coefficients',
      T. Regge, Nuovo Cimento, Volume 10, pp. 544 (1958)

    - [Liberatodebrito82] 'FORTRAN program for the integral of three
      spherical harmonics', A. Liberato de Brito,
      Comput. Phys. Commun., Volume 25, pp. 81-85 (1982)

    - [Rasch03] 'Efficient Storage Scheme for Pre-calculated Wigner 3j,
      6j and Gaunt Coefficients', J. Rasch and A. C. H. Yu, SIAM
      J. Sci. Comput. Volume 25, Issue 4, pp. 1416-1428 (2003)


    AUTHORS:

    - Jens Rasch (2009-03-24): initial version for Sage

    """

    if int(l_1)!=l_1 or int(l_2)!=l_2 or int(l_3)!=l_3:
        raise ValueError("l values must be integer")
        #return 0
    if int(m_1)!=m_1 or int(m_2)!=m_2 or int(m_3)!=m_3:
        raise ValueError("m values must be integer")

    bigL=(l_1+l_2+l_3)/2
    a1=l_1+l_2-l_3
    if (a1<0):
        return 0
    a2=l_1-l_2+l_3
    if (a2<0):
        return 0
    a3=-l_1+l_2+l_3
    if (a3<0):
        return 0
    if Mod(2*bigL,2)<>0:
#     if int(int(2*bigL)/2)<>int(bigL):
        return 0
    if (m_1+m_2+m_3)<>0:
        return 0
    if (abs(m_1)>l_1) or (abs(m_2)>l_2) or (abs(m_3)>l_3):
        return 0

    imin=max(-l_3+l_1+m_2,-l_3+l_2-m_1,0)
    imax=min(l_2+m_2,l_1-m_1,l_1+l_2-l_3)

    maxfact=max(l_1+l_2+l_3+1,imax+1)
    _calc_factlist(maxfact)

    argsqrt=(2*l_1+1)*(2*l_2+1)*(2*l_3+1)*_Factlist[l_1-m_1]\
             *_Factlist[l_1+m_1]*_Factlist[l_2-m_2]*_Factlist[l_2+m_2]\
             *_Factlist[l_3-m_3]*_Factlist[l_3+m_3]/(4*pi)
    ressqrt=argsqrt.sqrt()          # sqrt(argsqrt,prec)
    #if type(ressqrt) is ComplexNumber:
    #    ressqrt=ressqrt.real()
    prefac=Integer(_Factlist[bigL]*_Factlist[l_2-l_1+l_3]\
        *_Factlist[l_1-l_2+l_3]\
        *_Factlist[l_1+l_2-l_3])/_Factlist[2*bigL+1]\
        /(_Factlist[bigL-l_1]*_Factlist[bigL-l_2]*_Factlist[bigL-l_3])

    sumres=0
    for ii in range(imin,imax+1):
        den=_Factlist[ii]*_Factlist[ii+l_3-l_1-m_2]\
             *_Factlist[l_2+m_2-ii]*_Factlist[l_1-ii-m_1]\
             *_Factlist[ii+l_3-l_2+m_1]*_Factlist[l_1+l_2-l_3-ii]
        sumres=sumres+Integer((-1)**ii)/den

    res=ressqrt*prefac*sumres*(-1)**(bigL+l_3+m_1-m_2)
    if prec!=None:
        res=res.n(prec)
    return res
