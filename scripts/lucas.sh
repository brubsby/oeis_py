#!/bin/bash
#
# Some summary HTML for the status of factoring in generalized Lucas sequences.
# Assumes appropriate Java classpath.

if [[ ${1} == "--update" ]]; then
    update=1
    shift
fi

Q="-2 -1 1 2"
P="1 2 3 4 5 6 7 8 9 10 11 12"

if [[ -n ${update} ]]; then
    for q in ${Q}; do
        for p in ${P}; do
            u=u${p}.${q}.dat
            if [[ ! -r ${u} ]] || grep -q '(' "${u}" || ! grep -q '^1000 ' "${u}"; then
                echo "$(date +'%Y-%m-%d %H:%M:%S') Revising ${u} using factordb"
                cat "${u}" 2>/dev/null | python generalized_lucas.py "${p}" "${q}" factor-table | sponge "${u}"
                #sleep 300
            fi
            v=v${p}.${q}.dat
            if [[ ! -r ${v} ]] || grep -q '(' "${v}" || ! grep -q '^1000 ' "${v}"; then
                echo "$(date +'%Y-%m-%d %H:%M:%S') Revising ${v} using factordb"
                cat "${v}" 2>/dev/null | python generalized_lucas.py "${p}" "${q}" factor-table-v | sponge "${v}"
                #sleep 300
            fi
        done
    done
fi

{
    cat <<EOF
<html>
<head>
<style type="text/css">
</style>
<title>Factorization of generalized Lucas sequences</title>
</head>
<body>
<h1>Factorization of generalized Lucas sequences</h1>
Current status of Lucas sequence factorizations (n&le;1000). A green cell indicates completion.<p>
The case q=0 is trivial, with U(p,0,n)=p^(n-1) and V(p,0,n)=p^n.<p>
<h2>U(p,q,n) for 1&le;n&le;1000</h2>
<table style="float: left">
<tr><th></th><th bgcolor="#808080" colspan="2">First Holes</th></tr>
<tr><th bgcolor="#808080">p\q</th>
EOF
    for q in ${Q}; do
        echo "<th bgcolor=\"#808080\">${q}</th>"
    done
    echo "</tr>"
    for p in ${P}; do
        echo "<tr><th bgcolor=\"#808080\">${p}</th>"
        for q in ${Q}; do
            u=u${p}.${q}.dat
            if [[ ! -r ${u} ]]; then
                cell=""
                color=8080FF
            elif ! grep -q '(' "${u}"; then
                cell=""
                color=80FF80
            else
                cell="$(grep '(' "${u}" | head -1 | sed 's/ [^(]*(/ /;s/).*//' | awk '{print $1" C"length($2)}')"
                color=FF8080
            fi
            echo "<td bgcolor=\"#${color}\">${cell}</td>"
        done
        echo "</tr>"
    done
    cat <<EOF
</table>
<table style="float: left">
<tr><th></th><th bgcolor="#808080" colspan="2">Smallest Composite</th></tr>
<tr><th bgcolor="#808080">p\q</th>
EOF
    for q in ${Q}; do
        echo "<th bgcolor=\"#808080\">${q}</th>"
    done
    echo "</tr>"
    for p in ${P}; do
        echo "<tr><th bgcolor=\"#808080\">${p}</th>"
        for q in ${Q}; do
            u=u${p}.${q}.dat
            if [[ ! -r ${u} ]]; then
                cell=""
                color=8080FF
            elif ! grep -q '(' "${u}"; then
                cell=""
                color=80FF80
            else
                cell="$(grep '(' "${u}" | sed 's/ [^(]*(/ /;s/).*//' | awk '{print length($2)" "$1}' | sort -n | head -1 | awk '{print $2" C"$1}')"
                color=FF8080
            fi
            echo "<td bgcolor=\"#${color}\">${cell}</td>"
        done
        echo "</tr>"
    done
    cat <<EOF
</table>
<table style="float: left">
<tr><th></th><th bgcolor="#808080" colspan="2">#Composites</th></tr>
<tr><th bgcolor="#808080">p\q</th>
EOF
    for q in ${Q}; do
        echo "<th bgcolor=\"#808080\">${q}</th>"
    done
    echo "</tr>"
    for p in ${P}; do
        echo "<tr><th bgcolor=\"#808080\">${p}</th>"
        for q in ${Q}; do
            u=u${p}.${q}.dat
            if [[ ! -r ${u} ]]; then
                cell=""
                color=8080FF
            elif ! grep -q '(' "${u}"; then
                cell=""
                color=80FF80
            else
                cell="$(grep -c '(' "${u}")"
                color=FF8080
            fi
            echo "<td bgcolor=\"#${color}\">${cell}</td>"
        done
        echo "</tr>"
    done
    cat <<EOF
</table>
<br style="clear:both" />
<pre>
<a href="https://oeis.org/A000045">A000045</a> = U(1,-1,n)  = F(n)     Fibonacci numbers
<a href="https://oeis.org/A001045">A001045</a> = U(1,-2,n)  = J(n)     Jacobsthal numbers
<a href="https://oeis.org/A000129">A000129</a> = U(2,-1,n)  = P(n)     Pell numbers
<a href="https://oeis.org/A001477">A001477</a> = U(2,1,n)   = n        Integers
<a href="https://oeis.org/A001906">A001906</a> = U(3,1,n)   = F(2*n)
<a href="https://oeis.org/A001076">A001076</a> = U(4,-1,n)  = F(3*n)/2
<a href="https://oeis.org/A004187">A004187</a> = U(7,1,n)   = F(4*n)/3
<a href="https://oeis.org/A049666">A049666</a> = U(11,-1,n) = F(5*n)/5
</pre>
</div>
<h2>V(p,q,n) for 1&le;n&le;1000</h2>
<table style="float: left">
<tr><th></th><th bgcolor="#808080" colspan="2">First Holes</th></tr>
<tr><th bgcolor="#808080">p\q</th>
EOF
    for q in ${Q}; do
        echo "<th bgcolor=\"#808080\">${q}</th>"
    done
    echo "</tr>"
    for p in ${P}; do
        echo "<tr><th bgcolor=\"#808080\">${p}</th>"
        for q in ${Q}; do
            v=v${p}.${q}.dat
            if [[ ! -r ${v} ]]; then
                cell=""
                color=8080FF
            elif ! grep -q '(' "${v}"; then
                cell=""
                color=80FF80
            else
                cell="$(grep '(' "${v}" | head -1 | sed 's/ [^(]*(/ /;s/).*//' | awk '{print $1" C"length($2)}')"
                color=FF8080
            fi
            echo "<td bgcolor=\"#${color}\">${cell}</td>"
        done
        echo "</tr>"
    done
    cat <<EOF
</table>
<table style="float: left">
<tr><th></th><th bgcolor="#808080" colspan="2">Smallest Composite</th></tr>
<tr><th bgcolor="#808080">p\q</th>
EOF
    for q in ${Q}; do
        echo "<th bgcolor=\"#808080\">${q}</th>"
    done
    echo "</tr>"
    for p in ${P}; do
        echo "<tr><th bgcolor=\"#808080\">${p}</th>"
        for q in ${Q}; do
            v=v${p}.${q}.dat
            if [[ ! -r ${v} ]]; then
                cell=""
                color=8080FF
            elif ! grep -q '(' "${v}"; then
                cell=""
                color=80FF80
            else
                cell="$(grep '(' "${v}" | sed 's/ [^(]*(/ /;s/).*//' | awk '{print length($2)" "$1}' | sort -n | head -1 | awk '{print $2" C"$1}')"
                color=FF8080
            fi
            echo "<td bgcolor=\"#${color}\">${cell}</td>"
        done
        echo "</tr>"
    done
    cat <<EOF
</table>
<table style="float: left">
<tr><th></th><th bgcolor="#808080" colspan="2">#Composites</th></tr>
<tr><th bgcolor="#808080">p\q</th>
EOF
    for q in ${Q}; do
        echo "<th bgcolor=\"#808080\">${q}</th>"
    done
    echo "</tr>"
    for p in ${P}; do
        echo "<tr><th bgcolor=\"#808080\">${p}</th>"
        for q in ${Q}; do
            v=v${p}.${q}.dat
            if [[ ! -r ${v} ]]; then
                cell=""
                color=8080FF
            elif ! grep -q '(' "${v}"; then
                cell=""
                color=80FF80
            else
                cell="$(grep -c '(' "${v}")"
                color=FF8080
            fi
            echo "<td bgcolor=\"#${color}\">${cell}</td>"
        done
        echo "</tr>"
    done
    cat <<EOF
</table>
<br style="clear:both" />
<pre>
<a href="https://oeis.org/A000032">A000032</a> = V(1,-1,n) = L(n)     Lucas numbers
<a href="https://oeis.org/A014551">A014551</a> = V(1,-2,n) = j(n)     Jacobsthal-Lucas numbers
<a href="https://oeis.org/A002203">A002203</a> = V(2,-1,n) = Q(n)     Pell-Lucas numbers
          V(2,1,n)  = 2
<a href="https://oeis.org/A005248">A005248</a> = V(3,1,n)  = L(2n)
</pre>
</div>
</body>
</html>
EOF
} > summary.html
