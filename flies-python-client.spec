%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name: flies-python-client
Version: 0.3.0
Release: 1%{?dist}
Summary: Python Client for Flies Server

Group: Development/Tools
License: LGPLv2+
URL: http://code.google.com/p/flies/wiki/FliesPythonClient
Source0: http://jamesni.fedorapeople.org/%{name}/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch: noarch
BuildRequires: python-setuptools
Requires: python-polib
Requires: python-httplib2
%if 0%{?fedora} < 13
BuildRequires: python-devel
Requires: python-httplib2
%endif

%description
Flies Python client is a client that communicate with Flies server.

%prep
%setup -q

%build
python setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root, -)
%doc README COPYING COPYING.LESSER
%{python_sitelib}/*
%{_bindir}/*

%changelog
* Thu Oct 21 2010 James Ni <jni@redhat.com> - 0.3.0-1
- Fix the issues in extension support and update translation command

* Thu Oct 21 2010 James Ni <jni@redhat.com> - 0.2.0-1
- Add extension support and update translation command

* Wed Sep 29 2010 James Ni <jni@redhat.com> - 0.1.0-1
- Modify the user configuration file and command line options

* Wed Sep 08 2010 James Ni <jni@redhat.com> - 0.0.6-1
- Try to resolve the dependency of python-setuptools

* Mon Sep 06 2010 James Ni <jni@redhat.com> - 0.0.5-2
- Add requires for python-polib

* Tue Aug 31 2010 James Ni <jni@redhat.com> - 0.0.5-1
- Rename resservice in flieslib/__init__.py to docservice

* Mon Aug 30 2010 James Ni <jni@redhat.com> - 0.0.4-1
- Rename module resservice to docservice
- Set encode to UTF-8 when generate hash value for msgid of the po file
- Change functions in flies.py to private
- Fix a exception in projectservice and exception handler in flies
- Provide more "readable" output for httplib2 connection error

* Wed Aug 25 2010 James Ni <jni@redhat.com> - 0.0.3-3
- Add an error handler for list command
- Add cache to httplib2 

* Mon Aug 23 2010 James Ni <jni@redhat.com> - 0.0.3-2
- Include the example configuration file
- Add dependency of python-httplib2 for fedora 12(and less) 

* Fri Aug 20 2010 James Ni <jni@redhat.com> - 0.0.3-1
- Modify the __inin__.py for importing the module
- Modify the spec file and fliesrc.txt
- Rewrite README file for giving detail of commands and how to implement flies-python-lib in program
- Add COPYING.LESSER 

* Mon Aug 16 2010 James Ni <jni@redhat.com> - 0.0.2-2
- remove shebang from flies.py 

* Fri Aug 13 2010 James Ni <jni@redhat.com> - 0.0.2-1
- initial package (#623871)
