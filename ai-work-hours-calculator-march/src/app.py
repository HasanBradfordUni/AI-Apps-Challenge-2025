from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from utils.forms import WorkHoursForm
from ai.geminiPrompt import generate_summary

app = Flask(__name__)
app.config['SECRET_KEY'] = 'randomString'
Bootstrap5(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = WorkHoursForm()
    if form.validate_on_submit():
        contracted_hours = form.expected_hours.data
        time_frame = form.time_frame.data
        contracted_hours = f"{contracted_hours} hours per {time_frame}"
        work_hours_description = form.work_hours_description.data
        # Here you can call the AI model to generate a summary
        summary = generate_summary(contracted_hours, work_hours_description)
        # Here you can add logic to process the work hours
        return redirect(url_for('result', ai_summary=summary))
    return render_template('index.html', form=form)

@app.route('/result/<ai_summary>')
def result(ai_summary):
    # Here you can add logic to display the result
    return render_template('result.html', ai_summary=ai_summary)

if __name__ == '__main__':
    app.run(host='localhost', port=5000)