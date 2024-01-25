from flask import render_template, redirect, url_for, abort, request, \
    current_app, session
from . import main
from ..navs.nav_items import get_nav_items
from .forms import CalculateForm
from ..Calculation import CalculateAngles as ca
import os
from math import degrees
import importlib


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/')
def index():
    # return render_template('about_under_construction.html', imp0rt=importlib.import_module,
    #                        angle_signs="static/img/angle_signs.png")
    # return render_template('index.html', imp0rt = importlib.import_module)
    nav_items = get_nav_items()
    return render_template('sign_rules.html', imp0rt = importlib.import_module, nav_items=nav_items)


# @main.route('/case')
# def case():
#     return render_template('case.html', imp0rt = importlib.import_module)


@main.route('/op_planning', methods=['GET', 'POST'])
def op_planning():
    nav_items = get_nav_items()
    coronal_component_C = 0
    sagittal_component_S = 0
    torsion_component_T = 0
    values = {}
    form = CalculateForm()
    if request.method == 'GET':
        form.coronal_component_C.data = coronal_component_C
        form.sagittal_component_S.data = sagittal_component_S
        form.torsion_component_T.data = torsion_component_T
        # form.filename.data = f"osteotomy_result_{coronal_component_C}" + "_" + f"{sagittal_component_S}" + "_" + \
        #                      f"{torsion_component_T}" + ".txt"
    if form.validate_on_submit():
        filename, c_a_d, s_a_d, t_a_d, c_a, s_a, t_a, a_tad, a_oa, a_azi, a_ele, a_aor = \
            ca.calculate(form.coronal_component_C.data,
                         form.sagittal_component_S.data,
                         form.torsion_component_T.data)
        session['values'] = {
            "c_a_d": c_a_d,
            "s_a_d": s_a_d,
            "t_a_d": t_a_d,
            "c_a": c_a,
            "s_a": s_a,
            "t_a": t_a,
            "a_tad": a_tad,
            "a_oa": a_oa,
            "a_azi": a_azi,
            "a_ele": a_ele,
            "a_aor": a_aor
        }
        return redirect(url_for('.op_planning_results', values=session['values']))

    return render_template('calculate.html', form=form, imp0rt=importlib.import_module,
                           nav_items=nav_items)


@main.route('/op_planning_results', methods=['GET', 'POST'])
def op_planning_results():
    nav_items = get_nav_items()
    return render_template('op_planning_results.html', values=session['values'], degrees=degrees,
                           chr=chr, int=int, imp0rt=importlib.import_module, nav_items=nav_items)


# @main.route('/measure')
# def measure():
#     return render_template('measure.html', imp0rt = importlib.import_module)


@main.route('/sign')
def op():
    nav_items = get_nav_items()
    return render_template('sign_rules.html', imp0rt=importlib.import_module,
                           angle_signs="static/img/angle_signs.png", nav_items=nav_items)


# @main.route('/post_op')
# def post_op():
#     return render_template('post_op.html', imp0rt = importlib.import_module)
#
#
@main.route('/about')
def about():
    nav_items = get_nav_items()
    return render_template('about.html', imp0rt=importlib.import_module, nav_items=nav_items)


@main.route('/imprint')
def imprint():
    nav_items = get_nav_items()
    return render_template('imprint.html', imp0rt=importlib.import_module, nav_items=nav_items)


@main.route('/privacy_policy')
def privacy_policy():
    nav_items = get_nav_items()
    return render_template('privacy_policy.html', imp0rt=importlib.import_module, nav_items=nav_items)

# @main.route('/about_under_construction.html')
# def about_under_construction():
#     return render_template('about_under_construction.html', imp0rt=importlib.import_module)
