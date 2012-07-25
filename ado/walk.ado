*! walk a directory tree -- version 0.1 24jul012
version 11.2

capture program drop walk
program define walk, nclass
	syntax [using/], DESTination(name local) [PATtern(string)]
	mata: ado_walk("files", `"`using'"', `"`pattern'"')
	c_local `destination': copy local files
end

mata:
	mata set matastrict on

	void function ado_walk(string scalar dest, string scalar top, string scalar pattern) {
		string colvector files
		string scalar result, openq, closeq
		real scalar i

		openq = "\`" + `"""'
		closeq = `"""' + "'"

		files = walk(top, pattern)
		result = ""
		for (i = 1; i <= rows(files); i++) {
			result = result + openq + files[i] + closeq + " "
		}
		st_local(dest, result)
	}

	string colvector function walk(|string scalar top, string scalar pattern) {
		if (!direxists(top)) exit(error(3602))
		if (pattern == "") pattern = "*"
		string colvector files, dirs
		real scalar i
		files = dir(top, "files", pattern, 1)
		dirs = dir(top, "dirs", "*", 1)
		for (i = 1; i <= rows(dirs); i++) {
			files = files \ walk(dirs[i], pattern)
		}
		return(files)
	}
	
	/************** Testing code ******************/
	
	void test_walk() {
		string scalar oldwd, testroot
		string colvector str
		oldwd = pwd()
		testroot = tmpdirnme()
		mkdir(testroot)
		chdir(testroot)
		//make test structure
		chdir(oldwd)
	}
	
	string scalar tmpdirname(|string scalar where) {
		string scalar name
		if (where == "") where = "."
		do {
			name = pathjoin(where, "TEMP" + substr(strofreal(runiform(1,1), "%21x"), 4, 8))
		} while(direxists(name))
	}
end
