import json
import os
import re
import openai
from flask import Flask
from flask import render_template, make_response, request

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

openai.api_key = OPENAI_API_KEY

def escape_html_chars(text):
    """Escape HTML characters.""" 
    # replaced_text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
    return text.replace('\n', ' <br> ')


def ai_question(question):

    model = "gpt-3.5-turbo"

    message_list = []

    message_list.append({"role": "system", "content": "return x3d example code based on the question asked. do not return anything but the x3d code. do not provide comments"})
    message_list.append({"role": "user", "content":question})

    response = openai.ChatCompletion.create(
        model = model,
        messages = message_list
    )

    response_content = response['choices'][0]['message']['content']
    # response_role = response['choices'][0]['message']['role']

    # message_list.append({"role": response_role, "content": response_content})

    # message_list_json = json.dumps(message_list)
    # message_list_display = [d for d in message_list if d.get('role') != 'system']

    # for message in message_list_display:
    #     message['content'] = escape_html_chars(message['content'])

    # result = {
    #     "message_list": message_list,
    #     "message_list_display": message_list_display,
    #     "message_list_json": message_list_json
    # }

    return response_content


@app.route("/")
def catalyst():

    resp = make_response(render_template("catalyst.xhtml", **locals()),200)
    resp.headers['Content-Type'] = 'application/xhtml+xml'
    return resp


@app.route("/ai_create/", methods=["GET", "POST"])
def ai_create():

    question = ""
    matches = ""
    response = ""
    if request.method == "POST":

        question = request.form.get('question')
        response = ai_question(question)

        scene_pattern = re.compile(r'<Scene>(.*?)</Scene>', re.DOTALL)
        scenes = scene_pattern.findall(response)

        if len(scenes) > 0:
            response = f"<Scene>{scenes[0]}</Scene>"
        else:
            response = f"<Scene>{response}</Scene>"
        print(response)
        print("matches:")
        print(matches)

    resp = make_response(render_template("ai_create.xhtml", question=question, response=response),200)
    resp.headers['Content-Type'] = 'application/xhtml+xml'
    return resp


@app.route("/steps/")
def steps():

    resp = make_response(render_template("steps.xhtml", **locals()),200)
    resp.headers['Content-Type'] = 'application/xhtml+xml'
    return resp


if __name__ == "__main__":
    print("started local")
    app.run(debug=True, ssl_context='adhoc')
