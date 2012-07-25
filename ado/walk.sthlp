{smcl}
{* *! version 0.1  24jul2012}{...}
{cmd:help walk}
{hline}

{title:Title}

{p2colset 5 13 21 2}{...}
{p2col :{cmd:walk} {hline 2}}Walk a directory tree{p_end}
{p2colreset}{...}


{title:Syntax}

{p 8 15 2}{cmd:walk} {helpb using} {it:directory-name}{cmd:,}
		{opt dest:ination(name)} [{opt pat:tern(glob)}]

{p 4 6 2}
where {it:directory-name} is an existing directory name, possibly relative to
the current working directory. See {manhelp pwd D}. Don't forget to quote paths
with embedded spaces.


{title:Description}

{pstd}
{cmd:walk} returns a list of path names relative to the starting path that lead
to files (not directories), optionally matching a file-name pattern. Result is
left in a local macro {it:name} in the calling environment.


{title:Options}

{phang}
{opt dest:intation(name)} tells {cmd:walk} to create a local macro {it:name} in
the calling environment ({it:i.e.}, as though {cmd:walk} were a
{help extended_fcn:macro extended function} and you had written {cmd:local}
{it:name}{cmd:: walk} {it:...}). 

{pmore}
This argument is required for {cmd:walk} to work. If {cmd:walk} used
{help return:r()}-return values, it would run into length restrictions.

{phang}
{opt pat:tern(glob)} resticts {cmd:walk}'s search to those files whose names
{help f_strmatch:strmatch} {it:glob}. In a glob pattern, {cmd:"?"} means that
one character goes here, and {cmd:"*"} means that zero or more characters go
here.


{title:Examples}

{pstd}Find all CSV files in a project directory{p_end}

{phang2}{cmd:. walk using "../raw", destination(files) pattern("*.csv")}

{pstd}Then loop over those files{p_end}

	{cmd:foreach file of local files {c -(}}
		{txt:{it:...code referencing `files'...}}
	{cmd:{c )-}}

{title:Also see}

{psee}
{space 2}Help:  {manhelp dir D}, {manhelp extended_fcn D} (in particular, see {cmd::dir})
{p_end}
