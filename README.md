# PagePile Visual Filter

[This tool](https://pagepile-visual-filter.toolforge.org/) lets users filter a PagePile of images visually.

For more information,
please see the tool’s [on-wiki documentation page](https://commons.wikimedia.org/wiki/User:Lucas_Werkmeister/PagePile_Visual_Filter).

## Toolforge setup

On Wikimedia Toolforge, this tool runs under the `pagepile-visual-filter` tool name.
Source code resides in `~/www/python/src/`,
a virtual environment is set up in `~/www/python/venv/`,
logs end up in `~/uwsgi.log`.

If the web service is not running for some reason, run the following command:
```
webservice start
```
If it’s acting up, try the same command with `restart` instead of `start`.
Both should pull their config from the `service.template` file in the source code directory.

To update the service, run the following commands after becoming the tool account:
```
webservice shell
cd ~/www/python/src
git fetch
git diff @ @{u} # inspect changes
git merge --ff-only @{u}
webservice restart
```

If there were any changes in the Python environment (e.g. new dependencies),
add the following steps before the `webservice restart`:
```
webservice shell
source ~/www/python/venv/bin/activate
pip-sync ~/www/python/src/requirements.txt
```

## Local development setup

You can also run the tool locally, which is much more convenient for development
(for example, Flask will automatically reload the application any time you save a file).

```
git clone https://gitlab.wikimedia.org/toolforge-repos/pagepile-visual-filter.git
cd tool-pagepile-visual-filter
pip3 install -r requirements.txt
FLASK_ENV=development flask run
```

If you want, you can do this inside some virtualenv too.

## License

The code in this repository is released under the AGPL v3, as provided in the `LICENSE` file.
