from flask import Flask, render_template, redirect, url_for, request, flash 
from models import db, Customer, Service, Proffessional, Request 

from app import app
from werkzeug.security import generate_password_hash, check_password_hash 

@app.route('/')
def home():
    return render_template("index.html") 
