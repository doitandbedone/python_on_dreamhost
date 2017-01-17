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
1. Run a "naked" Python script through your browser.
1. Install any Python version using pyenv.
1. Create and use a virtualenv.
1. Install Python packages inside the virtualenv.
1. Run a Django project.
1. Commands to manage Passenger server
1. Run a Pyramid application
1. Important directories and files
1. Notes about Django


Why DreamHost?
--------------

If there are nice alternatives these days like Digital Ocean, Heroku or even
AWS, why use the old fashioned DreamHost shared plan?

Well, it's affordable: I have unlimited disk space, unlimited bandwidth,
unlimited and independent domains or subdomains for only US$ 10.95/month.

It's simple: I don't need to manage email, firewall, O.S updates, etc.

I can run cronjobs.

Each domain or subdomain has its own emails, ftp/ssh user, database, etc.

I have freedom to install my own Python version with virtualenv and Python
packages as well. For instance, Python 3 and Django (or Pyramid, or Flask).

In practice, I pay once and I can host how many projects I need. Besides that I
don't manage the machine. So, it's cheap and simple to me since I'm not a server
admin guy.


Creating your domain in DreamHost web panel
-------------------------------------------

The first thing you want to do is add your domain in Domains > Manage Domains
menu option.

There are 4 important fields to note when creating a new fully hosted domain or
subdomain:

1. Its name.
1. The username.
1. Web directory.
1. You must activate Passenger to run Python scripts.

After creating your new fully hosted domain, you must enable ssh for this new
created user in Users > Manage Users menu option to have shell access to your
server.

For the sake of this tutorial we'll consider creating "mygreatportal.com" with
username "john".


Enable login with ssh keys
--------------------------

Before anything else, setup login through ssh keys:

Copy your local `.ssh/id_rsa.pub` to `.ssh/authorized_keys` of your server. You
will be prompted for the password:

    $ ssh john@mygreatportal.com "umask 077; mkdir .ssh"
    $ cat ~/.ssh/id_rsa.pub | ssh john@mygreatportal.com "cat >> .ssh/authorized_keys"

**Note:** You must replace `john` and `mygreatportal` with the appropriate username and domain of your account.

Now you can login without password.


Run a "naked" Python script through your browser
------------------------------------------------

When you added your domain, there was a field called "Web directory". It is the
path to the Apache document root: `/home/john/mygreatportal.com/public/`.

Passenger runs a Python script located in the directory above the document root.
And this script **must** be named `passenger_wsgi.py`.

So, let's save our first script in it:

    # /home/john/mygreatportal.com/passenger_wsgi.py
    def application(environ, start_response):
        start_response('200 OK', [('Content-type', 'text/plain')])
        return ['Python running for mygreatproject.com']

I call this script "naked" because it simply runs the default Python version
available in DreamHost. At the time of this writing it was 2.7.3:

    $ python -V
    Python 2.7.3

You must restart the Passenger server, touching a specific file. First,
we'll create the directory to host it:

    $ mkdir ~/mygreatportal.com/tmp

Now, start the Passenger server:

    $ touch ~/mygreatportal.com/tmp/restart.txt

Each time you change the source code you'll want to restart the Passenger
server simply touching `~/mygreatportal.com/tmp/restart.txt`. It's a production
environment. The server doesn't look for updates in source code automatically.

Now, go to your web browser and head to http://mygreatportal.com

You should see a message

> Python running for mygreatproject.com

We haven't done great things by now, but we are sure the domain is correctly
configured and Python is running for us.

**One important thing to note:** The current directory for your script always will
be `~/mygreatproject.com/`.


Install any Python version using pyenv
--------------------------------------

We won't rely on the Python version delivered by DreamHost. Let's use [pyenv](https://github.com/yyuu/pyenv) to
run a modern Python.

Basically we must follow instructions in [Pyenv installation
instructions](https://github.com/yyuu/pyenv#installation) and in [Pyenv: simple
Python version
management](https://help.dreamhost.com/hc/en-us/articles/216137637-Pyenv-simple-Python-version-management):

    $ cd ~
    $ mkdir ~/tmp
    $ git clone https://github.com/yyuu/pyenv.git ~/.pyenv
    $ echo 'export TMPDIR="$HOME/tmp"' >> ~/.bash_profile
    $ echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
    $ echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
    $ echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
    $ pyenv install 3.6.0
    $ pyenv versions
    * system (set by /home/john/.pyenv/version)
      3.6.0

We need to activate our Python version:

    $ pyenv global 3.6.0
    $ pyenv versions
      system
    * 3.6.0 (set by /home/john/.pyenv/version)
    $ python -V
    Python 3.6.0


Create and use a virtualenv
---------------------------

As we all know, it's recommended to use Python with virtualenv. That's what
we'll do now:

    $ cd ~
    $ mkdir venv
    $ python -m venv ~/venv
    $ source ~/venv/bin/activate
    (venv) $ which python
    /home/john/venv/bin/python
    (venv) $ python -V
    Python 3.6.0

As you can see we're using Python 3.6.0 from our virtualenv but we still need to
change `passenger_wsgi.py` to work with our virtualenv:

    import sys, os
    
    HOME = os.environ.get('HOME')
    VENV = HOME + '/venv'
    INTERP = VENV + '/bin/python3'
    
    if sys.executable != INTERP:
        os.execl(INTERP, INTERP, *sys.argv)
    
    sys.path.insert(0, '{v}/lib/python3.6/site-packages'.format(v=VENV))
    
    def application(environ, start_response):
        start_response('200 OK', [('Content-type', 'text/plain')])
        message = 'Python {v} running'.format(v=sys.version)
        return [bytes(message, encoding='utf-8')]

Restart Passenger server, go to your web browser and see the result in
http://mygreatportal.com


Install Python packages inside the virtualenv
---------------------------------------------

We'are able to install packages to our virtualenv. Let's install Django:

    $ cd ~
    $ source ~/venv/bin/activate
    (venv) $ pip install django
    Collecting django
    ...
    Successfully installed django-1.10.5

Let's modify `passenger_wsgi.py` again to use Django:

    import sys, os
    import django
    
    HOME = os.environ.get('HOME')
    VENV = HOME + '/venv'
    INTERP = VENV + '/bin/python3'
    
    if sys.executable != INTERP:
        os.execl(INTERP, INTERP, *sys.argv)
    
    sys.path.insert(0, '{v}/lib/python3.6/site-packages'.format(v=VENV))
    
    def application(environ, start_response):
        start_response('200 OK', [('Content-type', 'text/plain')])
        message = 'Python {v} running Django {dv}'.format(v=sys.version, dv=django.__version__)
        return [bytes(message, encoding='utf-8')]

Restart Passenger server and refresh your browser window.


Run a Django project
--------------------

Our `passenger_wsgi.py` must be a little different. It won't use Django. It will
simply start a project that uses Django. See it:

    import sys, os
    
    HOME = os.environ.get('HOME')
    PROJECTNAME = 'myproject'
    SRCDIR = os.path.join(HOME, 'src', PROJECT_NAME)
    VENV = os.path.join(HOME, 'venv')
    INTERP = os.path.join(VENV, 'bin', 'python3')
    
    if sys.executable != INTERP:
        os.execl(INTERP, INTERP, *sys.argv)
    
    sys.path.insert(0, os.path.join(VENV, "lib", "python3.6", "site-packages"))
    sys.path.insert(0, SRCDIR)
    
    os.environ['DJANGO_SETTINGS_MODULE'] = PROJECTNAME + ".settings"
    
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()


This script makes some assumptions:

1. There must exist a `~/src/myproject` directory with the project's source code
   there.
1. There must exist a `~/src/myproject/myproject/settings.py` file.

Put your project in this directory, restart Passenger and refresh your web
browser.


Commands to manage Passenger server
-----------------------------------


See if your passenger server is running:

    $ pgrep -fl python3

Restart your application:

    $ touch ~/mygreatportal.com/tmp/restart.txt

Kill the passenger server if the restart above doesn't work. It'll be restarted
next time the site is accessed:

    $ pkill python3


Run a Pyramid application
-------------------------

`passenger_wsgi.py` to run a Pyramid application:

    import sys, os
    
    HOME = os.environ.get('HOME')
    PROJECTNAME = 'myproject'
    SRCDIR = os.path.join(HOME, 'src', PROJECT_NAME)
    VENV = os.path.join(HOME, 'venv')
    INTERP = os.path.join(VENV, 'bin', 'python3')
    
    if sys.executable != INTERP:
        os.execl(INTERP, INTERP, *sys.argv)
    
    sys.path.insert(0, os.path.join(VENV, "lib", "python3.6", "site-packages"))
    sys.path.insert(0, SRCDIR)
    
    from paste.deploy import loadapp
    application = loadapp('config:{s}/production.ini'.format(s=SRCDIR))


Important directories and files
-------------------------------

- `~/mygreatportal.com`: It's where Passenger looks for the Python stub
`passenger_wsgi.py` script to run your application.

- `~/mygreatportal.com/tmp/restart.txt`: Touch this file to restart your application.

- `~/mygreatportal.com/public`: Apache document root. Files here are accessible from
  the outside world.

- `~/tmp`: Temporary directory used by pyenv to build Python versions.

- `~/.pyenv`: Pyenv root directory.

- `~/venv`: Virtualenv root.

- `~/src`: Your source code.


Notes about Django
------------------

I recommend you adapt your `settings.py` file to read some runtime configuration
from envvars. Specially these ones:

- DEBUG
- ALLOWED_HOSTS
- STATIC_ROOT

These settings can vary from server to server. In production they have different
values from the development environment.

You must set these environment variables in your `~/.bash_profile`:

    DOMAIN=$(cat ~/.domainname)
    DJANGO_ALLOWED_HOSTS=$DOMAIN
    DJANGO_STATIC_ROOT=$HOME/$DOMAIN/public/static/
    DJANGO_DEBUG=false

Note: `DJANGO_STATIC_ROOT` must have the path to document root with "/static/" appended.

Run `manage.py collectstatic` on every deploy.

.end
