# GitHub Actions Lab

Lab consists of a docker GitHub runner and a docker exploit Linux host.

**Build**

To build the lab cd into `docker-github` directory and run `docker compose build`.

**GitHub Runner**

The GitHub runner requires the following environment variables being set

`GITHUB_TOKEN` - GitHub Token with repo level privileges

`GITHUB_ACTION_RUNNER_TOKEN` - Token provived by GitHub when configuring the self hosted runner

Start the GitHub runner container with command `docker compose run gh_runner`.

**Exploit Linux Host**

Start the exploit Linux Docker container with command `docker compose run -i exploit`. This will provide you with an interactive shell.

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

## References

- [GitHub Actions Security Vulnerability Blog](https://cycode.com/blog/github-actions-vulnerabilities/)
- [Security Hardening for GitHub Actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Docker GitHub Runner](https://dev.to/pwd9000/create-a-docker-based-self-hosted-github-runner-linux-container-48dh)
