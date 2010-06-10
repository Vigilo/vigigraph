NAME := vigigraph

all: qooxdoo build

qooxdoo: vigigraph/public/js/vigigraph.js
vigigraph/public/js/vigigraph.js: javascript/source/class/vigigraph/Application.js
	make -C javascript build
	cp -f javascript/build/script/vigigraph.js vigigraph/public/js
	cp -rf javascript/build/resource vigigraph/public/

clean_qooxdoo:
	$(RM) vigigraph/public/js/vigigraph.js
	$(RM) -r vigigraph/public/resource
	$(RM) -r javascript/build/

install: vigigraph/public/js/vigigraph.js
	$(PYTHON) setup.py install --single-version-externally-managed --root=$(DESTDIR) --record=INSTALLED_FILES
	mkdir -p $(DESTDIR)$(HTTPD_DIR)
	ln -f -s $(SYSCONFDIR)/vigilo/$(NAME)/$(NAME).conf $(DESTDIR)$(HTTPD_DIR)/
	echo $(HTTPD_DIR)/$(NAME).conf >> INSTALLED_FILES
	install -p -m 644 -D deployment/logrotate $(DESTDIR)$(SYSCONFDIR)/logrotate.d/$(NAME)
	echo $(SYSCONFDIR)/logrotate.d/$(NAME) >> INSTALLED_FILES
	mkdir -p /var/log/vigilo/$(NAME)

include buildenv/Makefile.common

MODULE := $(NAME)
CODEPATH := $(NAME)
lint: lint_pylint
tests: tests_nose
clean: clean_python clean_qooxdoo
