#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Config reader to read the configuration file
#
# Software is free software released under the "Modified BSD license"
#
# Copyright (c) 2017 	Pieter-Jan Moreels

# imports
import configparser
import os
import re
import sys

runPath = os.path.dirname(os.path.realpath(__file__))

class Configuration():
    ConfigParser = configparser.ConfigParser()
    ConfigParser.read(os.path.join(runPath, "../etc/configuration.ini"))
    default = {'host':  "127.0.0.1", 'port': 8080,
               'debug': True,
               'ssl':   False,         'sslCertificate': "./ssl/ssl.crt",
                                       'sslKey': "./ssl/ssl.key",
               'logging': True,        'logfile': "./log/webserver.log",
               'maxLogSize': '100MB',  'backlog': 5}

    @classmethod
    def readSetting(cls, section, item, default):
        result = default
        try:
            if type(default) == bool:
                result = cls.ConfigParser.getboolean(section, item)
            elif type(default) == int:
                result = cls.ConfigParser.getint(section, item)
            else:
                result = cls.ConfigParser.get(section, item)
        except:
            pass
        return result

    @classmethod
    def toPath(cls, path):
        return path if os.path.isabs(path) else os.path.join(runPath, "..", path)


    # WebServer
    @classmethod
    def getHost(cls):
        return cls.readSetting("Webserver", "Host", cls.default['host'])

    @classmethod
    def getPort(cls):
        return cls.readSetting("Webserver", "Port", cls.default['port'])

    @classmethod
    def getDebug(cls):
        return cls.readSetting("Webserver", "Debug", cls.default['debug'])

    # SSL
    @classmethod
    def useSSL(cls):
        return cls.readSetting("Webserver", "SSL", cls.default['ssl'])

    @classmethod
    def getSSLCert(cls):
        return cls.toPath(cls.readSetting("Webserver", "Certificate", cls.default['sslCertificate']))

    @classmethod
    def getSSLKey(cls):
        return cls.toPath(cls.readSetting("Webserver", "Key", cls.default['sslKey']))

    # Logging
    @classmethod
    def getLogfile(cls):
        return cls.toPath(cls.readSetting("Logging", "Logfile", cls.default['logfile']))

    @classmethod
    def getLogging(cls):
        return cls.readSetting("Logging", "Logging", cls.default['logging'])

    @classmethod
    def getMaxLogSize(cls):
        size = cls.readSetting("Logging", "MaxSize", cls.default['maxLogSize'])
        split = re.findall('\d+|\D+', size)
        try:
            if len(split) > 2 or len(split) == 0:
                raise Exception
            base = int(split[0])
            if len(split) == 1:
                multiplier = 1
            else:
                multiplier = (split[1]).strip().lower()
                if multiplier == "b":
                    multiplier = 1
                elif multiplier == "kb":
                    multiplier = 1024
                elif multiplier == "mb":
                    multiplier = 1024 * 1024
                elif multiplier == "gb":
                    multiplier = 1024 * 1024 * 1024
                else:
                    # If we cannot interpret the multiplier, we take MB as default
                    multiplier = 1024 * 1024
            return base * multiplier
        except Exception as e:
            print(e)
            return 100 * 1024

    @classmethod
    def getBacklog(cls):
        return cls.readSetting("Logging", "Backlog", cls.default['backlog'])
