Jx.Button.SelectorFlyout = new Class({
    Extends: Jx.Button.Flyout,

    initialize: function (options, url, hostid) {
        this.idselection = null;
        this.tree = new TreeGroup({
            title: this.options.label,
            url: url,
            hostid: hostid
        });
        options.content = this.tree.container;
        this.parent(options);
        this.tree.addEvent('select', this.selectItem.bind(this));

        // On adapte la fenêtre popup aux dépliements de l'arbre
        var adaptPopup = function(e) {
            if (!this.options.active) return;
            // On évite le scrolling dans le menu popup
            var size_x = this.content.getSize().x;
            var scroll_size_x = this.content.getScrollSize().x;
            if (scroll_size_x > size_x) {
                this.content.setStyle("width", scroll_size_x + 10);
                // 10: padding-right du div
            }
            // On adapte la bordure ombrée
            this.contentContainer.setContentBoxSize(
                    $(this.content).getMarginBoxSize());
        };
        this.tree.addEvent("branchloaded", adaptPopup.bind(this));
        this.tree.addEvent("nodedisclosed", adaptPopup.bind(this));

   },

    setItem: function (idselection, label) {
        this.idselection = idselection;
        this.setLabel(label);
        this.fireEvent("select", [idselection, label]);
    },

    selectItem: function (item) {
        this.setItem(item.options.data, item.options.label);
        this.hide();
    },

    //clicked: function (e) {
    //    if (!this.options.enabled)
    //        return;
    //    this.tree.selectGroup();
    //},

    redraw: function() {
        this.tree.redraw();
    }
});

var Toolbar = new Class({
    initialize: function () {
        this.jxtoolbar = new Jx.Toolbar({
            parent: $('toolbar')
        });

        this.global_refresh = new Jx.Button({
            tooltip: _('Globally change auto-refresh setting'),
            //image: app_path + 'images/refresh-all.png',
            image: app_path + 'images/refresh.png',
            toggle: true,
            onDown: function () {
                window.graphs.each(function (graph) {
                    graph.refresh_button.setActive(1);
                }, this.global_refresh);
            }.bind(this),
            onUp: function () {
                window.graphs.each(function (graph) {
                    graph.refresh_button.setActive(0);
                }, this.global_refresh);
            }.bind(this)
        });

        this.host_label = new Jx.Toolbar.Item(this.createLabel(_('Host:')));

        this.host_picker = new Jx.Button.SelectorFlyout({
                label: _('Select a host'),
                tooltip: _('Click me to select another host'),
            },
            app_path + 'rpc/hosttree',
            null
        );

        this.host_picker.addEvent("select", function() {
            var idselection = this.host_picker.idselection;
            if (this.graph_picker.tree.options.hostid != idselection) {
                this.graph_picker.tree.options.hostid = idselection;
                this.graph_picker.tree.redraw();
                this.graph_picker.setItem(null, this.graph_picker.options.label);
            }
            this.show_nagios.setEnabled(1);
            this.graph_picker.setEnabled(1);
        }.bind(this));

        this.show_nagios = new Jx.Button({
            //label: _('Nagios page'),
            tooltip: _('Display Nagios page for the selected host'),
            image: app_path + 'images/nagios-16.png',
            toggle: false,
            enabled: false,
            onClick: function () {
                var uri = new URI(
                    app_path + 'nagios/' +
                    encodeURIComponent(this.host_picker.getLabel()) +
                    '/cgi-bin/status.cgi'
                );
                uri.setData({
                    host: this.host_picker.getLabel(),
                    style: 'detail',
                    supNav: 1
                });
                window.open(uri.toString());
            }.bind(this)
        })

        this.graph_label = new Jx.Toolbar.Item(this.createLabel(_('Graph:')));

        this.graph_picker = new Jx.Button.SelectorFlyout({
                label: _('Select a graph'),
                tooltip: _('Click me to select another graph'),
                enabled: false
            },
            app_path + 'rpc/graphtree',
            null
        );

        this.graph_picker.addEvent("select", function (idselection, label) {
            if (idselection !== null) {
                //this.show_graph.setEnabled(1);
                new Graph(
                    {autoRefresh: this.global_refresh.isActive() ? 1 : 0},
                    this.host_picker.getLabel(),
                    this.graph_picker.getLabel()
                );
            }
        }.bind(this));

        this.show_graph = new Jx.Button({
            label: _('Graph'),
            tooltip: _('Display the contents of the selected graph'),
            toggle: false,
            enabled: false,
            onClick: function () {
                 new Graph(
                    {autoRefresh: this.global_refresh.isActive() ? 1 : 0},
                    this.host_picker.getLabel(),
                    this.graph_picker.getLabel()
                );
            }.bind(this)
        })

        // Remplissage de la barre d'outils
        this.jxtoolbar.add(this.global_refresh);
        this.jxtoolbar.add(this.show_nagios);
        this.jxtoolbar.add(new Jx.Toolbar.Separator());
        this.jxtoolbar.add(this.host_label); // à supprimer ?
        this.jxtoolbar.add(this.host_picker);
        this.jxtoolbar.add(new Jx.Toolbar.Separator());
        this.jxtoolbar.add(this.graph_label); // à supprimer ?
        this.jxtoolbar.add(this.graph_picker);
        //this.jxtoolbar.add(this.show_graph);

        // Vérification de la date de dernière modification en base, et
        // rechargement des arbres le cas échéant
        this.loadtime = new Date();
        this.req_expiration = new Request.JSON({
            method: "get",
            url: app_path + "rpc/dbmtime",
            onSuccess: function(result){
                if (!result) return;
                var mtime = Date.parse(result.mtime);
                if ((toolbar.loadtime - mtime) >= 0) return;
                // la base a changé, on recharge les arbres
                toolbar.host_picker.tree.redraw();
                toolbar.graph_picker.tree.redraw();
                // @todo: En théorie on devrait aussi vérifier que l'élément
                // sélectionné existe dans l'arbre, mais c'est un peu compliqué
                // avec le chargement dynamique. Il faudrait faire une requête
                // spécifique
                toolbar.loadtime = new Date();
            }
        });
        this.req_expiration.send.periodical(30 * 1000, this.req_expiration);
    },

    // Retourne un objet opaque qui possède un label,
    // et peut être ajouté à une Jx.Toolbar via Jx.Toolbar.Item.
    createLabel: function (label) {
        var container, content, span;

        container = new Element('div', {'class': 'jxButtonContainer'});
        content = new Element('span', {'class': 'jxButtonContent'});
        span = new Element('span', {
            'class': 'jxButtonLabel',
            text: label
        });
        span.setStyles({cursor: 'default'});

        span.inject(content);
        content.inject(container);

        return container;
    },

    // Vérifie si la base a changé, et recharge les sélecteurs en conséquence
    checkExpiration: function() {
        if (!this.req_expiration) { // ne creer qu'une instance
            this.req_expiration = new Request.JSON({
                method: "get",
                url: app_path + "rpc/dbmtime",
                onSuccess: function(result){
                    if (!result) return;
                    var mtime = Date.parse(result.mtime);
                    if ((toolbar.loadtime - mtime) >= 0) return;
                    // la base a changé, on recharge les arbres
                    if (toolbar.host_picker.idselection) {
                        toolbar.host_picker.tree.redraw();
                    }
                    if (toolbar.graph_picker.idselection) {
                        toolbar.graph_picker.tree.redraw();
                    }
                    // @todo: En théorie on devrait aussi vérifier que
                    // l'élément sélectionné existe dans l'arbre, mais c'est un
                    // peu compliqué avec le chargement dynamique. Il faudrait
                    // faire une requête spécifique
                    toolbar.loadtime = new Date();
                }
            });
        }
        this.req_expiration.send();
    }
});

toolbar = null;
window.addEvent('load', function () {
    window.toolbar = new Toolbar();
});
