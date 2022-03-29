import datetime
import json
import numpy as np
import random
from flask import Flask, render_template, request, url_for, flash, redirect, session
from flask_session import Session
import copy
# import config


app = Flask(__name__)
app.config['SECRET_KEY'] = '48c2a54bf8112bb79acbfbd4dd69c1c166c78065b26bfc44'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
messages = []
# n_users = 0
# user_input = list()
# total_cpu = 0
# total_ram = 0



@app.route('/',  methods=('GET', 'POST'))
def hello():
    if request.method == 'POST':
        # global n_users
        print(request.form)
        # 
        n_users = request.form['n_users']
        total_cpu = request.form['total_cpu']
        session["total_cpu"] = total_cpu
        # distribution = request.form['distribution']
        # global total_cpu
        # global total_ram
        
        session["total_ram"] = request.form['total_ram']
        session["n_users"] = n_users

        if not session.get("n_users"):
            flash('No of users is required!')
        # elif not distribution:
        #     flash('Distribution is required!')
        elif not session.get("total_ram"):
            flash('Total RAM is required!')
        elif not session.get("total_cpu"):
            flash('Total CPU is required!')
        else:
            # messages.append({'n_users': n_users, 'distribution': distribution})
            return redirect(url_for('user_scheudule', n_users=n_users))
    return render_template('index.html')

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/drf/')
def drf():
    schedule =  calculate_schedule()
    return render_template('drf.html', schedule=schedule)

@app.route('/user_scheudule/<n_users>', methods=('GET', 'POST'))
def user_scheudule(n_users):
    n_users = int(session.get("n_users"))
    print("No of users " , n_users)
    form_elements = list()
    # global user_input
    # config.user_input = list()
    session["user_input"] = list()
    start_id = 65
    
    for i in range(n_users):
        element = dict()
        element['id'] = chr(start_id + i)
        element['cpu'] = 'cpu' + str(i)
        element['ram'] = 'ram' + str(i)
        form_elements.append(element)
    # print(form_elements)
    
    if request.method == 'POST':
        # distribution = request.form['distribution']
        # user_cpu = request.form['cpu0']
        flag = True
        for idx, element in enumerate(form_elements):
            user = dict()
            user['id'] = chr(start_id + idx)
            user['cpu'] = int(request.form[element['cpu']])
            user['ram'] = int(request.form[element['ram']])
            session.get("user_input").append(user)
            if not request.form[element['cpu']] or not request.form[element['ram']]:
                flag = False
            
        if not flag:
            flash('Please fill the fields!')
        else:
            # messages.append({'n_users': n_users, 'distribution': distribution})
            # print("data recived from form : ",config.user_input)
            return redirect(url_for('drf'))
    return render_template('user_schedule.html', form_elements=form_elements)


def calculate_schedule():
   
    schedule = []
    ## convert cpu and ram to float to avoid int operations
    # global total_cpu
    # global total_ram
    # global n_users
    # global user_input
    total_cpu = session.get("total_cpu")
    total_ram = session.get("total_ram")
    n_users = session.get("n_users")
    print("no of users : ", n_users, "total cpu : ", total_cpu, "total ram : ", total_ram)
    total_cpu = float(total_cpu)
    total_ram = float(total_ram)
    n_users = int(n_users)
    cpu_remaining = total_cpu
    ram_remaining = total_ram
    result = list()
    dominant_shares = [0] * n_users

    ## calculate minimum dominant share index
    def argmin(iterable):
        return min(enumerate(iterable), key=lambda x: x[1])[0]

    ## randomly pick a user

    row = dict()
    user_index = random.randint(0, n_users -1 )
    print("inital random user index", user_index, "data : ", session.get("user_input") )
    row['schedule'] = session.get("user_input")[user_index]['id']
    users = copy.deepcopy(session.get("user_input"))
    ## initialize the users list to update dom. share and res.shares
    for idx, user in enumerate(users):
        user['res. share'] = [0,0]
        user['dom. share'] = 0
        del user['cpu']
        del user['ram']
    
    for idx, user in enumerate(users):
        if idx ==  user_index:
            user['res. share'][0] += session.get("user_input")[user_index]['cpu'] / total_cpu
            user['res. share'][1] += session.get("user_input")[user_index]['ram'] / total_ram
            cpu_remaining -= session.get("user_input")[user_index]['cpu']
            ram_remaining -= session.get("user_input")[user_index]['ram']
            user['dom. share'] = max(user['res. share'][0] , user['res. share'][0])
            dominant_shares[user_index] = user['dom. share']
    row['users'] = users
    row['cpu_toal_alloc'] = (total_cpu - cpu_remaining) / total_cpu
    row['ram_toal_alloc'] = (total_ram - ram_remaining) / total_ram
    result.append(row)
    ## cacluate the entire schedule
    while cpu_remaining > 0 and ram_remaining > 0:
        user_index = argmin(dominant_shares)
        # print("dominant_shares", user_index)
        
        row = copy.deepcopy(result[len(result)-1])
        row['schedule'] = session.get("user_input")[user_index]['id']
        for idx, user in enumerate(row['users']):
            # print(idx, "--", user)
            if idx ==  user_index:
                user['res. share'][0] += session.get("user_input")[user_index]['cpu'] / total_cpu
                user['res. share'][1] += session.get("user_input")[user_index]['ram'] / total_ram
                cpu_remaining -= session.get("user_input")[user_index]['cpu']
                ram_remaining -= session.get("user_input")[user_index]['ram']
                user['dom. share'] = max(user['res. share'][0] , user['res. share'][1])
                dominant_shares[user_index] = user['dom. share']
        # row['users'] = users
        row['cpu_toal_alloc'] = (total_cpu - cpu_remaining) / total_cpu
        row['ram_toal_alloc'] = (total_ram - ram_remaining) / total_ram
        result.append(row)

    # print(result)
    return result 
                                                                                                                                               
                                                                                                                                        
    
    
