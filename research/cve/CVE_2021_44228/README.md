# Apache Log4j CVE-2021-44228

## Background

AKA: *Log4Shell*

[CVE-2021-44228](https://nvd.nist.gov/vuln/detail/CVE-2021-44228)

Caused and categorised by "Improper Input Validation"

Apache Log4j library [download](https://archive.apache.org/dist/logging/log4j/)

Vulnerable version: [apache-log4j-2.14.1](https://archive.apache.org/dist/logging/log4j/2.14.1/apache-log4j-2.14.1-bin.zip)

Fixed version: [apache-log4j-2.15.0](https://archive.apache.org/dist/logging/log4j/2.15.0/apache-log4j-2.15.0-bin.zip)

Tutorial: [https://nakedsecurity.sophos.com/2021/12/13/log4shell-explained-how-it-works-why-you-need-to-know-and-how-to-fix-it/](https://nakedsecurity.sophos.com/2021/12/13/log4shell-explained-how-it-works-why-you-need-to-know-and-how-to-fix-it/)

## Log4j Lookup Feature

[Log4j Lookups](https://logging.apache.org/log4j/2.x/manual/lookups.html)

## Trouble shooting

- Keep getting Error in VSCode: Java server has crashed 5 times in the last 3 minutes
> Solution: F1 -> Java: Clean the Java Language Server Workspace -> Restart & Delete

## Debugging notes

PatternLayout.toSerializable
ln: 344
iteration 8 goes bang!!!

