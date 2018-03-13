#!/usr/bin/env python3
import os
import sys
from flask import Blueprint, Flask, render_template, request, url_for

controller = Blueprint('structure', __name__, url_prefix='/structure')


def get_text_descriptions(dept):

    # print("dept:", dept)
    # print("script: sys.argv[0] is", repr(sys.argv[0]))
    # print("script: __file__ is", repr(__file__))
    # print("script: cwd is", repr(os.getcwd()))

    txt_files = []
    txt_file_path = 'core/descriptions/{dept}/'.format(dept=dept)
    txt_files = [txt_file_path + x for x in os.listdir(txt_file_path) if x.endswith(".txt")]

    template_file = 'core/templates/{dept}.html'.format(dept=dept)

    # print('txt_files:', txt_files)
    # print('template_file:', template_file)

    # read each image file and add to template as list item
    ret_val = []
    with open(template_file, 'a') as t:
        for txt_file in txt_files:
            with open(txt_file, 'r') as i:
                for line in i:
                    ret_val.append(line)

    return ret_val


@controller.route("/router", methods=['GET', 'POST'])
def test():
    if request.method == 'GET':
        pass
        # print(request.method)
        # return request.method
    elif request.method == 'POST':
        dept = str(request.form['select_department'])
        #return dept
        if dept == 'none':
            return '', 204
        else:
            #return dept
            descts = get_text_descriptions(dept)
            # print(descts)
            return render_template('{dept}.html'.format(dept=dept), items=descts)


# @controller.route('/<string:title>', methods=['GET'])
# def lookup(title):
#     if title == 'Republic':  # TODO 2
#         return render_template('republic.html')  # TODO 2
#     else:
#         pass
