*! sort string variables in linear time -- version 1.0 2013-04-17
version 11.2

capture program drop strsort
program define strsort, nclass
	syntax varname(string)
	local len = int(real(substr("`:type `varlist''", 4, .)))
	mata:
		x = J(`c(N)', 0, "")
		st_sview(x, ., "`varlist'")
		lsdr_sort(x, `len')
end

/*
 * Translated by William Schwartz from Java by Robert Sedgwick and Kevin Wayne.
 * See their code at http://algs4.cs.princeton.edu/51radix/LSD.java.html and
 * their GPLv3 license at http://algs4.cs.princeton.edu/code/
 */
local R = 256 // Stata characters are extended ASCII bytes
mata:
mata set matastrict on
void function lsdr_sort(string colvector a, real scalar len) {
	real scalar N, d, i, r, j
	string colvector aux
	real colvector count
	N = rows(a)
	aux = J(rows(a), 1, "")
	for (d = len; d > 0; d--) {
		// sort by key-indexed counting on dth character
		count = J(`R' + 1, 1, 0)
		// Compute frequencies
		for (i = 1; i <= N; i++) {
			j = ascii(substr(a[i], d, 1)) + 1
			count[j] = count[j] + 1
		}
		// Compute cumulates
		for (r = 1; r <= `R'; r++)
			count[r + 1] = count[r + 1] + count[r]
		// Order the data
		for (i = 1; i <= N; i++) {
			j = ascii(substr(a[i], d, 1))
			r = count[j]
			aux[r] = a[i]
			count[j] = r + 1
		}
		// Copy back
		for (i = 1; i <= N; i++)
			a[i] = aux[i];
	}
}
end
