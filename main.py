from application import init_routes

if __name__ == '__main__':
    init_routes.app.run(host='localhost', port=5000, debug=True)
