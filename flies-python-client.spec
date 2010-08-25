%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name: flies-python-client
Version: 0.0.3
Release: 2%{?dist}
Summary: Python Client for Flies Server

Group: Development/Tools
License: LGPLv2+
URL: http://code.google.com/p/flies/wiki/FliesPythonClient
Source0: http://jamesni.fedorapeople.org/%{name}/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch: noarch
BuildRequires: python-setuptools
BuildRequires: python-polib
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
