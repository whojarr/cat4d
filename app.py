import json
import os
import re
import openai
import urllib.parse
from flask import Flask
from flask import render_template, make_response, request, redirect, url_for

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

openai.api_key = OPENAI_API_KEY

def escape_html_chars(text):
    """Escape HTML characters.""" 
    # replaced_text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
    return text.replace('\n', ' <br> ')


def ai_generate(question):
    model = "gpt-3.5-turbo"
    message_list = []
    message_list.append({"role": "system", "content": "return x3d example code based on the question asked. do not return anything but the x3d code. do not provide comments"})
    message_list.append({"role": "user", "content":question})

    response = openai.ChatCompletion.create(
        model = model,
        messages = message_list
    )
    response_content = response['choices'][0]['message']['content']

    return response_content


def ai_modify(question, source):
    model = "gpt-3.5-turbo"
    message_list = []
    message_list.append({"role": "system", "content": "update or add more detail the x3d source code based on the question asked. do not return anything but the x3d code. do not provide comments"})
    message_list.append({"role": "user", "content":question})
    message_list.append({"role": "user", "content":f'source: {source}'})

    response = openai.ChatCompletion.create(
        model = model,
        messages = message_list
    )
    response_content = response['choices'][0]['message']['content']

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
    scene = None
    x3d = None
    if request.method == "POST":

        if request.form.get('edit') == "edit":
            return redirect(url_for('ai_edit'), code=307)

        question = request.form.get('question')
        response = ai_generate(question)

        x3d_pattern = re.compile(r'<X3D>(.*?)<X3D>', re.DOTALL)
        x3ds = x3d_pattern.findall(response)

        scene_pattern = re.compile(r'<Scene>(.*?)</Scene>', re.DOTALL)
        scenes = scene_pattern.findall(response)

        if len(x3ds) > 0:
            x3d = response
        
        if len(scenes) > 0:
            scene = f"<Scene>{scenes[0]}</Scene>"
        else:
            scene = f"<Scene>{response}</Scene>"

    resp = make_response(render_template("ai_create.xhtml", question=question, x3d=x3d, scene=scene),200)
    resp.headers['Content-Type'] = 'application/xhtml+xml'
    return resp


@app.route("/ai_edit/", methods=["GET", "POST"])
def ai_edit():

    scene = None
    x3d = None
    question = request.form.get('question', '')
    if request.form.get('edit') == "edit":
         question = ""
    encoded_source = request.form.get('source', '')

    if not encoded_source == '':
        source = urllib.parse.unquote(encoded_source)
        x3d_pattern = re.compile(r'<X3D>(.*?)<X3D>', re.DOTALL)
        x3ds = x3d_pattern.findall(source)

        scene_pattern = re.compile(r'<Scene>(.*?)</Scene>', re.DOTALL)
        scenes = scene_pattern.findall(source)

        if len(x3ds) > 0:
            x3d = source
        
        if len(scenes) > 0:
            x3d = f"<X3D id='x3d' showStat='false' showLog='false' showProgress='bar' \
                version='3.3' noNamespaceSchemaLocation='http://www.web3d.org/specifications/x3d-3.3.xsd' \
                width='100%' height='600px'><Scene>{scenes[0]}</Scene></X3D>"
        else:
            x3d = f"<X3D id='x3d' showStat='false' showLog='false' showProgress='bar' \
                version='3.3' noNamespaceSchemaLocation='http://www.web3d.org/specifications/x3d-3.3.xsd' \
                width='100%' height='600px'><Scene>{source}</Scene></X3D>"

        if request.form.get('save') == 'save':
            print("save x3d")


        # response = ai_modify(question, x3d)
        if not question == '':
            response = ai_modify(question, x3d)
            x3d_pattern = re.compile(r'<X3D>(.*?)<X3D>', re.DOTALL)
            x3ds = x3d_pattern.findall(response)
            scene_pattern = re.compile(r'<Scene>(.*?)</Scene>', re.DOTALL)
            scenes = scene_pattern.findall(response)
            if len(x3ds) > 0:
                x3d = response
            if len(scenes) > 0:
                x3d = f"<X3D id='x3d' showStat='false' showLog='false' showProgress='bar' \
                    version='3.3' noNamespaceSchemaLocation='http://www.web3d.org/specifications/x3d-3.3.xsd' \
                    width='100%' height='600px'><Scene>{scenes[0]}</Scene></X3D>"
            else:
                x3d = f"<X3D id='x3d' showStat='false' showLog='false' showProgress='bar' \
                    version='3.3' noNamespaceSchemaLocation='http://www.web3d.org/specifications/x3d-3.3.xsd' \
                    width='100%' height='600px'><Scene>{source}</Scene></X3D>"
            question = ""


    resp = make_response(render_template("ai_edit.xhtml", question=question, x3d=x3d),200)
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
