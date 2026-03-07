\\lucas2.gp - Fast computation of Lucas sequences.
\\You can get a copy of this file  via anonymous ftp at
\\math.math.ucl.ac.be in the directory /pub/joye/pari.

\\lucas2(k,P,Q) returns the k-th terms of the Lucas sequences
\\{U_k(P,Q)} and {V_k(P,Q)} with parameters P and Q.

\\Usage:
        print("lucas2(k,P,Q)=k-th term of U_k(P,Q) and V_k(P,Q)");

{
        lucas2(k,P,Q,     n,s,j,Ql,Qh,Uh,Vl,Vh) =
        n = floor(log(k)/log(2)) + 1;
        s = 0;
        while( bittest(k,s) == 0, s = s + 1 );
        Uh = 1; Vl = 2; Vh = P;
        Ql = 1; Qh = 1;
        forstep( j = n-1, s+1, -1,
                Ql = Ql * Qh;
                if( bittest(k,j),
                        Qh = Ql * Q;
                        Uh = Uh * Vh;
                        Vl = Vh * Vl - P * Ql;
                        Vh = Vh * Vh - 2 * Qh,

                        Uh = Uh * Vl - Ql;
                        Vh = Vh * Vl - P * Ql;
                        Vl = Vl * Vl - 2 * Ql;
                        Qh = Ql;
                );
        );
        Ql = Ql * Qh; Qh = Ql * Q;
        Uh = Uh * Vl - Ql;
        Vl = Vh * Vl - P * Ql;
        Ql = Ql * Qh;
        for( j = 1, s,
                Uh = Uh * Vl;
                Vl = Vl * Vl - 2 * Ql;
                Ql = Ql * Ql;
        );
        [Uh,Vl]
}