from app import create_app, get_db


app = create_app()
app.app_context().push()


db = get_db()
db.create_all(app=create_app())
