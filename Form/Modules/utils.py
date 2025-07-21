from flask import render_template_string
import os

template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))

def render_temp(file_name, **kwargs):
    with open(template_path + "/" + file_name + ".html", 'r', encoding='utf-8') as f:
        template_content = f.read()
    return render_template_string(template_content, error="Form name is required.", **kwargs)

