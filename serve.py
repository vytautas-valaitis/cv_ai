import os, subprocess, requests, tempfile
import base64, json
from flask import Flask, render_template, request, jsonify

from skill_parser import fit_skill
from doc_parser import parse_doc

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
  return render_template('srv.html', msg='')

@app.route('/api/parse_skill', methods=['GET', 'POST'])
def parse_skill():
  content = request.json
  r = content['text']
  r = {'text': [r, r, r], 'skill': [None, None, None]}
  results = fit_skill.fit(r)
  return jsonify(results)
  
@app.route('/api/parse_doc', methods=['GET', 'POST'])
def add_message():
  content = request.json
  r = content['text']
  n = content['filename']

  bdata = base64.b64decode(r)
  with tempfile.TemporaryDirectory() as tmpdirname:
    tmp_dir = tmpdirname
  
    filename = tmp_dir + '/file.pdf'
    filename_json = tmp_dir + '/file.json'

    with open(os.path.join(tmp_dir, 'file.pdf'), 'wb') as fp:
      fp.write(bdata)

    parse_doc.main(tmp_dir = tmp_dir, filename = n)

    with open(tmp_dir + '/allSkills.json', 'r') as fj:
      jsonfile = json.load(fj)

    #os.remove(filename)
    #os.remove(filename_json)

  return jsonify(jsonfile)

if __name__ == '__main__':
  app.run()
