#include "Global.h"

#include "Rat.h"



#define	SORT_CWS	(0)

#define FIB_PERM	(27)		    /* print permutation for p<=# */



#define SMOOTH			(1)	/* print only regular simplicial */

#define NON_REF			(1)	/* allow non-reflexive input */

#define SSR_PRINT		(0)	/* SemiSimpleRoots, 2: also noFIPs */

#define BARY_PRINT		(1)	/* print if BARY_ZERO */

#define	ZEROSUM_PRINT		(1)	/* 1::Psum  2::kPsum  */

#define KP_VALUE		((P->n+1)/2)   /* (P->n+1)/2 is sufficient */

#define KP_PRINT		(3)	/* print if  sum kP !=0  at this k */

#define KP_EXIT			((P->n+1)/2)   /* exit if !=0 above this k */



#undef	OLD_IPS



#define     ALL_FANOS_BUT_INEFFICIENT         (0)



#define SL_Long		LLong		    /* has same problems as REgcd */



#if	(POLY_Dmax < 5)



#define NFX_Limit       903		/* 138b->255  153e->279  165c->327 */

#define X_Limit         9999		   /* 178c->375  218->399,462,483 */

#define VPM_Limit	9999



#else



#define NFX_Limit  1631721   /* 1631721 1 903 37947 233103 543907 815860    */

#define X_Limit    3263441   /* 3263442 1 1806 75894 466206 1087814 1631721 */

#define VPM_Limit  3263442   /* 1631721 1 903 37947 233103 543907 815860    */



#endif



/*   ------	some flags for testing	------ */



#define TEST_GLZ_VS_SL	(0)		/* exit on difference: GL vs. SL */

#define SHOW_NFX_LIMIT	(1)		/* exit on NFX_LIMIT violation */



#undef  WARN_BIG_NS			/* [1152] ...  1152 = sym(24-cell)  */

#undef	SHOW_BIG_NS			/* [1153] ...  printf VPM and exit  */



/*   ------  local typedefs and headers	------ */



typedef struct {int C[VERT_Nmax], L[VERT_Nmax], s;}             PERM;

typedef struct {int nv, nf, ns;}  				vNF;



#define	Fputs(S)	{fputs(S,outFILE);fputs("\n",outFILE);}



/*   ------	some useful routines	------ */



void NF_Coordinates(PolyPointList *_P, VertexNumList *_V, EqList *_F);



int  GLZ_Make_Trian_NF(Long X[][VERT_Nmax], int *n, int *nv,

		       GL_Long G[POLY_Dmax][POLY_Dmax]);    /* current=best */



int  SL2Z_Make_Poly_NF(Long X[][VERT_Nmax], int *n, int *nv,

		       SL_Long S[POLY_Dmax][POLY_Dmax]);    /* previous=bad */



int  Init_rVM_VPM(PolyPointList *P, VertexNumList *_V,EqList *_F,/* in */

	    	int *d,int *v,int *f, Long VM[POLY_Dmax][VERT_Nmax], /* out */

	    	Long VPM[VERT_Nmax][VERT_Nmax]);	/* return reflexive */



void Eval_Poly_NF(int *d,int *v,int *f, Long VM[POLY_Dmax][VERT_Nmax],

		Long VPM[VERT_Nmax][VERT_Nmax],			      /* in */

		Long pNF[POLY_Dmax][VERT_Nmax], int t);		     /* out */



void Make_VPM_NF(int *v, int *f, Long VPM[VERT_Nmax][VERT_Nmax],      /* in */

		PERM *CL,int *ns,Long VPM_NF[VERT_Nmax][VERT_Nmax]); /* out */



void Aux_pNF_from_vNF(PERM *CL,int *ns,int *v,int *d,

		Long VM[POLY_Dmax][VERT_Nmax],			      /* in */

		Long pNF[POLY_Dmax][VERT_Nmax],int *t);		     /* out */



void New_pNF_Order(int *v,int *f,PERM *CL,int *ns,Long VPM_NF[][VERT_Nmax]);



int  Make_Poly_NF(PolyPointList *_P, VertexNumList *_V, EqList *_F,

		Long pNF[POLY_Dmax][VERT_Nmax]);	  /* 1 if reflexive */



/*     	==============================================================      */



int  Aux_Make_Poly_NF(Long X[][VERT_Nmax], int *n, int *nv)

{    GL_Long G[POLY_Dmax][POLY_Dmax];

#if	(TEST_GLZ_VS_SL)

     int i,j,x; SL_Long S[POLY_Dmax][POLY_Dmax];Long XS[POLY_Dmax][VERT_Nmax];

     for(i=0;i<*n;i++)for(j=0;j<*nv;j++)XS[i][j]=X[i][j];

     x=GLZ_Make_Trian_NF(X,n,nv,G); SL2Z_Make_Poly_NF(XS,n,nv,S);

     for(i=0;i<*n;i++)for(j=0;j<*n;j++)  assert( S[i][j]==G[i][j]);

     for(i=0;i<*n;i++)for(j=0;j<*nv;j++) assert(XS[i][j]==X[i][j]);

	return x;

#else

	return GLZ_Make_Trian_NF(X,n,nv,G);

#endif

}

void Make_Poly_UTriang(PolyPointList *P)

{    if(VERT_Nmax<P->np) puts("Triang Form requires VERT_Nmax>=#Points"); else

     {	int i,j; Long UTF[POLY_Dmax][VERT_Nmax];

	for(i=0;i<P->np;i++)for(j=0;j<P->n;j++)UTF[j][i]=P->x[i][j];

	Aux_Make_Poly_NF(UTF,&P->n,&P->np);

	for(i=0;i<P->np;i++)for(j=0;j<P->n;j++)P->x[i][j]=UTF[j][i];

     }

}

/*     	==============================================================      */



GL_Long GL_Egcd(GL_Long A0, GL_Long A1, GL_Long *Vout0, GL_Long *Vout1)

{    GL_Long V0=A0, V1=A1, A2, X0=1, X1=0, X2=0;

     while((A2 = A0 % A1)) { X2=X0-X1*(A0/A1); A0=A1; A1=A2; X0=X1; X1=X2; }

     *Vout0=X1, *Vout1=(A1-(V0) * X1)/ (V1); return A1;

}

GL_Long GL_RoundQ(GL_Long N,GL_Long D)

{    GL_Long F; if(D<0) {D=-D; N=-N;} F=N/D; return F+(2*(N-F*D))/D;

}



GL_Long GL_W_to_GLZ(GL_Long *W, int d, GL_Long **GLZ)

{    int i, j; GL_Long G, *E=*GLZ, *B=GLZ[1];for(i=0;i<d;i++)assert(W[i]!=0);

     for(i=1;i<d;i++)for(j=0;j<d;j++)GLZ[i][j]=0;

     G=GL_Egcd(W[0],W[1],&E[0],&E[1]); B[0]=-W[1]/G; B[1]=W[0]/G;

     for(i=2;i<d;i++)

     {  GL_Long a, b, g=GL_Egcd(G,W[i],&a,&b); B=GLZ[i];

        B[i]= G/g; G=W[i]/g; for(j=0;j<i;j++) B[j]=-E[j]*G;  /* B=Base-Line */

        for(j=0;j<i;j++) E[j]*=a; E[j]=b;                     /* next Egcd */

        for(j=i-1;0<j;j--)                         /* I M P R O V E M E N T */

	{   GL_Long *Y=GLZ[j],rB=GL_RoundQ(B[j],Y[j]),rE=GL_RoundQ(E[j],Y[j]);

            int n; for(n=0;n<=j;n++) { B[n] -= rB*Y[n]; E[n] -= rE*Y[n]; }

	}   G=g;

     }

     return G;

}

int  GLZ_Make_Trian_NF(Long X[][VERT_Nmax], int *n, int *nv,

		       			       GL_Long G[POLY_Dmax][POLY_Dmax])

{    int i, j, C=-1, L; GL_Long g, W[POLY_Dmax], NF[POLY_Dmax][VERT_Nmax],

	*_G[POLY_Dmax], NG[POLY_Dmax][POLY_Dmax];for(i=0;i<*n;i++)_G[i]=NG[i];

     for(i=0;i<*n;i++)for(j=0;j<*n;j++)G[i][j]=(i==j);		  /* init G */

     for(i=0;i<*n;i++)for(j=0;j<*nv;j++)NF[i][j]=0;

     for(L=0;L<*n;L++)

     {  int N=0, p[POLY_Dmax];

        while(N==0)               /* find column C with N>0 non-zero entries */

        {   ++C; for(i=0;i<*n;i++)

	    {	for(j=0;j<*n;j++) NF[i][C]+=G[i][j]*X[j][C];

	    }

	    for(i=L;i<*n;i++) if(NF[i][C]) {W[N]=NF[i][C]; p[N++]=i;}

	}

        assert(N); if(N==1) {g=W[0]; _G[0][0]=1;} else g=GL_W_to_GLZ(W,N,_G);

	if(g<0) { g *= -1; for(i=0;i<N;i++)_G[0][i] *= -1; }

	NF[L][C]=g; for(i=L+1;i<*n;i++) NF[i][C]=0;

        for(i=0;i<*n;i++)

	{   GL_Long Cp[POLY_Dmax]; for(j=0;j<N;j++) Cp[j]=G[p[j]][i];

	    for(j=0;j<N;j++)

	    {	int k; G[p[j]][i]=0;

		for(k=0;k<N;k++) G[p[j]][i] += _G[j][k]*Cp[k];

	    }

	}

        if(L!=p[0])for(i=0;i<*n;i++)	     /* swap lines G[L] <-> G[p[0]] */

	{   GL_Long A=G[L][i]; G[L][i]=G[p[0]][i]; G[p[0]][i]=A;

	}

	for(i=0;i<L;i++)	 /* make upper diag minimal nonneg. */

	{   GL_Long R=NF[i][C]/NF[L][C];

	    if((NF[i][C]-R*NF[L][C])<0) R-=1;

	    NF[i][C]-=R*NF[L][C]; for(j=0;j<*n;j++)G[i][j]-=R*G[L][j];

	}

     }

     while(++C<*nv)for(i=0;i<*n;i++)for(j=0;j<*n;j++)NF[i][C]+=G[i][j]*X[j][C];

     for(i=0;i<*n;i++)for(j=0;j<*nv;j++) {

#ifdef	SHOW_NFX_LIMIT

	g=NF[i][j]; if(g<0) g=-g; if(g>NFX_Limit) { fprintf(stderr,

	    "NFX_Limit in GL -> %lld !!\n",(long long) g); return 0; } else

#endif

	X[i][j]=NF[i][j]; }

     return 1;

}

/*      =============================================================       */



void TEST_rVM_VPM(int *d,int *v,int *f, Long X[POLY_Dmax][VERT_Nmax],

	    	Long x[VERT_Nmax][VERT_Nmax])

{    int i,j,err=0; for(i=0;i<*v;i++)

     {	for(j=0;j<*d;j++) if(abs(X[j][i])>X_Limit) err=X[j][i];

	for(j=0;j<*f;j++) if(abs(x[j][i])>VPM_Limit) err=x[j][i];

     }	if(err)

     {	printf("TEST_VM_VPM: limits exceeded %d\n",err);

	printf("%d %d VM[%d][%d]:\n",*v,*d,*d,*v);

	for(j=0;j<*d;j++)

	{   for(i=0;i<*v;i++)printf("%3d ",(int) X[j][i]);puts("");

	}   puts("");

	printf("VPM[%d][%d]:\n",*f,*v);

	for(j=0;j<*f;j++)

	{   for(i=0;i<*v;i++)printf("%3d ",(int) x[j][i]);puts("");

	}   puts("");

	exit(0);

     }

}



int  Init_rVM_VPM(PolyPointList *_P,VertexNumList *_V,EqList *_F,/* in */

	    	int *d,int *v,int *f, Long X[POLY_Dmax][VERT_Nmax],  /* out */

	    	Long x[VERT_Nmax][VERT_Nmax])		/* return reflexive */

{    int i,j, ref=1;

     *v=_V->nv; *f=_F->ne; *d=_P->n;

     for(j=0;j<_F->ne;j++)                            	     /* compute VPM */

     {

	if(_F->e[j].c!=1) ref=0;

	for(i=0;i<_V->nv;i++)

        x[j][i]=Eval_Eq_on_V(&_F->e[j],_P->x[_V->v[i]],_P->n);

     }

     for(i=0;i<_V->nv;i++)

     {  Long *pv=_P->x[_V->v[i]];

	for(j=0;j<_P->n;j++) X[j][i]=pv[j];

     }

     TEST_rVM_VPM(d,v,f,X,x);

     return ref;

}



void New_pNF_Order(int *v,int *f,PERM *CL,int *ns,Long VPM_NF[][VERT_Nmax])

{    int i, j, pi[VERT_Nmax], c[VERT_Nmax];

     Long maxP[VERT_Nmax], sumP[VERT_Nmax];

     for(i=0;i<*v;i++)

     {	pi[i]=i; maxP[i]=sumP[i]=0; for(j=0;j<*f;j++)

	{   sumP[i]+=VPM_NF[j][i];

	    if(VPM_NF[j][i]>maxP[i])maxP[i]=VPM_NF[j][i];

	}

     }

     for(i=0;i<*v-1;i++)

     {	int n=i; for(j=i+1;j<*v;j++)

        {   if(maxP[j]<maxP[n]) n=j; else

	    if(maxP[j]==maxP[n]) if(sumP[j]<sumP[n]) n=j;

	}

        if(n!=i)

     	{   Long aP=maxP[i]; int a=pi[i];

	    maxP[i]=maxP[n]; maxP[n]=aP; pi[i]=pi[n]; pi[n]=a;

	    aP=sumP[i]; sumP[i]=sumP[n]; sumP[n]=aP;

	}

     }

     for(i=0;i<*ns;i++)

     {	int *C=CL[i].C; for(j=0;j<*v;j++) c[j]=C[pi[j]];

	for(j=0;j<*v;j++) C[j]=c[j];

     }

}



void Print_vNF(int *v, int *f, Long VPM[][VERT_Nmax], Long VPM_NF[][VERT_Nmax])

{    int i,j; fprintf(outFILE,"\nVPM NF (v=%d f=%d):\n",*v,*f); fflush(stdout);

     for(i=0;i<*f;i++)

     {  for(j=0;j<*v;j++)fprintf(outFILE,"%3d",(int)VPM[i][j]);

	fprintf(outFILE," =>");

	fflush(stdout);

        for(j=0;j<*v;j++)fprintf(outFILE,"%3d",(int)VPM_NF[i][j]);Fputs("");

	fflush(stdout);

     }	Fputs("");

}



void Eval_Poly_NF(int *d,int *v,int *f, Long VM[POLY_Dmax][VERT_Nmax],

		Long VPM[VERT_Nmax][VERT_Nmax],			      /* in */

		Long pNF[POLY_Dmax][VERT_Nmax],int t)		     /* out */

{    PERM *CL=(PERM *) malloc((SYM_Nmax+1) * sizeof(PERM));

     Long VPM_NF[VERT_Nmax][VERT_Nmax]; int ns; assert(CL!=NULL);

     Make_VPM_NF(v,f,VPM,CL,&ns,VPM_NF);	if(t)Print_vNF(v,f,VPM,VPM_NF);

     New_pNF_Order(v,f,CL,&ns,VPM_NF);

     Aux_pNF_from_vNF(CL,&ns,v,d,VM,pNF,&t);	free(CL);

#ifdef WARN_BIG_NS

#ifdef SHOW_BIG_NS

     if(SHOW_BIG_NS<=ns) {int i,j;    printf("ns=%d VM:\n",ns);fflush(stdout);

	for(i=0;i<*d;i++){for(j=0;j<*v;j++)printf("%2d ",(int)VM[i][j]);

	puts("");}	printf("ns=%d VPM:\n",ns);fflush(stdout);

	for(i=0;i<*f;i++){for(j=0;j<*v;j++)printf("%2d ",(int)VPM[i][j]);

	puts("");}	printf("ns=%d VPM_NF:\n",ns);fflush(stdout);

	for(i=0;i<*f;i++){for(j=0;j<*v;j++)printf("%2d ",(int)VPM_NF[i][j]);

	puts("");}	printf("ns=%d pNF:\n",ns);fflush(stdout);

	for(i=0;i<*d;i++){for(j=0;j<*v;j++)printf("%2d ",(int)pNF[i][j]);

	puts("");}	exit(0);}

#endif

#endif

}



/*   ========			tedious details of NFs		  =======   */

/*   Make_NF();     make NormalForm of VertexPairingMatrices       ======

 *

 *   To bring the VPM to normal form, NF=lexicographic if reading line by line

 *   we need permutations Cp and Lp of columns and lines: Make Cp's respecting

 *   rest symmetry to get maximal lines and remember them and their rest sym.

 *   1. Start with last permutation and append different refinements or throw

 *      everything below away if you find a `better' NF;

 *   2. Remember permutation and rest symmetry if equal; replace by last one

 *      if the `next' line is not good.

 *   In each step, i.e. after finding n lines of NF, their {Cp,Lp}'s and sym.

 *   s[i]=l, s[j]=i for i<j<=l  iff  {i,...,l} equiv;  else s[i]=i;

 */

void Aux_vNF_Line(int l,vNF *_X,Long x[][VERT_Nmax], PERM *CL,int *S,int *_ns)

{    int n=(*_ns), cf=0;	/*  cf=CompareFlag (ref. exists & o.k.      */

     Long *y, r[VERT_Nmax];	/*  r=ReferenceLine; y->X[line]		    */

     while(n--)      /*  go over CL (n from  *_ns-1  to  0), ns_* changes!  */

     {	PERM nP[VERT_Nmax];

	int c=0, L=l-1, np=0, *C, ccf=cf;	/*  ccf=column compare flag */

	*nP=CL[n];

	while(++L<_X->nf)			/*  init nP (from 1st col.) */

	{   int j=0; C=nP[np].C; y=x[nP[np].L[L]];

	    while(++j<=*S) if(y[C[c]]<y[C[j]]) swap(&C[c],&C[j]);

	    if(ccf)

	    {   Long d=y[*C]-*r;

		if(d<0) ;					/* BAD line */

		else if(d)				     /* BETTER line */

		{   *r=y[*C]; cf=0; *nP=nP[np]; nP[np=1]=CL[n]; *_ns=n+1;

		    swap(&(nP->L[l]),&(nP->L[L]));

		}

		else					      /* EQUAL line */

		{   swap(&(nP[np].L[l]),&(nP[np].L[L])); nP[++np]=CL[n];

		}

	    }

	    else 						/* NEW line */

	    {	*r=y[*C]; swap(&(nP[np].L[l]),&(nP[np].L[L]));

		nP[++np]=CL[n]; ccf=1;

	    }

	}

	while(++c<_X->nv)			       /* check/complete nP */

	{   int s=S[c]; L=np; ccf=cf;

	    if(s<c) s=S[s];

	    while(L--)

	    {	int j=c; C=nP[L].C; y=x[nP[L].L[l]];

		while(++j<=s) if(y[C[c]]<y[C[j]]) swap(&C[c],&C[j]);

		if(ccf)

		{   Long d=y[C[c]]-r[c];

		    if(d<0) {if(--np>L) nP[L]=nP[np];}		/* BAD line */

		    else if(d) 				     /* BETTER line */

		    {	r[c]=y[C[c]]; cf=0; np=L+1; *_ns=n+1;

		    }	/* else	; */			      /* EQUAL line */

		}

		else { r[c]=y[C[c]]; ccf=1; }

	    }

	}

	cf=1;

	if(--(*_ns) > n) CL[n]=CL[*_ns]; 		/*  write nP to CL  */

	if(SYM_Nmax < (cf=(*_ns+np)))

	{   printf("Need SYM_Nmax > %d !!\n",cf);exit(0);

	}

	for(L=0;L<np;L++) CL[(*_ns)++]=nP[L];

     }

     y=x[CL->L[l]];					       /* compute S */

     {	int c=0, *C=CL->C;

	while(c<_X->nv)

	{   int s=S[c]+1; S[c]=c; while(++c<s)

	    {   if(y[C[c]]==y[C[c-1]]) ++S[ S[c]=S[c-1] ];

	        else S[c]=c;

	    }

	}

     }

}

void Aux_vNF_Init(vNF *_X, Long x[][VERT_Nmax], PERM *CL, int *S, int *_ns)

{    int i, j, nn; Long *b, *y;

     PERM P, *q, *p;		       /* b=x[nb] -> best;  y=x[nn] -> next */

     for(i=0;i<_X->nf;i++) P.L[i]=i;

     for(j=0;j<_X->nv;j++) P.C[j]=j; /* init P */

     q=CL; *q=P; b=*x;          /* P=CL[ns-1] StartPerm; maximize 0-th line */

     for(j=1;j<_X->nv;j++)if(b[q->C[0]]<b[q->C[j]])swap(&q->C[0],&q->C[j]);

     for(i=1;i<_X->nv;i++)

     {  for(j=i+1;j<_X->nv;j++) if(b[q->C[i]]<b[q->C[j]])

        swap(&q->C[i],&q->C[j]);

     }

     for(nn=1;nn<_X->nf;nn++)			     /* maximize nn-th line */

     {  Long d; p=&CL[*_ns]; *p=P; y=x[nn]; /* nb=*q=*b=best, nn=*p=*y=next */

        {   int m=0; for(j=1;j<_X->nv;j++) if(y[p->C[m]]<y[p->C[j]]) m=j;

            if(m) swap(&p->C[0],&p->C[m]);

        }

        if((d=y[p->C[0]]-b[q->C[0]]) < 0) continue;   /* d<0 => forget this */

        for(i=1;i<_X->nv;i++)

        {   int m=i; for(j=i+1;j<_X->nv;j++) if(y[p->C[m]]<y[p->C[j]]) m=j;

            if(m>i) swap(&p->C[i],&p->C[m]);

            if(d==0) if((d=y[p->C[i]]-b[q->C[i]]) <0) break;

        }

        if(d<0) continue;

        swap(&p->L[0],&p->L[nn]);		 /* p->L[nn]=0; p->L[0]=nn; */

        if(d==0) (*_ns)++;

        else {*q=*p; *_ns=1; b=y;}                    /* d>0 => forget prev */

     }

     y=x[CL->L[0]]; S[0]=0; for(i=1;i<_X->nv;i++)	       /* compute S */

     if(y[CL->C[i]]==y[CL->C[i-1]]) ++S[ S[i]=S[i-1] ]; else S[i]=i;

}





int  Aux_XltY_Poly_NF(Long X[][VERT_Nmax],Long Y[][VERT_Nmax], int *n,int *nv)

{    int i, j; Long d;					  /* return "X < Y" */

     for(i=0;i<*n;i++)for(j=0;j<*nv;j++) if((d=X[i][j]-Y[i][j]))

     {	if(d<0) return 1; else return 0;

     }

     return 0;

}

void Print_Perm(int *p,int v,const char *s);

void TEST_pNF(int* C,Long V[][VERT_Nmax],Long X[][VERT_Nmax],

	      int* n,int* nv,int* try_)

{    int i,j; fprintf(outFILE,"Poly NF try[%d]:   C=",*try_);

     Print_Perm(C,*nv,"\n");

     for(i=0;i<*n;i++)

     {	for(j=0;j<*nv;j++) fprintf(outFILE," %3d",(int) V[i][j]);

	fprintf(outFILE," =>");

	for(j=0;j<*nv;j++) fprintf(outFILE," %3d",(int) X[i][j]); Fputs("");

     }

}



void Aux_Make_Triang(PERM *CL,int ns,Long V[][VERT_Nmax],int*n,int*nv,int *t)

{    int i, j, s, x=0, g=0, ps=1;		   /* x :: make X :: if X>Y */

     Long X[POLY_Dmax][VERT_Nmax], Y[POLY_Dmax][VERT_Nmax];

     for(i=0;i<*n;i++) for(j=0;j<*nv;j++) X[i][j]=V[i][CL->C[j]];

     if(!Aux_Make_Poly_NF(X,n,nv)) exit(0); 		  /* t>0: print NFs */

							  /*  -1: calc CL.s */

     if(*t) { if(*t>0) TEST_pNF(CL->C,V,X,n,nv,&g); else

              { CL->s=1; if(*t+1){puts("t<-1 in Aux_Make_Triang");exit(0);} }

            } for(s=1;s<ns;s++)CL[s].s=0;



     for(s=1;s<ns;s++)

     if(x)

     {	for(i=0;i<*n;i++) for(j=0;j<*nv;j++) X[i][j]=V[i][CL[s].C[j]];

     	if(!Aux_Make_Poly_NF(X,n,nv)) exit(0);

	if(Aux_XltY_Poly_NF(X,Y,n,nv)) x=0;



	if(*t)

	{   if(*t>0) TEST_pNF(CL[s].C,V,X,n,nv,&s);

	    if(x==0)

	    {	if(*t<0) { int k; for(k=g;k<s;k++) CL[k].s=0; CL[s].s=1;*t=-1;}

		g=s; ps=1;

	    }

	    else if(!Aux_XltY_Poly_NF(Y,X,n,nv))

		{ if(*t<0) {CL[s].s=1;(*t)--;} ps++;}

        }

     }

     else

     {	for(i=0;i<*n;i++) for(j=0;j<*nv;j++) Y[i][j]=V[i][CL[s].C[j]];

     	if(!Aux_Make_Poly_NF(Y,n,nv)) exit(0);

	if(Aux_XltY_Poly_NF(Y,X,n,nv)) x=1;



	if(*t)

	{   if(*t>0) TEST_pNF(CL[s].C,V,Y,n,nv,&s);

	    if(x==1)

	    {	if(*t<0) { int k; for(k=g;k<s;k++) CL[k].s=0; CL[s].s=1;*t=-1;}

		g=s; ps=1;

	    }

	    else if(!Aux_XltY_Poly_NF(X,Y,n,nv))

		{ if(*t<0) {CL[s].s=1;(*t)--;} ps++;}

	}

     }

     if(*t>0)

     fprintf(outFILE,

      "\nPoly NF:  NormalForm=try[%d]  #Sym(VPM)=%d  #Sym(Poly)=%d\n",g,ns,ps);

     if(x) for(i=0;i<*n;i++)for(j=0;j<*nv;j++) V[i][j]=Y[i][j];

     else  for(i=0;i<*n;i++)for(j=0;j<*nv;j++) V[i][j]=X[i][j];

}

/*   ========		END of 	tedious details of NFs		  =======   *

 *

 *	Make_VPM_NF		uses	Aux_vNF_Init, Aux_vNF_Line

 *

 *	Aux_pNF_from_vNF	uses	Aux_Make_Triang

 */

void Make_VPM_NF(int *v, int *f, Long x[VERT_Nmax][VERT_Nmax],      /* in */

		PERM *CL,int *ns,Long VPM_NF[VERT_Nmax][VERT_Nmax])  /* out */

{    int i, j, S[VERT_Nmax]; int nsF=0, nsM=0; 		     /* make VPM NF */



     volatile vNF auX; vNF *_X= (vNF*) &auX;  _X->nv=*v;_X->nf=*f; /* x=VPM */

     *ns=1; Aux_vNF_Init(_X, x, CL, S, ns);             /* init = 1st line */

     for(i=1;i<_X->nf-1;i++){Aux_vNF_Line(i,_X,x,CL,S,ns);  /* lines of NF */

#ifdef	WARN_BIG_NS

	if((WARN_BIG_NS<=(*ns))||nsF){ nsF=1;/*printf("ns[%d]=%d\n",i,*ns);*/}

#endif

	if(*ns>nsM) nsM=*ns; }

     _X->ns=*ns; for(i=0;i<_X->nv;i++)                /* write VPM-NF to _X */

     {  for(j=0;j<_X->nf;j++) /* _X->x */ VPM_NF[j][i]=x[CL->L[j]][CL->C[i]];

     }

     if(nsF)printf("WARNing: ns_max=%d -> ns=%d\n",nsM,*ns);

}



void Aux_pNF_from_vNF(PERM *CL,int *ns,int *v,int *d,

		Long VM[POLY_Dmax][VERT_Nmax],			      /* in */

		Long pNF[POLY_Dmax][VERT_Nmax],int *t)		     /* out */

{    int i,j;

     for(i=0;i<*d;i++)for(j=0;j<*v;j++) pNF[i][j]=VM[i][j];

     Aux_Make_Triang(CL,*ns,pNF,d,v,t);

}



int  Make_Poly_NF(PolyPointList *_P, VertexNumList *_V, EqList *_F,

		Long pNF[POLY_Dmax][VERT_Nmax])		  /* 1 if reflexive */

{    int d, v, f;

     Long VM[POLY_Dmax][VERT_Nmax], VPM[VERT_Nmax][VERT_Nmax];

     int ref=Init_rVM_VPM(_P,_V,_F,&d,&v,&f,VM,VPM);

     Eval_Poly_NF(&d,&v,&f,VM,VPM,pNF,0); return ref;

}



void Poly_Sym(PolyPointList *_P, VertexNumList *_V, EqList *_F, int *sym_num,

	int V_perm[][VERT_Nmax])

{    Long pNF[POLY_Dmax][VERT_Nmax];

     Make_Poly_Sym_NF(_P,_V,_F,sym_num,V_perm,pNF,0);

}

int  PermChar(int n)

{    if(n<10) return '0'+n; else if(n<36) return 'a'+n-10; else

     if(n<62) return 'A'+n-36; else

     {puts("Printing permutations only for #Vert<=62 !!");exit(0);} return 0;

}

void Print_Perm(int *p,int v,const char *s)

{    int i; for(i=0;i<v;i++) fprintf(outFILE,"%c",PermChar(p[i]));

     /*puts("");for(i=48;i<128;i++)printf("%c",i);*/ fprintf(outFILE,"%s",s);

}

int  Perm_String(int *p,int v,char *s)

{    int i=0; if(v<62) for(i=0;i<v;i++) s[i]=PermChar(p[i]); s[i]=0;return i;

}

int  Make_Poly_Sym_NF(PolyPointList *_P, VertexNumList *_V, EqList *_F,

		      int *SymNum, int V_perm[][VERT_Nmax],

		      Long NF[POLY_Dmax][VERT_Nmax], int traced)

{    int i, j, ns, t=-1, *d=&_P->n, *v=&_V->nv, *f=&_F->ne, *C;

     PERM *CL = (PERM *) malloc ( sizeof(PERM) *(SYM_Nmax+1));

     Long VM[POLY_Dmax][VERT_Nmax], VPM[VERT_Nmax][VERT_Nmax];

     Long VPM_NF[VERT_Nmax][VERT_Nmax];



     Init_rVM_VPM(_P,_V,_F,d,v,f,VM,VPM);

     if (traced) Eval_Poly_NF(&_P->n,&_V->nv,&_F->ne,VM,VPM,NF,1);

     Make_VPM_NF(v,f,VPM,CL,&ns,VPM_NF);

     New_pNF_Order(v,f,CL,&ns,VPM_NF);

     Aux_pNF_from_vNF(CL,&ns,v,d,VM,NF,&t);

     *SymNum=-t;i=0; while(0==CL[i].s) i++; C=CL[i].C;

     for(t=0;i<ns;i++) if(CL[i].s)		/* inv Perm: C[c0[i]]=C[i] */

       {for(j=0;j<*v;j++) V_perm[t][C[j]]=CL[i].C[j]; t++;}

     if(*SymNum<SYM_Nmax){int *s=V_perm[*SymNum];for(i=0;i<*v;i++)s[i]=C[i];}

     if(t!=*SymNum) { puts("Error in Poly_Sym!!"); exit(0);}

     if(traced)

     {	fprintf(outFILE,

	    "\nV_perm made by Poly_Sym (order refers to VertNumList):\n");

	for(i=0;i<*SymNum;i++) Print_Perm(V_perm[i],_V->nv,"\n");

      /*{for(j=0;j<_V->nv;j++)printf("%c",PermChar(V_perm[i][j]));puts("");}*/

     }

     free(CL); return ns;

}

void Aux_NF_Coord(PolyPointList *_P, Long VM[POLY_Dmax][VERT_Nmax], int *C,

		  	int *n, int *np, int *v)

{    SL_Long S[POLY_Dmax][POLY_Dmax], X[POLY_Dmax];

     Long V[POLY_Dmax][VERT_Nmax]; int i, j;

     for(i=0;i<*n;i++) for(j=0;j<*v;j++) V[i][j]=VM[i][C[j]];

     if(!SL2Z_Make_Poly_NF(V,n,v,S)) exit(0);

     for(j=0;j<*np;j++)

     {	for(i=0;i<*n;i++)

	{   int k=*n; X[i]=0; while(k--) X[i]+=_P->x[j][k]*S[i][k];

	}

	for(i=0;i<*n;i++) _P->x[j][i]=X[i];

     }

}



void NF_Coordinates(PolyPointList *_P, VertexNumList *_V, EqList *_F)

					     /* needs converted EqList !! */

{    PERM *CL; Long VM[POLY_Dmax][VERT_Nmax], VPM[VERT_Nmax][VERT_Nmax];

     int ns; CL=(PERM*) malloc((SYM_Nmax+1)*sizeof(PERM)); assert(CL!=NULL);

     Init_rVM_VPM(_P,_V,_F,&_P->n,&_V->nv,&_F->ne,VM,VPM);	/* make VPM */

     {	Long VPM_NF[VERT_Nmax][VERT_Nmax];

	Make_VPM_NF(&_V->nv,&_F->ne,VPM,CL,&ns,VPM_NF);		/* get PERM */

     	New_pNF_Order(&_V->nv,&_F->ne,CL,&ns,VPM_NF);	    /* improve PERM */

     }

     Aux_NF_Coord(_P,VM,CL->C,&_P->n,&_P->np,&_V->nv);	      /* improve _P */

     {	int f=_F->ne; VertexNumList V;		     /* EqList in new basis */

    	if(!IP_Check(_P,&V,_F)){puts("IP=0 in NF_Coords"); exit(0);}

	if((V.nv!=_V->nv)||(f!=_F->ne)) {puts("Error in NF_Coords"); exit(0);}

     }  free(CL);

}

int  Improve_Coords(PolyPointList *_P,VertexNumList *_V)

{    SL_Long S[POLY_Dmax][POLY_Dmax], X[POLY_Dmax];

     Long V[POLY_Dmax][VERT_Nmax]; int i, j;

     for(i=0;i<_P->n;i++) for(j=0;j<_V->nv;j++) V[i][j]=_P->x[_V->v[j]][i];

     if(!SL2Z_Make_Poly_NF(V,&(_P->n),&(_V->nv),S)) return 0;

     for(j=0;j<_P->np;j++)

     {	for(i=0;i<_P->n;i++)

	{   int k=_P->n; X[i]=0;

	    while(k--) X[i] += (long long) _P->x[j][k] * S[i][k];

	}

	for(i=0;i<_P->n;i++) _P->x[j][i]=X[i];

     }

	return 1;

}



/*  =================	SL(2,Z) - Version of Trian_NF	 =================  */

void SL_swap(SL_Long *X, SL_Long *Y)

{    SL_Long A=*Y; *Y=*X; *X=A;

}

SL_Long SL_Egcd(SL_Long A0, SL_Long A1, SL_Long *Vout0, SL_Long *Vout1)

{    register SL_Long V0=A0, V1=A1, A2, X0=1, X1=0, X2=0;

     while((A2 = A0 % A1)) { X2=X0-X1*(A0/A1); A0=A1; A1=A2; X0=X1; X1=X2; }

     *Vout0=X1, *Vout1=(A1-(V0) * X1)/ (V1); return A1;

}

/*   S * X = UpperTrian;  T * S = 1     (a b)   x = g           (d -b)(a b)=1

 *   g=EGCD(x,y,&a,&b); ax+by=g =>      (c d)   y   0           (-c a)(c d)=1

 *   c=-y/g, d=x/g => det(abcd)=1

 */



int  SL2Z_Make_Poly_NF(Long X[][VERT_Nmax], int *n, int *nv,

		       SL_Long S[POLY_Dmax][POLY_Dmax])

{    SL_Long NF[POLY_Dmax][VERT_Nmax], a, b, g;

     int i, j, C=-1, L;

     for(i=0;i<*n;i++)for(j=0;j<*n;j++)S[i][j]=(i==j);		  /* init S */

     for(i=0;i<*n;i++)for(j=0;j<*nv;j++)NF[i][j]=0;

     for(L=0;L<*n-1;L++)

     {  int N=0;

        while(!N)                /* find column C with N>0 non-zero entries */

        {   ++C; for(i=0;i<*n;i++)

	    {	for(j=0;j<*n;j++) NF[i][C]+=S[i][j]*X[j][C];

	    }

            if(NF[i=L][C]) N++;

	    while(++i<*n) if(NF[i][C])

	    {	N++;					 /* make NF[i][C]=0 */

		if(NF[L][C])

		{   SL_Long A;

		    g=SL_Egcd(NF[L][C],NF[i][C],&a,&b);

		    for(j=0;j<*n;j++)			/* c=-N_iC/g */

		    {	A=a*S[L][j]+b*S[i][j];		/* d= N_LC/g */

			S[i][j]=(NF[L][C]/g)*S[i][j]-(NF[i][C]/g)*S[L][j];

			S[L][j]=A;

		    }

		    NF[L][C]=g; NF[i][C]=0;

		}

		else

		{   SL_swap(&NF[L][C],&NF[i][C]);

		    for(j=0;j<*n;j++)SL_swap(&S[L][j],&S[i][j]);

		}

	    }

	    if(NF[L][C]<0)

	    {	NF[L][C]*=-1;for(j=0;j<*n;j++)S[L][j]*=-1;	    /* sign */

	    }

	    if(N) for(i=0;i<L;i++)	 /* make upper diag minimal nonneg. */

	    {	SL_Long R=NF[i][C]/NF[L][C];

		if((NF[i][C]-R*NF[L][C])<0) R-=1;

		NF[i][C]-=R*NF[L][C]; for(j=0;j<*n;j++)S[i][j]-=R*S[L][j];

	    }

	}

     }

     while(++C<*nv)

     {	for(i=0;i<*n;i++) for(j=0;j<*n;j++) NF[i][C]+=S[i][j]*X[j][C];

	if(L)if(NF[L][C])

	{   if(NF[L][C]<0)

	    {	NF[*n-1][C]*=-1; for(j=0;j<*n;j++) S[L][j]*=-1;

	    }

	    for(i=0;i<L;i++)		 /* make upper diag minimal nonneg. */

	    {	SL_Long R=NF[i][C]/NF[L][C];

		if((NF[i][C]-R*NF[L][C])<0) R-=1;

		NF[i][C]-=R*NF[L][C]; for(j=0;j<*n;j++)S[i][j]-=R*S[L][j];

	    }

	    L=0;

	}

     }

     for(i=0;i<*n;i++)for(j=0;j<*nv;j++)

     if( labs(X[i][j]=NF[i][j]) > NFX_Limit)

     {	fprintf(stderr,"NFX_Limit in SL: I need %ld !!\n",

		labs(X[i][j]));return 0;

     }

     return 1;

}

/*      =============================================================       */





/*  =================	weights, fibrations and quotients   ==============  */

Long GxP(GL_Long *Gi,Long *V,int *d)

{     Long x=0; int j; for(j=0;j<*d;j++) x+=Gi[j]*V[j]; return x;

}

void G_2_BxG(GL_Long **G,GL_Long **B,int *d,int *L)		/* G -> B.G */

{    GL_Long W[POLY_Dmax]; int l,c; for(c=0;c<*d;c++)

     {  for(l=*L;l<*d;l++)

	{   int j; W[l]=0; for(j=*L;j<*d;j++) W[l]+=B[l-*L][j-*L]*G[j][c];

	}   for(l=*L;l<*d;l++) G[l][c]=W[l];

     }						/* TEST_GLZmatrix(G,*d); */

}

#define	TEST

#undef  TEST_OUT

void TEST_GLZmatrix(GL_Long *G[POLY_Dmax], int d)

{	int x,y; GL_Long Ginv[POLY_Dmax][POLY_Dmax];

	Long X[POLY_Dmax][VERT_Nmax];

	for(x=0;x<d;x++)for(y=0;y<d;y++)X[x][y]=G[x][y];

	GLZ_Make_Trian_NF(X,&d,&d,Ginv);

	for(x=0;x<d;x++)for(y=0;y<d;y++)assert(X[x][y]==(x==y));

}

void INV_GLZmatrix(GL_Long G[][POLY_Dmax], int *d,GL_Long Ginv[][POLY_Dmax])

{	int x,y;

	Long X[POLY_Dmax][VERT_Nmax];

	for(x=0;x<*d;x++)for(y=0;y<*d;y++)X[x][y]=G[x][y];

	GLZ_Make_Trian_NF(X,d,d,Ginv);

	for(x=0;x<*d;x++)for(y=0;y<*d;y++)if(X[x][y]!=(x==y)) goto NoGLZ;

        return;

NoGLZ:	fputs("No GLZ-Matrix in INV_GLZmatrix:",stderr); for(x=0;x<*d;x++)

	{for(y=0;y<*d;y++) fprintf(stderr," %5ld",G[x][y]);puts("");}assert(0);

}

GL_Long GL_V_to_GLZ(GL_Long *V, GL_Long *G[POLY_Dmax], int d)

{    int i, j, p=0, z=0, P[POLY_Dmax], Z[POLY_Dmax]; GL_Long g, W[POLY_Dmax];

     for(i=0;i<d;i++) if(V[i]) {W[p]=V[(P[p]=i)];p++;} else Z[z++]=i;

	assert(z+p==d);

     if(p>1)

     {	g=GL_W_to_GLZ(W,p,G); if(g<0) for(i=0;i<p;i++) G[0][i]*= -1;

	i=p; while(i--)

	{   int x=P[i]; for(j=p;j<d;j++)G[j][x]=0; j=p;

	    while(j--) G[j][x]=G[j][i]; while(0<j--)G[j][x]=0;

	}   for(i=0;i<z;i++) for(j=0;j<d;j++) G[j][Z[i]] = (d-j==i+1);

     }

     else

     {	for(j=0;j<d;j++)for(i=0;i<d;i++)G[i][j]=(i==j); assert(p); if(P[0])

	{G[P[0]][P[0]]=G[0][0]=0; G[0][P[0]]=G[P[0]][0]=(V[P[0]]>0) ? 1 : -1;}

	else if(*V<0) G[0][0]=-1; g=V[P[0]];

     }	if(g<0) g=-g;

#ifdef	TEST_OUT

	for(i=0;i<d;i++){printf("G[%d]= ",i);for(j=0;j<d;j++)

	printf("%2d ",G[i][j]);printf("    V=%d\n",V[i]);}

	puts("testing GLZ in GL_V_to_GLZ"); fflush(0);

#endif

#ifdef	TEST

	{int x,y; TEST_GLZmatrix(G,d);

	for(x=0;x<d;x++){Long Y=0; for(y=0;y<d;y++) Y+=G[x][y]*V[y];

	   if(x) assert(Y==0); else assert(Y>0);}}

#endif

     return g;

}

Long V_to_G_GI(Long *V,int d, Long G[][POLY_Dmax],Long GI[][POLY_Dmax])

{    GL_Long AV[POLY_Dmax],AG[POLY_Dmax][POLY_Dmax],AGI[POLY_Dmax][POLY_Dmax],

	*P[POLY_Dmax];     Long g; int i,j;

     for(i=0;i<d;i++) {AV[i]=V[i]; P[i]=AG[i];}

     g=GL_V_to_GLZ(AV,P,d); INV_GLZmatrix(AG,&d,AGI);

     for(i=0;i<d;i++)for(j=0;j<d;j++){G[i][j]=AG[i][j];GI[i][j]=AGI[i][j];}

     return g;

}

int  TriMat_to_Weight(GL_Long T[][POLY_Dmax], int *p,int r,int *s,

	int *nw, Long W[][VERT_Nmax], int *Wmax)

{    int i,j; Long g, a, b, x[POLY_Dmax+1], *X=W[*nw];

     if(0<=(b=T[r][r-1])) return 0;

     g=Fgcd(a=T[r-1][r-1],-b);x[r-1]=-b/g;x[r]=a/g;

     for(j=r-2;0<=j;j--)

     {	a=T[j][j]; b=0; for(i=j+1;i<=r;i++)b-=x[i]*T[i][j];

	if(b<=0) return 0; else g=Fgcd(a,b); x[j]=b/g;

	a/=g; if(a>1) for(i=j+1;i<=r;i++) x[i]*=a;

     }	assert((*nw)++ < *Wmax);

     for(i=0;i<*p;i++)X[i]=0; for(i=0;i<=r;i++)X[s[i]]=x[i]; return 1;

#ifdef	TEST_OUT

	for(i=0;i<r;i++){printf("r=%d nw=%d:  ",r,*nw);

	    for(j=0;j<=r;j++)printf(" %2d",T[j][i]);puts("");}

	for(i=0;i<=r;i++)printf(" %2d",x[i]);printf("  =W  p=%d  S=",*p);

	for(i=0;i<=r;i++)printf(" %2d",s[i]);puts("");

#endif

}

Long XmY_vecdiff(Long *X, Long*Y, int n)

{    Long d; while(n--) if((d=X[n]-Y[n])) return d; return 0;

}

void Remove_Identical_Points(PolyPointList *P)

{    int i,p,s,r=0; for(p=0;p<P->np;p++)

     {	for(s=0;s<r;s++) if(0==XmY_vecdiff(P->x[p],P->x[s],P->n)) break;

	if(s==r) { if(r<p)for(i=0;i<P->n;i++)P->x[r][i]=P->x[p][i]; r++;}

     }	P->np=r;

}

int  PM_to_GLZ_for_UTriang(Long M[][VERT_Nmax],int *d,int *v,/* return rank */

                       GL_Long G[POLY_Dmax][POLY_Dmax])	  /* allows rank<*d */

{    int i,j,k,r=0; GL_Long B[POLY_Dmax][POLY_Dmax],*b[POLY_Dmax],

	*g[POLY_Dmax]; for(i=0;i<*d;i++) {b[i]=B[i]; g[i]=G[i];}

     for(i=0;i<*d;i++) for(j=0;j<*d;j++) G[i][j]=(i==j); for(i=0;i<*v;i++)

     {	GL_Long V[POLY_Dmax]; int nz=0; for(j=r;j<*d;j++)

	{   GL_Long x=0; for(k=0;k<*d;k++)x+=G[j][k]*M[k][i];if((V[j]=x))nz=1;}

	if(nz) {GL_V_to_GLZ(&V[r],b,*d-r); G_2_BxG(g,b,d,&r); r++;}

     }	return r;

}

typedef	Long PoMat[VERT_Nmax][POLY_Dmax];

typedef	Long VMat[POLY_Dmax][VERT_Nmax];

void Print2_PM(Long PM[][POLY_Dmax],int d,int p)

{    int i,j; for(i=0;i<d;i++)for(j=0;j<p;j++)

	fprintf(outFILE,"%2ld%c",PM[j][i],(j==p-1) ? '\n' : ' ');

}

void Print2_VM(VMat VM,int d,int p)

{    int i,j; for(i=0;i<d;i++)for(j=0;j<p;j++)

	fprintf(outFILE,"%2ld%c",VM[i][j],(j==p-1) ? '\n' : ' ');

}

typedef struct  {int p[SYM_Nmax][VERT_Nmax];}           VPerm;

int  InvariantSubspace(PolyPointList *P,VertexNumList *V,EqList *E)

{    int i,v, r=0, p=0, pri, EVsn, sn;

     VPerm *VP = (VPerm *) malloc(sizeof(VPerm));

     Long NF[POLY_Dmax][VERT_Nmax]; VMat Inv; assert(NULL != VP);

     EVsn=Make_Poly_Sym_NF(P,V,E,&sn,VP->p,NF,0); for(v=0;v<V->nv;v++)

     {	Long X[POLY_Dmax], g=0; for(i=0;i<P->n;i++)

	{   int s; X[i]=0; for(s=0;s<sn;s++)X[i]+=P->x[V->v[VP->p[s][v]]][i];

	    if(X[i]) g = g ? NNgcd(g,X[i]) : X[i];

	}   if(g>0)

	{   for(i=0;i<P->n;i++) {assert(0==(X[i]%g)); Inv[i][p]=X[i]/g;} p++;

	}

     }	pri=p; if(p>V->nv){fprintf(outFILE,"p=%d v=%d\n",p,V->nv);exit(0);}

     if(pri) fprintf(outFILE,"%d %d  #Sym=%d (<=%d)  ",P->n,V->nv,sn,EVsn);

     if(p)

     {	GL_Long G[POLY_Dmax][POLY_Dmax],B[POLY_Dmax][POLY_Dmax];

	r=PM_to_GLZ_for_UTriang(Inv,&P->n,&p,G); if(pri)

	{   VMat VM; int j; for(j=0;j<p;j++) for(i=0;i<P->n;i++) {VM[i][j]=0;

	    	for(v=0;v<P->n;v++) VM[i][j] += G[i][v]*Inv[v][j];

	    	if(i>=r)assert(VM[i][j]==0);                    }

	    fprintf(outFILE,"InvSubspace: dim=%d <(",r);

	    INV_GLZmatrix(G,&P->n,B); for(i=0;i<r;i++) for(v=0;v<P->n;v++)

	    fprintf(outFILE,

		"%ld%s",B[v][i],(v<P->n-1) ? "," : ((i+1==r) ? "":"),("));

	    fprintf(outFILE,")>\n");

	}

     }	else if(pri) fprintf(outFILE,"symmetric\n"); free(VP);

     if(pri){for(v=0;v<V->nv;v++)for(i=0;i<P->n;i++)Inv[i][v]=P->x[V->v[v]][i];

     	Print2_VM(Inv,P->n,V->nv);} if(pri)fflush(0); return r;

}

/*   Vol = #simp = GeomVol / dim!,  V=Vol(<F,p>), v=Vol(F), B=barcent(<A,p>)

 *	B=b+(p-b)/(D+1),  V=v*n,    n=dist(A,p),  D=dim(<F,p>)

 */

Long Simp_Vol_Barycent(PolyPointList *A,Long VM[][VERT_Nmax],Long *B,Long *N)

{    int i,j; Long I=0;  *N=A->np;

     for(i=0;i<A->n;i++) { B[i]=0; for(j=0;j<A->n+1;j++) B[i]+=A->x[j][i];

	I=NNgcd(I,B[i]);} if(I==0) *N=0; else I=Fgcd(I,*N);

     if(I>1) {(*N)/=I; for(i=0;i<A->n;i++) B[i]/=I;}

     for(i=1;i<A->np;i++)for(j=0;j<A->n;j++)VM[j][i-1]=A->x[i][j]-A->x[0][j];

     assert(A->np==A->n+1); Aux_Make_Poly_NF(VM,&A->n,&A->n);

     I=1; for(i=0;i<A->n;i++) I*=VM[i][i]; assert(I>0); return I;

}

Long SimplexVolume(Long *V[POLY_Dmax+1],int d)

{    Long I=1, VM[POLY_Dmax][VERT_Nmax]; int i,p;

     for(i=0;i<d;i++)for(p=0;p<d;p++) VM[i][p]=V[p][i];

     Aux_Make_Poly_NF(VM,&d,&d);

     for(i=0;i<d;i++) I*=VM[i][i]; assert(I>=0); return I;

}

void Print_GLZ(GL_Long G[][POLY_Dmax],int d,const char *c);

Long Aux_Vol_Barycent(PolyPointList *A, VertexNumList *V, EqList *E,

	Long *_B, Long *_N)

{    Long P[VERT_Nmax][POLY_Dmax],F[POLY_Dmax][VERT_Nmax],B[POLY_Dmax],g,

	vol=0; int i,j,e,p=A->np-1,D=A->n,ne=0; Equation Eq[VERT_Nmax];

     if(A->np==1+D) return Simp_Vol_Barycent(A,F,_B,_N);   p=A->np-1; *_N=1;

     for(i=0;i<D;i++){_B[i]=A->x[0][i];		      /* choose origin _B[] */

	for(j=0;j<A->np;j++)A->x[j][i]-=_B[i];}

     Find_Equations(A,V,E); assert(A->np=V->nv); for(e=0;e<D;e++) B[e]=0;

     for(i=0;i<p;i++)for(j=0;j<D;j++)P[i][j]=A->x[i+1][j];

     for(e=0;e<E->ne;e++) if(E->e[e].c){Eq[ne++]=E->e[e];assert(E->e[e].c>0);}

     for(e=0;e<ne;e++)

     {	Long Ze[POLY_Dmax],Ve,Be[POLY_Dmax],Ne,ZB[POLY_Dmax];

	GL_Long G[POLY_Dmax][POLY_Dmax],GI[POLY_Dmax][POLY_Dmax]; int f=0;

	for(i=0;i<p;i++) if(Eval_Eq_on_V(&Eq[e],P[i],D)==0)

	{   for(j=0;j<D;j++) F[j][f]=P[i][j]; f++;

	}   for(j=0;j<D;j++) Ze[j]=F[j][0]; 	      /* choose origin Ze[] */

	for(i=0;i<f;i++) for(j=0;j<D;j++) F[j][i]-=Ze[j];

	assert(D-1==PM_to_GLZ_for_UTriang(F,&D,&f,G));  A->n=D-1; A->np=f;

	for(i=0;i<A->np;i++)for(j=0;j<A->n;j++){A->x[i][j]=0;

	    for(f=0;f<D;f++)A->x[i][j]+=G[j][f]*F[f][i];}	     /*j=A->n*/

	for(i=0;i<A->np;i++){A->x[i][j]=0;for(f=0;f<D;f++)A->x[i][j]+= /*test*/

	G[j][f]*F[f][i];assert(A->x[i][j]==0);}	INV_GLZmatrix(G,&D,GI);

	/* if(D==4){Print_PPL(A,"GxP");Print_GLZ(GI,D,"GI");} */

	Ve=Aux_Vol_Barycent(A,V,E,Be,&Ne)*Eq[e].c; vol+=Ve;

	/* if(D==4){fprintf(outFILE,"%d<%d: E.c=%d V=%d ",e,ne,Eq[e].c,Ve);

	   for(i=0;i<D-1;i++)printf(" %d",Be[i]);printf("/%d = B/N\n",Ne);} */

        for(i=0;i<D;i++){ZB[i]=0;for(j=0;j<D-1;j++)ZB[i]+=GI[i][j]*Be[j];}

	g=Ne; for(i=0;i<D;i++)if(ZB[i]%g) g=NNgcd(g,ZB[i]); assert(g>0);

	Ne/=g;for(i=0;i<D;i++) ZB[i]=Ze[i]*Ne+ZB[i]/g; /* _B+=sum _N/V ZB/Ne */

        g=Fgcd(Ne,Ve); Ve/=g; Ne/=g;  g=Fgcd(Ne,*_N); Ne/=g; (*_N)/=g;

	for(i=0;i<D;i++) B[i]=Ne*B[i]+Ve*(*_N)*ZB[i]; (*_N) *= (Ne*g);

     }

     /*	g=((*_N)*=(vol*(D+1))); for(i=0;i<D;i++) g=NNgcd(g,B[i]); (*_N)/=g;

     	r=Fgcd(*_N,D); (*_N)/=r; r=D/r;

     	for(i=0;i<D;i++) _B[i]=(*_N)*_B[i]+r*B[i]/g; ... orig.vsn. */

     (*_N) *= (vol*(D+1)); for(i=0;i<D;i++) _B[i]=(*_N)*_B[i]+D*B[i];  g=*_N;

     for(i=0;i<D;i++) g=NNgcd(g,_B[i]); for(i=0;i<D;i++) _B[i] /=g; (*_N) /=g;

     return vol;

}



Long LatVol_Barycent(PolyPointList *P,VertexNumList *V,          /* bary=B/N */

	Long *B,Long *N)

{    PolyPointList *A=(PolyPointList *) malloc(sizeof(PolyPointList)); int i,j;

     VertexNumList aV; EqList aE,*e=&aE; Long vol; A->n=P->n; A->np=V->nv;

     for(i=0;i<V->nv;i++) for(j=0;j<P->n;j++) A->x[i][j] = P->x[V->v[i]][j];

     vol=Aux_Vol_Barycent(A,&aV,e,B,N); free(A);

#ifdef	TEST_OUT

	Print_PPL(P,"result for:"); printf("vol=%d, B=",vol);

	for(i=0;i<P->n;i++)printf("%d ",B[i]);printf("/ %d\n",*N);

#endif

     for(i=0;i<P->n;i++) if(B[i]) break;

     if(i==P->n) (*N)=0; return vol;  /* N=0 iff B=0 */

}



int ZeroSum(Long *A,Long *B,int d){while(d--)if(A[d]+B[d])return 0;return 1;}



int SemiSimpleRoots(PolyPointList *P,EqList *E,Long **R){

  int e,p,d=P->n,N=0; for(p=0;p<P->np;p++){ int z=0; for(e=0;e<E->ne;e++)

    if(0==Eval_Eq_on_V(&E->e[e],P->x[p],P->n))z++; if(z==1) R[N++]=P->x[p];}

  if(N%2) return 0;  if(N==0) return -1;

  for(e=0;e<P->n;e++){Long s=0; for(p=0;p<N;p++) s+=R[p][e]; if(s) return 0;}

  /*for(p=0;p<N;p++){for(e=0;e<N;e++)if(e!=p)if(ZeroSum(R[p],R[e],d)) break;

      if(e==N)return 0;}*/

  for(p=0;p<N;p++){ for(e=p+1;e<N;e++) if(ZeroSum(R[p],R[e],d)) break;

    if(e==N) return 0; if(e>p+1){Long *X=R[e];R[e]=R[p+1];R[p+1]=X;} p++;}

  return N;}





typedef struct { int v, d; Long **x;}                   Matrix;/* Line[v][d] */

void Init_Matrix(Matrix *M,int v, int d){               /* v=#vec, d=dim */

  int i; M->x=(Long **) malloc (v*(sizeof(Long *)+d*sizeof(Long)));

  assert(M->x != NULL); M->d=d; M->v=v;

  M->x[0]=(Long *)(&(M->x[v])); for(i=1;i<v;i++) M->x[i]=&M->x[i-1][d];}

void Free_Matrix(Matrix *M){free(M->x);M->v=M->d=0;}

void Print_LMatrix(Matrix M, char *s){int i,j;

  fprintf(outFILE,"%d %d LV %s\n",M.v,M.d,s); for(i=0;i<M.v;i++){ for(j=0;

    j<M.d;j++) fprintf(outFILE,"%2ld%s",M.x[i][j],(j+1==M.d) ? "\n" : " ");}}

Long VxV(Long *X,Long *Y,int d){Long z=X[0]*Y[0];

  while(--d) z+=X[d]*Y[d]; return z;}

Long V_to_GLZ(Long *V,Matrix G){          /* V may contain NULLs, return gcd */

  int i,j,d=G.v,p=0,z=0,*P,*Z = (int*)malloc(d*(2*sizeof(int)+sizeof(Long)));

  Long g,*W; assert(Z!=NULL); P=&Z[d]; W=(Long *) &P[d];

  for(i=0;i<d;i++) if(V[i]) {W[p]=V[(P[p]=i)];p++;} else Z[z++]=i;

  assert(z+p==G.d);

  if(p>1){ g=W_to_GLZ(W,&p,G.x); if(g<0) for(i=0;i<p;i++) G.x[0][i]*= -1; i=p;

    while(i--) { int x=P[i]; for(j=p;j<d;j++)G.x[j][x]=0; j=p;

      while(j--) G.x[j][x]=G.x[j][i]; while(0<j--)G.x[j][x]=0; }

    for(i=0;i<z;i++) for(j=0;j<d;j++) G.x[j][Z[i]] = (d-j==i+1); }

  else { for(j=0;j<d;j++)for(i=0;i<d;i++)G.x[i][j]=(i==j); assert(p);

    if(P[0]) {G.x[P[0]][P[0]]=G.x[0][0]=0;

      G.x[0][P[0]]=G.x[P[0]][0]=(V[P[0]]>0) ? 1 : -1;}

    else if(*V<0) G.x[0][0]=-1; g=V[P[0]]; } if(g<0) g=-g;

  for(j=0;j<d;j++) assert(VxV(V,G.x[j],d)==((j==0)*g)); free(Z);

  return g;}

void Aux_G_2_BxG(Matrix G,Matrix B){    /* don't use INV_GLZ::infinite loop */

  int l,c,d=G.d,L=d-B.d; Long *X=B.x[d-1]; assert(L>0);

  for(c=0;c<d;c++) { for(l=L;l<d;l++) { int j; X[l]=0; for(j=L;j<d;j++)

      X[l]+=B.x[l-L][j-L]*G.x[j][c]; } for(l=L;l<d;l++) G.x[l][c]=X[l];}}

void Aux_MinNonNeg_UT(Matrix M,Matrix G,int c,int r,int d,Long D){

  int i,j; for(i=0;i<r;i++){Long X=VxV(G.x[i],M.x[c],d), R=X/D;

    if(X-R*D<0)R-=1; for(j=0;j<d;j++)G.x[i][j]-=R*G.x[r][j];}}

int  Make_G_for_GxMT_UT(Matrix M,Matrix G){ /* GxM upper trian, return rank */

  int i,j,r=0,v=M.v,d=M.d; Matrix B; Long *V=(Long*)malloc(d*sizeof(Long));

  assert(G.v==d); assert(G.d==d); assert(V!=NULL); Init_Matrix(&B,d,d);

  for(i=0;i<d;i++) for(j=0;j<d;j++) G.x[i][j]=(i==j);

  for(i=0;i<v;i++){ int nz=0;

    for(j=r;j<d;j++) if((V[j]=VxV(G.x[j],M.x[i],d))) nz=1;

    if(nz) {if(r) {Long D; B.d=B.v=d-r; D=V_to_GLZ(&(V[r]),B);

      Aux_G_2_BxG(G,B); Aux_MinNonNeg_UT(M,G,i,r,d,D);}

      else V_to_GLZ(V,G); r++;}}

  free(V); Free_Matrix(&B); return r;}



void Circuit(int d,Long **P,Long *C){/* find C[d+1] with C.P=0 for P[d+1][d] */

  int i,j; Matrix G, T; Init_Matrix(&T,d,d+1); Init_Matrix(&G,T.d,T.d);

  for(i=0;i<=d;i++) for(j=0;j<d;j++) T.x[j][i]=P[i][j]; assert(T.d==T.v+1);

  if(T.v!=Make_G_for_GxMT_UT(T,G)) {puts("Error in Circuit");

    Print_LMatrix(G,"GLZ"); Print_LMatrix(T,"circuit");}

  for(i=0;i<T.d;i++) C[i]=G.x[T.v][i]; Free_Matrix(&G); Free_Matrix(&T);}



#define	KPF	1



/*   check simplicial; if(vol) check FANO, i.e. vol==1

 */

int  SimpUnimod(PolyPointList *P,VertexNumList *V,EqList *E,int vol)

{    int v,d=P->n; for(v=0;v<V->nv;v++)

     {	int e=0,i=0; Long *X=P->x[V->v[v]], *Y[POLY_Dmax+1];

	for(e=0;e<E->ne;e++) if(0==Eval_Eq_on_V(&E->e[e],X,d))

	{ if(i==d) return 0; Y[i++]=E->e[e].a;}		       /* simplicial */

	if(vol) if(1!=(i=SimplexVolume(Y,d))) return 0;	       /* unimodular */

     }	return 1;

}

/*   check simplicial and (if vol) FANO for M-lattice polytope

 */

int  SimpUnimod_M(PolyPointList *P,VertexNumList *V,EqList *E,int vol)

{    int e,d=P->n; for(e=0;e<E->ne;e++)

     {	int v=0,i=0; Long *Y[POLY_Dmax+1];

	for(v=0;v<V->nv;v++) if(0==Eval_Eq_on_V(&E->e[e],P->x[V->v[v]],d))

	{ if(i==d) return 0; Y[i++]=P->x[V->v[v]];}	       /* simplicial */

	if(vol) if(1!=(i=SimplexVolume(Y,d))) return 0;	       /* unimodular */

     }	return 1;

}

#define RelativeSimplexVolume	LinRelSimplexVolume

int  AffRelSimplexVolume(Long *X[POLY_Dmax],int v,int d) /* S-dim=v<=dim */

{    int i,j,k,r=0,det=1; GL_Long B[POLY_Dmax][POLY_Dmax], *b[POLY_Dmax],

        Y[POLY_Dmax][POLY_Dmax],       G[POLY_Dmax][POLY_Dmax], *g[POLY_Dmax];

     for(i=0;i<d;i++) {b[i]=B[i]; g[i]=G[i];

		      for(j=1;j<v;j++)Y[j-1][i]=X[j][i]-X[0][i];} v--;

     for(i=0;i<d;i++) for(j=0;j<d;j++) G[i][j]=(i==j);

     for(i=0;i<v;i++)

     {  GL_Long V[POLY_Dmax]; int nz=0; for(j=r;j<d;j++)

        { GL_Long x=0; for(k=0;k<d;k++)x+=G[j][k]*Y[i][k]; if((V[j]=x))nz=1;}

        if(nz) {det*=GL_V_to_GLZ(&V[r],b,d-r); G_2_BxG(g,b,&d,&r); r++;}

     }  assert(r==v);

     return det;



}



int  LinRelSimplexVolume(Long *X[POLY_Dmax],int v,int d) /* S-dim=v<=dim */

{    int i,j,k,r=0,det=1; GL_Long B[POLY_Dmax][POLY_Dmax],*b[POLY_Dmax],

        G[POLY_Dmax][POLY_Dmax],*g[POLY_Dmax];

     for(i=0;i<d;i++) {b[i]=B[i]; g[i]=G[i];}

     for(i=0;i<d;i++) for(j=0;j<d;j++) G[i][j]=(i==j);

     for(i=0;i<v;i++)

     {  GL_Long V[POLY_Dmax]; int nz=0; for(j=r;j<d;j++)

        { GL_Long x=0; for(k=0;k<d;k++)x+=G[j][k]*X[i][k]; if((V[j]=x))nz=1;}

        if(nz) {det*=GL_V_to_GLZ(&V[r],b,d-r); G_2_BxG(g,b,&d,&r); r++;}

     }	/* if(r!=v){printf("r=%d v=%d\n",r,v);} */

	  assert(r==v);

#ifndef TEST_VOL

     assert(det==AffRelSimplexVolume(X,v,d));

     if(v==2){Long Y[POLY_Dmax]; for(i=0;i<d;i++)Y[i]=X[0][i]-X[1][i];

	r=NNgcd(Y[0],Y[1]); for(i=2;i<d;i++) r=NNgcd(r,Y[i]); assert(r==det);

	}

#endif

     return det;

}

void PrettyPrintDualVert(PolyPointList *P,int vn,EqList *E,int dpn)

{    int i,j;  fprintf(outFILE,"%d %d  %sM:%d %d N:%d %d\n",P->n,E->ne,

	"Vertices of P* (N-lattice)    ",P->np,vn,dpn,E->ne);

     for(j=0;j<P->n;j++)  {for(i=0;i<E->ne-1;i++)fprintf(outFILE,"%2ld ",

	E->e[i].a[j]); fprintf(outFILE,"%2ld\n",E->e[i].a[j]);}

     for(i=0;i<E->ne;i++) assert(E->e[i].c==1);

}

void PrintFanoVert(PolyPointList *P, VertexNumList *V)

{    Long *Z=P->x[0],*N[4*VERT_Nmax]; int i,j,n=0; assert(P->n==4);

     for(i=0;i<V->nv;i++) assert(V->v[i]<V->nv);

     for(i=V->nv;i<P->np;i++){Long *X=P->x[i]; if((X[0]-Z[0])%2==0)

	if((X[1]-Z[1])%2==0)if((X[2]-Z[2])%2==0)if((X[3]-Z[3])%2==0) N[n++]=X;}

     fprintf(outFILE,"P/2: %d points (%d vertices) of P'=P/2 (M-lattice):\n",

	V->nv+n,V->nv);

     for(j=0;j<P->n;j++) {fprintf(outFILE,"P/2: ");

	for(i=0;i<V->nv;i++)fprintf(outFILE,"%2ld ",(P->x[i][j]-Z[j])/2);

	for(i=0;i<n;i++)fprintf(outFILE," %2ld",(N[i][j]-Z[j])/2);

	fprintf(outFILE,"\n");}

}

void Make_FaceIPs(PolyPointList *_P, VertexNumList *_V, EqList *_E,

		  PolyPointList *_DP, FaceInfo *_I);

void Eval_BaHo(FaceInfo *_I, BaHo *_BH);

#define No_OLD_FACE_LIST

#define SQnum_Max	64		/* assume el(0)=min, el::++-- */

int  Add_Square_To_Rel(int el[4],int r,int v,Long rel[SQnum_Max][VERT_Nmax],

	int C[SQnum_Max])

{    int i,j,l,c=el[0]; Long N[VERT_Nmax];

     assert((el[0]<v)&&(el[1]<v)&&(el[2]<v)&&(el[3]<v));

     if(r==0){ C[0]=el[0]; for(i=0;i<v;i++) rel[0][i]=0;

	rel[0][el[0]]=rel[0][el[1]]=1; rel[0][el[2]]=rel[0][el[3]]=-1;

	return 1;}					 /* initialize */

#ifdef	TEST_RK

	printf("rk=%d  el=%ld %ld %ld %ld\n",r,el[0],el[1],el[2],el[3]);

	for(i=0;i<r;i++){for(j=0;j<v;j++)printf(" %2d",rel[i][j]);

	printf(" =rel-in C=%d\n",C[i]);}

#endif

     for(i=0;i<v;i++) N[i]=0; N[el[0]]=N[el[1]]=1; N[el[2]]=N[el[3]]=-1;

     for(l=0;l<r;l++){

        if(c<C[l]){assert(r<SQnum_Max); for(j=r;j>l;j--)

	    { for(i=0;i<v;i++) rel[j][i]=rel[j-1][i]; C[j]=C[j-1];}

	    for(i=0;i<v;i++) rel[l][i]=N[i]; C[l]=c; return r+1;

/* puts("insert New before l-th line");exit(0); */

	}

        else if(c==C[l]) {Long A=rel[l][c], B=N[c], g=NNgcd(A,B);

	assert(g>0); A/=g; B/=g;

#ifdef	TEST_RK

	printf("reduce New with %d-th line: N= A/g*N-B/g*rel find new c:\n",l);

	for(j=0;j<v;j++)printf(" %2d",N[j]);printf(" =N-init c=%d\n",c);

#endif

	j=c; for(c=0;j<v;j++) if((N[j]=A*N[j]-B*rel[l][j])) if(c==0) c=j;

#ifdef	TEST_RK

	for(j=0;j<v;j++)printf(" %2d",N[j]);printf(" =N-reduced c=%d\n",c);

    for(i=0;i<=r;i++){for(j=0;j<v;j++)printf("%2d ",rel[i][j]);puts("out");}

#endif

	if(c==0) { /* puts("no rank increase"); */ return r;}

	}

     }	assert(r<SQnum_Max); for(i=0;i<v;i++)rel[r][i]=N[i];C[r]=c; return r+1;

}

int  PyramidIP(PolyPointList *P,VertexNumList *V,EqList *E,FaceInfo *FI)

{    int i,j,IP=0; Long *X=P->x[V->v[0]];

     for(i=0;i<P->np;i++){Long *Xi=P->x[i]; int e,eq=0;

	for(e=0;e<E->ne;e++){if(0==Eval_Eq_on_V(&E->e[e],Xi,P->n)) eq++;}

	if(eq==1) if((X[0]-Xi[0])%2==0)if((X[1]-Xi[1])%2==0)

	    if((X[2]-Xi[2])%2==0)if((X[3]-Xi[3])%2==0) IP++;

     }  assert(IP<2);

     j=0;for(i=0;i<FI->nf[3];i++) if(FI->nip[3][i])j++;  if(IP)assert(j);

/*     if(j>0){char c[2]; c[1]=0; c[0]='0'+j; Print_VL(P,V,c);exit(0);} */

     return IP;

}

int  Divisibility_Index(PolyPointList *P,VertexNumList *V)

{    int i,j; Long g=0,x; assert(V->nv>1);

     for(i=0;i<P->n;i++)if(!g) g=labs(P->x[V->v[1]][i]-P->x[V->v[0]][i]);

     for(j=1;j<V->nv;j++)for(i=0;i<P->n;i++)

     {	x=labs(P->x[V->v[j]][i]-P->x[V->v[0]][i]);

	if(x) g=Fgcd(g,x); if(g<2) return 1;

     } return g;

}



int  Obstructed_Conifold_Deformations(int S[SQnum_Max][4], int M[SQnum_Max],

	int Q, int R, int v, Long rel[SQnum_Max][VERT_Nmax], int C[SQnum_Max])

{    int s,bad=0; for(s=0;s<Q;s++) if(M[s]==1)

     {	int i,j,rk=0,el[4];

	for(i=0;i<s;i++){for(j=0;j<4;j++)el[j]=S[i][j];

	    rk=Add_Square_To_Rel(el,rk,v,rel,C);}

	for(i=s+1;i<Q;i++){for(j=0;j<4;j++)el[j]=S[i][j];

	    rk=Add_Square_To_Rel(el,rk,v,rel,C);}

	assert(rk<=R); if(rk<R) bad++;

     }	return bad;

}



#define FANO_CONIFOLD	(0)       	/* default: 0=CY-conifold, 1=FANO */

					/* 2-faces basic squar OR vol=1  */

int  ConifoldSing(PolyPointList *P,VertexNumList *V,EqList *E,

	PolyPointList *dP,EqList *dE,int divby)

{    int i,j, nf=0, nsq=0, ndpt=0, rk=0,CF,/* #cd2face #squares #double-pts.*/

     	C[SQnum_Max];Long rel[SQnum_Max][VERT_Nmax];/* rank squar-relations */

     static int npol,nosq,five,nonbasic,ncon,fano; INCI *FInc;

     int PIC, S[SQnum_Max][4], M[SQnum_Max];

     FaceInfo *_FI=(FaceInfo *) malloc(sizeof(FaceInfo)); assert(P->n==4);

     if(divby==0){if(FANO_CONIFOLD) divby=2; else divby=1;} /* set default */

     assert(divby/100<=2); 	if(divby>99) {PIC=divby%100; CF=divby/100;}

     else if (divby>9) {PIC=divby%10; CF=divby/10;} else {PIC=0;CF=divby;}

/*

 *   1st criterion: points::dP->np==dV->nv::cd4+cd1+1::cd0::IPip

 * 	Fano(trian+coni::N & M::\D=2\D'): need	Vol(\D')=2#(\D')-8 <=64

 *						doublepoints = l/2(edges(\D))

 */

     if(_FI==NULL) {printf("ConifoldSing: Unable to allocate _FI\n"); exit(0);}

     Make_Incidence(P, V, E, _FI); npol++;

     nf=_FI->nf[1]; FInc=_FI->f[1]; /* cd2-faces of dP :: edge of P :: */

#ifdef OLD_FACE_LIST

	assert(nF==nf);

#endif

     Make_FaceIPs(P,V,E,dP,_FI);

     for(j=0;j<nf;j++){int e=0, el[4], sq=0; Long *X[POLY_Dmax];

	INCI I=FInc[j]; int f=INCI_abs(I); if(f<3){Print_EL(E,&dP->n,0,"E");

	    Print_PPL(dP,"dP");Print_EL(dE,&dP->n,0,"dE");

	    printf("e<3: nf=%d I=",nf);Print_INCI(FInc[j]);} assert(f>2);

	if(f>4){five++; /* more than 4 vertices */ free(_FI); return 0;}

	i=E->ne;while(!INCI_EQ_0(I)){i--;if(INCI_M2(I))el[e++]=i;I=INCI_D2(I);}

	assert(e==f);for(i=0;i<e;i++)X[i]=E->e[el[i]].a;

	if(e==4){

	    for(i=0;i<P->n;i++)if(X[0][i]+X[1][i]-X[2][i]-X[3][i]) break;

	    if(i==P->n) sq=1;

	    if(!sq){for(i=0;i<P->n;i++)

		if(X[0][i]+X[2][i]-X[1][i]-X[3][i])break;if(i==P->n)sq=2;}

	    if(!sq){for(i=0;i<P->n;i++)

		if(X[0][i]+X[3][i]-X[1][i]-X[2][i])break;if(i==P->n)sq=3;}

	    if(sq==0){nosq++; free(_FI); return 0;} /* 4 vertices: no square */

	}

#ifdef	PRINT_COORD

	{int l;for(l=0;l<e;l++){printf("X[%d]=",l);for(i=0;i<P->n;i++)

	    printf("%3ld ",X[l][i]);printf(" j=%d fn=%d\n",j, nf);}}

#endif

        if(1<RelativeSimplexVolume(X,3,P->n)){nonbasic++;free(_FI);return 0;}

	if(e==4){int mul=0,vv[2]; INCI ID=_FI->v[1][j];		i=el[3];

	    if(sq==2) el[3]=el[0]; else if(sq==3) {el[3]=el[1]; el[1]=el[0];}

	    else if(sq==1) {el[3]=el[1];el[1]=el[2];el[2]=el[0];}

	    else assert(0); el[0]=i; assert((i<el[1])&&(i<el[2])&&(i<el[2]));

	    rk=Add_Square_To_Rel(el,rk,E->ne,rel,C);

            for(i=0;i<4;i++) S[nsq][i]=el[i];			i=V->nv;

	    while(!INCI_EQ_0(ID)){i--; if(INCI_M2(ID)) vv[mul++]=V->v[i];

		ID=INCI_D2(ID);} assert(mul==2);

	    mul=P->x[vv[1]][0]-P->x[vv[0]][0];for(i=1;i<P->n;i++){

		mul=NNgcd(mul,P->x[vv[1]][i]-P->x[vv[0]][i]);}

	    assert(mul==1+_FI->nip[1][j]);	M[nsq]=mul;

	    if(CF==2){assert(mul%2==0);mul/=2;}

	    ndpt+=mul; nsq++;}

     }	if(nsq) ncon++;	    /* doublePts=sum_sq(l(sq^*))   [over 2 for fano] */



     if(CF==2) {Long xB[POLY_Dmax],xN; 				/* Fano case */

	int py=PyramidIP(P,V,E,_FI),

        pic=E->ne-4-rk,		/* vertices of \D^*(N) - 4 - rank(relations) */

	h12=1+ndpt-rk-py,   	/* 1 + doublePts - rk - facetIP(\D')=pyramid */

	vol=LatVol_Barycent(P,V,xB,&xN);assert(0==vol%16);vol/=16; /* degree */

     if((PIC==0)||(PIC==pic))   /* restrict output to PIC=pic */

	{ printf("pic=%d  deg=%2d  h12=%2d  rk=%d #sq=%d ",pic,vol,h12,rk,nsq);

	    printf("#dp=%d py=%d  F=%d %d %d %d #Fano=%d\n",ndpt,py,

	    	_FI->nf[0],_FI->nf[1],_FI->nf[2],_FI->nf[3],++fano);

	    PrettyPrintDualVert(P,V->nv,E,dP->np); PrintFanoVert(P,V);}

	free(_FI);return 1;}



     else if((ndpt==0)&&(V->nv!=P->n+1)) {free(_FI);return 0;}

     else { BaHo BH; 					  /* Calabi-Yau case */

	    int pic, cs, Ind=Divisibility_Index(P,V), I3=Ind*Ind*Ind,

		sing=Obstructed_Conifold_Deformations(S,M,nsq,rk,E->ne,rel,C);

	    Long xB[POLY_Dmax], xN, vol=LatVol_Barycent(P,V,xB,&xN),

		c2h=12*(P->np-1)-2*vol;

	/*  VertexNumList dV; EqList *auxE=(EqList *) malloc(sizeof(EqList));

	    int volN;assert(auxE!=NULL);Find_Equations(dP,&dV,auxE);free(auxE);

	    assert(dV.nv==E->ne); volN=LatVol_Barycent(dP,&dV,xB,&xN);

	 */ BH.mp=P->np; BH.mv=V->nv; BH.nv=E->ne; BH.np=dP->np; BH.n=P->n;

	    Eval_BaHo(_FI, &BH); pic=BH.h1[1]-rk; cs=BH.h1[2]+ndpt-rk;

	    if(pic>1)if(ndpt==0) {free(_FI);return 0;}   /* ndpt=0 for pic=1 */

	    assert(c2h%Ind==0); c2h/=Ind; assert(vol%I3==0);

	if((PIC==0)||(PIC==pic)) /* restrict output to PIC=pic */

	    {printf("pic=%d h12=%d E=%d ",pic,cs,2*(pic-cs));

	     if(pic==1)	printf("H^3=%ld c2H=%ld ",vol/I3,c2h);

	     printf(" sing=%d rk=%d #sq=%d #dp=%d  ",sing,rk,nsq,ndpt);

	     printf("toric=%d,%d  F=%d %d %d %d #CY=%d\n",BH.h1[1],BH.h1[2],

		_FI->nf[0],_FI->nf[1],_FI->nf[2],_FI->nf[3],ncon);

	     PrettyPrintDualVert(P,V->nv,E,dP->np);}

	free(_FI); return nsq;}

}



void Einstein_Metric(CWS *CW,PolyPointList *P,VertexNumList *V,EqList *E)

{    int i,j,tot=0,reg=0,sym=0,ksum=0,sum=0,bary=0,ssroot=0,nofip=0,NR=NON_REF;

     PolyPointList *A = (PolyPointList *) malloc(sizeof(PolyPointList));

     Long S, **root=(Long**)malloc(POINT_Nmax*sizeof(Long**)), *d=NULL,

	PM[VERT_Nmax][VERT_Nmax]; assert(A!=NULL); assert(root!=NULL);

     while(Read_CWS_PP(CW,P))/* nis=noinvss s=sum ks=ksum bcz=bary0 ssr(oot) */

     {	Long C[POLY_Dmax], N; int nis,r=0,s,ks,bcz,ssr, R=KP_VALUE; char c[90];

	Long kPM[VERT_Nmax][VERT_Nmax];

#if(NON_REF)

     	Long D[EQUA_Nmax]; d=D;

#endif

        *c=0; tot++;nis=S=0; A->np=0;A->n=P->n;

	if(SMOOTH) {if(!Ref_Check(P,V,E)) continue;} else

	if(NR) Find_Equations(P,V,E); else assert(Ref_Check(P,V,E));

#if	SMOOTH

        if(!SimpUnimod(P,V,E,1)) continue; reg++;

#endif

	Sort_VL(V); for(i=0;i<V->nv;i++) assert(V->v[i]<V->nv);

	if(NR) for(i=0;i<E->ne;i++) d[i]=E->e[i].c;

	LatVol_Barycent(P,V,C,&N);bcz=(N==0);if(bcz)bary++;/*BaryCenterZero*/



        Make_VEPM(P,V,E,PM); Complete_Poly(PM,E,V->nv,P);

        ssr=SemiSimpleRoots(P,E,root); if(ssr)ssroot++; if(ssr<0)nofip++;



    	for(j=0;j<E->ne;j++) {int x=KPF; if(NR) x*=d[j];

	    for(i=0;i<V->nv;i++) kPM[j][i]=x*PM[j][i]; E->e[j].c=x;

	}   A->np=0; Complete_Poly(kPM,E,V->nv,A);

	if(NR) for(i=0;i<E->ne;i++) E->e[i].c=d[i];



	for(i=0;i<A->n;i++)

	{   for(j=0;j<A->np;j++) S+=A->x[j][i]; if(S)

	    {	/* if(bcz) Print_PPL(P,"bary=0 for Psum!=0"); */ break;}

	}   if(S) {s=0;r=1;} else {s=1;sum++;}



	if(S==0) for(r=2;r<=R;r++)

	{   for(j=0;j<E->ne;j++) {int x=r*KPF; if(NR) x*=d[j];

	        for(i=0;i<V->nv;i++) kPM[j][i]=x*PM[j][i]; E->e[j].c=x; }

	    A->np=0; Complete_Poly(kPM,E,V->nv,A);	S=0;

	    if(NR) for(i=0;i<E->ne;i++) E->e[i].c=d[i];

	    else for(i=0;i<E->ne;i++) E->e[i].c=1;

	    for(i=0;i<A->n;i++)

	    {   for(j=0;j<A->np;j++) S+=A->x[j][i]; if(S) break;

	    }

	    if(S!=0) break;

	}   ks=(S==0);

	if(S!=0) if(r>=KP_PRINT)

	{   fprintf(stderr,"%d %d  Nonzero at r=%d P\n",P->n,V->nv,r);

	    for(i=0;i<P->n;i++){for(j=0;j<V->nv;j++)fprintf(stderr,"%3ld%s",

		P->x[V->v[j]][i], (j+1<(V->nv)) ? " " : "\n");}fflush(0);

	}

	if(S!=0) if(r>KP_EXIT)

	{   fprintf(stderr,"%d %d  Counterexample at r=%d P\n",P->n,V->nv,r);

	    for(i=0;i<P->n;i++){for(j=0;j<V->nv;j++)fprintf(stderr,"%3ld%s",

		P->x[V->v[j]][i], (j+1<(V->nv)) ? " " : "\n");}fflush(0);

	    exit(0);

	}



	if(S==0)

	{   int is; ksum++; for(i=0;i<E->ne;i++) E->e[i].c=1; if(bcz==0){

	    	Print_PPL(P,"Inconsistent: bary!=0 for kPsum==0");exit(0);}

	    is=InvariantSubspace(P,V,E); nis=!is; if(nis) sym++; assert(bcz);

#ifdef	PRINT_ALL_ZEROSUM

	    if(is==0) Print_PPL(P,is ? "zerosum" : "symmetric");fflush(0);

#endif

	}   /* else if(bcz) Print_PPL(P,"bary=0 for kPsum!=0"); */



        strcat(c,"PPL:"); if(nis) strcat(c," symmetric");

	if(ks) strcat(c," kPsum"); else if(s) strcat(c," Psum");

	if(bcz) strcat(c," bary"); if(ssr) strcat(c," semisimple");



	if( ((SSR_PRINT)&&(ssr>0))||((SSR_PRINT>1)&&ssr)||((BARY_PRINT)&&bcz)

	     ||((ZEROSUM_PRINT==1)&&s)||((ZEROSUM_PRINT==2)&&ks) )

	{   int nr=(ssr+1) ? ssr : 0; printf("%d %d    v=%d p=%d roots=%d  "

	    ,P->n,V->nv+nr,V->nv,P->np,nr); puts(c); for(i=0;i<P->n;i++){

	    for(j=0;j<V->nv;j++)printf("%2ld ",P->x[V->v[j]][i]);printf("  ");

	    for(j=0;j<nr;j++)printf(" %2ld",root[j][i]);puts("");

	}   /* Print_PPL(P,c); */ }



/*

#if	(SSR_PRINT)

	if((ssr>0) || ((SSR_PRINT<0)&&ssr))

	{int nr=(ssr+1) ? ssr : 0; printf("%d %d  v=%d roots=%d p=%d  "

	  ,P->n,V->nv+nr,V->nv,nr,P->np); puts(c); for(i=0;i<P->n;i++){

	  for(j=0;j<V->nv;j++)printf("%2d ",P->x[V->v[j]][i]);printf("  ");

	  for(j=0;j<nr;j++)printf(" %2d",root[j][i]);puts("");

	} / * Print_PPL(P,c); * / }

#else

	if(ssr||nis||s||bcz) Print_PPL(P,c);

#endif

*/

     }fprintf(outFILE,"#poly=%d ",tot);if(reg)fprintf(outFILE,"(%dfano) ",reg);

     fprintf(outFILE,"#symm=%d #kPsum=%d #Psum=%d bary=%d ssroot=%d (%d)\n",

	sym,ksum,sum,bary,ssroot,ssroot-nofip); free(A);free(root);exit(0);

}



void Check_New_Fiber(Long PM[][POLY_Dmax], /*int *p,*/ int *d, /*int *nw,*/

	int *s, int r, FibW *F);

int  TriMat_to_WeightZ(GL_Long T[][POLY_Dmax], int *d,int *p,int r,int *s,

	int *nw, Long W[][VERT_Nmax], int *Wmax, FibW *F);

void IPS_Rec_New_Vertex(Long PM[][POLY_Dmax], int *p, int *d, int *nw,

	Long W[][VERT_Nmax], int *Wmax, GL_Long ***G,

	GL_Long *GI[POLY_Dmax][POLY_Dmax],

	GL_Long **GN, GL_Long T[][POLY_Dmax], int *s,int r, FibW *FW,int *CD)

{    int i,j,k, *n=&s[r]; GL_Long *X=T[r];    /* printf("called r=%d\n",r); */

     for(*n=s[r-1]+1;*n<*p;(*n)++)

     {	Long *P=PM[*n]; for(i=0;i<*d;i++)

	{   X[i]=0; for(j=0;j<*d;j++) X[i]+=G[r-1][i][j]*P[j];

	}   for(j=r;j<*d;j++) if(X[j]) break;

#ifdef	TEST_OUT

	printf("X=T[r=%d]:",r);for(i=0;i<*d;i++)printf(" %d",X[i]);

	printf(" j=%d   s=",j);for(i=0;i<=r;i++)printf(" %d",s[i]);puts("");

#endif

	if(j<*d)

	{   X[r]=GL_V_to_GLZ(&X[r],GN,*d-r); for(i=r+1;i<*d;i++) X[i]=0;

	    for(i=r;i<*d;i++) for(j=0;j<*d;j++) { G[r][i][j]=0;

		for(k=0;k<*d-r;k++)G[r][i][j]+=GN[i-r][k]*G[r-1][r+k][j];}

#ifdef TEST

	TEST_GLZmatrix(G[r],*d);

	for(i=0;i<*d;i++){Long Z=0; for(j=0;j<*d;j++) Z+= G[r][i][j]*P[j];

	assert(Z==X[i]);}

#endif

	    IPS_Rec_New_Vertex(PM,p,d,nw,W,Wmax,G,GI,GN,T,s,r+1,FW,CD);

	}

	else if(*CD==0) TriMat_to_WeightZ(T,d,p,r,s,nw,W,Wmax,FW);

	else if((*d-r<=*CD)&&(*d>r)&&(r>1))

	if(TriMat_to_WeightZ(T,d,p,r,s,nw,W,Wmax,FW))

	    Check_New_Fiber(PM,d,s,r,FW);

     }					    /* printf("finished r=%d\n",r); */

}

#ifdef	CHECK_Nref_FIRST

int  Fiber_Ref_Check(Long PM[][POLY_Dmax], int *d, int *p, int *v,

	GL_Long G[POLY_Dmax][POLY_Dmax], GL_Long Ginv[][POLY_Dmax],

	Long X[VERT_Nmax][VERT_Nmax], PolyPointList *A, int r)

{    int i,j; VertexNumList V; EqList E;

     int l,c=0; for(i=0;i<*p;i++)

     {	for(l=r;l<*d;l++) if(GxP(G[l],PM[i],d)) break; if(l==*d)

	{   for(l=0;l<r;l++) A->x[c][l]=GxP(G[l],PM[i],d); c++;

	}

     }  A->np=c; A->n=r; if(!Ref_Check(A,&V,&E)) return 0; /* only necessary */

#else

int  Fiber_Ref_Check(Long PM[][POLY_Dmax], int *d, /*int *p,*/ int *v,

	GL_Long G[POLY_Dmax][POLY_Dmax], /* GL_Long Ginv[][POLY_Dmax],

	Long X[VERT_Nmax][VERT_Nmax],  */  PolyPointList *A, int r)

{    int i,j; VertexNumList V; EqList E;

#endif

     A->np=*v; A->n=*d; for(i=0;i<*v;i++) for(j=0;j<*d;j++)

	A->x[i][j]=GxP(G[j],PM[i],d); /* reflexivity of projection */

     assert(Ref_Check(A,&V,&E)); EL_to_PPL(&E,A,d); A->n=r;

     Remove_Identical_Points(A); return Ref_Check(A,&V,&E);

}

void Add_Ref_Fibers(Long PM[][POLY_Dmax], int *d, int *v, int *s,

	GL_Long G[][POLY_Dmax][POLY_Dmax], int *n, PolyPointList *A, int r)

{    int i,j,c,l; Long X[VERT_Nmax][VERT_Nmax],x; 	/* n==nf */

     GL_Long Ginv[POLY_Dmax][POLY_Dmax];

     for(i=0;i<r;i++)for(j=0;j<*d;j++) X[j][i]=PM[s[i]][j];

     PM_to_GLZ_for_UTriang(X,d,&r,G[*n]); INV_GLZmatrix(G[*n],d,Ginv);

     for(i=0;i<*n;i++) 				/* check if already found */

     {	int newfib=0; for(j=r;j<*d;j++) for(c=0;c<r;c++)

	{   x=0; for(l=0;l<*d;l++) x+=G[i][j][l]*Ginv[l][c]; if(x)newfib=1;

	}   if(!newfib) return;

     }  if(Fiber_Ref_Check(PM,d, /*p,*/ v,G[*n], /*Ginv,X,*/ A,r))

     {	assert(*n < VERT_Nmax); (*n)++; }

}



typedef struct {GL_Long G[VERT_Nmax][POLY_Dmax][POLY_Dmax],

		GK[VERT_Nmax][POLY_Dmax][POLY_Dmax],

		B[VERT_Nmax][POLY_Dmax][POLY_Dmax];

		int nf; PolyPointList F;}			     ek3fli;

void Fiber_Rec_New_Point(PolyPointList *_P, int *v,/* already selected r pts */

	GL_Long ***G, GL_Long *GI[POLY_Dmax][POLY_Dmax], GL_Long **GN,

	GL_Long T[][POLY_Dmax], int *s, int r, ek3fli *F, int *fdim)

{    int i,j,k,*d=&_P->n,*n=&s[r] /*,p=_P->np-1*/ ; GL_Long *X=T[r];

     for(*n=s[r-1]+1; *n<_P->np-(*fdim)+r; (*n)++)

     {	Long *P=_P->x[*n]; for(i=0;i<*d;i++)

	{   X[i]=0; for(j=0;j<*d;j++) X[i]+=G[r-1][i][j]*P[j];

	}   for(j=r;j<*d;j++) if(X[j]) break;

	if(j<*d) 			      /* non-zero :: rank increased */

	{   X[r]=GL_V_to_GLZ(&X[r],GN,*d-r); for(i=r+1;i<*d;i++) X[i]=0;

	    for(i=r;i<*d;i++) for(j=0;j<*d;j++) { G[r][i][j]=0;

		for(k=0;k<*d-r;k++)G[r][i][j]+=GN[i-r][k]*G[r-1][r+k][j];}

            if(r<(*fdim)-1) Fiber_Rec_New_Point(_P,v,G,GI,GN,T,s,r+1,F,fdim);

	    else Add_Ref_Fibers(_P->x,d,v,s,F->G,&F->nf,&F->F,r+1);

	}

     }

}

void Reflexive_Fibrations(PolyPointList *P, int nv, ek3fli *F,int fdim)

{    int n, i, j, d=P->n, s[POLY_Dmax];

     GL_Long T[POLY_Dmax+1][POLY_Dmax],*X=T[0], **G[POLY_Dmax],*GN[POLY_Dmax],

	*GI[POLY_Dmax][POLY_Dmax], GX[(POLY_Dmax*(POLY_Dmax+3))/2][POLY_Dmax];

     F->nf=0; for(j=0;j<d;j++) GN[j]=GX[j];    /* init GLZ pointers */

     for(n=0;n<d;n++) {for(i=0;i<d;i++)/* G=G-list GN=G-new GI->lines of GX */

        if(i<n) GI[n][i]=GI[n-1][i]; else GI[n][i]=GX[j++]; G[n]=GI[n];}

     for(n=0;n<P->np-fdim;n++)

     {	s[0]=n; for(i=0;i<d;i++) X[i]=P->x[n][i]; GL_V_to_GLZ(X,G[0],d);

	for(i=0;i<d;i++) {X[i]=0; for(j=0;j<d;j++)X[i]+=G[0][i][j]*P->x[n][j];}

	Fiber_Rec_New_Point(P,&nv,G,GI,GN,T,s,1,F,&fdim);

     }

}

void AuxDPolyData(PolyPointList *P,PolyPointList *A,int*v,int*n,int*f)

{    Long X[VERT_Nmax][VERT_Nmax]; EqList E; VertexNumList V;

     assert(Ref_Check(P,&V,&E)); *v=V.nv; EL_to_PPL(&E,A,&P->n);

     assert(Ref_Check(A,&V,&E)); *f=V.nv; Make_VEPM(A,&V,&E,X);

     Complete_Poly(X,&E,V.nv,A); *n=A->np;

}

void Test_EK3_Fibration(PolyPointList *P,int edim,

	GL_Long G[POLY_Dmax][POLY_Dmax])

{    int s[VERT_Nmax],t[VERT_Nmax],d=P->n,p=P->np-1; PolyPointList *A;

     assert(NULL != (A=(PolyPointList*) malloc(sizeof(PolyPointList))));

     {	int i,j,e,k, v,n,f; Long PM[VERT_Nmax][POLY_Dmax]; for(i=0;i<p;i++)

	{   for(j=0;j<d;j++)PM[i][j]=GxP(G[j],P->x[i],&d);

	    while(!PM[i][--j]) if(j==0) break;

	    if(j<edim) t[i]=0; else if(j==edim) t[i]=1; else t[i]=2;

	}   j=0;

	for(i=0;i<p;i++) if(t[i]==0)s[j++]=i; e=j;

	for(i=0;i<p;i++) if(t[i]==1)s[j++]=i; k=j;

	for(i=0;i<p;i++) if(t[i]==2)s[j++]=i; fprintf(outFILE,"%d %d  ",d,p);

        for(i=0;i<e;i++)for(j=0;j<edim;j++)A->x[i][j]=PM[s[i]][j];A->n=edim;

puts("PM");

for(j=0;j<d;j++)for(i=0;i<p;i++) (P->np>20) ?

fprintf(outFILE,"%2ld%s",PM[s[i]][j],(i==p-1) ? "\n" : " ") :

fprintf(outFILE,"%4ld%s",PM[s[i]][j],(i==p-1) ? "\n" : " ");

A->np=e;Print_PPL(A,"Elliptic");

	A->np=e;AuxDPolyData(A,A,&v,&n,&f);

	printf("Em:%d %d n:%d %d\n",n,f,e+1,v);

        for(i=0;i<k;i++)for(j=0;j<edim+1;j++) A->x[i][j]=PM[s[i]][j];

A->n=edim+1;A->np=k;Print_PPL(A,"K3");

        A->n=edim+1; A->np=k; AuxDPolyData(A,A,&v,&n,&f);

	printf("  K:%d %d n:%d %d  ",n,f,k+1,v); AuxDPolyData(P,A,&v,&n,&f);

	printf("M:%d %d N:%d %d  pi=",A->np,f,P->np,v);

	for(i=0;i<p;i++)printf("%d",s[i]);puts("");

	for(j=0;j<d;j++)for(i=0;i<p;i++) (P->np>20) ?

	  fprintf(outFILE,"%2ld%s",PM[s[i]][j],(i==p-1) ? "\n" : " ") :

	  fprintf(outFILE,"%4ld%s",PM[s[i]][j],(i==p-1) ? "\n" : " ");

     }	free(A);

}



void Print_Elliptic_K3_Fibrations(PolyPointList *P,int edim,

	GL_Long G[VERT_Nmax][POLY_Dmax][POLY_Dmax],int nk)

{    int x,s[VERT_Nmax],t[VERT_Nmax],d=P->n,p=P->np-1; PolyPointList *A=NULL;

     if(nk)assert(NULL != (A=(PolyPointList*) malloc(sizeof(PolyPointList))));

     for(x=0;x<nk;x++)

     {	int i,j,e,k, v,n,f; Long PM[VERT_Nmax][POLY_Dmax]; for(i=0;i<p;i++)

	{   for(j=0;j<d;j++)PM[i][j]=GxP(G[x][j],P->x[i],&d);

	    while(!PM[i][--j]) if(j==0) break;

	    if(j<edim) t[i]=0; else if(j==edim) t[i]=1; else t[i]=2;

	}   j=0;

	for(i=0;i<p;i++) if(t[i]==0)s[j++]=i; e=j;

	for(i=0;i<p;i++) if(t[i]==1)s[j++]=i; k=j;

	for(i=0;i<p;i++) if(t[i]==2)s[j++]=i; fprintf(outFILE,"%d %d  ",d,p);

        for(i=0;i<e;i++)for(j=0;j<edim;j++)A->x[i][j]=PM[s[i]][j];

	A->n=edim; A->np=e; AuxDPolyData(A,A,&v,&n,&f);

	fprintf(outFILE,"Em:%d %d n:%d %d",n,f,e+1,v);

        for(i=0;i<k;i++)for(j=0;j<edim+1;j++) A->x[i][j]=PM[s[i]][j];

        A->n=edim+1; A->np=k; AuxDPolyData(A,A,&v,&n,&f);

	fprintf(outFILE,"  Km:%d %d n:%d %d  ",n,f,k+1,v);

	AuxDPolyData(P,A,&v,&n,&f);

	fprintf(outFILE,"M:%d %d N:%d %d",A->np,f,P->np,v);

	if(p<=FIB_PERM)

	{   fprintf(outFILE,"  p="); Print_Perm(s,p,"\n");

	}	/*for(i=0;i<p;i++)printf("%d ",s[i]);*/ else Fputs("");

        for(i=0;i<p;i++)for(j=0;j<d;j++)A->x[i][j]=PM[s[i]][j];A->n=d;A->np=p;

	Make_Poly_UTriang(A);

	for(j=0;j<d;j++)for(i=0;i<p;i++) (P->np>20) ?

	  fprintf(outFILE,"%2ld%s",A->x[i][j],(i==p-1) ? "\n" : " ") :

	  fprintf(outFILE,"%4ld%s",A->x[i][j],(i==p-1) ? "\n" : " ");

     }	if(nk)free(A);

}

void All_CDn_Fibrations(PolyPointList *P,int nv,int cd)

{    int x, fdim=P->n-cd; ek3fli *F = (ek3fli *) malloc ( sizeof(ek3fli) );

     PolyPointList *A=&F->F;assert(F!=NULL); Reflexive_Fibrations(P,nv,F,fdim);

     for(x=0;x<F->nf;x++)

     {	int i,j,s[VERT_Nmax],t[VERT_Nmax],d=P->n,p=P->np-1,fn,v,n,f;

	Long PM[VERT_Nmax][POLY_Dmax]; for(i=0;i<p;i++)

	{   for(j=0;j<d;j++)PM[i][j]=GxP(F->G[x][j],P->x[i],&d);

	    while(!PM[i][--j]) if(j==0) break; if(j<fdim) t[i]=0; else t[i]=1;

	}   j=0;

	for(i=0;i<p;i++) if(t[i]==0)s[j++]=i; fn=j;

	for(i=0;i<p;i++) if(t[i]==1)s[j++]=i; fprintf(outFILE,"%d %d  ",d,p);

        for(i=0;i<fn;i++)for(j=0;j<fdim;j++)A->x[i][j]=PM[s[i]][j];A->n=fdim;

	A->np=fn; AuxDPolyData(A,A,&v,&n,&f);

	fprintf(outFILE,"m:%d %d n:%d %d  ",n,f,fn+1,v);

	AuxDPolyData(P,A,&v,&n,&f);

	fprintf(outFILE,"M:%d %d N:%d %d",A->np,f,P->np,v);

	if(p<=FIB_PERM){fprintf(outFILE,"  p="); Print_Perm(s,p,"\n");

	} /* for(i=0;i<p;i++)printf("%d",s[i]); }puts("");*/ else Fputs("");

	for(j=0;j<d;j++)for(i=0;i<p;i++) (P->np>20) ?

	  fprintf(outFILE,"%2ld%s",PM[s[i]][j],(i==p-1) ? "\n" : " ") :

	  fprintf(outFILE,"%4ld%s",PM[s[i]][j],(i==p-1) ? "\n" : " ");

     }	free(F);

}



void Print_GLZ(GL_Long G[][POLY_Dmax],int d,const char *c)

{    int i,j; for(i=0;i<d;i++) {fprintf(outFILE,"%s: ",c);

	for(j=0;j<d;j++)fprintf(outFILE,"%3ld ",G[i][j]);Fputs("");}

}

typedef struct {GL_Long x[POLY_Dmax][POLY_Dmax];} DxD; /* workaround for -O3 */

void Elliptic_K3_Fibration(PolyPointList *P, int nv, int edim)

{    int c,e, *d=&P->n, /*p=P->np-1,*/ cd=P->n-edim, nb=0, nk=0;

     GL_Long  GE[POLY_Dmax][POLY_Dmax], *ge[POLY_Dmax];

     ek3fli *F = (ek3fli *) malloc ( sizeof(ek3fli) ); assert(F!=NULL);

     Reflexive_Fibrations(P,nv,F,edim); for(c=0;c<*d;c++) ge[c]=GE[c];

     for(e=0;e<F->nf;e++) for(c=0;c<P->np-1;c++)

     {	int i,j,nz=0,newf=1; GL_Long *b[POLY_Dmax], X[POLY_Dmax];

	for(i=edim;i<P->n;i++) if((X[i]=GxP(F->G[e][i],P->x[c],&P->n))) nz=1;

	if(nz) /* find new B; compare/add B; BxG-FiberRefCheck; print */

	{   GL_Long Binv[POLY_Dmax][POLY_Dmax];

	    for(i=0;i<cd;i++) b[i]=F->B[nb][i];

	    GL_V_to_GLZ(&X[edim],b,cd);

	    INV_GLZmatrix(F->B[nb],&cd,Binv);

     	    for(i=0;i<nb;i++)                      /* check if already found */

     	    {  	int l,C=0; nz=0; for(j=1;j<cd;j++)     /* for(C=0;C<r;C++) */

        	{   GL_Long x=0; for(l=0;l<*d;l++) x+=F->B[i][j][l]*Binv[l][C];

		    if(x) {nz=1; break; }		/* r->1, d->cd */

        	}   if(nz==0) { newf=0; break; }

	    }	if(newf)

	    {	for(i=0;i<*d;i++)for(j=0;j<*d;j++) GE[i][j]=F->G[e][i][j];

		G_2_BxG(ge,b,d,&edim); INV_GLZmatrix(GE,d,Binv);

		if(Fiber_Ref_Check(P->x,d,/*&p,*/&nv,GE,/*Binv,VV,*/

				   &F->F,edim+1))

		   {nb++; assert(nb<VERT_Nmax);} /* < VERT_Nmax K3 per ell */

	    }	/* printf("e=%d  c=%d  np=%d  nb=%d\n",e,c,P->np,nb); */

	}	/* printf("e=%d c=%d nb=%d  ",e,c,nb); */

	if(c+2==P->np) 						/* finish e */

	{   int n; for(n=0;n<nb;n++)

	    { for(i=0;i<*d;i++)for(j=0;j<*d;j++)F->GK[nk][i][j]=F->G[e][i][j];

		for(i=0;i<*d;i++) { ge[i]=F->GK[nk][i]; b[i]=F->B[n][i];}

		G_2_BxG(ge,b,d,&edim); assert(++nk < VERT_Nmax);

/* 	printf("\nTest_EK3: e=%d nf=%d  n=%d nb=%d\n",e,F->nf,n,nb);

	Test_EK3_Fibration(P,edim,F->GK[nk-1]); */

	    }	for(i=0;i<*d;i++) ge[i]=GE[i]; nb=0;

	}

     }	Print_Elliptic_K3_Fibrations(P,edim,F->GK,nk); free(F);

}

void IP_Simplex_Fiber(Long PM[][POLY_Dmax], int p, int d, /* need PM[i]!=0 */

	FibW *F, int Wmax, int CD)

{    int n,i,j, s[POLY_Dmax+1]; int *nw=&F->nw;     /* nw=#IP_Simp <= Wmax */

     GL_Long T[POLY_Dmax+1][POLY_Dmax],*X=T[0], **G[POLY_Dmax],*GN[POLY_Dmax],

	*GI[POLY_Dmax][POLY_Dmax], GX[(POLY_Dmax*(POLY_Dmax+3))/2][POLY_Dmax];

     *nw=0; /*s[-1]=-1;*/ for(j=0;j<d;j++)GN[j]=GX[j]; /* init GLZ pointers */

     assert(p<=VERT_Nmax);/* G=G-list GN=G-new GI=ptr. at lines of GX=space */

     F->nf=0; for(n=0;n<d;n++) {for(i=0;i<d;i++)

	if(i<n) GI[n][i]=GI[n-1][i]; else GI[n][i]=GX[j++]; G[n]=GI[n];}

     for(n=0;n<p-1;n++)

     {	s[0]=n; for(i=0;i<d;i++) X[i]=PM[n][i];

        GL_V_to_GLZ(X,G[0],d);

	for(i=0;i<d;i++) {X[i]=0; for(j=0;j<d;j++)X[i]+=G[0][i][j]*PM[n][j];}

	IPS_Rec_New_Vertex(PM,&p,&d,nw,F->W,&Wmax,G,GI,GN,T,s,1,F,&CD);

     }if(!CD)if(*nw<p-d){printf("ERROR: nw=%d < codim=%d\n",*nw,p-d);exit(0);}

     /* if(*nw>p-d) printf("WARNING: nw=%d > #pts-dim=%d\n",*nw,p-d); */

     for(i=0;i<*nw;i++)for(n=0;n<d;n++){Long sum=0;

     for(j=0;j<p;j++)sum+=PM[j][n]*F->W[i][j];

     if(sum){printf("At line %d ERROR in W =",n);

	for(j=0;j<p;j++)printf(" %ld",F->W[i][j]);puts("");exit(0);}}

}

void IP_Simplex_Decomp(Long PM[][POLY_Dmax], int p, int d, /* need PM[i]!=0 */

	int *nw,Long W[][VERT_Nmax],int Wmax,int CD) /* nw=#IP_Simp <= Wmax */

{    int n,i,j, s[POLY_Dmax+1]; FibW *FW=NULL;

     GL_Long T[POLY_Dmax+1][POLY_Dmax],*X=T[0], **G[POLY_Dmax],*GN[POLY_Dmax],

	*GI[POLY_Dmax][POLY_Dmax], GX[(POLY_Dmax*(POLY_Dmax+3))/2][POLY_Dmax];

     *nw=0; /*s[-1]=-1;*/ for(j=0;j<d;j++)GN[j]=GX[j]; /* init GLZ pointers */

     assert(p<=VERT_Nmax);/* G=G-list GN=G-new GI=ptr. at lines of GX=space */

     for(n=0;n<d;n++) {for(i=0;i<d;i++)

	if(i<n) GI[n][i]=GI[n-1][i]; else GI[n][i]=GX[j++]; G[n]=GI[n];}

     for(n=0;n<p-1;n++)

     {	s[0]=n; for(i=0;i<d;i++) X[i]=PM[n][i];

        GL_V_to_GLZ(X,G[0],d);

	for(i=0;i<d;i++) {X[i]=0; for(j=0;j<d;j++)X[i]+=G[0][i][j]*PM[n][j];}

	IPS_Rec_New_Vertex(PM,&p,&d,nw,W,&Wmax,G,GI,GN,T,s,1,FW,&CD);

     }if(!CD)if(*nw<p-d){printf("ERROR: nw=%d < codim=%d\n",*nw,p-d);exit(0);}

     /* if(*nw>p-d) printf("WARNING: nw=%d > #pts-dim=%d\n",*nw,p-d); */

     for(i=0;i<*nw;i++)for(n=0;n<d;n++){Long sum=0;

     for(j=0;j<p;j++)sum+=PM[j][n]*W[i][j];

     if(sum){printf("At line %d ERROR in W =",n);

	for(j=0;j<p;j++)printf(" %ld",W[i][j]);puts("");exit(0);}}

}

void Aux_Make_Dual_Poly(PolyPointList *P, VertexNumList *V, EqList *E)

{    Long VM[VERT_Nmax][POLY_Dmax]; int i,j, d=P->n, e=E->ne, v=V->nv;

     assert(e<=VERT_Nmax); P->np=V->nv=e; E->ne=v;

     for(i=0;i<v;i++)for(j=0;j<d;j++) VM[i][j]=P->x[V->v[i]][j];

     for(i=0;i<e;i++){for(j=0;j<d;j++)P->x[i][j]=E->e[i].a[j]; V->v[i]=i;}

     for(i=0;i<v;i++){for(j=0;j<d;j++)E->e[i].a[j]=VM[i][j]; E->e[i].c=1;}

     assert(Ref_Check(P,V,E));

}

#undef	TEST

#define	TEST

#undef	TEST_OUT

void Aux_IPS_Print_Poly(PolyPointList *_P, VertexNumList *_V,

	int np,int nw,int VS,int CD)

{    int j; if(VS) Print_VL(_P,_V,"vertices of P-dual and IP-simplices");

     else   Print_PPL(_P,"points of P-dual and IP-simplices");

     for(j=0; j<np; j++) fprintf(outFILE,"-----");

     if(CD) fprintf(outFILE,"         fibrations:\n");

     else { fprintf(outFILE,"         #=%d",nw); if(nw>np-_P->n)

         fprintf(outFILE," > %d=#pts-dim",np-_P->n);fputs("\n",outFILE);}

}

void Aux_IPS_Print_W(Long *W,int w,int cd)

{    int j, d=0; for(j=0;j<w;j++){fprintf(outFILE," %4d",(int)W[j]);d+=W[j];}

     fprintf(outFILE," %4d=d  codim=%d",d,cd);

}

void Aux_IPS_Print_WP(Long *W,int w,int cd)

{    int j, d=0; for(j=0;j<w;j++){fprintf(outFILE,(w>19) ? " %2d" : " %4d",

	(int)W[j]);d+=W[j];} fprintf(outFILE," %3d=d  codim=%d",d,cd);

}

void Print_Fiber_PolyData(PolyPointList *P,VertexNumList *V,Long *W,int w,

	int n,int nw,int VS,int CD)

{    int cd=0, j, Mmp, Mmv, Mnp, Mnv, Nmp, Nmv, Nnp, Nnv; static int f;

     for(j=0; j<w; j++) if(!W[j]) cd++; cd=cd+P->n-w+1;

     if(CD==0) Aux_IPS_Print_W(W,w,cd); else if(n==0) f=0;



     if(CD||((cd>0)&&(cd<3)&&((P->n)-cd>1)))

     {	int i, s=0, p, D=P->n, d=P->n-cd, fib, ref;

	Long X[VERT_Nmax][VERT_Nmax];

	GL_Long G[POLY_Dmax][POLY_Dmax],Ginv[POLY_Dmax][POLY_Dmax];

	EqList e; VertexNumList v; PolyPointList *F

	    = (PolyPointList *) malloc(sizeof(PolyPointList));assert(F!=NULL);

	for(p=0;p<w;p++)if(W[p]){for(i=0;i<D;i++) X[i][s]=P->x[p][i]; s++;}

#ifdef	TEST_OUT

	{int j; puts("");for(i=0;i<D;i++){printf("X=");

	for(j=0;j<s;j++)printf("%2d ",X[i][j]);puts("");}}

#endif

	PM_to_GLZ_for_UTriang(X,&D,&s,G); INV_GLZmatrix(G,&D,Ginv);

#ifdef	TEST_OUT

	{int j; puts("");for(i=0;i<D;i++){printf("G[%d]= ",i);

	for(j=0;j<D;j++)printf("%2d ",G[i][j]);printf("    X=");

	for(j=0;j<s;j++)printf("%2d ",X[i][j]);puts("");}}

#endif

	for(p=0;p<V->nv;p++)for(i=0;i<D;i++){GL_Long x=0; for(s=0;s<D;s++)

	    x+=G[i][s]*P->x[V->v[p]][s]; F->x[p][i]=x;}

	F->np=P->np; F->n=D; assert(Ref_Check(F,&v,&e));

	Aux_Make_Dual_Poly(F,&v,&e); Make_VEPM(F,&v,&e,X);

	Complete_Poly(X,&e,v.nv,F); F->n=d; Remove_Identical_Points(F);

	fib=Ref_Check(F,&v,&e); Mmp=F->np;Mmv=v.nv;Mnv=e.ne;

	if(fib){Aux_Make_Dual_Poly(F,&v,&e); Make_VEPM(F,&v,&e,X);

	      Complete_Poly(X,&e,v.nv,F); Mnp=F->np;} else Mnp=0;



	if(fib&&CD) {if(f==0){f=1;Aux_IPS_Print_Poly(P,V,w,nw,VS,CD);}

	    Aux_IPS_Print_W(W,w,cd); fprintf(outFILE,

		" fiber m:%d %d n:%d %d\n",Mmp,Mmv,Mnp,Mnv); return;}

	s=0; F->np=P->np;F->n=D; for(p=0;p<w;p++) /* now check ref in N only */

	if(W[p]){for(i=0;i<D;i++) F->x[s][i]=P->x[p][i]; s++;}

	for(p=0;p<w;p++)if(!W[p]){for(i=0;i<D;i++)F->x[s][i]=P->x[p][i]; s++;}

	for(p=w;p<P->np;p++) for(i=0;i<D;i++) F->x[p][i]=P->x[p][i];

	Make_Poly_UTriang(F);

	s=0; for(p=0;p<P->np;p++)

	{   for(i=d;i<D;i++) if(F->x[p][i]) break;

	    if(i==D) {if(s<p) for(i=0;i<d;i++) F->x[s][i]=F->x[p][i]; s++;}

	}   F->n=d;F->np=s;ref=Ref_Check(F,&v,&e);Nmv=e.ne; Nnp=F->np;Nnv=v.nv;

#ifdef	TEST_OUT

	puts("\nFiber:");Print_PPL(F,"Fiber");

#endif

	if(ref)

	{   Long PM[VERT_Nmax][VERT_Nmax]; Aux_Make_Dual_Poly(F,&v,&e);

	    Make_VEPM(F,&v,&e,PM); Complete_Poly(PM,&e,v.nv,F); Nmp=F->np;

	    if(fib)fprintf(outFILE," fiber m:%d %d n:%d %d",Mmp,Mmv,Mnp,Mnv);

	    else fprintf(outFILE," m:%d %d f:%d // m:%d %d n:%d %d",

		Mmp,Mmv,Mnv,Nmp,Nmv,Nnp,Nnv);

	}

	else fprintf(outFILE," m:%d %d f:%d // f:%d n:%d %d",

		Mmp,Mmv,Mnv,Nmv,Nnp,Nnv);

	free(F);

     }	fprintf(outFILE,"\n");

}

#ifdef OLD_IPS			    /* switch of Check_New_Fiber in ... !!! */

void IP_Simplices(PolyPointList *_P, int nv, int PS,int VS,int CDin){

  int i, nw, np = VS ? nv : _P->np-1; Long W[FIB_Nmax][VERT_Nmax];

  VertexNumList V; V.nv=nv; for (i=0;i<nv;i++) V.v[i]=i; int CD;

  for (i=V.nv; i<_P->np-1; i++) if(Vec_is_zero(_P->x[i],_P->n)) {

    Swap_Vecs(_P->x[i],_P->x[_P->np-1],_P->n);

    break;} CD=CDin; assert(CD<4);

  IP_Simplex_Decomp(_P->x,np,_P->n,&nw,W,FIB_Nmax,CD);

  if(nw==0) return;

  if(CD==0) Aux_IPS_Print_Poly(_P,&V,np,nw,VS,CD);

  for(i=0; i<nw; i++) Print_Fiber_PolyData(_P,&V,W[i],np,i,nw,VS,CD);

}

void Check_New_Fiber(Long PM[][POLY_Dmax],int*,int*,int,FibW*)

{    ;}

#else

void Check_New_Fiber(Long PM[][POLY_Dmax],int *d,

	int *s, int r, FibW *F)

{    int i,j,c,l,*n=&F->nf; Long X[VERT_Nmax][VERT_Nmax],x;

     GL_Long Ginv[POLY_Dmax][POLY_Dmax];

     for(i=0;i<r;i++)for(j=0;j<*d;j++) X[j][i]=PM[s[i]][j];

     PM_to_GLZ_for_UTriang(X,d,&r,F->G[*n]); INV_GLZmatrix(F->G[*n],d,Ginv);

     for(i=0;i<*n;i++) if(r==F->r[i])		/* check if already found */

     {	int newfib=0; for(j=r;j<*d;j++) for(c=0;c<r;c++)

	{   x=0; for(l=0;l<*d;l++) x+=F->G[i][j][l]*Ginv[l][c]; if(x)newfib=1;

	}   if(!newfib) {if(!F->PS) F->nw--; return;}

     }

     F->P->np=F->nv; F->P->n=*d; for(i=0;i<F->nv;i++) for(j=0;j<*d;j++)

	F->P->x[i][j]=GxP(F->G[*n][j],PM[i],d); /* reflexivity of projection */

     {	VertexNumList V; EqList E; assert(Ref_Check(F->P,&V,&E));

	EL_to_PPL(&E,F->P,d); F->P->n=r; Remove_Identical_Points(F->P);

	if(Ref_Check(F->P,&V,&E))

	{   assert(*n<VERT_Nmax); F->f[*n]=F->nw-1; F->r[*n]=r; (*n)++;

	}   else if(!F->PS) F->nw--;

     }

}

void Print_Fibrations(PolyPointList *P,FibW *F)

{    int n; char C[VERT_Nmax]; VertexNumList V; EqList E; for(n=0;n<F->nf;n++)

     {	int s[VERT_Nmax], i,r=F->r[n],*d=&P->n,l,c=0,N;	for(i=0;i<P->np-1;i++)

        {   for(l=r;l<*d;l++) if(GxP(F->G[n][l],P->x[i],d)) break;

	    if(l==*d){for(l=0;l<r;l++)F->P->x[c][l]=GxP(F->G[n][l],P->x[i],d);

		s[c++]=i;}

	}   F->P->np=c; F->P->n=r; assert(Ref_Check(F->P,&V,&E));

	for(i=0;i<P->np-1;i++) C[i]='_'; for(i=0;i<c;i++)C[s[i]]='p';

	for(i=0;i<V.nv;i++) C[s[V.v[i]]]='v'; for(i=0;i<P->np-1;i++)

	    fprintf(outFILE,"%s%c", (P->np>20) ? "  " : "    ",C[i]);

	N=F->P->np+1; fprintf(outFILE,"  cd=%d  ",*d-r);

	EL_to_PPL(&E,F->P,&r); assert(Ref_Check(F->P,&V,&E));

	{   Long X[VERT_Nmax][VERT_Nmax]; Make_VEPM(F->P,&V,&E,X);

	    Complete_Poly(X,&E,V.nv,F->P);}

	fprintf(outFILE,"m:%d %d n:%d %d\n",F->P->np,V.nv,N,E.ne);

     }

}

void IP_Simplices_Docu()

{    puts("Allowed fibration flags: 1 2 3 11n 22n 33n 12n 23n with n=[ 123]");

     printf("1,2,3: only fibrations spanned by IP simplices with codimension");

     puts(" <= 1,2,3\n11,22,33: all fibrations with codimension 1,2,3");

     puts("12,23: all codim-1 fibered fibrations with codimension 1,2");

     puts("NNn with n=1,2,3: same as NN and n\n");

     exit(0);

}

void Print_QuotZ(int Z[][VERT_Nmax],int *M,int p,int n)

{    int i,j; for(i=0;i<n;i++)

     {	fprintf(outFILE," /Z%d:",M[i]);

	for(j=0;j<p;j++) fprintf(outFILE," %d",Z[i][j]);

     }

}

void Print_Quotient(Long *V[VERT_Nmax],int d,int v)

{    Long Z[POLY_Dmax][VERT_Nmax], G[POLY_Dmax][POLY_Dmax], M[POLY_Dmax],

	D[POLY_Dmax]; int i,j,r;

     fprintf(outFILE," I=%d",Sublattice_Basis(d,v,V,Z,M,&r,G,D));

     for(i=0;i<r;i++)

     {	fprintf(outFILE," /Z%ld:",M[i]);

	for(j=0;j<v;j++) fprintf(outFILE," %ld",Z[i][j]);

     }

}





void IP_Simplices(PolyPointList *_P, int nv, int PS,int VS,int CDin)

{    int i,j,CD=0,np=_P->np-1; FibW *F = (FibW *) malloc( sizeof(FibW) );

     VertexNumList V; assert(F!=NULL); F->ZS=((PS<0)||(VS<0));

     for (i=nv; i<_P->np-1; i++) if(Vec_is_zero(_P->x[i],_P->n)) {

     Swap_Vecs(_P->x[i],_P->x[_P->np-1],_P->n); break;}

     if((CDin<0)||(CDin>333)) IP_Simplices_Docu();

     if(CDin<10) {CD=CDin; CDin=0;} else if(CDin>99) {CD=CDin % 10; CDin/=10;}

     switch(CDin){ case 0: case 11: case 22: case 33: case 12: case 23: break;

	default: IP_Simplices_Docu(); }	 if(CD > 3) IP_Simplices_Docu();

     if(VS||CDin)

     {  if(nv && (!PS)) {for(i=0;i<nv;i++) V.v[i]=i; V.nv=nv;} else

	{   EqList E; assert(Ref_Check(_P,&V,&E)); nv=V.nv-1;

	    for(i=0;i<nv;i++) for(j=i+1;j<V.nv;j++)

	    if(V.v[i]>V.v[j]) swap(&V.v[i],&V.v[j]); nv=V.v[V.nv-1]+1;

	}

     }

     if(VS)

     {  Print_VL(_P,&V,"vertices of P-dual and IP-simplices");

	for(i=0; i<V.nv; i++) fprintf(outFILE,"-----");

	if(V.nv==nv) IP_Simplex_Fiber(_P->x,nv,_P->n,F,FIB_Nmax,0); else

	{   Long P[VERT_Nmax][POLY_Dmax];

	    for(i=0;i<V.nv;i++)for(j=0;j<_P->n;j++)P[i][j]=_P->x[V.v[i]][j];

	    IP_Simplex_Fiber(P,V.nv,_P->n,F,FIB_Nmax,0);

	}

	fprintf(outFILE,"   #IP-simp=%d",F->nw); if(F->nw>V.nv-_P->n)

	fprintf(outFILE," > %d=#pts-dim",V.nv-_P->n);

	if(F->ZS)

        {   Long *pl[VERT_Nmax]; for(i=0;i<V.nv;i++)pl[i]=_P->x[V.v[i]];

	    Print_Quotient(pl,_P->n,V.nv);

	}   fputs("\n",outFILE);

	for(i=0; i<F->nw; i++)

	{   int cd=_P->n-V.nv+1 ; for(j=0;j<V.nv;j++) if(!F->W[i][j]) cd++;

	    Aux_IPS_Print_W(F->W[i],V.nv,cd);   if(F->ZS) if(F->nz[i])

		Print_QuotZ(&F->Z[F->n0[i]],&F->M[F->n0[i]],nv,F->nz[i]);

	    fprintf(outFILE,"\n");

	}

     }	if(CD)

     {  F->P=(PolyPointList *)malloc(sizeof(PolyPointList));

	assert(F->P!=NULL); F->PS=PS; F->nv=nv;

     }	if(CD||PS)

     {	/* if(CD)*/ IP_Simplex_Fiber(_P->x,np,_P->n,F,FIB_Nmax,CD);

	/* else IP_Simplex_Decomp(_P->x,np,_P->n,&F->nw,F->W,FIB_Nmax,CD);*/

	if(F->nw) { fprintf(outFILE,"%d %d  %s\n",_P->n,_P->np,

	    "points of P-dual and IP-simplices"); for(i=0;i<_P->n;i++)

	    {	for(j=0;j<_P->np;j++) fprintf(outFILE,(_P->np>20) ? " %2d" :

		" %4d", (int)_P->x[j][i]);fprintf(outFILE,"\n");}}

	if(PS)

	{   for(i=0; i<np; i++) fprintf(outFILE,(np>20) ? "---" : "-----");

	    fprintf(outFILE,"    #IP-simp=%d",F->nw); if(F->nw>np-_P->n)

	    fprintf(outFILE," > %d=#pts-dim",np-_P->n); fputs("\n",outFILE);

	    for(i=0; i<F->nw; i++)

	    {   int cd=_P->n-np+1 ; for(j=0;j<np;j++) if(!F->W[i][j]) cd++;

	        Aux_IPS_Print_WP(F->W[i],np,cd); if(F->ZS) if(F->nz[i])

		Print_QuotZ(&F->Z[F->n0[i]],&F->M[F->n0[i]],np,F->nz[i]);

		fprintf(outFILE,"\n");

	    }

	}

	if(CD)

	{   for(i=0; i<np; i++) fprintf(outFILE, (np>20) ? "---" : "-----");

	    fprintf(outFILE,"    #fibrations=%d",F->nf); fputs("\n",outFILE);

	    Print_Fibrations(_P,F);

	}

     }

     if(CDin) switch(CDin){

	case 11:	All_CDn_Fibrations(_P,nv,1);	break;

	case 22:	All_CDn_Fibrations(_P,nv,2); 	break;

	case 33:	All_CDn_Fibrations(_P,nv,3); 	break;

	case 12:	Elliptic_K3_Fibration(_P,nv,_P->n-2); break;

	case 23:	Elliptic_K3_Fibration(_P,nv,_P->n-3); break; }

     if(CD) free(F->P); free(F); return;

}

void IP_Fiber_Data(PolyPointList *PD,PolyPointList *AuxP,int nv,/* PD::N-lat.*/

     Long G[VERT_Nmax][POLY_Dmax][POLY_Dmax],int fd[VERT_Nmax],int *nf,int CD)

{    int i,j,k; FibW *F = (FibW *) malloc ( sizeof(FibW) ); assert(NULL != F);

     F->P=AuxP; F->PS=F->ZS=0; F->nv=nv;

     IP_Simplex_Fiber(PD->x,PD->np-1,PD->n,F,FIB_Nmax,CD); *nf=F->nf;

     for(i=0;i<*nf;i++) { fd[i]=F->r[i];

	for(j=0;j<PD->n;j++)for(k=0;k<PD->n;k++) G[i][j][k]=F->G[i][j][k];

     }	free(F);

}					/* aux routine for nef package */

#endif

/*      =============================================================       */



/*      =============================================================       */

/* find GLZ G such that G*P generates a diagonal basis D;  basis = Ginv x D */

/*   minimum of column gcd's -> basis vector -> while(line-entry%g) reduce  */

Long AuxColGCD(int *d, int l, GL_Long G[][POLY_Dmax], Long *X)

{    Long g=labs(GxP(G[l],X,d)), x;

     while(++l<*d) if((x=labs(GxP(G[l],X,d)))) g=(g) ? Fgcd(g,x) : x; return g;

}

void Normalize_Diagonal(int *d, Long *D, GL_Long **G)

{    int a,b,i; for(a=0;a<*d-1;a++) for(b=a+1;b<*d;b++) if(D[b]%D[a])

     {	GL_Long A, B, g=GL_Egcd(D[a],D[b],&A,&B), X=-D[b]/g, Y=D[a]/g, L;

	D[b]*=D[a]/g; D[a]=g; for(i=0;i<*d;i++)

	{   L=A*G[a][i]+B*G[b][i]; G[b][i]=X*G[a][i]+Y*G[b][i]; G[a][i]=L;

	}

     }	for(i=1;i<*d;i++) assert((D[i]%D[i-1])==0);

}

int  GL_Lattice_Basis(int d, int p, Long *P[POLY_Dmax],    /* return index */

	GL_Long GM[][POLY_Dmax], Long *D, GL_Long BM[][POLY_Dmax])

{    int L,C;Long g,a,index=1;GL_Long V[POLY_Dmax],*G[POLY_Dmax],*B[POLY_Dmax];

     static int x;x++; for(L=0;L<d;L++){V[L]=P[0][L]; G[L]=GM[L]; B[L]=BM[L];}

     for(L=0;L<d;L++)for(C=0;C<d;C++)G[L][C]=(L==C); for(L=0;L<d-1;L++)

     {	int l,c=0; g=0; for(C=0;C<p;C++) if((a=labs(AuxColGCD(&d,L,GM,P[C]))))

	{   if(a==1)

	    {   for(l=L;l<d;l++)V[l]=GxP(G[l],P[C],&d); g=GL_V_to_GLZ(&V[L],B,

		   d-L); G_2_BxG(G,B,&d,&L); c=p; break;  /* P[c] -> B, G.B */

	    }

	    else					 /* search best gcd */

	    {   if((g==0)||(a<g)) {g=a; c=C;}

	    }

	}

	if(c<p)					  /* check for divisibility */

	{   for(l=L;l<d;l++)V[l]=GxP(G[l],P[c],&d);g=GL_V_to_GLZ(&V[L],B,d-L);

	    G_2_BxG(G,B,&d,&L);  			  /* P[c] -> B, G.B */

	    for(C=0;C<p;C++) if((a=GxP(G[L],P[C],&d)) % g)  /* improve line */

	    {	Long vg,va; V[L]=Egcd(g,a,&vg,&va);

		for(l=L+1;l<d;l++) V[l]=va*GxP(G[l],P[C],&d);

		assert(0==g % (vg=GL_V_to_GLZ(&V[L],B,d-L)));

		g=vg; c=C; C=0; G_2_BxG(G,B,&d,&L);

	    }			      /* C==p if finished with improvements */

	}   D[L]=g; index*=g;

     }  g=0; assert(L==d-1);

	for(C=0;C<p;C++) if((a=labs(GxP(G[L],P[C],&d)))) g=(g)? Fgcd(g,a) : a;

	D[L]=g; index*=g; Normalize_Diagonal(&d,D,G); INV_GLZmatrix(GM,&d,BM);

     return index;

}

int  Make_Lattice_Basis(int d, int p, Long *P[POLY_Dmax],  /* index=det(D) */

	Long G[][POLY_Dmax], Long *D) /* G x P generates diagonal lattice D */

{    int i,j,I; GL_Long GLG[POLY_Dmax][POLY_Dmax], Ginv[POLY_Dmax][POLY_Dmax];

     I=GL_Lattice_Basis(d,p,P,GLG,D,Ginv);

     for(i=0;i<d;i++)for(j=0;j<d;j++) G[i][j]=GLG[i][j]; return I;

}

void Old_QuotZ_2_SublatG(Long Z[][POLY_Dmax],int *m,int *M,int *d,

     Long G[][POLY_Dmax]) 		      /* normalize and diagonalize Z */

{    int i,j,k,r;GL_Long GT[POLY_Dmax][POLY_Dmax],Ginv[POLY_Dmax][POLY_Dmax];

     Long g, A[POLY_Dmax][VERT_Nmax];

#ifdef	TEST_QZ

	for(i=0;i<*m;i++){for(j=0;j<*d;j++)printf("%2d  ",Z[i][j]);

	printf("/%d  input\n",M[i]);}

#endif

     for(i=0;i<*m;i++)

     {	g=labs(Z[i][0]); for(j=1;j<*d;j++)if(Z[i][j])g=Fgcd(g,labs(Z[i][j]));

	if(g!=1){if(Fgcd(g,M[i])==1){/*printf("g=%d M=%d\n",g,M[i]);exit(0)*/;}

	else {printf("Non-effective group action [%d]\n",i);exit(0);}}

     }

     for(i=0;i<*m-1;i++)for(j=*m-1;j>i;j--) /* reduce: (g1.g2)  m=lcm(m1,m2) */

     {	int mi,mj;Long *Zi,*Zj;g=Fgcd(M[i],M[j]);/* g2^(m2/m') m'=gcd(m1,m2) */

	mi=M[i]/g; mj=M[j]/g; Zi=Z[i]; Zj=Z[j]; M[i]*=mj; M[j]=g;

	for(k=0;k<*d;k++)

	{   Zi[k]=mj*Zi[k]+mi*Zj[k]; if((Zi[k]%=M[i])<0) Zi[k]+=M[i];

	    if(M[j]>1) {if((Zj[k]%=M[j])<0) Zj[k]+=M[j];}

	}

     }  while(M[*m-1]==1)(*m)--; assert(*m>0);for(i=0;i<*m;i++)assert(M[i]>1);

     for(i=0;i<*m;i++) {Long *Zi=Z[i]; for(j=0;j<*d;j++)

     {	if((Zi[j]%=M[i]) < 0) Zi[j]+=M[i]; A[j][i]=Zi[j];}}

     r=PM_to_GLZ_for_UTriang(A,d,m,GT); INV_GLZmatrix(GT,d,Ginv);

     for(i=0;i<*d;i++)for(j=0;j<*d;j++)G[i][j]=Ginv[j][i];/* Z*G lower trian */

#ifdef	TEST_QZ

	printf("rank=%d  m=%d\n",r,*m);

	for(i=0;i<*m;i++){for(j=0;j<*d;j++)printf("%2d  ",Z[i][j]);

	printf("/%d  normalized\n",M[i]);}

        for(i=0;i<*m;i++){for(j=0;j<*d;j++)printf("%2d  ",GxP(GT[j],Z[i],d));

	printf("/%d  Z*G diagonal\n",M[i]);}

        for(i=0;i<*d;i++){for(j=0;j<*d;j++)printf("%2d  ",G[i][j]);

	printf("=G[%d]\n",i);}

	/*   *m=0; for(i=0;i<*d;i++)for(j=0;j<*d;j++)G[i][j]=(i==j); */

#endif

     assert((*m) == r);

}



/*	g=gcd(M1,M2),  L=lcm(M1,M2)=M1.m2=m1.M2=m1.m2.g, a*m1+b*m2=1        *

 *      G1=g1.g2   (order L),  G2=g2/G1^(a*m1)=g2^b*m2/g1^a*m1  (order g).  */

Long Phase(Long *Z,int p){Long s=0;while(p--)s+=Z[p];return s;}

void Print_QuotientZ(int *r,int *p,Long Z[POLY_Dmax][VERT_Nmax],Long *M)

{    int i,j; fprintf(stderr,"Z-action:\n");

     for(i=0;i<*r;i++){for(j=0;j<*p;j++)

	fprintf(stderr,"%5ld ",Z[i][j]); fprintf(stderr,"  /Z%ld\n",M[i]);}

}

void Normalize_QuotientZ(int *r,int *p,Long Z[POLY_Dmax][VERT_Nmax],Long *M)

{    int i,j=0,k;

     /* for(i=0;i<*r;i++) if(Phase(Z[i],*p)%M[i])  ... don't check phase::I/O

     {	fprintf(stderr,"\nZ%d[i=%d]:",M[i],i); for(k=0;k<*p;k++)

	fprintf(stderr," %d",Z[i][k]); fprintf(stderr,

	"\ndet!=1 in Normalize_QuotientZ\n\n");exit(0);

     } */					/* Print_QuotientZ(r,p,Z,M); */

     for(i=0;i<*r;i++) {Long g=M[i]; assert(g>0);

        for(k=0;k<*p;k++) g=NNgcd(g,Z[i][k]); if(g>1){M[i]/=g;

            for(k=0;k<*p;k++) Z[i][k]/=g;}}



     for(i=0;i<*r;i++) if(M[i]>1) { if(i>j)

	{Long *Zi=Z[i],*Zj=Z[j]; for(k=0;k<*p;k++)Zj[k]=Zi[k]; M[j]=M[i];}

	j++; }  else assert(M[i]==1); *r=j;	     /* drop trivial factors */

     for(i=0;i<*r;i++) {Long *z=Z[i];j=M[i];		 /* make min non-neg */

	for(k=0;k<*p;k++)if((z[k]%=j)<0)z[k]+=j;}

     for(i=0;i<*r-1;i++)for(j=*r-1;j>i;j--)if(M[i]%M[j]) /* Mi -> L; Mj -> g */

     {  Long g=Fgcd(M[i],M[j]),*Zi=Z[i],*Zj=Z[j]; int mi=M[i]/g,mj=M[j]/g;

        M[i]*=mj; for(k=0;k<*p;k++) Zi[k] = (mj*Zi[k]+mi*Zj[k]) % M[i];

        if(g>1)						       /* compute G2 */

	{   Long A,B; assert(1==Egcd(mi,mj,&A,&B)); M[j]=g;

	    for(k=0;k<*p;k++) {	Zj[k]-=A*Zi[k]; assert(0==(Zj[k]%mj));

		Zj[k]/=mj; if((Zj[k]%=g)<0) Zj[k]+=g; }

	}

	else if(j==*r-1) (*r)--;			     	  /* drop G2 */

	else { Zi=Z[*r-1]; for(k=0;k<*p;k++)Zj[k]=Zi[k]; M[j]=M[--(*r)];

	}

     }	/* Print_QuotientZ(r,p,Z,M); */

}

void Test_Effective_Zaction(int *r,int *d,Long Z[POLY_Dmax][VERT_Nmax],Long *M)

{    int i,j; Long g; for(i=0;i<*r;i++)

     {	g=labs(Z[i][0]); for(j=1;j<*d;j++)if(Z[i][j])g=Fgcd(g,labs(Z[i][j]));

	if(g!=1){if(Fgcd(g,M[i])==1){/*printf("g=%d M=%d\n",g,M[i]);exit(0)*/;}

	else {printf("Non-effective group action [%d]\n",i);exit(0);}}

     }

}

void QuotZ_2_SublatG(Long Z[][VERT_Nmax],int *m,Long *M,int *d,

     Long G[][POLY_Dmax]) 		      /* normalize and diagonalize Z */

{    int i,j,r;GL_Long GT[POLY_Dmax][POLY_Dmax],Ginv[POLY_Dmax][POLY_Dmax];

     Long A[POLY_Dmax][VERT_Nmax];

     Normalize_QuotientZ(m,d,Z,M); 	/* don't check determinants !!! */

     Test_Effective_Zaction(m,d,Z,M);

     for(i=0;i<*m;i++) for(j=0;j<*d;j++) A[j][i]=Z[i][j];

     r=PM_to_GLZ_for_UTriang(A,d,m,GT); INV_GLZmatrix(GT,d,Ginv);

     for(i=0;i<*d;i++)for(j=0;j<*d;j++)G[i][j]=Ginv[j][i];/* Z*G lower trian */

#ifdef	TEST_QZ

	printf("rank=%d  m=%d\n",r,*m);

	for(i=0;i<*m;i++){for(j=0;j<*d;j++)printf("%2d  ",Z[i][j]);

	printf("/%d  normalized\n",M[i]);}

        for(i=0;i<*m;i++){for(j=0;j<*d;j++)printf("%2d  ",GxP(GT[j],Z[i],d));

	printf("/%d  Z*G diagonal\n",M[i]);}

        for(i=0;i<*d;i++){for(j=0;j<*d;j++)printf("%2d  ",G[i][j]);

	printf("=G[%d]\n",i);}

	/*   *m=0; for(i=0;i<*d;i++)for(j=0;j<*d;j++)G[i][j]=(i==j); */

#endif

     assert((*m) == r);

}







int  GL_Lattice_Basis_QZ(int d,int p, Long *P[VERT_Nmax], Long *D, /* index */

	Long Z[][VERT_Nmax], Long *M, int *r,

	GL_Long GM[][POLY_Dmax], GL_Long BM[][POLY_Dmax]);

/*   PM_2_Quotie ... general purpose making quotients from PointMatrix

 *   Aux_Mat_2_Q ... translating triantular form on T[s[i]] ... onto FibW

 */

int  PM_2_QuotientZ(Long PM[VERT_Nmax][POLY_Dmax], int *d, int *p,

	Long Z[POLY_Dmax][VERT_Nmax], Long M[POLY_Dmax], int *n)

{    int i,j,I,rk=0; GL_Long G[POLY_Dmax][POLY_Dmax],B[POLY_Dmax][POLY_Dmax];

     Long D[POLY_Dmax],*P[VERT_Nmax];for(j=0;j<*p;j++)P[j]=PM[j];

     for(i=0;i<*d;i++)for(j=0;j<*p;j++)Z[i][j]=PM[j][i];

     *n=PM_to_GLZ_for_UTriang(Z,d,p,G);

     if(*n<*d) for(i=0;i<*n;i++)for(j=0;j<*p;j++)

     {	PM[j][i]=0; for(I=0;I<*d;I++)PM[j][i]+=G[i][I]*Z[I][j];

     }

	I=GL_Lattice_Basis_QZ(*n,*p,P,D,Z,M,&rk,G,B);

#ifdef TEST_OUT

     puts("PM_2_QuotientZ:\n"); for(i=0;i<rk;i++)

	printf("%d ",M[i]) ;printf("  index=%d\n",I); for(i=0;i<rk;i++)

	{for(j=0;j<*p;j++)printf("%3d ",GxP(G[i],PM[j],d)); printf("=GxP Z%d="

	,M[i]);for(j=0;j<*p;j++)printf(" %2d",Z[i][j]);puts("");}

#endif

     *n=rk; return I;

}

void Aux_Mat_2_QuotientZ(GL_Long T[][POLY_Dmax],int *D,int *np,int *d,int *s,

	FibW *F)

{    int i,j, rk,p=*d+1, *z[POLY_Dmax], *m=NULL;

     Long PM[VERT_Nmax][POLY_Dmax], M[POLY_Dmax], Z[POLY_Dmax][VERT_Nmax];

     for(i=0;i<*D;i++) for(j=0;j<p;j++) PM[j][i]=T[j][i];

#ifdef	TEST_out

	{int i,j,dd=*D,pp=p;for(i=0;i<dd;i++){for(j=0;j<pp;j++)

		printf("%3d",PM[j][i]);puts(" =PM2in");}}

#endif

     PM_2_QuotientZ(PM,D,&p,Z,M,&rk); 		assert(F->nw>0);

#ifdef	TEST_out

	{int i,j,dd=rk,pp=p;for(i=0;i<dd;i++){for(j=0;j<pp;j++)

		printf("%3d",PM[j][i]);puts(" =PM2out");}}

#endif

     F->n0[F->nw-1] = (F->nw>1) ? (F->n0[F->nw-2]+F->nz[F->nw-2]) : 0;

     F->nz[F->nw-1] = rk; assert(F->n0[F->nw-1]+F->nz[F->nw-1] <= FIB_Nmax);

     j=F->n0[F->nw-1]; for(i=0;i<rk;i++) {z[i]=F->Z[j+i]; m=&F->M[j];}

/*	assert(rk>=0);printf("rk=%d s[0]=%d i=%d j=%d\n",rk,s[0],i,j); */

     for(i=0;i<rk;i++)for(j=0;j<*np;j++)z[i][j]=0; for(i=0;i<rk;i++)m[i]=M[i];

     for(i=0;i<rk;i++)for(j=0;j<p;j++) z[i][s[j]]=Z[i][j];

#ifdef	TEST_out

			printf("F->nw=%d\n",F->nw);

	for(i=0;i<rk;i++) { printf("Z%d:",M[i]);

	for(j=0;j<p;j++) printf(" %2d",Z[i][j]); puts("");}

#endif

     return;

}

int  TriMat_to_WeightZ(GL_Long T[][POLY_Dmax], int *d,int *p,int r,int *s,

	int *nw, Long W[][VERT_Nmax], int *Wmax, FibW *F)

{    if(TriMat_to_Weight(T,p,r,s,nw,W,Wmax))

     {	if(F!=NULL) if(F->ZS) Aux_Mat_2_QuotientZ(T,d,p,&r,s,F); return 1;

     }	else return 0;

}

Long AuxLinRelGPZ(Long *A,int *j,Long *D,int *d,Long GP[][POLY_Dmax],int *p,

	Long Z[][VERT_Nmax])

{    Long s=0,g=0; int i,l; for(l=0;l<*p;l++){A[l]=(l==(*j)); for(i=0;i<*d;i++)

	A[l]-=(GP[*j][i]/D[i])*Z[i][l]; g=(g) ? NNgcd(A[l],g) : A[l];}

     if(g) {for(l=0;l<*p;l++) s+=(A[l]/=g); return s;} else return 0;

}

void Test_Phase(int d,int p,Long *P[],Long Z[][VERT_Nmax],Long *M,int r,char*c)

{    int i,j; for(i=0;i<r;i++) if(Phase(Z[i],p)%M[i]) break; if(i==r) return;

     fprintf(stderr,"\nDet!=1 for group action (%d<r=%d) Z%ld:",i,r,M[i]);

     for(j=0;j<p;j++)fprintf(stderr," %ld",Z[i][j]);fprintf(stderr,

	"\n%d %d  Input polytope (N lattice): %s\n",d,p,c);for(i=0;i<d;i++)

     for(j=0;j<p;j++)fprintf(stderr,"%5ld%s",P[j][i],(j==p-1)?"\n":" ");

     exit(0);

}

int  ImprovePhase(int L,Long *A,Long *D,int *d,Long GP[][POLY_Dmax],int *p,

	Long Z[][VERT_Nmax])

{    int j,m=D[L],ms; Long s, *z=Z[L], x=Phase(z,*p) % m; if(x==0) return 1;

     if(x<0)x+=m; for(j=*p-1;0<=j;j--)

     {	Long a,b,r,l; s=AuxLinRelGPZ(A,&j,D,d,GP,p,Z) % m; if(s==0) continue;

	if(s<0)s+=m; if(2*s>m){for(l=0;l<*p;l++)A[l]*=-1;s=m-s;}

	ms=Egcd(m,s,&a,&b); if((r=x/ms)) for(l=0;l<*p;l++) z[l]-=r*b*A[l];

#ifdef TEST_ImpPhase

        for(l=0;l<*p;l++)printf("%2d ",A[l]); printf("=lr[%d]   s=%d\n",j,s);

	printf("ms=%d m=%d s=%d a=%d b=%d r=%d x=%d\n",ms,m,s,a,b,r,x);

#endif

	x=Phase(z,*p) % m; if(x==0) return 1; if(x<0)x+=m;

     }	return 0;

}

int  GL_Lattice_Basis_QZ(int d,int p, Long *P[VERT_Nmax], Long *D, /* index */

	Long Z[][VERT_Nmax], Long *M, int *r,

	GL_Long GM[][POLY_Dmax], GL_Long BM[][POLY_Dmax])

{    Long g,a,index=1,*Y; GL_Long V[POLY_Dmax], *G[POLY_Dmax], *B[POLY_Dmax];

     int L,C, tz=(p<VERT_Nmax); Long GP[VERT_Nmax][POLY_Dmax], A[VERT_Nmax];

     for(L=0;L<d;L++){G[L]=GM[L]; B[L]=BM[L]; for(C=0;C<d;C++)G[L][C]=(L==C);}

     for(L=0;L<d-1;L++)

     {	int l,c=0; g=0; for(C=0;C<p;C++) if((a=labs(AuxColGCD(&d,L,GM,P[C]))))

	{   if(a==1)

	    {   for(l=L;l<d;l++)V[l]=GxP(G[l],P[C],&d); g=GL_V_to_GLZ(&V[L],B,

		   d-L); G_2_BxG(G,B,&d,&L); c=p; break;  /* P[c] -> B, G.B */

	    }

	    else					 /* search best gcd */

	    {   if((g==0)||(a<g)) {g=a; c=C;}

	    }

	}

	if(tz)					/* action :: lattice basis */

	{    for(l=0;l<p;l++) A[l]=0; A[(c<p) ? c : C] = 1;

	}

	if(c<p)					  /* check for divisibility */

	{   for(l=L;l<d;l++)V[l]=GxP(G[l],P[c],&d);g=GL_V_to_GLZ(&V[L],B,d-L);

	    G_2_BxG(G,B,&d,&L);  			  /* P[c] -> B, G.B */

	    for(C=0;C<p;C++) if((a=GxP(G[L],P[C],&d)) % g)  /* improve line */

	    {	Long vg,va; V[L]=Egcd(g,a,&vg,&va);

		if(tz) {for(l=0;l<p;l++) A[l]*=vg; A[C]+=va;}

		for(l=L+1;l<d;l++) V[l]=va*GxP(G[l],P[C],&d);

		assert(0==g % (vg=GL_V_to_GLZ(&V[L],B,d-L)));

		g=vg; c=C; C=0; G_2_BxG(G,B,&d,&L);

	    }			      /* C==p if finished with improvements */

	}   D[L]=g; index*=g; if(tz) 	      /* tz::compute GP[L], A, Z[L] */

	{   for(c=0;c<p;c++) GP[c][L]=GxP(G[L],P[c],&d); Y=Z[L];

	    for(l=0;l<=L;l++){V[l]=0;for(c=0;c<p;c++)V[l]+=A[c]*GP[c][l];}

#ifdef TEST

	    for(l=L+1;l<d;l++) {V[l]=0;for(c=0;c<p;c++)

		V[l]+=A[c]*GxP(G[l],P[c],&d); assert(V[l]==0);}

#endif

	    assert(V[L]==g); for(c=0;c<p;c++) Y[c]=A[c]; for(l=0;l<L;l++)

            {   Long R=0; for(c=0;c<p;c++) R+=A[c]*GP[c][l];

		/* printf("V[%d]=%d  R[%d]=%d/%d\n",l,V[l],l,R,D[l]); */

		R/=D[l]; for(c=0;c<p;c++) Y[c]-=R*Z[l][c];

            }

	}

     }  assert(L==d-1); /* for(C=0;C<p;C++) GP[C][L]=GxP(G[L],P[C],&d); */



	if(tz)

	{   int c,l; Long vg,va; for(C=0;C<p;C++) GP[C][L]=GxP(G[L],P[C],&d);

	    Y=Z[L]; C=0; while(!GP[C][L]) assert(C++ < p);

	    g=GP[C][L]; for(c=0;c<p;c++) A[c]=0; A[C]=1; for(c=C+1;c<p;c++)

	    {	if((a=GP[c][L]) % g) {g = Egcd(g,a,&vg,&va);

	for(l=C;l<p;l++) A[l]*=vg; A[c]+=va;}

	    }   if(g<0){g=-g; for(c=0;c<p;c++) A[c]*=-1;}

	index*=D[L]=g; for(c=0;c<p;c++) Y[c]=A[c]; for(l=0;l<L;l++)

            {   Long R=0; for(c=0;c<p;c++) {

		/* printf("GP[c][%d]=%d  R[%d]=%d/%d\n",l,GP[c][l],l,R,D[l]);*/

		R+=A[c]*GP[c][l]; 		}

		R/=D[l]; for(c=0;c<p;c++) Y[c]-=R*Z[l][c];

            }

	for(L=0;L<d;L++) if(Phase(Z[L],p)%D[L]!=0)	/* test determinant */

	if(!ImprovePhase(L,A,D,&d,GP,&p,Z)) if(d<4) {int i,j; fprintf(stderr,

    "\nUnable to remove phase of Z%d. Please send a bug report with\nthe ",L);

	fprintf(stderr,"following data to  kreuzer@hep.itp.tuwien.ac.at\n\n");

	fprintf(stderr,"%d %d  Points:\n",d,p); for(i=0;i<d;i++){

	for(j=0;j<p;j++)fprintf(stderr," %4ld",P[j][i]);fprintf(stderr,"\n");}

	for(i=0;i<d;i++){fprintf(stderr,"Z%d:  ",i);for(j=0;j<p;j++)

	fprintf(stderr," %4ld",Z[i][j]);fprintf(stderr,"  -> %ld /%ld\n",

	Phase(Z[i],p)%D[i],D[i]);} for(i=0;i<d;i++){fprintf(stderr,"GP: ");

	for(j=0;j<p;j++)fprintf(stderr,"%5ld",GP[j][i]);fprintf(stderr,"\n");}

	fprintf(stderr,"\n"); exit(0);}

	    for(L=0;L<d;L++) for(l=0;l<d;l++)		/* test Z.GP == D */

	    {   g=0;for(c=0;c<p;c++)g+=Z[L][c]*GP[c][l];assert(g==D[l]*(l==L));

	    }

	    for(l=0;l<d;l++){if(D[l]>1)for(c=0;c<p;c++)	/* make Z min nonneg */

		if((Z[l][c]%=D[l])<0)Z[l][c]+=D[l];}

	}   else

	{   g=0; for(C=0;C<p;C++) if((a=labs(GxP(G[L],P[C],&d))))

		g = (g) ? Fgcd(g,a) : a; index *= D[L]=g; if(index!=1){puts(

	"Unexpected in GL_Lattice_Basis_QZ: index>1 for p>VERT_Nmax");exit(0);}

	}   *r = (index==1) ? 0 : d;

#ifdef TEST

	if(tz)for(L=0;L<d;L++)for(C=0;C<p;C++)assert(GP[C][L]%D[L]==0);

#endif

     for(L=0;L<d;L++)M[L]=D[L]; Normalize_QuotientZ(r,&p,Z,M);

     /* Test_Phase(d,p,P,Z,D,*r,"GL_Lattice_Basis_QZ"); */

     Normalize_Diagonal(&d,D,G); INV_GLZmatrix(GM,&d,BM); return index;

}

int  Sublattice_Basis(int d, int p, Long *P[],              /* index=det(D) */

	Long Z[][VERT_Nmax], Long *M, int *r,

	Long G[][POLY_Dmax], Long *D) /* G x P generates diagonal lattice D */

{    int i,j,I; GL_Long GLG[POLY_Dmax][POLY_Dmax], Ginv[POLY_Dmax][POLY_Dmax];

     I=GL_Lattice_Basis_QZ(d,p,P,D, Z,M,r, GLG,Ginv);

     /* Test_Phase(d,p,P,Z,M,*r,"Sublattice_Basis"); */

     for(i=0;i<d;i++)for(j=0;j<d;j++) G[i][j]=GLG[i][j]; return I;

}



void Sort_CWS(CWS *W)

{    int i,j, N=W->N,w=W->nw, nz=0,np=0, z[AMBI_Dmax], p[AMBI_Dmax],

	pi[AMBI_Dmax], X[AMBI_Dmax]; Long *L=W->W[0];

     for(i=0;i<N;i++)if(L[i]) p[np++]=i; else z[nz++]=i;

     for(i=0;i<np;i++) pi[i]=p[i]; for(i=0;i<nz;i++) pi[np+i]=z[i];

     for(i=0;i<np-1;i++)for(j=np-1;j>i;j--)

	if(L[pi[j-1]]<L[pi[j]])swap(&pi[j-1],&pi[j]);	if(W->nw>1)

     {	L=W->W[1]; for(i=np;i<N-1;i++)for(j=N-1;j>i;j--)

	if(L[pi[j-1]]<L[pi[j]])swap(&pi[j-1],&pi[j]);

     }	for(j=0;j<w;j++)

     {	for(i=0;i<N;i++)X[i]=W->W[j][pi[i]];for(i=0;i<N;i++)W->W[j][i]=X[i];

     }  for(j=0;j<W->nz;j++)

     {	for(i=0;i<N;i++)X[i]=W->z[j][pi[i]];for(i=0;i<N;i++)W->z[j][i]=X[i];

     }

}

Long WZ_to_GLZ(Long *W,Long *Waux,int *d,Long **G)    /* allows components=0 */

{    int i,j,r=0,J; Long g; for(i=0;i<*d;i++) if(W[i]) Waux[r++]=W[i];

     if(r<2){for(i=0;i<*d;i++)for(j=0;j<*d;j++)G[i][j]=(i==j);

	if(r==1){for(i=0;i<*d;i++)if(W[i]) break; G[0][i]=G[i][0]=1;

	    G[0][0]=G[i][i]=0; return W[i];} else return 0;}

     g=W_to_GLZ(Waux,&r,G); if(r<*d)

     {	j=0; for(i=0;i<*d;i++) if(W[i]) Waux[j++]=i;

     	J=0; while(W[J]) J++; assert(J<*d);

     	for(j=r-1;J<=j;j--)for(i=0;i<r;i++)G[i][Waux[j]]=G[i][j]; /* nonzero */

     	J=0; for(i=0;i<*d;i++) if(W[i]==0) Waux[J++]=i;

     	for(j=0;j<J;j++) for(i=0;i<r;i++)G[i][Waux[j]]=0;    /* zero columns */

     	for(i=r;i<*d;i++)for(j=0;j<*d;j++)G[i][j]=0;	    /* trivial lines */

     	for(i=r;i<*d;i++)G[i][Waux[i-r]]=1; assert(J+r==(*d));

     }

     for(i=0;i<*d;i++){Long t=0;for(j=0;j<*d;j++)t+=G[i][j]*W[j];

	if(t!=g*(i==0)) break;}

     if(i<*d)

     {	fprintf(stderr,"\nError in WZ_to_GLZ (overflow?):\n");for(i=0;i<*d;i++)

	fprintf(stderr,"%ld ",W[i]);fprintf(stderr,"=W  nonzero=%d<%d\n",r,*d);

	for(i=0;i<*d;i++){fprintf(stderr,"G[%d]=",i);  for(j=0;j<*d;j++)

	fprintf(stderr,"%2ld%s",G[i][j],(*d-1==j)?"\n":" ");} exit(0);

     }	return g;

}

Long MxV(Long *Mi, Long *V,int *d)

{    Long x=0; int j; for(j=0;j<*d;j++) x+=Mi[j]*V[j]; return x;

}

void C_to_BrxC(Long **B,Long **C,Long *Xaux,int *r,int *d)/* B::r_last_coor */

{    int l,c,n=*d-*r; for(c=0;c<*d;c++) { for(l=0;l<*r;l++) Xaux[l]=C[n+l][c];

	for(l=0;l<*r;l++) C[n+l][c]=MxV(B[l],Xaux,r); }

}

void Print_xxG(Long **G, int *d, char *s)

{    int i,j; for(i=0;i<*d;i++) {for(j=0;j<*d;j++)

	fprintf(outFILE,"%3ld ",G[i][j]); fprintf(outFILE,"%s\n",s);}

}

int  VP_2_CWS(Long *V[], int n, int v, CWS *CW)

{    int i,j,r, R=0,nw, p[FIB_Nmax],d[FIB_Nmax],wp[FIB_Nmax];

     volatile Long BM[AMBI_Dmax][AMBI_Dmax], CM[AMBI_Dmax][AMBI_Dmax];

     Long Z[POLY_Dmax][VERT_Nmax], G[POLY_Dmax][POLY_Dmax], M[POLY_Dmax],

	D[POLY_Dmax], VM[VERT_Nmax][POLY_Dmax], W[FIB_Nmax][VERT_Nmax],

	*B[AMBI_Dmax], *C[AMBI_Dmax], X[AMBI_Dmax];   if(v>AMBI_Dmax)return 0;

     for(j=0;j<v;j++)for(i=0;i<n;i++)VM[j][i]=V[j][i];

     IP_Simplex_Decomp(VM,v,n,&nw,W,FIB_Nmax,0); for(r=0;r<nw;r++)

     {	p[r]=d[r]=0; for(i=0;i<v;i++) {if(W[r][i])p[r]++; d[r]+=W[r][i];}

	if(p[r]>p[R]) R=r; if(p[R]==p[r]) if(d[r]<d[R]) R=r;  /* p_max d_min */

     }

     for(j=0;j<v;j++) CW->W[0][j]=W[R][j]; CW->d[0]=d[R]; CW->nw=1;

     for(i=0;i<nw;i++) wp[i]=i;					/* w-permut: */

     for(i=0;i<nw-1;i++)

     {	int J=i; for(j=i+1;j<nw;j++) if(d[wp[j]]<d[wp[J]]) J=j;

	r=wp[J]; for(j=J;j>i;j--) wp[j]=wp[j-1]; wp[i]=r;

     }

     for(j=0;j<v;j++) for(i=0;i<v;i++) CM[i][j]=BM[i][j]=(i==j);

     for(j=0;j<v;j++) {C[j]=(Long *)CM[j]; B[j]=(Long *)BM[j];}

     WZ_to_GLZ(CW->W[0],X,&v,C);

     for(r=0;r<nw;r++)

     {	int cd=v-CW->nw; Long Y[AMBI_Dmax]; R=wp[r];

	for(i=CW->nw;i<v;i++) Y[i]=MxV(C[i],W[R],&v);

	for(i=CW->nw;i<v;i++) if(Y[i]) break; 		if(i==v) continue;

	for(j=0;j<v;j++) CW->W[CW->nw][j]=W[R][j];CW->d[CW->nw]=d[R];

#ifdef	TEST_OUT

	for(i=0;i<v;i++)printf("%d ",W[R][i]);printf("=W  Y=");

	for(i=CW->nw;i<v;i++)printf("%d ",Y[i]); puts("");Print_xxG(C,&v,"C");

#endif

	WZ_to_GLZ(&Y[CW->nw],X,&cd,B); C_to_BrxC(B,C,X,&cd,&v); CW->nw++;

	/*Print_XXG(B,&cd,"B"); Print_xxG(C,&v,"BxC");*/

	assert(CW->nw<=v-n); if(CW->nw==v-n) break;

     }	assert(CW->nw==v-n);

     Sublattice_Basis(n,v,V,Z,M,&r,G,D);

     for(i=0;i<r;i++){for(j=0;j<v;j++)CW->z[i][j]=Z[i][j];CW->m[i]=M[i];}

     /* for(i=0;i<r;i++)assert(Phase(Z[i],v)%CW->m[i]==0); */

     CW->N=v; CW->nz=r;

#if  (SORT_CWS)

	Sort_CWS(CW);

#endif

     return 1;

}



void Print_if_Divisible(PolyPointList *P,VertexNumList *V)

{    char divi[99]; Long g=Divisibility_Index(P,V); if(g<2) return;

     sprintf(divi,"divisible by factor=%ld",g); Print_VL(P,V,divi);

}



void Aux_Complete_Poly(PolyPointList *P,VertexNumList *V,EqList *E) /* ??? */

{    int e,v; Long MaxDist[EQUA_Nmax][VERT_Nmax];

     assert(E->ne > P->n);		/* check spanning of dimension */

     for(e=0;e<E->ne;e++)

     {	MaxDist[e][0]=Eval_Eq_on_V(&E->e[e],P->x[V->v[0]],P->n);

	for(v=1;v<V->nv;v++)

	{   Long X=Eval_Eq_on_V(&E->e[e],P->x[V->v[v]],P->n);

	    if(X>MaxDist[e][0]) MaxDist[e][0]=X;

	}

     }	Complete_Poly(MaxDist,E,1,P);

}	/* Complete_Poly unfortunetely requires Matrix[][VERT_Nmax] */



void Make_Dilat_Poly(PolyPointList *P,VertexNumList *V,EqList *E,int k,

	PolyPointList *kP)

{    int e,v; Long MaxDist[EQUA_Nmax][VERT_Nmax]; kP->np=0;

     assert(E->ne > P->n);		/* check spanning of dimension */

     for(e=0;e<E->ne;e++)

     {	MaxDist[e][0]=Eval_Eq_on_V(&E->e[e],P->x[V->v[0]],P->n);

	for(v=1;v<V->nv;v++)

	{   Long X=Eval_Eq_on_V(&E->e[e],P->x[V->v[v]],P->n); assert(X>=0);

	    if(X>MaxDist[e][0]) MaxDist[e][0]=X;

	}   MaxDist[e][0] *= k; E->e[e].c *= k;

     }	Complete_Poly(MaxDist,E,1,kP); for(e=0;e<E->ne;e++) E->e[e].c /= k;

}



void LatVol_IPs_degD(PolyPointList *P,VertexNumList *V,EqList *E,int g)

{    Long vB[POLY_Dmax],vol,Z; int e,j;

     vol=LatVol_Barycent(P,V,vB,&Z); printf("vol=%ld, baricent=(",vol);

     for(j=0;j<P->n;j++)printf("%s%ld",j?",":"",vB[j]); printf(")/%ld\n",vol);

     if(g)

     {	PolyPointList *gP = (PolyPointList *) malloc(sizeof(PolyPointList));

	j=0; for(e=0;e<E->ne;e++) if(E->e[e].c==0)j++; if(j<P->n) { puts(

	    "-B#: IPs at degree D is only implemented for Gorenstein cones!");

	    exit(0);}	  /* parallel-epiped ... to be done */

  	assert(gP!=NULL); gP->n=P->n;gP->np=0; Make_Dilat_Poly(P,V,E,g,gP);

	if(POLY_Dmax*VERT_Nmax<gP->np){puts("increase dim of IP");exit(0);}

								puts("IPs:");

	for(j=0;j<gP->np;j++){ int i,cd=0; for(e=0;e<E->ne;e++)

	    if(E->e[e].c==0) if(0==Eval_Eq_on_V(&E->e[e],gP->x[j],P->n)) cd++;

	    if((cd==0)||(E->ne==P->n+1))

	    {   for(i=0;i<P->n;i++) printf(" %ld",gP->x[j][i]);

		printf("  cd=%d",cd); puts("");}

	}   /* Print_PPL(gP,"gPoly"); */	free(gP);

     }



     if(0){puts("-B#: (I)Ps at degree D, only implemented if 0 is a vertex!");

	puts("to be done");exit(0);}  /* parallel-epiped */

}



int  Check_ANF_Form(Long VM[][VERT_Nmax], int d, int v)

{    int i, r=1, c=0; Long G[POLY_Dmax];

     for(i=0;i<=d;i++) if(VM[i][0]) break; c+=(i==d+1);    /* 0 == VM[0] */

     for(i=1;i<=d;i++) if(VM[i][1]) break; c+=(i==d+1); c+=(VM[0][1]==1);

     if(c!=3) {Print_Matrix(VM, d+1, v+1,"unexpected AFF-NF"); return 1;}

     G[0]=1; for(c=2;c<=v;c++)

     {	for(i=r+1;i<=d;i++)if(VM[i][c])

	    {Print_Matrix(VM, d+1, v+1,"rank increase>1 in AFF-NF");return 1;}

	if(VM[r][c])				/* rank++ => solve G.Vc==1 */

	{   Long g=1; for(i=0;i<r;i++) g-=G[i]*VM[i][c];

	    if(g%VM[r][c]==0) {G[r]=g/VM[r][c]; r++;}

	    else{Print_Matrix(VM,d+1,v+1,"inconsistent ANF (r++)");return 1;}

	}

	else			/*  check G.Vc==1  */

	{   Long g=1; for(i=0;i<r;i++) g-=G[i]*VM[i][c];

	    if(g){Print_Matrix(VM,d+1,v+1,"inconsistent ANF (G)");return 1;}

	}

     }	/* Print_Matrix(VM, d+1, v+1,"Affine-NF"); */         return 0;

}



void Reduce_ANF_Form(Long VM[][VERT_Nmax], int d, int v)

{    int i,j; for(i=0;i<d;i++) for(j=0;j<v-1;j++) VM[i][j]=VM[i+1][j+2];

}



void Make_ANF(PolyPointList *P,VertexNumList *V,       /* affine normal form */

	      EqList *E, Long VM[POLY_Dmax][VERT_Nmax])

{    int i,j, d=P->n, v=V->nv, e=E->ne, p=P->np; assert(V->nv<VERT_Nmax);

     assert(P->n<POLY_Dmax); assert(P->np<POINT_Nmax);



     /* Print_PPL(P,"in");Print_VL(P,V,"vertices");Print_EL(E,&P->n,0,"eq-in");

	PairMat PM; Make_VEPM(P,V,E,PM); Print_Matrix(PM, E->ne, V->nv,"PM");*/

     for(i=0;i<v;i++) P->x[V->v[i]][d]=1; P->n=d+1; 	V->nv++;

     for(j=0;j<=d;j++) P->x[p][j]=0; P->np=p+1;		V->v[v]=p;

     for(i=0;i<e;i++) {E->e[i].a[d]=E->e[i].c; E->e[i].c=0;}

     for(j=0;j<d;j++) E->e[e].a[j]=0;E->e[e].a[d]=-1;   E->e[e].c=1; E->ne++;

     /* Print_PPL(P,"AFF");Print_VL(P,V,"AFFvert");Print_EL(E,&P->n,0,"AFFeq");

	Make_VEPM(P,V,E,PM); Print_Matrix(PM, E->ne, V->nv,"AFF-PM"); */



     Make_Poly_NF(P,V,E,VM);

     if(Check_ANF_Form(VM,d,v)) {Print_PPL(P,"unexpected in ANF");

				fprintf(stderr,"unexpected ANF");exit(0);}

     Reduce_ANF_Form(VM,d,v);	for(i=0;i<d;i++) VM[i][v-1]=0;



     for(i=0;i<e;i++)E->e[i].c=E->e[i].a[d];	  /* restore original P,E,V */

     P->n=d;P->np=p; V->nv=v;E->ne=e;

     /* Print_PPL(P,"Pout");Print_VL(P,V,"Vout");Print_EL(E,&P->n,0,"Eout");*/

}



void EPrint_VL(PolyPointList *_P, VertexNumList *V,double f){

  int i,j; fprintf(stderr,"%d %d  fat=%f\n",_P->n,V->nv,f);

  for(i=0;i<_P->n;i++) { for(j=0;j<V->nv;j++)

    fprintf(stderr," %3ld",_P->x[V->v[j]][i]);fprintf(stderr,"\n");}}



void Print_Facets(PolyPointList *P,VertexNumList *V,EqList *E)

{    int e,err=0; Long VM[POLY_Dmax][VERT_Nmax];

     for(e=0;e<E->ne;e++)

     {	int c=0, v, j; for(v=0;v<V->nv;v++)

	if(0==Eval_Eq_on_V(&E->e[e],P->x[V->v[v]],P->n))

	{   for(j=0;j<P->n;j++) VM[j][c]=P->x[V->v[v]][j]; c++;

	}   for(j=0;j<P->n;j++) for(v=0;v<c;v++) VM[j][v]-=VM[j][c-1];

	Aux_Make_Poly_NF(VM,&P->n,&c);

	for(j=0;j<c;j++) if(VM[P->n-1][j]!=0) err=1;

	if(err){ int i; fprintf(stderr,"%d %d  VM c=%d\n",P->n,V->nv,c);

	    for(i=0;i<P->n;i++){for(j=0;j<c;j++)

		fprintf(stderr," %3ld",VM[i][j]);fputs("",stderr);}

	    EPrint_VL(P,V,0); assert(0);}

	Print_Matrix(VM,P->n-1,c,"");

     }

}



#ifdef FIND_OCTAHEDRON

int  FindOctahedron(PolyPointList *P,VertexNumList *V,EqList *E){Matrix M,G;

  int n,i, x=0, X[90*VERT_Nmax]; for(n=1;n<P->np;n++){int l; for(l=0;l<n;l++)

    { for(i=0;i<P->n;i++) if(P->x[l][i]+P->x[n][i]) break;

      if(i==P->n) {assert(x<90*VERT_Nmax); X[x++]=n;}}}	     // x[l] == -x[n]

  Init_Matrix(&M,x,P->n); Init_Matrix(&G,P->n,P->n);

  for(n=0;n<x;n++)for(i=0;i<P->n;i++)M.x[n][i]=P->x[X[n]][i];

  n=(M.d==Make_G_for_GxMT_UT(M,G));Free_Matrix(&M);Free_Matrix(&G); return n;}

#endif



int  CodimTwoFaceNum(PolyPointList *P,VertexNumList *V,EqList *E)

{    int i, j, n=0, LiVj[FACE_Nmax];

     INCI FI[FACE_Nmax], EI[ 2*VERT_Nmax ];	assert(E->ne<= 2*VERT_Nmax );

     for(i=0;i<E->ne;i++) EI[i]=Eq_To_INCI(&E->e[i],P,V);    /* EqInci=facet */

     for(i=1;i<E->ne;i++) for(j=0; j<i; j++)

     {	int k; INCI x=INCI_AND(EI[i],EI[j]);		/* x=candidate */

	for(k=0;k<n;k++)

	{   if(INCI_LE(FI[k],x))    			/* y=FI[k] */

                if(INCI_EQ(x,FI[k])) 		break;	/* x==y */

		else {FI[k]=x;LiVj[k]=i+j*V->nv;break;}	/* x>y :: y=x; */

            else if(INCI_LE(x,FI[k]))		break;	/* x<y :: break */

        }

	if(n==k) {assert(k<FACE_Nmax); LiVj[n]=i+j*V->nv; FI[n++]=x;}



#ifdef	FIND_OCTAHEDRON				/* dirty for Fano-Projection */

     }	if(P->n!=4){int k,l; Long edge=0;

	for(k=0;k<n;k++)  { Long x=0; i=LiVj[k]/V->nv; j=LiVj[k]%V->nv;

	for(l=0;l<P->n;l++) x=NNgcd(x,E->e[i].a[l]-E->e[j].a[l]);

	if(x>edge)edge=x; } printf("|edge|<=%ld\n",edge); assert(edge>0);



	if(0==FindOctahedron(P,V,E)) Print_PPL(P,"contains no octahedron");

#endif



     }	return n;	 /* non-comparable => new */

}





/*   requires E,V pre-allocation; computes E,V; completes points; returns np

 */

Long Poly_Point_Count(PolyPointList *P,VertexNumList *V,EqList *E)

{    Find_Equations(P,V,E); Aux_Complete_Poly(P,V,E); return P->np;

}





#if(0)



#define	TESTfano		 0

#define	FanoProjNPmax		14

#define FPcirNmax		15

#define PrintFanoProjCand	 1		/* 			 */



#define INCIbits		unsigned long long

int getNI(int N,INCIbits I){return (I>>N)%2;}		/* read INCIDENCE */



int Make_Fano5d(PolyPointList *,int *,EqList *,

		int symDP, int nc, int CC[FPcirNmax][FanoProjNPmax]);





int Fano5d(PolyPointList *P,VertexNumList *V,EqList *E){

  int e,d=P->n,np=P->np-1,z,n=V->nv,nc=0,D[VERT_Nmax],p[POLY_Dmax],symDP=1;

  char s[99]="FanoProjection candidate #nnn"; int CC[FPcirNmax][FanoProjNPmax];

  static int FPc; INCIbits FI[VERT_Nmax],CI[FPcirNmax];

  PolyPointList *Q; EqList *F;  Matrix G, M;		   /* assert(d==4); */

  if(FanoProjNPmax<=np)return 0; assert(d<POLY_Dmax);assert(E->ne<=VERT_Nmax);

  for(z=np;0<=z;z--){{for(n=0;n<d;n++)if(P->x[z][n])break;}if(n==d)break;}

  assert(0<=z); if(z<np)for(n=0;n<d;n++){P->x[z][n]=P->x[np][n];P->x[np][n]=0;}

  for(e=0;e<E->ne;e++) FI[e]=0; for(n=0;n<np;n++) D[n]=1;

  for(e=0;e<E->ne;e++){Long *Y[POLY_Dmax]; int i=0;

    for(n=0;n<np;n++) if(0==Eval_Eq_on_V(&E->e[e],P->x[n],d)){FI[e]+=1<<n;

      if(i>d) return 0; p[i++]=n;}  for(n=0;n<i;n++) Y[n]=P->x[p[n]];

    if(i==d) {if(1!=(SimplexVolume(Y,d))) return 0;}/* simplicial unimodular */

    else {int p1=0,m1=0,p2=0,m2=0,sum=0; Long C[POLY_Dmax]; assert(i==d+1);

      Circuit(d,Y,C); for(i=0;i<=d;i++) {sum+=C[i];

	if(C[i]>0) {if(C[i]>1) p2++; else p1++;}

	else if(C[i]<0) {if(C[i]<-1) m2++; else m1++;}}

      if(sum || (m2*p2)) return 0;     /* Batyrev :: inconsistent projection */

      CI[nc]=0; for(i=0;i<=d;i++) {D[p[i]]=0; if(C[i])CI[nc]+=1<<p[i];}

      for(i=0;i<nc;i++) if(CI[nc]==CI[i]) break;  /* already known circuit? */

      if(i==nc) {for(i=0;i<np;i++) CC[nc][i]=0;	  /* init new circuit */

	if(p2)for(i=0;i<=d;i++) CC[nc][p[i]]=-C[i];/* if(p2) => change signs */

	else for(i=0;i<=d;i++) CC[nc][p[i]]=C[i];

	if(p2||m2) {symDP=0; CC[nc][np]=0;}	 /* circuits with abs(C[])>1 */

	else CC[nc][np]=1;   assert(++nc<FPcirNmax);}

	/* for(i=0;i<=d;i++)printf("%d ",p[i]); printf(" =>  ");

	   for(i=0;i<=d;i++)printf("%ld ",C[i]); puts(" [circuit]"); */

      }

    }

  if(PrintFanoProjCand){int c; FILE *OF=outFILE; outFILE=stdout;

    n=++FPc; e=99; while(n){s[--e]='0'+(n%10);n/=10;}

    for(n=26;n<125-e;n++) s[n]=s[e+n-26]; s[n]=0; Print_PPL(P,s); outFILE=OF;

    printf("Facets[%d]:",E->ne); for(e=0;e<E->ne;e++){

      printf(" "); for(n=0;n<np;n++) printf("%d",getNI(n,FI[e]));} puts("");

    for(c=0;c<nc;c++){int f; printf("Circuit[%d]=",c); for(n=0;n<np;n++)

      printf("%d",getNI(n,CI[c])); printf("  coeffs =");

      for(n=0;n<np;n++)if(getNI(n,CI[c]))printf(" %d",CC[c][n]);printf("  in");

      for(f=0;f<E->ne;f++)if((FI[f]&CI[c])==CI[c])printf(" F[%d]",f);puts("");}

    printf("DoublePt = "); for(n=0;n<np;n++) printf("%d",D[n]); puts("");}



  Init_Matrix(&M,d,d); Q = (PolyPointList *) malloc(sizeof(PolyPointList));

  Init_Matrix(&G,d,d); F = (EqList *) malloc(sizeof(EqList));

  Q->n=P->n+1; for(n=0;n<d;n++) for(z=0;z<d;z++) Q->x[n][z]=(n==z);



  for(e=0;e<E->ne;e++) {int c,x=0,X[FanoProjNPmax];   /* BEGIN go over CELLS */



    void MakeCellBasisFanoP(int *Z){INCIbits I=0;	/* BEGIN base change */

      int i, j, k, l, DP[FanoProjNPmax+1]; DP[np]=1;



      for(i=0;i<d;i++) {for(j=0;j<d;j++) M.x[j][i]=P->x[Z[j]][i]; I+=1<<Z[i];}

      assert(d==Make_G_for_GxMT_UT(M,G)); for(k=0;k<d;k++) {

        for(l=0;l<d;l++){Long s=0; for(i=0;i<d;i++) s+=G.x[l][i]*P->x[Z[k]][i];

	  if(s!=(k==l)){if(TESTfano==1)		     /* >> test UnitBasis << */

	    {Print_LMatrix(G,"G");Print_LMatrix(M,"M");exit(0);} return;}}}

      for(k=0;k<d;k++) {DP[k]=D[Z[k]]; Q->x[P->np-1][k]=0; Q->x[k][d]=0;}

      Q->np=P->np; Q->x[np][d]=0; l=0; for(k=d;k<np;k++) {Q->x[k][d]=0;

        while(getNI(l,I)) l++; DP[k]=D[l];   if(TESTfano==1)printf("l=%d ",l);

	for(i=0;i<d;i++){Q->x[k][i]=0;

	  for(j=0;j<d;j++) Q->x[k][i]+=G.x[i][j]*P->x[l][j]; }

	l++;} 		   if(TESTfano==1){puts("");Print_PPL(Q,"fano");} else

		     if(TESTfano==2){Q->n--;Print_PPL(Q,"fanoP");Q->n++;} else

      if(inFILE!=stdin)Make_Fano5d(Q,DP,F,symDP,nc,CC);}/* ENDof base change */



    for(n=0;n<np;n++) if(getNI(n,FI[e])) X[x++]=n;

    if(x==d) MakeCellBasisFanoP(X);		/* simplical facet case */

    else {int Y[POLY_Dmax]; assert(x==d+1);	/*  circuit facet case  */

      for(c=0;c<nc;c++)if((CI[c]&FI[e])==CI[c])break;

      assert(c<nc); for(n=0;n<x;n++) if(getNI(X[n],CI[c])){ /* drop X[n] */

	int y=0; for(z=0;z<x;z++) if(z!=n) Y[y++]=X[z];

	if(abs(CC[c][X[n]])==1) MakeCellBasisFanoP(Y);} /* call MakeCBF */

      if(TESTfano==1){for(c++;c<nc;c++)if((CI[c]&FI[e])==CI[c])break;

	assert(c==nc);}

      }					   /* ENDof circuit facet case  */

    }						      /* ENDof go over CELLS */



  free(Q); free(F); Free_Matrix(&M); Free_Matrix(&G); return 1;}



/*

 * P->x[p][n] = n-th coordinate of p-th point with  0 <= n < d,  0 <= p < np.

 * For 4d projections of 5d Fanos we have d=4  (but P->n is already set to 5).

 * Dpt[i] is 1 if  P->x[i]  may be a double point and is 0 otherwise.

 * The first d points on P->x[0,...,d-1] have been transformed to a standard

 *     	basis and the last point P->x[np-1] denotes the origin 0.

 * The subroutine  "Print_Fano5d(P,Dpt)"  now needs to assign the last

 *	coordinate to the $np$ points on P and possible add further $na$

 *	points if there are $na$ double points. For each of the assignments

 *      P->np has to be set to np+na and after a reflexivity check

 *	if(Ref_Check(P,&V,F)) the polytope is printed by  Print_PPL(P,"fano");

 */



int TempVecUpdate0(int tempvec[], int l, int* atotal_zeiger, int limitwert,

	int singlelimit, int* zero_zeiger){

					/*Erhoehung von tempvec und atotal*/



/* Hier ist l Laenge von tempvec, atotal_zeiger zeigt auf atotal=Summe der

   Eintraege, und limitwert max. Summe */



  #if (ALL_FANOS_BUT_INEFFICIENT)

    singlelimit++;

  #endif



  int akt=l-1; /* akt. Index, der erhoeht werden soll */



  while(akt >= 0){

    if ((*atotal_zeiger < limitwert) && (tempvec[akt] < singlelimit)){



     if (tempvec[akt] == 0) *zero_zeiger = *zero_zeiger - 1;



     tempvec[akt]++;

     *atotal_zeiger = *atotal_zeiger + 1; /* ist <=limitwert */

     return 1;

   }



   if (tempvec[akt] != 0) *zero_zeiger = *zero_zeiger + 1;



   *atotal_zeiger -= tempvec[akt];

   tempvec[akt]=0;

   akt=akt-1;

  }

  return 0;

}



int TempVecUpdate1(int tempvec[], int l, int* atotal_zeiger, int limitwert,

	int dpindex, int singlelimit, int* zero_zeiger){

/* Erhoehung von tempvec und atotal, wobei ein Index auf DP zeigt */



/* Hier ist l Laenge von tempvec, atotal_zeiger zeigt auf atotal=Summe der

   Eintraege (inkl. DP), limitwert max. Summe, dpindex Index von DP */



  #if (ALL_FANOS_BUT_INEFFICIENT)

    singlelimit++;

  #endif



  int akt=l-1;/*akt. Index, beginnt hinten*/



  while(akt >= 0){

    if (akt==dpindex){

      if(((*atotal_zeiger+1) < limitwert) && ((tempvec[akt]+1) < singlelimit)){



        if (tempvec[akt] == 0) *zero_zeiger = *zero_zeiger - 1;



        tempvec[akt]++;

        *atotal_zeiger = *atotal_zeiger + 2; /* ist <= limitwert */

        return 1;

      }

      *atotal_zeiger -= 2*tempvec[akt]; /* akt springt eine Stelle

							weiter nach vorne */



      if (tempvec[akt] != 0) *zero_zeiger = *zero_zeiger + 1;



      tempvec[akt]=0;

      akt=akt-1;

    }

    else{

      if ((*atotal_zeiger < limitwert) && (tempvec[akt] < singlelimit)){



        if (tempvec[akt]==0) *zero_zeiger = *zero_zeiger - 1;



        tempvec[akt]++;

        *atotal_zeiger = *atotal_zeiger + 1; /* ist <=limitwert */

        return 1;

      }

      *atotal_zeiger -= tempvec[akt]; /* akt springt eine Stelle

							weiter nach vorne */



      if (tempvec[akt] != 0) *zero_zeiger = *zero_zeiger + 1;



      tempvec[akt]=0;

      akt=akt-1;

    }

  }

  return 0;

}



/* Falls Fano, gibt 1 zurueck */

int DisplayFano(PolyPointList *P, EqList *E){

 VertexNumList V;

 if(Ref_Check(P,&V,E)) { if(SimpUnimod_M(P,&V,E,1))

   { Print_PPL(P,"fano"); return 1;

   }

 }

 return 0;

}



int CCtest(PolyPointList *P, int d, int np, int nc,

					int CC[FPcirNmax][FanoProjNPmax]){

  int i,j,temp;



  #if (ALL_FANOS_BUT_INEFFICIENT)

   return 1;

  #else



  for(i=0;i<nc;i++)/*Ueber alle Circuits laufen*/

    {

    if (CC[i][np-1] == 0)/*Also vom Typ 1 0 0 1 -2 Schluss 0*/

      {

        temp=0;

	for(j=0;j<(np-1);j++)

	  temp += P->x[j][d]*CC[i][j];

        if ((temp + P->x[np-1][d])!=0)

          return 0;

      }

    else/*Also vom Typ 1 -1 1 0 -1 Schluss 1*/

      {

        /*1. Fall: 1 -1 1 0 -1 1 stimmt!*/

        temp=0;

	for(j=0;j<np;j++)

	  temp += P->x[j][d]*CC[i][j];

        if (temp !=0)

	  {/*2. Fall: -1 1 -1 0 1 1 stimmt!*/

           temp=0;

    	   for(j=0;j<(np-1);j++)

     	     temp -= P->x[j][d]*CC[i][j];

           if ((temp + P->x[np-1][d])!=0)

            return 0;

	  }

      }

    }

  return 1;



  #endif

}



/* Bestimmt alle Moeglichkeiten fuer Fanos, gibt Anzahl zurueck */

int CalculateFano(PolyPointList *P,EqList *E, int d, int np, int na,

		  int aDP, int bDP, int cDP, int s[], int modeDP,

		  int zeronumber, int nc, int CC[FPcirNmax][FanoProjNPmax]){



  /*zeronumber gibt Anzahl an 0-Abstaenden an, muss <= d+1 sein*/



  int nf_temp=0;



  int i;



  P->np = np+1+na;



  /***  Bestimmen von letzten Koordinaten von Ecken ganz oben ueber

	d, ..., np-2; sowie schliesslich von DPs drunter

   	so dass Bedingung erfuellt ist, dass Summe aller Abstaende >= 1

	kleiner/gleich Dimension von P = d+1 ist

        und einzelner Abstand (Wert) <= d. (Neuer Satz) ***/



  int l=np-1-d; /* Ist immer > 0 */

  int tempvec[FanoProjNPmax]; /* Hat (bis auf Faelle 5,6) Laenge l, Indizes

		gehen von 0, ..., l-1=np-2-d, und entsprechen d, ..., np-2 */

  int atotal; /* Gibt totale Summe aller Abstaende an, von Indizes in

						tempvec (und DPs darunter) */



  for (i=0;i<l-1;i++){

	tempvec[i]=0;

  }



  if (modeDP==1){

  /** Fall: Es gibt ueberhaupt keine DPs

			(oder nur 1 DP in 0, ..., d-1 -> mit Wert 0) **/



  atotal=1; /* min. Wert */

  tempvec[l-1]=1;

  zeronumber = zeronumber + l - 1;



     do{

       if (zeronumber <= (d+1)){

       for(i=0;i<l;i++){

	 P->x[i+d][d]=-s[i+d]-tempvec[i];

       }

       if (CCtest(P,d,np,nc,CC) == 1)

         nf_temp=nf_temp+DisplayFano(P,E);

       }

     } while(TempVecUpdate0(tempvec, l, &atotal, d+1, d, &zeronumber));

  } else if (modeDP==2){

  /**   Fall: 0 ist DP, aber es gibt sonst keine DPs

			(oder nur 1 DP in 0, ..., d-1 -> mit Wert 0) **/



  atotal=0; /* min. Wert */

  tempvec[l-1]=0;

  zeronumber = zeronumber + l;



     do{

       if (zeronumber <= (d+1)){

       for(i=0;i<l;i++){

	 P->x[i+d][d]=-s[i+d]-tempvec[i];

       }

       if (CCtest(P,d,np,nc,CC) == 1)

         nf_temp=nf_temp+DisplayFano(P,E);

       }

     }while(TempVecUpdate0(tempvec, l, &atotal, d, d, &zeronumber));

  }

  else if (modeDP==3){

  /** Fall: 0 ist kein DP, aber es gibt noch einen DP, nicht in 0, ..., d-1 **/



     atotal=1; /* min. Wert */

     tempvec[l-1]=0;

     zeronumber = zeronumber + l;



     do{

       if (zeronumber <= (d+1)){

       for(i=0;i<l;i++){

	 P->x[i+d][d]=-s[i+d]-tempvec[i];

       }

       /* Letzte Koordinate von DP ausserhalb bestimmen */

       P->x[np+1][d]=P->x[aDP][d]-1;



       if (CCtest(P,d,np,nc,CC) == 1)

         nf_temp=nf_temp+DisplayFano(P,E);

       }

     }while(TempVecUpdate1(tempvec, l, &atotal, d+1, aDP-d, d, &zeronumber));

  }

  else if (modeDP==4){

  /** Fall: 0 ist DP, und es gibt noch einen DP, nicht in 0, ..., d-1 **/



     atotal=1; /* min. Wert */

     tempvec[l-1]=0;

     zeronumber = zeronumber + l;



     do{

       if (zeronumber <= (d+1)){

       for(i=0;i<l;i++){

	 P->x[i+d][d]=-s[i+d]-tempvec[i];

       }

       /* Letzte Koordinate von DP ausserhalb bestimmen */

       P->x[np+2][d]=P->x[bDP][d]-1;



       if (CCtest(P,d,np,nc,CC) == 1)

         nf_temp=nf_temp+DisplayFano(P,E);

       }

     }while(TempVecUpdate1(tempvec, l, &atotal, d, bDP-d, d, &zeronumber));

  }

  else if (modeDP==5){

  /**Fall: 0 ist kein DP, aber es gibt noch einen DP in 0, ..., d-1 und einen

     ausserhalb (schon bestimmt)**/



     atotal=0;/*min. Wert*/

     int zwstelle=bDP-d;

     zeronumber = zeronumber + l - 1;



     /* Zwei Teile von d, ..., np-2: d, ..., bDP-1, und bDP+1, ..., np-2

     also: 0, ..., bDP-1-d=zwstelle-1, und bDP+1-d=zwstelle+1, ..., np-2-d=l-1

     entspricht: 0, ..., zwstelle-1, und zwstelle, ..., l-2

						in tempvec der Laenge l-1*/



     do{

       if (zeronumber <= (d+1)){

       for(i=0;i<zwstelle;i++){

	 P->x[i+d][d]=-s[i+d]-tempvec[i];

       }

       for(i=zwstelle;i<l-1;i++){

	 P->x[i+d+1][d]=-s[i+d+1]-tempvec[i];

       }



       if (CCtest(P,d,np,nc,CC) == 1)

         nf_temp=nf_temp+DisplayFano(P,E);

       }

     }while(TempVecUpdate0(tempvec, l-1, &atotal, d, d, &zeronumber));

   }

  else if (modeDP==6){

  /** Fall: 0 ist DP, und es gibt noch einen DP in 0, ..., d-1 und einen

	ausserhalb (schon bestimmt)**/



     atotal=0; /* min. Wert */

     int zwstelle=cDP-d;

     zeronumber = zeronumber + l - 1;



     /* Zwei Teile von d, ..., np-2: d, ..., cDP-1, und cDP+1, ..., np-2

     also: 0, ..., cDP-1-d=zwstelle-1, und cDP+1-d=zwstelle+1, ..., np-2-d=l-1

     entspricht: 0, ..., zwstelle-1, und zwstelle, ..., l-2

						in tempvec der Laenge l-1*/



     do{

       if (zeronumber <= (d+1)){

       for(i=0;i<zwstelle;i++){

	 P->x[i+d][d]=-s[i+d]-tempvec[i];

       }

       for(i=zwstelle;i<l-1;i++){

	 P->x[i+d+1][d]=-s[i+d+1]-tempvec[i];

       }



       if (CCtest(P,d,np,nc,CC) == 1)

         nf_temp=nf_temp+DisplayFano(P,E);

       }

     }while(TempVecUpdate0(tempvec, l-1, &atotal, d-1, d, &zeronumber));

  }



  return nf_temp;

}



/* Berechnet alle moeglichen (d+1)-dim. Fanos (mit <= maxVnumber Ecken), die

	auf d-dim. Polytop projezieren; gibt Anzahl aus;

   ACHTUNG bei ALL_FANOS_BUT_INEFFICIENT=0: Es fehlen genau die eindeutigen mit

   d+2 Ecken (Fanosimplex) und 3*(d+1) Ecken (nur in gerader Dimension d+1) */





int Make_Fano5d(PolyPointList *P,int *Dpt,EqList *E,	    /* nc=#Circuits */

	int symDP,int nc,int CC[FPcirNmax][FanoProjNPmax]){/* CC=CircCoeffs */

  int nf=0; int d=P->n-1, np=P->np;/*Achtung, anders als oben wirklich ALLE

							Gitterpunkte von P*/





  #if (ALL_FANOS_BUT_INEFFICIENT)

     int maxVnumber=3*P->n;

  #else

     int maxVnumber=3*P->n-1;

     /* Reicht da jede n-dim. Fano <= 3n-1 Ecken hat; mit

	genau einer bekannten Ausnahme mit 3n Ecken, falls n gerade ist */

  #endif



  /*Circuits sind (bei np=6) entweder von Form 1 0 0 1 -2 Schluss 0 (np=6)

				oder 1 -1 1 0 -1 Schluss 1*/



  int i,j,k;



  /*Folgende Variablen werden hier bestimmt:*/

  int aDP=-1,bDP=-1,cDP=-1;/*Indizes von Doppelpunkten*/

  int s[FanoProjNPmax+1];/*Summe der Koordinaten (0, ..., d-1)*/



  /*Bestimmen von s*/



  for(i=0;i<np;i++){

    s[i] = 0;



    for(j=0;j<d;j++){

      s[i]=s[i]+P->x[i][j];

    }

  }



  /* Bestimmung von letzter Koordinate von (oberen) Ecken ueber 0, ..., d-1

	und ueber np-1=Proj.ecke */



  for(i=0;i<d;i++){

   P->x[i][d]=0;

  }

  P->x[np-1][d]=1;



  /*0-Punkt wird eingefuegt an Stelle np*/



  for(j=0;j<=d;j++){

     P->x[np][j]=0;

    }



  /**Bestimmen von Doppelpunkten (werden an Stellen np+1, np+2, np+3

	eingefuegt); gibt unterschiedliche Faelle (wird als letzte Variable

				uebergeben)**/



  /*printf("\n1.Fall: Keine DPs\n");*/

  nf = nf + CalculateFano(P,E,d,np,0,aDP,bDP,cDP,s,1,0,nc,CC);/*Keine DPs*/



  if ((maxVnumber-np) > 0){



  /*1 oder 2 DPs, aber keiner ist 0*/



  for(i=0;i<d;i++){

    if (Dpt[i]==1){

      aDP=i;

      for(k=0;k<d;k++){

        P->x[np+1][k]=P->x[aDP][k];

      }

      P->x[np+1][d]=-1;

      /*printf("\n1.Fall: 1 DP am Anfang (%d)\n", aDP);*/

      nf = nf + CalculateFano(P,E,d,np,1,aDP,bDP,cDP,s,1,1,nc,CC);

					/*1 DP in 0,...,d-1; aber nicht 0-DP*/



      if ((maxVnumber-np) > 1){



	/*wegen Satz von Casagrande bzw. klar: keine 2 DPs in 0, ..., d-1*/



      for(j=d;j<np-1;j++){

	if ((Dpt[j]==1) && (ZeroSum(P->x[i],P->x[j],d))){

          bDP=j;

          for(k=0;k<d;k++){

            P->x[np+2][k]=P->x[bDP][k];

	  }

          P->x[np+2][d]=0;/*Das ist Satz von Casagrande*/

          P->x[bDP][d]=1;

          /*printf("\n5.Fall: 2 DPs, 1 am Anfang (%d,%d)\n", aDP,bDP);*/

          nf = nf + CalculateFano(P,E,d,np,2,aDP,bDP,cDP,s,5,2,nc,CC);

					/* noch 1 DP nicht in 0, ..., d-1 */

	}

      }

      }

    }

  }



  for(i=d;i<np-1;i++){

    if (Dpt[i]==1){

      aDP=i;

      for(k=0;k<d;k++){

        P->x[np+1][k]=P->x[aDP][k];

      }

      /*printf("\n3.Fall: 1 DP nicht am Anfang (%d)\n", aDP);*/

      nf = nf + CalculateFano(P,E,d,np,1,aDP,bDP,cDP,s,3,0,nc,CC);

			/*   1 DP, nicht in 0, ..., d-1; aber nicht 0-DP  */

    }

  }



  /*	Nach Satz von Casagrande und Reid nicht moeglich, dass 2 DPs,

	ungleich 0, gibt, die nicht in 0, ..., d-1 sind			*/



  /*0 ist jetzt DP, Obstruktion: kein Circuit mit Koeffizient von

							Absolutbetrag > 1*/

  if (symDP==1){



  aDP = np-1;

  for(k=0;k<d;k++){

    P->x[np+1][k]=0;

  }

  P->x[np+1][d]=-1;



  nf = nf + CalculateFano(P,E,d,np,1,aDP,bDP,cDP,s,2,0,nc,CC);

						/*  Ausser 0-DP keine DPs  */



  if ((maxVnumber-np) > 1){



  for(i=0;i<d;i++){

    if (Dpt[i]==1){

      bDP=i;

      for(k=0;k<d;k++){

        P->x[np+2][k]=P->x[bDP][k];

      }

      P->x[np+2][d]=-1;

      /*printf("\n2.Fall: 0 ist DP, 1 DP am Anfang (%d,%d)\n",aDP,bDP);*/

      nf = nf + CalculateFano(P,E,d,np,2,aDP,bDP,cDP,s,2,1,nc,CC);

				/*noch 1 DP in 0, ..., d-1 ausser 0-DP*/



      if ((maxVnumber-np) > 2){



	/*wegen Satz von Casagrande bzw. klar: keine 2 DPs in 0, ..., d-1*/



      for(j=d;j<np-1;j++){

	if ((Dpt[j]==1) && (ZeroSum(P->x[i],P->x[j],d))){

          cDP=j;

          for(k=0;k<d;k++){

            P->x[np+3][k]=P->x[cDP][k];

	  }

          P->x[np+3][d]=0;/*Das ist Satz von Casagrande*/

          P->x[cDP][d]=1;

/*printf("\n6.Fall: 0 ist DP, 2 DPs, 1 am Anfang (%d,%d,%d)\n",aDP,bDP,cDP);*/

          nf = nf + CalculateFano(P,E,d,np,3,aDP,bDP,cDP,s,6,2,nc,CC);

			/*noch 2 DPs, einer in 0, ..., d-1, ausser 0-DP*/

	}

      }

      }

    }

  }



  /*	Nach Satz von Casagrande und Reid nicht moeglich, dass 2 DPs,

	ungleich 0, gibt, die nicht in 0, ..., d-1 sind			*/



  for(i=d;i<np-1;i++){

    if (Dpt[i]==1){

      bDP=i;

      for(k=0;k<d;k++){

        P->x[np+2][k]=P->x[bDP][k];

      }

      /*printf("\n4.Fall: 0 ist DP, 1 DP nicht am Anfang (%d,%d)\n",aDP,bDP);*/

      nf = nf + CalculateFano(P,E,d,np,2,aDP,bDP,cDP,s,4,0,nc,CC);

			/*noch 1 DP, nicht in 0, ..., d-1, ausser 0-DP*/

    }

  }

  }

  }

  }



  /*printf("\n SCHLUSS (von 1 Zelle): nf=%d\n",nf);*/

  return nf;/* nf = number of output polytopes (just for statistics) */

}



#endif
