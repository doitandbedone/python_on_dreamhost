Running Python 3 applications on DreamHost shared hosting
=========================================================

Sources:

- http://wiki.dreamhost.com/Django
- http://wiki.dreamhost.com/Passenger
- https://help.dreamhost.com/hc/en-us/articles/216137637-Pyenv-simple-Python-version-management (for pyenv)
- https://nokyotsu.com/qscripts/2015/05/deploy-a-python-web-application-on-dreamhost-with-pyenv.html (for pyenv - maybe not useful)


What we'll see here
-------------------

1. Create a fully hosted domain to run Python applications
1. Enable login with ssh keys
1. Prepare environment for improvements
1. Understand how Python is executed in DreamHost
1. Commands to manage Passenger server
1. Run a "naked" Python script through your browser
1. Install any Python version using pyenv
1. Create and use a virtualenv
1. Install Python packages inside the virtualenv
1. Run a Django project
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

1. Its name
1. The username
1. Web directory
1. You must activate Passenger to run Python scripts

After creating your new fully hosted domain, you must enable ssh for this new
created user in Users > Manage Users menu option to have shell access to your
server.

For the sake of this tutorial we'll consider creating "mygreatportal.com" with
username "john".


Enable login with ssh keys
--------------------------

Before anything else, setup login through ssh keys.

Copy your local `.ssh/id_rsa.pub` to `.ssh/authorized_keys` of your server. You
will be prompted for the password:

    $ ssh john@mygreatportal.com "umask 077; mkdir .ssh"
    $ cat ~/.ssh/id_rsa.pub | ssh john@mygreatportal.com "cat >> .ssh/authorized_keys"

**Note:** You must replace `john` and `mygreatportal.com` with the appropriate username and domain of your account.

Now you can login without password.


Prepare environment for improvements
------------------------------------

There are important information we should keep track from the beginning using
environment variables:

    $ echo ' ' >> ~/.bash_profile
    $ echo '# general' >> ~/.bash_profile
    $ echo 'DOMAIN_NAME=mygreatportal.com' >> ~/.bash_profile
    $ echo 'DOMAIN_ROOT=~/$DOMAIN_NAME' >> ~/.bash_profile
    $ echo 'DOCUMENT_ROOT=$DOMAIN_ROOT/public' >> ~/.bash_profile
    $ exec $SHELL

We'll use these variables extensively throughout the process of setting up the
environment.

The `~/.bash_profile` script is executed whenever you login to your account and
every time you start the application server as well.

`$DOMAIN_NAME` will be used where you need to know it, without hardcoding. If
you use Django you'll need it in `ALLOWED_HOSTS` setting. Replace
"mygreatportal.com" with your domain name.

`$DOMAIN_ROOT` is where everything about our projet will lives, e.g, source
code, sqlite database, config files, etc.

`$DOCUMENT_ROOT` is served directly by Passenger. It is used to keep static
files, e.g, images, css files, js scripts and so on. **Source code and
configuration files must not be here!**


Understand how Python is executed in DreamHost
----------------------------------------------

DreamHost uses an application server called Passenger to run Ruby, node.js and
Python scripts.

The overall chain is:

1. Apache receives an incoming request to a domain that has Passenger active.
1. If the URI exists as a file in `$DOMAIN_ROOT/public/` directory as a file,
   this file is served.
1. If the file doesn't exist, Apache forwards the request to Passenger.
1. Passenger executes the file `$DOMAIN_ROOT/passenger_wsgi.py`.

So, you always need a file called `passenger_wsgi.py` inside your `$DOMAIN_ROOT`
directory. This is the entry point to your project. Or, in other words,
`passenger_wsgi.py` will call your project.

**Don't forget:** The current directory for your script will always
be `$DOMAIN_ROOT`.


Commands to manage Passenger server
-----------------------------------

As any application server, Passenger runs in a separate process and can be
started, killed and restarted.

To check if your Passenger server is running:

    $ pgrep -fl python3

To kill the Passenger server:
    $ pkill python3

Passenger is restarted the next time the site is accessed and it isn't running
yet.

To restart Passenger any time you make a new deploy or change some configuration
file read at the startup process:

    $ touch $DOMAIN_ROOT/tmp/restart.txt


Run a "naked" Python script through your browser
------------------------------------------------

Our first script will just certify our Passenger is working properly.

As you already know, it must be `passenger_wsgi.py` inside `$DOMAIN_ROOT`:

    # passenger_wsgi.py
    def application(environ, start_response):
        start_response('200 OK', [('Content-type', 'text/plain')])
        return ['Python running for my project']

I call this script "naked" because it simply runs the default Python version
available in DreamHost. At the time of this writing it was 2.7.3:

    $ python -V
    Python 2.7.3

Now, go to your web browser and head to http://mygreatportal.com

Remember to use your own domain name, instead of mygreatportal.com

You should see the message below:

> Python running for my project

We haven't done great things by now, but we are sure the domain is correctly
configured and Python is running.


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
    $ echo 'export TMPDIR=~/tmp' >> ~/.bash_profile
    $ echo 'export PYENV_ROOT=~/.pyenv' >> ~/.bash_profile
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

Our `passenger_wsgi.py` must be a little different. It won't use Django but it will
start a stub script to launch a Django project. See it:

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
    
    # Launch django project
    os.environ['DJANGO_SETTINGS_MODULE'] = PROJECTNAME + ".settings"
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()


This script makes some assumptions:

1. There must exist a `~/src/myproject` directory with the project's source code
   there.
1. There must exist a `~/src/myproject/myproject/settings.py` file.

Put your project in this directory, restart Passenger and refresh your web
browser.


Run a Pyramid application
-------------------------

The version of `passenger_wsgi.py` to run a Pyramid application is only slightly
different from our previous version for Django:

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
    
    # Launch pyramid application
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

I recommend you to adapt your `settings.py` script to read some runtime
configuration from envvars. Specially these ones:

- DEBUG
- ALLOWED_HOSTS
- STATIC_ROOT

These settings can vary from server to server. In production they have different
values from the development environment.

I like to create the `~/.domainname` file with the domain name. So, my
`~/.bash_profile` becomes generic enough:

    $ echo 'mygreatportal.com' > ~/.domainname

You must set these environment variables in your `~/.bash_profile`:

    # django
    DJANGO_DEBUG=false
    DJANGO_ALLOWED_HOSTS=$DOMAIN
    DJANGO_STATIC_ROOT=$DOCUMENT_ROOT/static/

Static files must be filled on each deploy with:

    (venv) $ python manage.py collectstatic

Run this from your project root directory, i.e, the same directory where
`manage.py` file is located.

.end
