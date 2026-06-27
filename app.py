from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Home Page (Landing Page)
@app.route('/')
def home():
    return render_template('login.html') # Yahan tumhara naya UI design show hoga

# Login Page Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Captured: {username} / {password}") # Data console mein dikhega
        return "Login successful! (Redirecting...)"
    return render_template('login.html')

# Sign Up Page Route
@app.route('/signup')
def signup():
    return "Sign Up Page is currently under construction!"

if __name__ == '__main__':
    app.run(debug=True)
