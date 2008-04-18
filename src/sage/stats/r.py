from sage.interfaces.r import R, RElement

#my own copy
myR = R()

def ttest(x,y,conf_level = 0.95, **kw):
   """
   T-Test using R

   Arguments:
      x, y -- vectors of same length
      conf_level -- confidence level of the interval, [0,1) in percent

   Result:
      Tuple: (p-value, R return object)

   Example:
      sage: a, b = ttest([1,2,3,4,5],[1,2,3,3.5,5.121]); a
      0.941026372027427
   """
   if len(x) != len(y):
      raise AttributeError, "vectors x and y must be of same length"

   test = myR.t_test(x,y,conf_level = conf_level, **kw)._sage_()
   t = test.get('DATA').get('p_value')
   return t, test
