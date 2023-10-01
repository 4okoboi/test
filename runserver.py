from main import app, global_init

if __name__ == "__main__":
    global_init('sqlite:///users.sqlite')
    app.run()
