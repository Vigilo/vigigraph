# -*- coding: utf-8 -*-
"""
Suite de tests du formulaire de sélection des hôtes et groupes d'hôtes.
"""
from nose.tools import assert_equal
import transaction

from vigigraph.tests import TestController
from vigilo.models.session import DBSession
from vigilo.models.tables import SupItemGroup, Permission
from vigilo.models.demo.functions import add_supitemgroup, \
    add_host, add_host2group, add_usergroup, add_user, \
    add_supitemgrouppermission, add_usergroup_permission


class TestHostSelectionForm(TestController):
    """
    Teste le formulaire de sélection des
    hôtes et groupes d'hôtes de Vigigraph.
    """

    def setUp(self):
        """Préparation de la base de données de tests."""

        # Initialisation de la base
        super(TestHostSelectionForm, self).setUp()

        # Ajout d'un groupe d'hôtes principal
        mainhostgroup = add_supitemgroup(u'mhg', None)

        # Ajout d'un premier groupe d'hôtes de second niveau
        hostgroup1 = add_supitemgroup(u'hg1', mainhostgroup)

        # Ajout d'un second groupe d'hôtes de second niveau
        hostgroup2 = add_supitemgroup(u'hg2', mainhostgroup)

        # Ajout de trois hôtes
        host1 = add_host(u'host1')
        host2 = add_host(u'host2')
        host3 = add_host(u'host3')

        # Ajout du premier hôte dans le groupe d'hôtes principal.
        add_host2group(host1, mainhostgroup)
        # Ajout du deuxième hôte dans le premier
        # groupe d'hôtes de second niveau.
        add_host2group(host2, hostgroup1)
        # Ajout du troisième hôte dans le second
        # groupe d'hôtes de second niveau.
        add_host2group(host3, hostgroup2)

        # Ajout de trois groupes d'utilisateurs
        poweruser_group = add_usergroup(u'powerusers')
        user_group = add_usergroup(u'users')
        visitor_group = add_usergroup(u'visitor')

        # Ajout de trois utilisateurs
        add_user(u'poweruser', u'some.power@us.er',
            u'Power User', u'poweruserpass', u'powerusers')
        add_user(u'user', u'some.random@us.er',
            u'User', u'userpass', u'users')
        add_user(u'visitor', u'some.visiting@us.er',
            u'', u'visitorpass', u'visitor')

        # Ajout des permissions sur le groupe d'hôtes
        # principal pour le premier groupe d'utilisateurs
        add_supitemgrouppermission(mainhostgroup, poweruser_group)

        # Ajout des permissions sur le premier groupe d'hôtes
        # secondaire pour le second groupe d'utilisateurs
        add_supitemgrouppermission(hostgroup1, user_group)

        # Ajout de la permission 'vigigraph-access' aux groupes d'utilisateurs
        perm = Permission.by_permission_name(u'vigigraph-access')
        add_usergroup_permission(poweruser_group, perm)
        add_usergroup_permission(user_group, perm)
        add_usergroup_permission(visitor_group, perm)

        # Validation des ajouts dans la base
        DBSession.flush()
        transaction.commit()

##### Premier onglet déroulant du formulaire #####

    def test_get_main_host_groups_when_allowed(self):
        """
        Récupération des groupes d'hôtes principaux avec les bons droits
        """

        # Récupération du groupe d'hôtes 'mhg' dans la base de données
        mainhostgroup = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'mhg').first()

        # Récupération des groupes d'hôtes principaux
        # accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
            '/rpc/maingroups', {
            }, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste de groupes
        # d'hôtes retournée contient bien 'mhg'
        assert_equal(
            json, {"items": [
                [mainhostgroup.name, unicode(mainhostgroup.idgroup)]
            ]}
        )

        # Récupération des groupes d'hôtes principaux
        # accessibles à l'utilisateur 'user'
        response = self.app.post(
            '/rpc/maingroups', {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste de groupes
        # d'hôtes retournée contient bien 'mhg'
        assert_equal(
            json, {"items": [[
                mainhostgroup.name,
                unicode(mainhostgroup.idgroup)
            ]]}
        )

    def test_get_main_host_groups_when_not_allowed(self):
        """
        Récupération des groupes d'hôtes principaux sans les bons droits
        """

        # Récupération des groupes d'hôtes principaux
        # accessibles à l'utilisateur 'visitor'
        response = self.app.post(
            '/rpc/maingroups', {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste de groupes d'hôtes retournée est bien vide
        assert_equal(
            json, {"items": []}
        )

##### Deuxième onglet déroulant du formulaire #####

    def test_get_host_groups_when_allowed(self):
        """
        Récupération des groupes d'hôtes secondaires avec les bons droits
        """

        # Récupération du groupe d'hôtes 'mhg' dans la base de données
        mainhostgroup = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'mhg').first()

        # Récupération du groupe d'hôtes 'hg1' dans la base de données
        hostgroup1 = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'hg1').first()

        # Récupération du groupe d'hôtes 'hg2' dans la base de données
        hostgroup2 = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'hg2').first()

        # Récupération des groupes d'hôtes
        # accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
            '/rpc/hostgroups?maingroupid=%s' % (mainhostgroup.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste de groupes d'hôtes retournée
        # contient bien 'No subgroup', 'hg1', et 'hg2'
        assert_equal(
            json, {"items": [
                ['No subgroup', unicode(mainhostgroup.idgroup)],
                [hostgroup1.name, unicode(hostgroup1.idgroup)],
                [hostgroup2.name, unicode(hostgroup2.idgroup)],
            ]}
        )

        # Récupération des groupes d'hôtes
        # accessibles à l'utilisateur 'user'
        response = self.app.post(
            '/rpc/hostgroups?maingroupid=%s' % (mainhostgroup.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste de groupes
        # d'hôtes retournée contient bien 'hg1'
        assert_equal(
            json, {"items": [
                [hostgroup1.name, unicode(hostgroup1.idgroup)]
            ]}
        )

    def test_get_host_groups_when_not_allowed(self):
        """
        Récupération des groupes d'hôtes secondaires sans les bons droits
        """

        # Récupération du groupe d'hôtes 'mhg' dans la base de données
        mainhostgroup = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'mhg').first()

        # Récupération des groupes d'hôtes
        # accessibles à l'utilisateur 'visitor'
        response = self.app.post(
            '/rpc/hostgroups?maingroupid=%s' % (mainhostgroup.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste de groupes d'hôtes
        # retournée contient uniquement 'No subgroups'
        assert_equal(
            json, {"items": [['No subgroup', '%s'
                % (mainhostgroup.idgroup, )]]}
        )

    def test_get_host_groups_from_inexisting_main_group(self):
        """
        Récupération des groupes d'hôtes d'un groupe principal inexistant
        """

        # Récupération des groupes d'hôtes accessibles à l'utilisateur
        # 'visitor' et appartenant à un groupe principal inexistant
        response = self.app.post(
            '/rpc/hostgroups?maingroupid=6666666', {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste de groupes d'hôtes
        # retournée contient uniquement 'No subgroups'
        assert_equal(
            json, {"items": [['No subgroup', '6666666']]}
        )

##### Troisième onglet déroulant du formulaire #####

    def test_get_hosts_when_allowed(self):
        """
        Récupération des hôtes avec les bons droits
        """

        # Récupération du groupe d'hôtes 'mhg' dans la base de données
        mainhostgroup = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'mhg').first()

        # Récupération du groupe d'hôtes 'hg1' dans la base de données
        hostgroup1 = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'hg1').first()

        # Récupération du groupe d'hôtes 'hg2' dans la base de données
        hostgroup2 = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'hg2').first()

        # Récupération des hôtes du groupe 'mhg'
        # accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
            '/rpc/hosts?othergroupid=%s' % (mainhostgroup.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste d'hôtes retournée contient bien 'host1'
        assert_equal(
            json, {"items": [
                ['host1', unicode(mainhostgroup.idgroup)],
            ]}
        )

        # Récupération des hôtes du groupe 'hg1'
        # accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
            '/rpc/hosts?othergroupid=%s' % (hostgroup1.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste d'hotes retournée contient bien 'host2'
        assert_equal(
            json, {"items": [
                ['host2', unicode(hostgroup1.idgroup)],
            ]}
        )

        # Récupération des hôtes du groupe 'hg1'
        # accessibles à l'utilisateur 'user'
        response = self.app.post(
            '/rpc/hosts?othergroupid=%s' % (hostgroup1.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste d'hôtes retournée contient bien 'host2'
        assert_equal(
            json, {"items": [
                ['host2', unicode(hostgroup1.idgroup)],
            ]}
        )

        # Récupération des hôtes du groupe 'hg2'
        # accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
            '/rpc/hosts?othergroupid=%s' % (hostgroup2.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste d'hotes retournée contient bien 'host3'
        assert_equal(
            json, {"items": [
                ['host3', unicode(hostgroup1.idgroup)],
            ]}
        )

    def test_get_hosts_when_not_allowed(self):
        """
        Récupération des hôtes sans les bons droits
        """

        # Récupération du groupe d'hôtes 'mhg' dans la base de données
        mainhostgroup = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'mhg').first()

        # Récupération du groupe d'hôtes
        # secondaire 'hg1' dans la base de données
        hostgroup1 = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'hg1').first()

        # Récupération du groupe d'hôtes
        # secondaire 'hg2' dans la base de données
        hostgroup2 = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'hg2').first()

        # Récupération des hôtes du groupe 'mhg'
        # accessibles à l'utilisateur 'user'
        response = self.app.post(
            '/rpc/hosts?othergroupid=%s' % (mainhostgroup.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste
        # d'hôtes retournée est vide
        assert_equal(
            json, {"items": []}
        )

        # Récupération des hôtes du groupe 'hg2'
        # accessibles à l'utilisateur 'user'
        response = self.app.post(
            '/rpc/hosts?othergroupid=%s' % (hostgroup2.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste
        # d'hôtes retournée est vide
        assert_equal(
            json, {"items": []}
        )

        # Récupération des hôtes du groupe 'mhg'
        # accessibles à l'utilisateur 'visitor'
        response = self.app.post(
            '/rpc/hosts?othergroupid=%s' % (mainhostgroup.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste
        # d'hôtes retournée est vide
        assert_equal(
            json, {"items": []}
        )

        # Récupération des hôtes du groupe 'hg1'
        # accessibles à l'utilisateur 'visitor'
        response = self.app.post(
            '/rpc/hosts?othergroupid=%s' % (hostgroup1.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste d'hôtes retournée est vide
        assert_equal(
            json, {"items": []}
        )

        # Récupération des hôtes du groupe 'hg2'
        # accessibles à l'utilisateur 'visitor'
        response = self.app.post(
            '/rpc/hosts?othergroupid=%s' % (hostgroup2.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste d'hôtes retournée est vide
        assert_equal(
            json, {"items": []}
        )

    def test_get_hosts_from_inexisting_secondary_group(self):
        """
        Récupération des hôtes d'un groupe secondaire inexistant
        """

        # Récupération des hôtes accessibles à l'utilisateur
        # 'visitor' et appartenant à un groupe secondaire inexistant
        response = self.app.post(
            '/rpc/hosts?othergroupid=6666666', {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste retournée est vide
        assert_equal(
            json, {"items": []}
        )

