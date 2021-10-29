from STATQ import create_app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        from STATQ import db
        db.create_all()
    app.run(host="0.0.0.0", debug=True)
