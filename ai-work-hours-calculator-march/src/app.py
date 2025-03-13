from flask import Flask, render_template, redirect, url_for
from utils.forms import WorkHoursForm
from ai.geminiPrompt import generate_work_hours_summary

app = Flask(__name__)
app.config['SECRET_KEY'] = 'randomString'

@app.route('/', methods=['GET', 'POST'])
def index():
    form = WorkHoursForm()
    if form.validate_on_submit():
        contracted_hours = form.expected_hours.data
        time_frame = form.time_frame.data
        contracted_hours = f"{contracted_hours} hours per {time_frame}"
        work_hours_description = form.work_hours_description.data
        # Here you can call the AI model to generate a summary
        summary = generate_work_hours_summary(contracted_hours, work_hours_description)
        responses = summary.split("\n")
        summary = ""
        for response in responses:
            response = response.strip("#").strip("*")
            if response.startswith("Total"):
                summary += "<h2>"+response+"</h2><br>"
            elif response.startswith("Overtime") or response.startswith("Undertime"):
                summary += "<h3>"+response+"</h3><br>"
            else:
                summary += response+"<br>"
            print(summary)
        # Here you can add logic to process the work hours
        return render_template('index.html', form=form, ai_summary=summary)
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(host='localhost', port=6922)