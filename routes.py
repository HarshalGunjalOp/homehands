from flask import Flask, render_template, redirect, url_for, request, flash 
from models import db, Customer, Service, Proffessional, Request 

from app import app
from werkzeug.security import generate_password_hash, check_password_hash 

@app.route('/login')
def login():
    return render_template("login.html", page_data={"title":"Login Page"}) 
