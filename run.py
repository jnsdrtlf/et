#!/usr/bin/env python3

if __name__ == '__main__':
    import sys
    import os
    from app import create_app

    root = os.path.abspath(os.path.dirname(sys.argv[0]))
    app, db = create_app(root)
    app.run(port=5000)
