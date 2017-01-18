import sys, os
import django

DOMAIN_ROOT = os.environ.get('DOMAIN_ROOT')
VENV = os.path.join(DOMAIN_ROOT, '.virtualenv')
INTERP = os.path.join(VENV, 'bin', 'python3')

if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.insert(0, os.path.join(VENV, 'lib', 'python3.6', 'site-packages'))

def application(environ, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    message = 'Python {v} running Django {dv}.'.format(v=sys.version, dv=django.__version__)
    return [bytes(message, encoding='utf-8')]
