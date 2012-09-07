*! Like encode but for dates -- version 0.1 2012-09-05

capture program drop date_encode
program define date_encode, rclass
	version 11.2
	syntax varname[, REPLAcement(string) TOPyear(integer 0) FORMat(string)]
	if (`topyear' == 0) {
		local topyear = real(substr(c(current_date), -4, .)) + 1
	}
	if (`"`format'"' == "") {
		local format = "MDY"
	}
	tempvar new
	generate long `new' = date(`varlist', `"`format'"', `topyear')
	format `new' %td
	label variable `new' `"`:variable label `varlist''"'
	return local label: variable label `varlist'
	if (`"`replacement'"' != "") {
		confirm new variable `replacement'
		local usereplace = 1
	}
	else local usereplace = 0
	nobreak {
		drop `varlist'
		if (`usereplace') rename `new' `replacement'
		else			  rename `new' `varlist'
	}
end
