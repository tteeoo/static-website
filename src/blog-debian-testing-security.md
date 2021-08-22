# Configuring Debian Testing With Security Updates

by Theo Henson — 2021-08-21

Recently, I switched from running [Artix Linux](https://artixlinux.org/) to [Debian](https://debian.org/) on my main desktop machine.
While I still want new packages, I like Debian more than Artix (as a project and for how it works),
hence [Debian Testing](https://wiki.debian.org/DebianTesting)—essentially rolling release Debian:
much newer than the stable branch and more stable than the unstable branch—a comfortable middle-ground for an ex-Arch user.

There's one problem: security updates take extra time to reach Debian Testing, due to the way they are delivered.
This isn't too big of a deal for most desktop users, but it is certainly good practice to configure them as I do below.

This method involves:

1. adding the unstable and experimental repositories to the package manager's sources (while making testing have a higher priority)
2. automatically running a script which checks for security vulnerabilities from those repositories whenever you run `apt update`
3. prioritizing the installation of packages which fix those updates
 
which in effect installs security updates from unstable/experimental, while keeping everything else on testing.

The Debian wiki links to a [forum thread](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=725934) on how to do this, which this post is based on.

---

Edit `/etc/apt/sources.list`, adding the following lines:

```
deb http://deb.debian.org/debian/ unstable main non-free contrib
deb-src http://deb.debian.org/debian/ unstable main non-free contrib

deb http://deb.debian.org/debian/ experimental main non-free contrib
deb-src http://deb.debian.org/debian/ experimental main non-free contrib
```

Create `/etc/apt/preferences.d/00hybrid` to set the repositories' priority:

```
Package: *
Pin: release a=testing
Pin-Priority: 800

Package: *
Pin: release a=unstable
Pin-Priority: 700

Package: *
Pin: release a=experimental
Pin-Priority: 600
```

This will make sure that if you are installing a package that testing has, it will come from testing,
even if unstable or experimental has a newer version.

Next, we'll make an exception to this priority for security updates.
Install the `debsecan` package if you don't already have it, which is used to search for fixed vulnerabilities.
Download (or copy) [this script](https://gitlab.com/anarcat/puppet/-/raw/b6bc3e3dc982abcc4100143abb6594404b1241ac/site-modules/profile/files/debsecan-apt-priority) (made by users on the aforementioned forum thread) to `/usr/local/sbin/debsecan-apt-priority` and make sure it is executable.

Create the file `/etc/apt/apt.conf.d/00debsecan` and add this line to call the script when you run `apt update`:

```
APT::Update::Pre-Invoke { "/usr/local/sbin/debsecan-apt-priority"; };
```

A welcome side effect of this configuration is that when you try to install a package which unstable has but testing doesn't, apt will grab it from unstable.
