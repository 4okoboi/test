from main import app, global_init

if __name__ == '__main__':
    global_init('sqlite:///users.sqlite')
    app.run(debug=True, host='127.0.0.1', port=3000)
