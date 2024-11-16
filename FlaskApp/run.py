from flask import Flask, render_template


app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

#to login
@app.route('/login')
def login():
    return render_template('login.html')

#to logout
@app.route('/logout')
def logout():
    return render_template("logout.html")

#to view the stocks
@app.route('/view')
def view():
    return render_template("view_stocks.html")

#to view a members profile (their stocks, holdings, watchlist)
@app.route('/profile')
def profile():
    return render_template("profile.html")

if __name__ == '__main__':
   app.run()
