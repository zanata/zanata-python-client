%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Summary: Python Client for Flies Server
Name: flies-python-client
Version: 0.0.2
Release: 1%{?dist}
Source0: http://jamesni.fedorapeople.org/%{name}/%{name}-%{version}.tar.gz
License: LGPLv2+
Group: Development/Tools
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: python-setuptools
BuildRequires: python-polib
BuildArch: noarch
URL: http://code.google.com/p/flies/wiki/FliesPythonClient

%description
Flies Python client is a client that communicate with Flies server.

%prep
%setup -q

%build
python setup.py build

%install
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root, -)
%doc README COPYING
%{_bindir}/*
%{_libdir}/*

%changelog 
* Mon Aug 16 2010 James Ni <jni@redhat.com> - 0.0.2-1
- remove shebang from flies.py 

* Fri Aug 13 2010 James Ni <jni@redhat.com> - 0.0.2-1
- initial package (#623871)
