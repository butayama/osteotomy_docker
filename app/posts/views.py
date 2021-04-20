from flask import render_template

from . import posts


@posts.route('/measure')
def measure():
    return render_template('../posts/measure.html')
