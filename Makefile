NAME := vigigraph

all: build

include buildenv/Makefile.common
MODULE := $(NAME)
CODEPATH := $(NAME)
EPYDOC_PARSE := vigigraph\.controllers

install: build install_python install_data
install_pkg: build install_python_pkg install_data

install_python: $(PYTHON)
	$(PYTHON) setup.py install --record=INSTALLED_FILES
install_python_pkg: $(PYTHON)
	$(PYTHON) setup.py install --single-version-externally-managed --root=$(DESTDIR) --record=INSTALLED_FILES

install_data: deployment/logrotate.conf
	# Permissions de la conf
	chmod a+rX -R $(DESTDIR)$(SYSCONFDIR)/vigilo/$(NAME)
	[ `id -u` -ne 0 ] || chgrp $(HTTPD_USER) $(DESTDIR)$(SYSCONFDIR)/vigilo/$(NAME)/*.ini
	chmod 600 $(DESTDIR)$(SYSCONFDIR)/vigilo/$(NAME)/*.ini
	# Apache
	mkdir -p $(DESTDIR)$(HTTPD_DIR)
	ln -f -s $(SYSCONFDIR)/vigilo/$(NAME)/$(NAME).conf $(DESTDIR)$(HTTPD_DIR)/
	echo $(HTTPD_DIR)/$(NAME).conf >> INSTALLED_FILES
	mkdir -p $(DESTDIR)/var/log/vigilo/$(NAME)
	install -m 644 -p -D deployment/logrotate.conf $(DESTDIR)/etc/logrotate.d/$(NAME)
	# Déplacement du app_cfg.py
	mv $(DESTDIR)`grep '$(NAME)/config/app_cfg.py$$' INSTALLED_FILES` $(DESTDIR)$(SYSCONFDIR)/vigilo/$(NAME)/
	ln -s $(SYSCONFDIR)/vigilo/$(NAME)/app_cfg.py $(DESTDIR)`grep '$(NAME)/config/app_cfg.py$$' INSTALLED_FILES`
	echo $(SYSCONFDIR)/vigilo/$(NAME)/app_cfg.py >> INSTALLED_FILES
	# Cache
	mkdir -p $(DESTDIR)$(LOCALSTATEDIR)/cache/vigilo/sessions
	chmod 750 $(DESTDIR)$(LOCALSTATEDIR)/cache/vigilo/sessions
	[ `id -u` -ne 0 ] || chown $(HTTPD_USER): $(DESTDIR)$(LOCALSTATEDIR)/cache/vigilo/sessions

lint: lint_pylint
tests: tests_nose
clean: clean_python

.PHONY: install_pkg install_python install_python_pkg install_data
