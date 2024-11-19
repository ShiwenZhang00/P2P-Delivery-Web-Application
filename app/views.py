# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Flask modules
from flask   import render_template, request, redirect, url_for, flash, session, json
from jinja2  import TemplateNotFound
from datetime import datetime, timedelta


# App modules
from app import app, dbConn, cursor
# from app.models import Profiles
app.secret_key = '90000'
# App main route + generic routing
@app.route('/')
def index():
    if 'userdata' not in session:
        return render_template('index.html')
    else:
        return render_template('index1.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/legacy')
def legacy():
    return render_template('legacy.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')

@app.route('/delete')
def delete():
    return render_template('delete.html')


@app.route('/usermodify')
def modify():
    user_birth = session['userdata']['UserBirth']
    birth_date = datetime.strptime(user_birth, "%a, %d %b %Y %H:%M:%S %Z")
    formatted_birth = birth_date.strftime("%Y-%m-%d")

    user_creation = session['userdata']['UserDateOfCreation']
    creation_date = datetime.strptime(user_creation, "%a, %d %b %Y %H:%M:%S %Z")
    formatted_creation = creation_date.strftime("%Y-%m-%d")
    return render_template('usermodify.html', formatted_birth=formatted_birth, formatted_creation=formatted_creation)


@app.route('/deleteSubmit', methods=['POST'])
def deletesubmit():
    email = request.form.get('deemail')
    sql = "DELETE FROM UserProfile WHERE UserEmail = %s"
    cursor.execute(sql, (email))
    session.clear()
    flash('Your profile deleted successfully!!!')
    return render_template('index.html')

@app.route('/signupSubmit', methods=['POST'])
def signupsubmit():
    email = request.form.get('email')
    lname = request.form.get('lname')
    fname = request.form.get('fname')
    gender = request.form.get('gender')
    birth = request.form.get('birth')
    phone = request.form.get('phone')
    pword1 = request.form.get('pword1')
    pword2 = request.form.get('pword2')
    current_datetime = datetime.now()
    current_date = current_datetime.date()
    error = False
    
    if not email or email=="":
        error = True
        flash('Eamil is required')
    
    if not lname:
        error = True
        flash('Last name is required')
    
    if not fname:
        error = True
        flash('First name is required')

    if not gender:
        error = True
        flash('Gender is required')
        
    if not birth:
        error = True
        flash('Date of birth is required')

    if not phone or phone=="":
        error = True
        flash('Phone Number is required')
    
    if not pword1 or pword1=="":
        error = True
        flash('Password is required')
    
    if not pword2 or pword2=="":
        error = True
        flash('Check password is required')

    if pword1 != pword2:
        error = True
        flash('The password before and after is inconsistent. Please enter your password again!!!')

    if error:
        return render_template('signup.html', email=email, lname=lname, fname=fname, gender=gender, birth=birth, phone=phone, pword1=pword1, pword2=pword2)  
    else:
        sql = "INSERT INTO UserProfile (UserEmail, UserLastName, UserFirstName, UserGender, UserBirth, UserPhoneNumber, UserPassword, UserDateOfCreation) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        print(cursor.mogrify(sql, (email, lname, fname, gender, birth, phone, pword1, current_date)))
        cursor.execute(sql, (email, lname, fname, gender, birth, phone, pword1, current_date))
        flash('New user profile added successfully')
    
    return render_template('signin.html', email=email, lname=lname, fname=fname, gender=gender, birth=birth, phone=phone, pword1=pword1)

def check_password(UserEmail, UserPassword):
    with dbConn.cursor() as cursor:    
            sql = "SELECT * FROM UserProfile WHERE UserEmail=%s AND UserPassword=%s"
            cursor.execute(sql, (UserEmail, UserPassword))
            result = cursor.fetchone()
            session['userdata'] = result
    return result

@app.route('/signinSubmit', methods=['POST'])
def signinsubmit():
    inemail = request.form.get('inemail')
    inpword = request.form.get('inpword')
    error = False

    if not inemail:
        error = True
        flash('Email is required')
    
    if not inpword:
        error = True
        flash('Password is required')

    user = check_password(inemail, inpword)
    if user is None:
        error=True
        flash("Your email or password wrong! Please try again!!!")

    if error:
        return render_template('signin.html', inemail=inemail, inpword=inpword)
    else:
        if inemail == session['userdata']['UserEmail'] and inpword == session['userdata']['UserPassword']:
            flash("Correct!")
            #session['userdata']['UserDateOfCreation'] = formatted_creation
            return render_template('profile.html', inemail=inemail, inpword=inpword)


@app.route('/profile')
def profile():
    if 'userdata' in session:
        email = session['userdata']['UserEmail']
        sql = "select * from UserProfile where UserEmail=%s"
        print(cursor.mogrify(sql, (email)))
        cursor.execute(sql, (email))
        userdata = cursor.fetchone()
        session['userdata'] = userdata
        return render_template('profile.html', userdata=userdata)
    
    else:
        flash("You need to log in first! Please log in!")
        return render_template('signin.html')

@app.route('/modifySubmit', methods=['POST'])
def modifysubmit():
    userid = session['userdata']['UserID']
    lname = request.form.get('lname')
    fname = request.form.get('fname')
    gender = request.form.get('gender')
    birth = request.form.get('birth')
    phone = request.form.get('phone')
    pword1 = request.form.get('pword1')

    sql = "UPDATE UserProfile SET UserLastName = %s, UserFirstName = %s, UserGender = %s, UserBirth = %s, UserPhoneNumber = %s, UserPassword = %s WHERE UserID = %s"
    print(cursor.mogrify(sql, (lname, fname, gender, birth, phone, pword1, userid)))
    cursor.execute(sql, (lname, fname, gender, birth, phone, pword1, userid))
    flash('Your own profile updated successfully')
    return redirect(url_for('profile'))

@app.route('/orderSubmit', methods=['POST'])
def orderSubmit():
    # Get the user input values from the form
    # email = request.form.get('email')
    print("request.form:",request.form)
    pnumber = request.form.get('pnumber')
    add = request.form.get('add')
    time = request.form.get('time')
    fee = request.form.get('fee')
    merchant = request.form.get('merchant')
    desc = request.form.get('desc')
    email = session['userdata']['UserEmail']
    error = False

    if not email or email.strip() =="":
        error = True
        flash('Your e-mail address is required')

    if not pnumber or pnumber.strip() =="":
        error = True
        flash('Your phone number is required')
    
    if not add or add.strip() == "":
        error = True
        flash('Your delivery address is required')

    if not time:
        error = True
        flash('The delivery time is required')
    # else:
        # Check if the submitted delivery time is at least one hour later than the current time
        # current_time = datetime.now()
        # now_hour = hour(current_time)
        # submitted_time = datetime.strptime(time, '%H:%M')
        # if submitted_time < current_time + timedelta(hours=9):
        #     error = True
        #     flash('The delivery time must be at least one hour from now')
        
    
    if not fee or fee.strip() == "":
        error = True
        flash('The delivery fee is required')
    

    if not merchant:
        error = True
        flash('You have to select the merchant')

    if not desc or desc.strip() == "":
        error = True
        flash('You have to describe the products you want to buy')
   
        
        
    #database operations
    if error:
        #return to the form page
        sql = "select * from Merchants" 
        cursor.execute(sql)
        merchant_list = cursor.fetchall()
        return render_template('create_order.html', email=email, pnumber=pnumber, add=add, time=time, fee=fee, merchant_list=merchant_list, desc=desc)
    else:
        # do the database 

        sql = "INSERT INTO Request (email, PhoneNumber, DeliveryAddress, DeliveryTime, ReqDeliveryFee, MerchantName, RequestContent) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        # print(cursor.mogrify(sql, (email, pnumber, add, time, fee, merchant, desc)))
        cursor.execute(sql, (email, pnumber, add, time, fee, merchant, desc))
        #conn.commit()

        # dbConn.commit()

        flash('Order placed successfully! Please wait for acceptance.')
            
        return redirect('/orderList')

@app.route('/orderList')
def orderList():
    if 'userdata' in session:
        sql = "SELECT * FROM Request"
        cursor.execute(sql)
        order_list = cursor.fetchall()
        print("order_list:", order_list)
        return render_template('order_list.html', order_list=order_list)
    else:
        flash("You need to log in first! Please log in!")
        return render_template('signin.html')

@app.route('/acceptOrder', methods=['GET'])
def acceptOrder():
    if 'userdata' in session:
        email = session['userdata']['UserEmail']
        rid = request.args.get('Id2')
        atime = datetime.now()
        if rid:
            print(rid)
            sql = "SELECT * FROM Request WHERE rid = %s"
            print(cursor.mogrify(sql,(rid,)))
            cursor.execute(sql, (rid,))
            result = cursor.fetchone()
            print(result)
        #IndexError: tuple index out of range
            if result['Acceptance'] == 1:
                return "Error: Cannot accept the order, which has been accepted."
            else:
                if result['email'] == email:
                    return "Error: You can not accept the order from yourself."
                else:
                    sql2 = "INSERT INTO RequestAcceptance (rid, email, AcceptanceTime) VALUES (%s, %s, %s)"
                    print(cursor.mogrify(sql2,(rid, email, atime)))
                    cursor.execute(sql2, (rid, email, atime))
                    sql3 = "UPDATE Request SET Acceptance = 1 WHERE rid = %s"
                    cursor.execute(sql3,(rid))
                    return 'Accept successfully!'
        else:
            return "order not found"
    else:
        flash("You need to log in first!!! Please log in!!!")
        return redirect(url_for('signin'))

@app.route('/myAcOrder',methods=['GET'])
def myAcOrder():
    if 'userdata' in session:
        email = session['userdata']['UserEmail']
        sql = 'SELECT * FROM RequestAcceptance WHERE email = %s'
        print(cursor.mogrify(sql,(email)))
        cursor.execute(sql, (email))
        result = cursor.fetchall()
        print(result)
        acOrder_list = []
        if result:
            for row in result:
                rid1 = row['rid']
                sql2 = 'SELECT * FROM Request WHERE rid = %s'
                print(cursor.mogrify(sql2, (rid1,)))
                cursor.execute(sql2, (rid1,))
                acOrder = cursor.fetchone()
                if acOrder:
                    acOrder_list.append(acOrder)
            return render_template('myAcOrder.html',result=result, acOrder_list=acOrder_list)
        else:
            return "Your account has not received any order."
    else:
        flash("You need to log in first!!! Please log in!!!")
        return redirect(url_for('signin'))

@app.route("/cancelAcceptance")
def cancelAcceptance():
    if 'userdata' in session:
        email = session['userdata']['UserEmail']
        rid = request.args.get('Id')
        if rid:
            print(rid)
            sql = "DELETE FROM RequestAcceptance WHERE rid = %s"
            print(cursor.mogrify(sql,(rid,)))
            cursor.execute(sql, (rid,))
            sql2 = "UPDATE Request SET Acceptance = 0 WHERE rid = %s"
            print(cursor.mogrify(sql2,(rid,)))
            cursor.execute(sql2, (rid,))
            return 'Cancel Acceptance Successfully!'
        else:
            return "order not found"
    else:
        flash("You need to log in first!!! Please log in!!!")
        return redirect(url_for('signin'))


@app.route('/gender')
def genderGraph():

    sql = "select UserGender as label, COUNT(*) as value from UserProfile GROUP BY UserGender"
    cursor.execute(sql)
    gGender = cursor.fetchall()
    chartData = json.dumps(gGender)
        
    return render_template('graphGender.html', chartData=chartData)


@app.route('/age')
def ageGraph():
    sql = "select cast((YEAR(CURDATE()) - YEAR(UserBirth)) as char) AS label, COUNT(*) as value from UserProfile GROUP BY label"
    cursor.execute(sql)
    gAge = cursor.fetchall()
    chartData = json.dumps(gAge)
    return render_template('graphAge.html', chartData=chartData)

@app.route("/graph")
def graph():
        sql = "SELECT * FROM Request WHERE Acceptance='1'"
        cursor.execute(sql)
        order_list = cursor.fetchall()

        year_dict = {}
        month_dict = {}
        day_dict = {}
        for item in order_list:
            delivery_time = item['DeliveryTime']
            day_str = delivery_time.strftime('%Y-%m-%d')
            month_str = delivery_time.strftime('%Y-%m')
            year_str = delivery_time.strftime('%Y')
            print("day_str:", day_str)
            print("month_str:", month_str)
            print("year_str:", year_str)
            if day_str not in day_dict:
                day_dict[day_str] = 0
            day_dict[day_str] += 1
            if month_str not in month_dict:
                month_dict[month_str] = 0
            month_dict[month_str] += 1
            if year_str not in year_dict:
                year_dict[year_str] = 0
            year_dict[year_str] += 1

        year_list = [{'label': item, 'value': year_dict[item]} for item in year_dict]
        month_list = [{'label': item, 'value': month_dict[item]} for item in month_dict]
        day_list = [{'label': item, 'value': day_dict[item]} for item in day_dict]

        year_chart = json.dumps(year_list)
        month_chart = json.dumps(month_list)
        day_chart = json.dumps(day_list)

        return render_template("graph.html", year_chart=year_chart, month_chart=month_chart, day_chart=day_chart)


@app.route('/orderView')
def orderview():
    return render_template('orderView.html')

@app.route('/Submit')
def submit():
    if 'userdata' in session:
        sql = "select * from Merchants" 
        cursor.execute(sql)
        merchants = cursor.fetchall()
        email = session['userdata']['UserEmail']
        return render_template('submitOrder.html', merchants=merchants, email=email)
    else:
        flash("You need to log in first! Please log in!")
        return render_template('signin.html')
                

@app.route('/OrderInsert', methods=['POST'])
def OrderInsert():
    # Get the user input values from the form
    email = request.form['email']
    pnumber = request.form.get('pnumber')
    add = request.form.get('add')
    time = request.form.get('time')
    rtime = datetime.now()
    fee = request.form.get('fee')
    merchant = request.form.get('merchant')
    desc = request.form.get('desc')
    ac = 0
    error = False

    #input validation

    if not pnumber or pnumber.strip() =="":
        error = True
        flash('Your phone number is required')
    
    if not add or add.strip() == "":
        error = True
        flash('Your delivery address is required')

    if not time:
        error = True
        flash('The delivery time is required')
    else:
        # Check if the submitted delivery time is at least one hour later than the current time
        current_time = datetime.now()
        submitted_time = datetime.strptime(time, '%Y-%m-%dT%H:%M')
        if submitted_time < current_time + timedelta(hours=9):
            error = True
            flash('The delivery time must be at least one hour from now')
        
    
    if not fee or fee.strip() == "":
        error = True
        flash('The delivery fee is required')
    

    if not merchant:
        error = True
        flash('You have to select the merchant')

    if not desc or desc.strip() == "":
        error = True
        flash('You have to describe the products you want to buy')
   
        
        
    #database operations
    if error:
        #return to the form page

        sql = "SELECT * FROM Merchants"
        cursor.execute(sql)
        merchants = cursor.fetchall()

        # Return to the form page with error messages and form data
        return render_template('submitOrder.html', email=email, pnumber=pnumber, add=add, time=time, fee=fee, merchant=merchant, desc=desc, merchants=merchants)
    else:
        # do the database 

        sql = "INSERT INTO Request (email, PhoneNumber, DeliveryAddress, DeliveryTime, ReqDeliveryFee, MerchantName, RequestContent, RequestTime, Acceptance) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        print(cursor.mogrify(sql, (email, pnumber, add, time, fee, merchant, desc, rtime, ac)))
        cursor.execute(sql, (email, pnumber, add, time, fee, merchant, desc, rtime,ac))
        return render_template('orderSuccess.html')
    
@app.route('/orderSuccess')
def success():
    return render_template('orderSuccess.html')


@app.route('/myOrder')      
def myOrder():
    if 'userdata' in session:
        email = session['userdata']['UserEmail']
        sql = "SELECT * FROM Request WHERE email = %s"
        cursor.execute(sql, (email))
        myorders = cursor.fetchall()
        return render_template('MyOrder.html', myorders=myorders)
    else:
        flash("You need to log in first! Please log in!")
        return render_template('signin.html')
            

@app.route('/deleteOrder', methods=['GET'])
def delete_order():
   
    ridd = request.args.get('orderId')
    if ridd:
        sql = 'SELECT * FROM Request WHERE rid= %s'
        print(cursor.mogrify(sql,(ridd)))
        cursor.execute(sql,(ridd))
        result = cursor.fetchone()
        print(result)
        if result['Acceptance'] == 1:
            return "Error: Can not delete, the order has been accepted"
        else:
            sql2 = 'DELETE FROM Request WHERE rid = %s'
            print(cursor.mogrify(sql2,(ridd,)))
            cursor.execute(sql2,(ridd,))
            return render_template('deleteSuccess.html')
        
    else:
        return "Error: Order not found."
        
'''
sql = "DELETE FROM Request WHERE rid = %s AND Acceptance != 1"
        print(cursor.mogrify(sql,(ridd,)))
        cursor.execute(sql, (ridd,))
        affected_rows = cursor.rowcount
        
        if affected_rows > 0:
            return render_template('deleteSuccess.html')
        else:
            return "Error: Cannot delete, order not found or has been accepted."
'''    
  


@app.route('/modifyOrder')
def modify_order():
    ridm = request.args.get('orderId2')

    if ridm:
        print(ridm)
        sql = 'SELECT * FROM Request WHERE rid= %s'
        print(cursor.mogrify(sql,(ridm)))
        cursor.execute(sql,(ridm))
        selected = cursor.fetchone()
        print(selected)
        if selected['Acceptance'] == 1:
            return "Error: Can not modify, the order has been accepted"
        else:
            return render_template('modify.html',rid=selected['rid'], email=selected['email'], pnumber=selected['PhoneNumber'], add=selected['DeliveryAddress'], time=selected['DeliveryTime'], fee=selected['ReqDeliveryFee'], merchant=selected['MerchantName'], desc=selected['RequestContent'])
        
    else:
        return "Error: Order not found."
    
@app.route('/modifyInvalidation', methods=['POST'])
def modifyInvalidation():
    rid = request.form.get('rid')
    email = request.form.get('email')
    pnumber = request.form.get('pnumber')
    add = request.form.get('add')
    time = request.form.get('time')
    fee = request.form.get('fee')
    merchant = request.form.get('merchant')
    desc = request.form.get('desc')
    
    error = False

    #input validation

    if not pnumber or pnumber.strip() =="":
        error = True
        flash('Your phone number is required')
    
    if not add or add.strip() == "":
        error = True
        flash('Your delivery address is required')

    if not time:
        error = True
        flash('The delivery time is required')
    else:
        # Check if the submitted delivery time is at least one hour later than the current time
        current_time = datetime.now()
        submitted_time = datetime.strptime(time, '%Y-%m-%dT%H:%M')
        if submitted_time < current_time + timedelta(hours=9):
            error = True
            flash('The delivery time must be at least one hour from now')
        
    
    if not fee or fee.strip() == "":
        error = True
        flash('The delivery fee is required')
    

    if not desc or desc.strip() == "":
        error = True
        flash('You have to describe the products you want to buy')
   
        
        
    #database operations
    if error:
        #return to the form page
        invalid = True
        return render_template('modify.html', rid=rid, email=email, pnumber=pnumber, add=add, time=time, fee=fee, merchant=merchant, desc=desc, invalid=invalid)
    else:
        # do the database 
        sql = "UPDATE Request SET email = %s, PhoneNumber = %s, DeliveryAddress = %s, DeliveryTime = %s, ReqDeliveryFee = %s, RequestContent = %s WHERE rid = %s"
        print(cursor.mogrify(sql, (email, pnumber, add, time, fee, desc, rid)))
        cursor.execute(sql, (email, pnumber, add, time, fee, desc, rid))
        return render_template('modifySuccess.html')


@app.route('/merchantChart')
def merchantChart():
    sql = 'select MerchantName as label, COUNT(*) as value from Request GROUP BY MerchantName'
    cursor.execute(sql)
    results = cursor.fetchall()
    chartData = json.dumps(results)
    return render_template('merchantChart.html', results=chartData)

    
