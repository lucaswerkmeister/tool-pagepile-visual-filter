# PagePile Visual Filter

[This tool](https://pagepile-visual-filter.toolforge.org/) lets users filter a PagePile of images visually.

For more information,
please see the tool’s [on-wiki documentation page](https://commons.wikimedia.org/wiki/User:Lucas_Werkmeister/PagePile_Visual_Filter).

## Toolforge setup

On Wikimedia Toolforge, this tool runs under the `pagepile-visual-filter` tool name,
using the [Toolforge Components Service](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Deploy_your_tool) to coordinate
building a container with the [Toolforge Build Service](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Build_Service)
and then deploying that for the webservice.
The components configuration is in the `toolforge.yaml` file.

To start a new deployment,
run the following command on Toolforge after becoming the tool account:

```sh
toolforge components deployment create
```

This should automatically kick off an image build and restart the webservice at the end.

### Details and troubleshooting

To inspect the overall deployment status, run:

```sh
toolforge components deployment show
```

To debug the image build step, it may be useful to trigger an image build explicitly –
you can add `--ref=foobar` to build from the `foobar` branch instead of the `main` branch:

```sh
toolforge build start https://gitlab.wikimedia.org/toolforge-repos/pagepile-visual-filter
```

The web frontent is a Flask WSGI app using gunicorn,
and runs as the `pagepile-visual-filter` job,
which you may inspect with commands like these:

```sh
toolforge jobs show pagepile-visual-filter
toolforge jobs logs pagepile-visual-filter
kubectl get deployment pagepile-visual-filter
kubectl exec -it deployment/pagepile-visual-filter -- bash
```

### Configuration

The tool reads configuration from both the `config.yaml` file (if it exists)
and from any environment variables starting with `TOOL_*`.
The config file is more convenient for local development;
the environment variables are used on Toolforge:
list them with `toolforge envvars list`.

For the available configuration variables, see the `config.yaml.example` file.

### Update

The tool should automatically be updated on every push to the `main` branch.
To trigger a manual update, run `toolforge components deployment create` as described above.

## Local development setup

You can also run the tool locally, which is much more convenient for development
(for example, Flask will automatically reload the application any time you save a file).

```
git clone https://gitlab.wikimedia.org/toolforge-repos/pagepile-visual-filter.git
cd tool-pagepile-visual-filter
pip3 install -r requirements.txt -r dev-requirements.txt
FLASK_ENV=development flask run
```

If you want, you can do this inside some virtualenv too.

## License

The code in this repository is released under the AGPL v3, as provided in the `LICENSE` file.
