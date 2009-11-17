# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""Vigigraph Controller"""

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from vigigraph.lib.base import BaseController
from vigigraph.model import DBSession, metadata
from vigigraph.controllers.error import ErrorController
from vigigraph.controllers.rpc import RpcController
from vigigraph import model
from repoze.what.predicates import Any, not_anonymous

__all__ = ['RootController']


class RootController(BaseController):
    """
    The root controller for the vigigraph application.
    
    All the other controllers and WSGI applications should be mounted on this
    controller. For example::
    
        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()
    
    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.
    
    """
    error = ErrorController()
    rpc = RpcController()

    @expose('index.html')
    @require(Any(not_anonymous(), msg=_("You need to be authenticated")))
    def index(self):
        """Handle the front-page."""
        return dict(page='index')

    @expose('login.html')
    def login(self, came_from=url('/')):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)
    
    @expose()
    def post_login(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.
        
        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect(url('/login', came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.
        
        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)
