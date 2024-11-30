from app import app, db

#Main method
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)