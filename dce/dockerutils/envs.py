import os

DEV_DOCKER_HOST = os.getenv('DEV_DOCKER_HOST') or 'http://192.168.100.30:1234'
DEV_DOCKER_USER = os.getenv('DEV_DOCKER_USER') or 'admin'
DEV_DOCKER_PASS = os.getenv('DEV_DOCKER_PASS') or 'admin'
