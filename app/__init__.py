# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Import core packages
import os
import pymysql
import pymysql.cursors

# Import Flask 
from flask import Flask

# Inject Flask magic
app = Flask(__name__)

app.secret_key = '000000'

dbConn = pymysql.connect(
    host='116.62.160.40',
    user='misy410group13',
    password='@GtMEKzZrhhTAOsF7',
    database='misy410group13',
    port=3306,
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

cursor = dbConn.cursor()


# Import routing to render the pages
from app import views
