"""LLM product search server stub — REST:8000."""

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/query')
def query():
    name = request.args.get('name', '')
    return jsonify({'zone_id': None, 'query': name})


@app.route('/find_product')
def find_product():
    query_str = request.args.get('query', '')
    return jsonify({'zone_id': None, 'query': query_str})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
