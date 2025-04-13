from flask import Flask, render_template, redirect, url_for, request, jsonify
from utils.forms import WorkHoursForm
from ai.geminiPrompt import generate_work_hours_summary
from datetime import datetime, timedelta

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
        return render_template('index.html', form=form, ai_summary=summary)
    return render_template('index.html', form=form)

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        firstOperand = data['firstOperand']
        secondOperand = data['secondOperand']
        operator = data['operator']
        
        result = calculate_hours(firstOperand, secondOperand, operator)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def calculate_hours(firstOperand, secondOperand, operator):
    firstOperand = firstOperand.split(".")
    secondOperand = secondOperand.split(".")
    if operator == '+':
        result = timedelta(hours=int(firstOperand[0]), minutes=int(firstOperand[1])) + timedelta(hours=int(secondOperand[0]), minutes=int(secondOperand[1]))
        result = str(result).split(",")
        result = result[1].split(":") if len(result) > 1 else result[0].split(":")
        result = str(int(result[0])) + "." + str(int(result[1]))
        return result
    elif operator == '-':
        result = timedelta(hours=int(firstOperand[0]), minutes=int(firstOperand[1])) - timedelta(hours=int(secondOperand[0]), minutes=int(secondOperand[1]))
        result = str(result).split(",")
        result = result[1].split(":") if len(result) > 1 else result[0].split(":")
        result = str(int(result[0])) + "." + str(int(result[1]))
        return result
    elif operator == '*':
        result = timedelta(hours=int(firstOperand[0]), minutes=int(firstOperand[1])) * int(secondOperand[0])
        result = str(result).split(",")
        result = result[1].split(":") if len(result) > 1 else result[0].split(":")
        result = str(int(result[0])) + "." + str(int(result[1]))
        return result
    elif operator == '/':
        result = timedelta(hours=int(firstOperand[0]), minutes=int(firstOperand[1])) / int(secondOperand[0])
        result = str(result).split(",")
        result = result[1].split(":") if len(result) > 1 else result[0].split(":")
        result = str(int(result[0])) + "." + str(int(result[1]))
        return result
    else:
        raise ValueError("Invalid operator")

if __name__ == '__main__':
    app.run(host='localhost', port=6922)