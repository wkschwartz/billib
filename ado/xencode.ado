*! simplified interface to encode -- version 0.1 2012-09-05

capture program drop xencode
program define xencode, nclass
	version 11.2
	syntax varname [if] [in], [REPLAcement(string) Label(name) noExtend]
	if (`"`replacement'"' == "") {
		tempvar replacement
		local samename = 1
	}
	else local samename = 0
	if ("`label'" != "") local label label(`label')
	encode `varlist' `if' `in', generate(`replacement') `label' `extend'
	// Following code copied from clonevar.ado version 1.0.1 13oct2004
	local w : variable label `varlist'
	if (`"`w'"' != "") label variable `replacement' `"`w'"'
	tokenize `"`: char `varlist'[]'"' 
	while (`"`1'"' != "") {
			char `replacement'[`1'] `"`: char `varlist'[`1']'"' 
			mac shift 
	}
	
	nobreak {
		drop `varlist'
		if (`samename') {
			rename `replacement' `varlist'
			local replacement `varlist'
		}
	}
end
