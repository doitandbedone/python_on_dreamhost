Running Python 3 applications on DreamHost shared hosting
=========================================================


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
1. Run a Django project
1. Run a Pyramid application
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
environment variables.

See `bash_profile` file in this repository.

To update your environment after you modify your `~/.bash_profile`, run:

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

As you already know, it must be `passenger_wsgi.py` inside `$DOMAIN_ROOT`.

See `passenger_wsgi_naked.py` in this repository.

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

    $ cd $DOMAIN_ROOT
    $ mkdir .virtualenv
    $ python -m venv $DOMAIN_ROOT/.virtualenv
    $ source $DOMAIN_ROOT/.virtualenv/bin/activate
    (.virtualenv) $ which python
    /home/john/mygreatportal.com/.virtualenv/bin/python
    (.virtualenv) $ python -V
    Python 3.6.0

Let's install a package inside our virtualenv:

    (.virtualenv) $ pip install django
    Collecting django
    ...
    Successfully installed django-1.10.5

Now we need to modify `passenger_wsgi.py` to make it identify the virtualenv.

See `passenger_wsgi_virtualenv.py` in this repository.

Restart Passenger server and refresh your browser window.

This example just checked if the virtualenv is being identified by Passenger.
Note we didn't run a Django project yet. We just imported django and showed its
version.


Run a Django project
--------------------

`passenger_wsgi.py` will not return a message anymore. It will launch our Django
project.

We have to head Python to our project source code and make `passenger_wsgi.py`
return our application object to be run by Passenger. This is our real Django
project.

See `passenger_wsgi_django.py` in this repository.

The script above makes some assumptions:

1. There must exist a directory named `myproject` inside `$DOMAIN_ROOT` with the
   project's source code.
1. There must exist a `$DOMAIN_ROOT/myproject/myproject/settings.py` file.

If you have any dependencies on Python packages, it's time to install them now,
usually using pip. Remember to activate you virtualenv before.

    $ source $DOMAIN_ROOT/.virtualenv/bin/activate
    (.virtualenv) $ pip install -r requirements.txt

Restart Passenger and refresh your web browser to see your project running.


Run a Pyramid application
-------------------------

The version of `passenger_wsgi.py` to run a Pyramid application is only slightly
different from our previous version for Django.

See `passenger_wsgi_pyramid.py` in this repository.


Notes about Django
------------------

I recommend you to adapt your `settings.py` script to read some runtime
configuration from envvars. Specially these ones:

- DEBUG
- ALLOWED_HOSTS
- STATIC_ROOT

These settings can vary from server to server. In production they have different
values from the development environment and you must set them in
`~/.bash_profile`:

    # django
    DJANGO_DEBUG=false
    DJANGO_ALLOWED_HOSTS=$DOMAIN
    DJANGO_STATIC_ROOT=$DOCUMENT_ROOT/static/

Static files must be filled on each deploy with:

    $ source $DOMAIN_ROOT/.virtualenv/bin/activate
    (.virtualenv) $ cd $DOMAIN_ROOT/myproject
    (.virtualenv) $ python manage.py collectstatic

Run `collectstatic` from the same directory where `manage.py` file lives.


--------------------------------------------------

Sources:

- http://wiki.dreamhost.com/Django
- http://wiki.dreamhost.com/Passenger
- https://help.dreamhost.com/hc/en-us/articles/216137637-Pyenv-simple-Python-version-management
- http://blog.mattwoodward.com/2016/06/installing-python-3-and-django-on.html

.end
