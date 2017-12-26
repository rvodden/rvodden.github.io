--- 
published: false
--- 
# Let's have a proper Bash at this

Much of the pipeline I work on is held together, at least a little bit,
with bash scripts. Bash scripting gets a very bad rep, mostly for being
unpredictable. I believe this is largely undeserved. There are some neat
tricks which help make bash scripts significantly more reliable.
Production ready if you like. So I'm going to take you through some of the
ways I like to make my bash scripts a bit more robust.

## Example

Let's work through a typical example. Let's say I've got a number of
services, and I need to generate a password for each of them, and store it
in a copy of Vault. It doesn't matter if you're not familiar with Vault.
For the purposes of this article, its a tool which lets you store
key-value pairs at locations. It has a command line client which allows
reading and writing of these values.

So I have a list of services, one to a line, in a file called
`services.lst`. I might write a short script like this one to generate
a password for each one and stick it in vault. 

```sh
#!/usr/bin/env bash

ACCOUNT=$1 ENVIRONMENT=$2

echo iptmimartdb |while read rec
do
    service=$(echo $rec |cut -f1)
    echo $service
    db_pass=$(pwgen)
    vault write secret/$1-$2/MI/${service}/db_pass value=$db_pass
done
```

This script will work as designed, but I think there are a number of ways
in which this shouldn't be considered "production ready".

1. Input parameters are not validated

### Input parameters are not validated
