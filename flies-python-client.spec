%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name: flies-python-client
Version: 0.8.0
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
* Mon Mar 07 2011 James Ni <jni@redhat.com> - 0.8.0
- Stable release

* Wed Feb 23 2011 James Ni <jni@redhat.com> - 0.7.6-1
- Rename the command line option, add a Logger class for better output, set copytrans default value to true, make the
  extensions to a list of gettext and comment. 

* Tue Feb 22 2011 James Ni <jni@redhat.com> - 0.7.4-1
- Fix issue 245:stop processing when type 'n', Add version service, rename the command line option and help info, add
  InternalServerError

* Mon Feb 21 2011 James Ni <jni@redhat.com> - 0.7.3-1
- Fix issue 244, issue 245, issue 247 and issue 30, add command list for 'flies publican', rewrite the README

* Fri Feb 18 2011 James Ni <jni@redhat.com> - 0.7.2-1
- Rename the gettextutil to publicanutil, Remove the translator from textFlowTarget, Add more help info

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 24 2011 James Ni <jni@redhat.com> - 0.7.1-1
- Fix typo and make help more user-friendly

* Mon Jan 24 2011 James Ni <jni@redhat.com> - 0.7.0-1
- Add copyTrans option to client

* Tue Jan 04 2011 James Ni <jni@redhat.com> - 0.6.1-1
- Add exception handler for empty extensions

* Wed Dec 29 2010 James Ni <jni@redhat.com> - 0.6.0-1
- Create pot file with content retrieved from server, user could choose keep or delete the content on the flies
  server when pushing publican

* Tue Dec 07 2010 James Ni <jni@redhat.com> - 0.5.1-1
- Fix bugs and add some log info for python client

* Thu Dec 02 2010 James Ni <jni@redhat.com> - 0.5.0-1
- Make the script compatible with python 2.4

* Mon Nov 29 2010 James Ni <jni@redhat.com> - 0.4.0-1
- Add command line option for translation folder and importPo, read and write multiple locale, read the flies.xml first

* Wed Oct 27 2010 James Ni <jni@redhat.com> - 0.3.2-1
- Fix a typo in project creation

* Fri Oct 22 2010 James Ni <jni@redhat.com> - 0.3.1-1
- Fix an issue in project creation

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
