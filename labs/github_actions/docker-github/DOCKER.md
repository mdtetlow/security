# Docker Labs Instructions

Note:
> All commands demonstrated in this lab are for posix systemd. If you're running the lab in a Windows environment then take the steps to install Docker kit for Windows and substiture the comments for equivilent Windows commands.

There are 2 Docker containers and a Docker bridge network making up this lab. Docker Compose is used to simplify deployment.

- Containers
  - A GitHub Action Self-hosted runner
  - A Linux hot connected to the same network as the Self-hosted runner
Network
  - `gh_runner_net`
  - subnet: `172.18.0.0`

## Build

```shell
$> cd ./docker-github
$> docker compose build
```

## Start Run Docker containers

### GitHub Actions self-hosted runner

**PreReq**

The following environment variables need to be set to run the GitHub Actions self-hosted runner:

| Variable | Description | Reference |
|-|-|-|
| `GITHUB_TOKEN` | GitHub Personal Access Token with repo level privileges | [how to create a GitHub Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) |
| `GITHUB_ACTION_RUNNER_TOKEN` | Token provided by GitHub when configuring the self hosted runner| [adding-self-hosted-runners](https://docs.github.com/en/actions/hosting-your-own-runners/adding-self-hosted-runners) - extract the token from the setup page |

examples:

```shell
$> export GITHUB_TOKEN=<your-github-access-token>
$> export GITHUB_ACTION_RUNNER_TOKEN=<COPIED_TOKEN>`
```

**Run Docker Container**

Start the GitHub self-hosted runner container

```shell
$> docker compose run gh_runner
```

### Bad Actor Linux Host

This container is only needed you want to experiment with the reverse-shell example.

To start the Linux host and get an interactive shell:

```shell
$> docker compose run -i exploit
```
