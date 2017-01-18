# ~/.bash_profile: executed by bash(1) for login shells.
#
# Model for DreamHost shared host accounts.

# general
umask 002
PS1='$? $SHLVL [\u@\h]$ '
set -o vi
export DOMAIN_NAME=mydomain.com  # fill with your domain name
export DOMAIN_ROOT=~/$DOMAIN_NAME
export DOCUMENT_ROOT=$DOMAIN_ROOT/public

# pyenv
export TMPDIR=~/tmp
export PYENV_ROOT=~/.pyenv
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# django
export DJANGO_STATIC_ROOT=$DOCUMENT_ROOT/static
export DJANGO_DEBUG=false
export DJANGO_ALLOWED_HOSTS=$DOMAIN_NAME
