from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from utils.forms import WorkHoursForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'randomString'
Bootstrap5(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = WorkHoursForm()
    if form.validate_on_submit():
        username = form.username.data
        hours_worked = form.hours_worked.data
        # Here you can add logic to process the work hours
        return redirect(url_for('result', username=username, hours_worked=hours_worked))
    return render_template('index.html', form=form)

@app.route('/result/<hours_worked>')
def result(hours_worked):
    # Here you can add logic to display the result
    return f"You have worked {hours_worked} hours."

if __name__ == '__main__':
    app.run(host='localhost', port=5000)