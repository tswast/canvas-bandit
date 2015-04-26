# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from flask import Flask, render_template, session, request

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'



@app.route('/')
def index():
    print 'render index'
    return render_template('index.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0')
