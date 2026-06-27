from flask import Flask, render_template, request

app = Flask(__name__)

# Root route - Login page dikhayega
@app.route('/')
def home():
    return render_template('login.html')

# Form submission handle karega
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Yahan hum baad mein Playwright ka logic add karenge
    print(f"User attempting login: {username}")
    return "Login credentials captured! (Backend logic pending)"

if __name__ == '__main__':
    app.run(debug=True)
