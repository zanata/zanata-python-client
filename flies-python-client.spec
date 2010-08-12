%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Summary: Python Client for Flies Server
Name: flies-python-client
Version: 0.0.2
Release: 1%{?dist}
Source0: http://jamesni.fedorapeople.org/%{name}/%{name}-%{version}.tar.gz
License: LGPLv2+
Group: Development/Tools
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch
BuildRequires: python-setuptools
BuildRequires: python-polib
Requires: python-polib

%description
Flies Python client is a client that communicate with Flies server for creating project
or iteration, retrieving info of projects, single project or single iteration.
It also provide publican support for pull or push the content with Flies server.

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

