from app import create_app


UPLOAD_FOLDER = '/app/static/imgs'

app = create_app()

if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.run(debug=True)
