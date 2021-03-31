from sweater import app
import logging.config

logging.config.fileConfig('logger.conf')
logger = logging.getLogger('main')


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
