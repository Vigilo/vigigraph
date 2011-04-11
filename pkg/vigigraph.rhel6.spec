%define module  @SHORT_NAME@

Name:       vigilo-%{module}
Summary:    @SUMMARY@
Version:    @VERSION@
Release:    1%{?svn}%{?dist}
Source0:    %{name}-%{version}.tar.gz
URL:        @URL@
Group:      System/Servers
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-build
License:    GPLv2
Buildarch:  noarch

BuildRequires:   python-distribute
BuildRequires:   python-babel

Requires:   python-distribute
Requires:   vigilo-turbogears
Requires:   mod_wsgi


%description
@DESCRIPTION@
This application is part of the Vigilo Project <http://vigilo-project.org>

%prep
%setup -q
# A cause des permissions sur /var/log/httpd sur Red Hat
sed -i -e '/<IfModule mod_wsgi\.c>/a WSGISocketPrefix run/wsgi' deployment/%{module}.conf

%build
make PYTHON=%{__python} SYSCONFDIR=%{_sysconfdir}

%install
rm -rf $RPM_BUILD_ROOT
make install \
    DESTDIR=$RPM_BUILD_ROOT \
    SYSCONFDIR=%{_sysconfdir} \
    PYTHON=%{__python}

# %find_lang %{name} # ne fonctionne qu'avec les fichiers dans /usr/share/locale/


%post
/sbin/service httpd condrestart > /dev/null 2>&1 || :

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc COPYING
%dir %{_sysconfdir}/vigilo
%dir %{_sysconfdir}/vigilo/%{module}
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.conf
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.py
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.wsgi
%config(noreplace) %attr(640,root,apache) %{_sysconfdir}/vigilo/%{module}/*.ini
%{_sysconfdir}/httpd/conf.d/%{module}.conf
%dir %{_localstatedir}/log/vigilo/
%attr(750,apache,apache) %{_localstatedir}/log/vigilo/%{module}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{module}
%attr(750,apache,apache) %{_localstatedir}/cache/vigilo/sessions
%{python_sitelib}/*

