# Add, in order, brew and gem install directories. Pypy install-scripts must be
# after /usr/local/bin
export PATH=/usr/local/bin:/usr/local/sbin:/usr/local/opt/ruby/bin:/usr/local/share/pypy:$PATH
export FINDBUGS_HOME=/usr/local/Cellar/findbugs/2.0.2/libexec
if [ -f $(brew --prefix)/etc/bash_completion ]; then
	. $(brew --prefix)/etc/bash_completion
fi
alias ls="ls -GFh"

# Make PS1 shorter and more useful
PS1="\[\033[01;34m\]\w\[\033[00m\] \[\033[01;32m\]$ \[\033[00m\]"

# Amazon Web Services CLI command completion
complete -C aws_completer aws
