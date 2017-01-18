def application(environ, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    message = 'Python running for my project'
    return [message]
