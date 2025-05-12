import flask
import os
app = flask.Flask(__name__)
app.config['FLAG'] = "ddd"

@app.route('/')
def index():
    return open(__file__).read()

@app.route('/shrine/<path:shrine>')
def shrine(shrine):
    return flask.render_template_string(shrine)

if __name__ == '__main__':
    app.run(debug=True)