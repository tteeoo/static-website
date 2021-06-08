# Creating a Self-Hosted Git Server With a Simple Front-End 

by Theo Henson — 2021-06-08

## Introduction

This article will walk you through the process of setting up a Git server which can be pushed to, cloned from, and browsed, using a static site generator called [stagit](https://codemadness.org/stagit.html) as a front-end.
You can see my stagit-made site at [git.theohenson.com](https://git.theohenson.com).

Requirements:

* Some sort of Linux server (it could be as simple as a Raspberry Pi, or a VPS).
* At least a basic understanding of Git and the shell.
* A way to serve HTML files.

## Access via SSH

Git offers a number of protocols to push, pull, and clone repositories. Basic functionality can be achieved simply with SSH.

First, create a new `git` user on your server (do not give it root privileges).
Set its home directory to `/srv/git`, which is where your repositories will be stored.
Presuming that you are using SSH to interact with this server, you should already have it set up.
If you use SSH keys for authentication, configure them for the `git` user now.

Next, as the `git` user, initialize a new bare repository called "test" with `git init --bare test.git`.
A "bare" repository is essentially a directory that only stores configuration data and file changes, but not files themselves (i.e., it lacks a working tree).
The contents of the typical `.git` subdirectory are located in the top level of each bare repository.
This is desirable for a server, as no one will be editing files on it.

On your development computer, attempt to clone the repository with `git clone ssh://git@<server ip>/srv/git/test.git`.
Create a file, add it, commit, and you should be able to push.

To recap what we've done so far, these commands should have been ran on your server:

```
# useradd git -d /srv/git -m
# passwd git
# su git

$ cd /srv/git
$ git init --bare test.git
```

Then, on your development machine:

```
$ git clone ssh://git@<server ip>/srv/git/test.git
$ cd test
$ open test
$ git add test
$ git commit -m "Initial commit"
$ git push
```

This is the basic functionality of Git, although there are still two key features to implement: unauthenticated cloning, and a front-end.

## Unauthenticated Cloning

With our current setup, only people who have the `git` user's SSH credentials can read and write to the server's repositories.
If you want anyone to be able to clone a repository (but not be able to push), some extra steps are required.

We will need to make another way to access the server, other than SSH: the Git daemon.
Assuming you're using systemd on your server (if you aren't then you should be able to figure this step out), create the file `/etc/systemd/system/git-daemon.service` and enter the following:

```
[Unit]
Description=Start Git Daemon

[Service]
ExecStart=/usr/bin/git daemon --reuseaddr --base-path=/srv/git/ /srv/git/
Restart=always
RestartSec=500ms
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=git-daemon
User=git
Group=git

[Install]
WantedBy=multi-user.target
```

Start the daemon and enable it with the command `systemctl enable --now git-daemon`.
Inside of the directory for each repository you want to be publicly accessible, create the file `git-daemon-export-ok` (it does not need any content), which tells Git it's allowed to serve that repository.
You will also need to make your router forward the port `9418` to your server.

Anyone can now clone your test repository from above with the URL `git://<server ip>/test.git`, but only you can push with `ssh://git@<server ip>/srv/git/test.git`.

## Stagit as a Simple Front-End

Stagit, from [codemadness.org](https://codemadness.org/stagit.html), is a static site generator for Git repositories. It is free and open-source, released under the MIT License.
It creates a simple website displaying commit information, files, and more.

Before setting up stagit, we can add some metadata to our repository. Inside the bare repo, create the files `description`, and `owner`, filled with a short description of the repository, and your name, respectively.
Then create the file `url` with the public cloning link (`git://<server ip>/test.git`). All of this information will be read and displayed by stagit.

Install stagit by cloning it from `git://git.codemadness.org/stagit`, `cd`ing, and running `make install` as root.
Now, create a directory which will house the website's files. `/srv/stagit` is used in this guide.
Inside that directory, make the file `create.sh` as follows:

```
#!/bin/sh
# makes an index and static pages in $curdir for each repository directory in $reposdir.

# path must be absolute
reposdir="/srv/git"
curdir="/srv/stagit"

# make index
stagit-index "${reposdir}/"*/ > "${curdir}/index.html"

# make files per repo
for dir in "${reposdir}/"*/; do

        # strip .git suffix
        r=$(basename "${dir}")
        d=$(basename "${dir}" ".git")
        printf "%s... " "${d}"

        mkdir -p "${curdir}/${d}"
        cd "${curdir}/${d}" || continue
        stagit -c ".cache" "${reposdir}/${r}"

        # symlinks
        ln -sf log.html index.html
        ln -sf ../style.css style.css
        ln -sf ../logo.png logo.png
        ln -sf ../favicon.png favicon.png

        echo "done"
done
```

Make sure your repository is on the right branch, then run this script to create the website files in `/srv/stagit`, and again each time you create a new repository in `/srv/git`.

In order for the website to update when you push to your git server, we will create a hook for the repository.
Make a file called `post-receive` in the `hooks` directory of your repo (`/srv/git/test.git/hooks/post-receive`) and ensure it is executable with `chmod +x`:

```
#!/bin/sh

reponame="test"

reposdir="/srv/git"
curdir="/srv/stagit"

# detect git push -f
force=0
while read -r old new ref; do
        hasrevs=$(git rev-list "$old" "^$new" | sed 1q)
        if test -n "$hasrevs"; then
                force=1
                break
        fi
done

# remove commits and .cache on git push -f
if test "$force" = "1"; then
        rm -rf "${curdir}/${reponame}/.cache" "${curdir}/${reponame}/commits"
fi

# make index
stagit-index "${reposdir}/"*/ > "${curdir}/index.html"

cd "${curdir}/${reponame}"
stagit -c ".cache" "${reposdir}/${reponame}.git"
```

You will need to create this hook in each new repository; remember to change the value of `$reponame`.

To review, when you want to create a new repository you will need to:

* Run `git init --bare <repo name>.git` in `/srv/git`.
* Create the files `git-daemon-export-ok`, `description`, `owner`, and `url`, filling in the appropriate information.
* Copy the `post-receive` script into the `hooks` directory of the repo, and change it to use the correct repository name.
* Make sure the repo is on the right branch, then `cd` over to `/srv/stagit` and run the `create.sh` script.

### Serving the Website

To be able to view the website you will need a web server, but setting one up is out of the scope of this article.
Chances are, you already have a system for serving HTML files, and if you do, it's just a matter of pointing your server at `/srv/stagit`.

## Conclusion

All and all, the process of creating a Git server with a front-end is fairly simply, although the amount of setup could be intimidating.
I hope the process this guide describes has helped you learn more about Git, as it did for me.
