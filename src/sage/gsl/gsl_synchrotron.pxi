cdef extern from "gsl/gsl_sf_synchrotron.h":

  double  gsl_sf_synchrotron_1(double x)

  int  gsl_sf_synchrotron_1_e(double x, gsl_sf_result * result)

  double  gsl_sf_synchrotron_2(double x)

  int  gsl_sf_synchrotron_2_e(double x, gsl_sf_result * result)
