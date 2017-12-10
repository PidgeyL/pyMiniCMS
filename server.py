#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Main server
#
# Software is free software released under the "Modified BSD license"
#
# Copyright (c) 2017 	Pieter-Jan Moreels

# imports
import importlib
import logging
import os
import random
import sys

from flask              import Flask, request, Response, render_template, abort
from logging.handlers   import RotatingFileHandler
from tornado.httpserver import HTTPServer
from tornado.ioloop     import IOLoop
from tornado.wsgi       import WSGIContainer

from lib.Config import Configuration as conf
from web.Routes import ROUTES, ROOT

class WebServer():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config['SECRET_KEY'] = str(random.getrandbits(256))

    def __init__(self):
        self.pages  = {}
        self.routes = []
        
        # Register routes
        self.app.add_url_rule('/',            view_func=self.index,      methods=['GET'])
        self.app.add_url_rule('/<path:page>', view_func=self.parse_page, methods=['GET'])
        # Register Error Handlers
        self.app.register_error_handler(404, self.page_not_found)

        # Register custom paths
        for route in ROUTES:
            try:
                content = {}
                if route['r'] in self.routes:
                    print("Duplicate route in Routes file: %s"%route['r'])
                    sys.exit(101)
                path = os.path.abspath(conf.toPath(os.path.join('templates', route['p'])))
                if not os.path.exists(path):
                    print("%s (specified in Routes file) does not exist"%path)
                    sys.exit(102)
                if route.get('c'):
                    for ch in route['c']:
                        try:
                            path = os.path.join('lib', 'ContentHandlers', ch['h'])
                            absp = os.path.abspath(path+".py")
                            if not os.path.exists(absp):
                                print("%s (specified in Routes file) does not exist"%absp)
                                sys.exit(103)
                            i  = importlib.import_module(path.replace("/", "."))
                            cg = getattr(i, path.split("/")[-1])(ch.get('s', {}))
                            content.update(cg.getContent())
                        except Exception as e:
                            print("Check syntax %s"% path)
                            print(e)
                            sys.exit(104)
                self.routes.append(route['r'])
                self.pages[route['r']] = {'p': route['p'], 'c': content}
            except Exception as e:
                print(e)
                print("Malformed Routes file")
                sys.exit(100)
            # check if file exists
            # load related stuff

    ##################
    # ROUTE HANDLERS #
    ##################
    def index(self):
        return self.parse_page(ROOT)

    def parse_page(self, page):
        if page not in self.routes:
            abort(404)
        else:
          return render_template(self.pages[page]['p'], **self.pages[page]['c'])
        
    ##################
    # Error Messages #
    ##################
    def page_not_found(self, e):
        return render_template('404.html'), 404


    ########################
    # Web Server Functions #
    ########################
    # signal handlers
    def sig_handler(self, sig, frame):
        print('Caught signal: %s' % sig)
        IOLoop.instance().add_callback(self.shutdown)

    def shutdown(self):
        MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 3
        print('Stopping http server')
        self.http_server.stop()

        print('Will shutdown in %s seconds ...' % MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
        io_loop = IOLoop.instance()
        deadline = time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN

        def stop_loop():
            now = time.time()
            if now < deadline and (io_loop._callbacks or io_loop._timeouts):
                io_loop.add_timeout(now + 1, stop_loop)
            else:
                io_loop.stop()
                print('Shutdown')
        stop_loop()

    def start(self):
        # logging
        if conf.getLogging():
            logfile = conf.getLogfile()
            pathToLog = logfile.rsplit('/', 1)[0]
            if not os.path.exists(pathToLog):
                os.makedirs(pathToLog)
            file_handler = RotatingFileHandler(logfile, maxBytes=conf.getMaxLogSize(), backupCount=conf.getBacklog())
            file_handler.setLevel(logging.ERROR)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)
            self.app.logger.addHandler(file_handler)

        #for route in web.Routes.get_routes(self): self.addRoute(route)

        if conf.getDebug():
            # start debug flask server
            self.app.run(host=conf.getHost(), port=conf.getPort(), debug=True)
        else:
            # start asynchronous server using tornado wrapper for flask
            # ssl connection
            print("Server starting...")
            if conf.useSSL():
                ssl_options = {"certfile": os.path.join(_runPath, "../", conf.getSSLCert()),
                                "keyfile": os.path.join(_runPath, "../", conf.getSSLKey())}
            else:
                ssl_options = None
            signal.signal(signal.SIGTERM, self.sig_handler)
            signal.signal(signal.SIGINT,  self.sig_handler)

            self.http_server = HTTPServer(WSGIContainer(self.app), ssl_options=ssl_options)
            self.http_server.bind(conf.getPort(), address=conf.getHost())
            self.http_server.start(0)  # Forks multiple sub-processes
            IOLoop.instance().start()

if __name__ == '__main__':
    server = WebServer()
    server.start()
