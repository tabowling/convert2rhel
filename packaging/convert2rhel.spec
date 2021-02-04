%if 0%{?rhel} && 0%{?rhel} <= 7
%{!?__python2: %global __python2 /usr/bin/python2}
%global __python %{__python2}
%global python_pkgversion %{nil}
%else
%{!?__python3: %global __python3 /usr/bin/python3}
%global __python %{__python3}
%global python_pkgversion %{python3_pkgversion}
%endif

Name:           convert2rhel
Version:        0.16
Release:        1%{?dist}
Summary:        Automates the conversion of RHEL derivative distributions to RHEL

License:        GPLv3+
URL:            https://github.com/oamg/convert2rhel
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python%{python_pkgversion}-devel
BuildRequires:  python%{python_pkgversion}-setuptools
BuildRequires:  python%{python_pkgversion}-six
%if 0%{?rhel} && 0%{?el8}
BuildRequires:  python3-pexpect
%endif
%if 0%{?rhel} && 0%{?rhel} <= 7
BuildRequires:  pexpect
%endif

Requires:       rpm
Requires:       python%{python_pkgversion}
Requires:       python%{python_pkgversion}-setuptools
Requires:       python%{python_pkgversion}-six
%if 0%{?rhel} && 0%{?el8}
Requires:       dnf
# dnf-utils includes yumdownloader we use
Requires:       dnf-utils
Requires:       grubby
Requires:       python3-pexpect
%endif
%if 0%{?rhel} && 0%{?rhel} <= 7
Requires:       yum
# yum-utils includes yumdownloader we use
Requires:       yum-utils
Requires:       pexpect
%endif


%description
The purpose of the convert2rhel tool is to provide an automated way of
converting the installed other-than-RHEL OS distribution to Red Hat Enterprise
Linux (RHEL). The tool replaces all the original OS-signed packages with the
RHEL ones. Available are conversions of CentOS 6/7/8 and Oracle Linux 6/7/8 to
the respective major version of RHEL.

%prep
%setup -q

%build
%{__python} setup.py build
%{__python} setup.py build_manpage

# Do not include unit tests in the package
rm -rf build/lib/%{name}/unit_tests
# Do not include the man building script
rm -rf build/lib/man

%install
%{__python} setup.py install --skip-build --root %{buildroot}

rm -rf %{buildroot}%{python_sitelib}/%{name}/data

# Create the /usr/share/convert2rhel/ directory for storing data like GPG keys and config files
install -d %{buildroot}%{_datadir}/%{name}/
cp -a build/lib/%{name}/data/version-independent/. \
      %{buildroot}%{_datadir}/%{name}
cp -a build/lib/%{name}/data/%{rhel}/%{_arch}/. \
      %{buildroot}%{_datadir}/%{name}

# Create a directory into which convert2rhel downloads RHSM-related packages
install -d %{buildroot}%{_datadir}/%{name}/subscription-manager/

# Create a temporary directory /var/lib/convert2rhel/ - used mainly for backing up files during the conversion
install -d %{buildroot}%{_sharedstatedir}/%{name}/
install -d %{buildroot}%{_sharedstatedir}/%{name}/backup/
install -d %{buildroot}%{_sharedstatedir}/%{name}/rhsm/

install -d -m 755 %{buildroot}%{_mandir}/man8
install -p man/%{name}.8 %{buildroot}%{_mandir}/man8/

%files

%if 0%{?el6} && 0%{?rhel}
# without this on CentOS/OL 6, rpmlint gives an error "E: files-attr-not-set"
%defattr(-,root,root,-)
%endif

%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_sharedstatedir}/%{name}/
%{python_sitelib}/%{name}*

%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc README.md
%attr(0644,root,root) %{_mandir}/man8/%{name}.8*

%changelog
* Thu Feb 4 2021 Michal Bocek <mbocek@redhat.com> 0.16-1
- Not requiring users to download redhat-release and subscription-manager with
  its dependencies prior the conversion when using RHSM.
- Remove subscription-manager dependencies from the convert2rhel spec file by
  installing subscription-manager through yum/dnf instead of rpm.
- The --variant option for choosing RHEL variant was broken. Instead of fixing
  it we remove all the related code. The system is always converted to RHEL
  Server variant in case of RHEL 6 and 7. RHEL 8 has no variants. Using the
  --variant option now prints a warning.
- Update Red Hat EULA to the 2019 version.
- Messages of importance are printed in color in the terminal.
- When printing a list of packages, we print the package vendor by default, or
  the packager when the vendor information is not available.

* Fri Jan 8 2021 Michal Bocek <mbocek@redhat.com> 0.15-1
- add missing CentOS 8 packages to be removed prior the conversion

* Thu Dec 17 2020 Michal Bocek <mbocek@redhat.com> 0.14-1
- fix same version kernel not being replaced silently
- not renaming the original system repofiles anymore
- fix printing package installation repo with dnf
- warn users if same repo in both enable/disablerepo options
- improve manpage/help for the enable/disablerepo options

* Fri Nov 13 2020 Michal Bocek <mbocek@redhat.com> 0.13-1
- allow conversions of CentOS and Oracle Linux 8
- fix "TypeError: execve()" py2.6-related error when calling external commands
- remove unused code related to using offline snapshot or RHEL repositories
- remove all Red Hat Network (RHN)-related code as RHN has been shut down
- set POSIX/C locale at the start of running the tool
- remove python-syspurpose dependency from spec - not available on OL 7 and 8
- replace the word blacklist with exclude/excluded
- clearing yum versionlock that could cause the conversion to fail
- printing rpm files that were modified during the conversion
- minor UX improvements and test infrastructure improvements

* Wed Aug 19 2020 Michal Bocek <mbocek@redhat.com> 0.12-1
- require --enablerepo with --disable-submgr
- fix failing conversions if gpgcheck=1 not in used custom repos
- always logging debug info to the log file
- unnecessary backup of kernel packages is not being performed
- add missing python-setuptools dependency on RHEL 6 to a spec file
- unregister from RHN Classic if in use
- change a temporary folder path from /tmp/convert2rhel/ to /var/lib/convert2rhel
- add the ability to specify custom RHSM URL
- unsubscribe from RHSM during a rollback
- drop the support for conversions of RHEL 5
- make sure that RHEL kernel has been installed correctly during the conversion
- fix parsing RHSM output due to its change in RHEL 7.8
- fix stopping the convert2rhel execution when not running as root
- the convert2rhel.log file is not being overwritten but appended
- do not traceback when intentionally stopping the conversion
- do not ask for subscription SKU pool IDs when activation key is used

* Tue May 12 2020 Michal Bocek <mbocek@redhat.com> 0.11-1
- updated license in spec files from GPLv3 to GPLv3+
- set up automated pylint and unit test coverage checks in GitHub
- removed packit smoke test
- fixed packit configuration for downstream release proposals

* Wed May 06 2020 Michal Bocek <mbocek@redhat.com> 0.10-1
- fixed rpm dependencies
- blacklisted kmod-kvdo causing a transaction failure on CentOS 7
- convert2rhel exits with 0 on a help message
- added packit configuration for Copr builds and unit testing on a PR

* Fri Dec 13 2019 Michal Bocek <mbocek@redhat.com> 0.9-1
- basic rollback capability up to the point before replacing all pkgs
- added basic system tests running on CentOS 5/6/7 Vagrant boxes
- unit tests can be run now in CentOS 5/6/7 Docker images
- improved handling of kernel installation corner cases
- added possibility to upgrade i386 OL5
- added --debug option
- license changed from GPLv2 to GPLv3
- autogenerating manpage
- collecting output of 'rpm -Va' before the conversion
- added possibility to use custom repositories instead of RHSM
- removed bundled rpms and repomapping for the public release

* Fri Nov 10 2017 Michal Bocek <mbocek@redhat.com> 0.8-1
- added support for conversion from CentOS/OL 5 to RHEL 5
- the oldest supported version is CentOS/OL 5.6

* Fri Mar 31 2017 Michal Bocek <mbocek@redhat.com> 0.7-1
- remove shebang from all the python scripts
- update spec to create arch specific rpms
- move all the tool data into /usr/share/convert2rhel/
- remove ppc64 RHEL 6 data - CentOS 6 and OL 6
  were not released for this arch
- create new SystemReleaseFile class for handling
  /etc/system-release
- do not print traceback on keyboard interrupt
- move initializing Red Hat GPG key fingerprint variable
  from main to gpgkey.py
- update configs to add centos-release* to blacklist

* Wed Jul 20 2016 Michal Bocek <mbocek@redhat.com> 0.6-1
- Code refactored and split into new files
- Added support for CentOS/OL 6 to RHEL 6 conversion
- Created 'framework' for unit tests
- Added logging to a file

* Wed Jun 15 2016 Michal Bocek <mbocek@redhat.com> 0.5-1
- The tool renamed to convert2rhel.
- All the original kernels are removed during the conversion now.
- Added man page.
- EULA needs to be accepted before the conversion.
- Packages are filtered per signature, not per vendor.
- Added support for conversions from Oracle Linux 7 to RHEL 7.
- Added support for --auto-attach, --activationkey and --org
  subscription-manager arguments.

* Mon May 09 2016 Michal Bocek <mbocek@redhat.com> 0.4-1
- Added both interactive and cmd line option for choosing RHEL variant.
- Added autodetection of platform architecture.
- Implemented handling of unsuccessful subscription attachment.
- Added a config file for each supported distribution.
- Added possibility to blacklist conflicting pkgs.

* Thu Apr 28 2016 Michal Bocek <mbocek@redhat.com> 0.3-1
- Added determining appropriate RHEL repository to use for upgrade.

* Mon Apr 25 2016 Michal Bocek <mbocek@redhat.com> 0.2-1
- Added dark matrix data

* Tue Apr 19 2016 Michal Bocek <mbocek@redhat.com> 0.1-1
- Initial RPM release
