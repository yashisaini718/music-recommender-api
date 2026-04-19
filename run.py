from app import create_app
# the main running for the project

app=create_app()
if __name__=="__main__":
    app.run(debug=True)