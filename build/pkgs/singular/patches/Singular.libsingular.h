#ifndef SINGULAR__H
#define SINGULAR__H

#include <math.h>
#include "singular/mod2.h"
#include "singular/structs.h"
#include "singular/polys.h"
#include "singular/longrat.h"
#include "singular/longalg.h"
#include "singular/numbers.h"
#include "singular/febase.h"
#include "singular/ring.h"
#include "singular/omalloc.h"
#include "singular/clapsing.h"
#include "singular/fast_maps.h"
#include "singular/kstd1.h"
#include "singular/tgb.h"
#include "singular/sparsmat.h"
#include "singular/rintegers.h"
#include "singular/rmodulo2m.h"
#include "singular/rmodulon.h"


int siInit(char *);

/* we need this function in Sage*/
number nr2mMapZp(number from);


#endif //SINGULAR__H
