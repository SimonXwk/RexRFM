if __name__ == '__main__':
    from app import create_app
    create_app('development').run(host='0.0.0.0', port=5005)
