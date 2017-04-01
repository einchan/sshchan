sshchan
=======

A textboard environment implemented in Python. At the moment it is a script meant to be run server-side by a user connecting to that server using ssh. It hopes to be configurable and secure.

How to Install / Dependencies
---

**Please read [`docs/sshchan-deployment.txt`](docs/sshchan-deployment.txt) for a full guide on setting up a functional, safe chan.**

	git clone http://neetco.de/chibi/sshchan.git sshchan
	cd sshchan
	python3 setup.py
That should set up the basic chan for you. From there, read the documentation [`docs/config.md`](docs/config.md) for more admin stuff.

### gui status
GUI will require `urwid` module, which is a third-party module. It can be obtained from https://pypi.python.org/pypi/urwid.

Configuration
---

The `admin.py` script helps you to configure the server. Run that and type `h` at the command prompt to get some help.

Roadmap
---

* Working urwid GUI
* Wordfilters
* Reports, banning and warnings
* File uploads via one of the pomf clones with shortened links added to post contents
* Secure admin authentication (via GPG)

Related projects
---
* undoall's [sshchan-functional](https://github.com/undo-all/sshchan-functional)
* blha303's [sshchan-web](https://github.com/blha303/sshchan-web)
