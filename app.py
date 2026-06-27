from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Yahan tumhari condition (Real ID check)
    if username == "kushal" and password == "12345":
        return "Login Success! Welcome back."
    else:
        return "Incorrect username or password. Please try again."

if __name__ == '__main__':
    app.run(debug=True)
