from website import create_app

app = create_app()

if __name__ == '__main__': # Başka bir dosya tarafından import edilirse çalışmaz
    app.run(debug=True)
