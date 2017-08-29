import os

DCE_USERNAME = 'admin'
DCE_PASSWORD = 'admin'

DCE_HOST_2_6 = os.getenv('DCE_HOST_2_6') or '192.168.100.30'
DCE_HOST_2_8 = os.getenv('DCE_HOST_2_8') or '192.168.1.85'

DCE_HOST = os.getenv('DCE_HOST') or DCE_HOST_2_6
