Running Python 3 applications on DreamHost shared hosting
=========================================================

Sources:

- http://wiki.dreamhost.com/Django
- http://wiki.dreamhost.com/Passenger
- https://help.dreamhost.com/hc/en-us/articles/216137637-Pyenv-simple-Python-version-management (for pyenv)
- https://nokyotsu.com/qscripts/2015/05/deploy-a-python-web-application-on-dreamhost-with-pyenv.html (for pyenv - maybe not useful)


What we'll see here
-------------------

1. Create a fully hosted domain to run Python applications.
1. Enable login with ssh keys.
1. Run a Python script through a browser.
1. Install any Python version using pyenv.
1. Create and use a virtualenv.
1. Install Python packages inside the virtualenv.
1. Run and configure a Django application.


Why DreamHost?
--------------

1. It's affordable: unlimited disk space, unlimited bandwidth, unlimited and
   independent domains or subdomains for only US$ 10.95/month.

1. I don't need to manage email and firewall.

1. I can run cronjobs.

1. Each domain or subdomain has its own emails, ftp/ssh user, database, etc.

1. I have freedom to install my own Python version with virtualenv and Python
   packages as well. For instance, Python 3 and Django.



Introduction
------------

DreamHost runs Python through Passenger. You must activate Passenger when
creating your domain in DreamHost control panel.

DreamHost gives you some freedom:

  - Install your own Python version.
  - Configure a virtualenv.
  - Manage your Passenger.
  - Run deploy scripts.
  - Have git bare repositories.
  - Log in with ssh keys, without password.

We will see ways to run Python 3 applications in Passenger with some scenarios:

1. A simple Python 3 script
1. A Django project
1. A Pyramid application


Technical background
--------------------

Your DreamHost account has these important data about it:

  - ssh username
  - configured (sub)domain

Let''s assume these data for our examples below:

  - ssh username: john
  - configured domain: myapp.aprendapython.com.br

This is the directory structure you have when you log through ssh for the first time into `john@myapp.aprendapython.com.br`:

```
    /home/john
    ├── Maildir
    │   └── ...
    ├── logs
    │   └── myapp.aprendapython.com.br
    └── myapp.aprendapython.com.br
        └── public
```

We will create new directories to accomplish this structure:

```
/home/john
├── Maildir
│   └── ...
├── logs
│   └── myapp.aprendapython.com.br
├── myapp.aprendapython.com.br
│   ├── public
│   ├── tmp
│   │   └── restart.txt
│   └── passenger_wsgi.py
├── bin
│   └── python-3.4.3
├── git
│   └── myapp.git
├── src
│   ├── myapp
│   └── myapp.egg-info
└── venv
    ├── bin
    ├── include
    ├── lib
    ├── lib64 -> lib
    └── share

```

Important notes:

  - `~/myapp.aprendapython.com.br/passenger_wsgi.py`: entry point of your application
  - `~/myapp.aprendapython.com.br/tmp/restart.txt`: touch this file to restart your application
  - `~/bin`: user bin dir
  - `~/git`: git bare repos, with hooks
  - `~/src`: source code to run your application
  - `~/venv`: Python virtualenv
  - The current directory for your script is `~/myapp.aprendapython.com.br`


Commands to manage your Passenger server:

  - `$ pgrep -fl python3`: see if your passenger server is running.
  - `$ touch ~/myapp.aprendapython.com.br/tmp/restart.txt`: restart your application.
  - `$ pkill python3`: kill the passenger server if the restart above doesn''t work.



Activate login with ssh keys
----------------------------

Before anything else, setup login through ssh keys:

Copy your local `.ssh/id_rsa.pub` to `.ssh/authorized_keys` of your server. You will be prompted for the password:


    $ ssh <user>@<server>.dreamhost.com "umask 077; mkdir .ssh"
    $ cat $HOME/.ssh/id_rsa.pub | ssh <user>@<server>.dreamhost.com "cat >> .ssh/authorized_keys"

**Note:** You must replace `<user>` and `<server>` with the appropriate username and servername of your account.

Now you can login without password.



Create the git repository
-------------------------

When logged into your server:

    $ cd
    $ mkdir git
    $ git init --bare myapp.git

Now you can run locally, in your local copy of your git repository:

    $ git remote add origin ssh://<user>@<server>.dreamhost.com/~/git/myapp.git

**Note:** you can name your git repository as you want.




Install Python 3 in a virtualenv
--------------------------------

The virtualenv will be in ~/venv dir.


```
#!/bin/bash


_main () {
    mkdir --parent ~/bin
    install_python
    create_virtualenv
    install_some_packages
}


install_python () {
    mkdir --parent ~/tmp
    cd ~/tmp

    wget http://www.python.org/ftp/python/3.4.3/Python-3.4.3.tgz
    tar zxvf Python-3.4.3.tgz
    cd Python-3.4.3

    ./configure --prefix=$HOME/bin/python-3.4.3
    make
    make install

    echo 'export PATH=$HOME/bin/python-3.4.3/bin:$PATH' >> ~/.bash_profile
    echo 'source ~/.bash_profile' >> ~/.bashrc

    cd
    rm -rf ~/tmp
}


create_virtualenv () {
    source ~/.bash_profile
    python3 -m venv $HOME/venv
    source ~/venv/bin/activate
}


install_some_packages () {
    pip3 install ipython
}

_main
```


Running a simple Python 3 script
--------------------------------

```
# Save this script as ~/myapp.aprendapython.com.br/passenger_wsgi.py

import sys, os

HOME = os.environ.get('HOME')
VENV = HOME + '/venv'
INTERP = VENV + '/bin/python3'

if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

cwd = os.getcwd()
sys.path.insert(0, '{v}/lib/python3.4/site-packages'.format(v=VENV))

def application(environ, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    message = 'Passenger funcionando com Python {v} no diretorio {cwd}'.format(v=sys.version, cwd=cwd)
    return [bytes(message, encoding='utf-8')]
```


Running a Django project
------------------------

```
# Save this script as ~/myapp.aprendapython.com.br/passenger_wsgi.py

import sys, os

HOME = os.environ.get('HOME')
SRCDIR = HOME + '/src'
PROJECTNAME = '<my_project_name>'
VENV = HOME + '/venv'
INTERP = VENV + '/bin/python3'

if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.insert(0, '{v}/lib/python3.4/site-packages'.format(v=VENV))
sys.path.insert(0, SRCDIR))

os.environ['DJANGO_SETTINGS_MODULE'] = '{p}.settings'.format(p=PROJECTNAME)
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```


Running a Pyramid project
-------------------------

```
# Save this script as ~/myapp.aprendapython.com.br/passenger_wsgi.py

import sys, os

HOME = os.environ.get('HOME')
SRCDIR = HOME + '/src'
VENV = HOME + '/venv'
INTERP = VENV + '/bin/python3'

if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# cwd = os.getcwd()
sys.path.insert(0, '{v}/lib/python3.4/site-packages'.format(v=VENV))
sys.path.insert(0, SRCDIR))

from paste.deploy import loadapp
application = loadapp('config:{s}/production.ini'.format(s=SRCDIR))
```


Notes about Django
------------------

You must set these environment variables in your `~/.bash_profile`:

    DOMAIN=escola.viniciusban.com
    DJANGO_ALLOWED_HOSTS=$DOMAIN
    DJANGO_STATIC_ROOT=$HOME/$DOMAIN/public/static/
    DJANGO_DEBUG=false

Note: `DJANGO_STATIC_ROOT` must contain the same value of "Web directory" in
your domain's control panel in DreamHost, with "/static/" appended. Example:

Make your `settings.py` script understand these environment variables
accordingly.

Run `manage.py collectstatic`.

.end
