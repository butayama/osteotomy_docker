from flask_nav.elements import Navbar, View


# TODO https://stackoverflow.com/questions/36505091/flask-nav-bootstrap-navbar-dynamic-construction-align-some
#  -element-to-the-right

class NavItems:
    topbar = Navbar('',
                    View('OSTEOTOMY', 'main.index'),
                    View('CASE', 'main.case'),
                    View('OP_PLANNING', 'main.op_planning'),
                    View('OP', 'main.op'),
                    View('POST_OP', 'main.post_op'),
                    View('ABOUT', 'main.about'),

                    )

    rightbar = Navbar('',
                      View('LOG IN', 'auth.login'),

                      )

    not_used = Navbar('',
                      View('INDEX_01', 'auth.index_01'),
                      View('DETAILS', 'auth.details'),
                      View('DETAILS_01', 'auth.details_01'),
                      View('POST_OP1', 'auth.post_op1'),
                      View('ABOUT_01', 'auth.about_01'),
                      View('FORUM', 'main.index'),
                      View('LOG IN', 'auth.login'),
                      )
