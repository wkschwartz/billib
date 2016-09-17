# Add, in order, brew and gem install directories. Pypy install-scripts must be
# after /usr/local/bin
export PATH=/usr/local/bin:/usr/local/sbin:/usr/local/opt/ruby/bin:/usr/local/share/pypy:/usr/local/opt/go/libexec/bin:/usr/local/share/pypy:$PATH
export FINDBUGS_HOME=/usr/local/Cellar/findbugs/3.0.1/libexec
export GOPATH=~/Documents/go
if [ -f $(brew --prefix)/etc/bash_completion ]; then
	. $(brew --prefix)/etc/bash_completion
fi
alias ls="ls -GFh"

# Sublime Text alias
alias subl="/Applications/Sublime\ Text.app/Contents/SharedSupport/bin/subl"

# Without this, every time you switch branches with different sets of files on a
# Python project and rerun your tests, you'd need to run
# find -type f -name "*.py[co]" -delete; find -type d -name "__pycache__" -delete
export PYTHONDONTWRITEBYTECODE=1

# Make PS1 shorter and more useful
PS1="\[\033[01;34m\]\w\[\033[00m\] \[\033[01;32m\]$ \[\033[00m\]"

# Amazon Web Services CLI command completion
complete -C aws_completer aws

# If Postgres is installed and we're on Mac OS, then Postgres was probably
# installed with Homebrew, so I problaby want PGDATA to be what's below.
PGDATA="/usr/local/var/postgres"
if [[ "$(uname)" == 'Darwin' ]] && [[ -e $PGDATA ]]; then
	export PGDATA
fi
