---
title: Let's Git ready to rumble
draft: False
---
## Solving it

If found myself with a rather strange git problem. As far as I was aware,
I was tracking a remote, however when ever I git a `git pull`, my bash
prompt would show me as having commits outstanding.

``` 
[voddenr:~/repository] master(4)+i ± 
```

Looking at the commit tree, it would seem that `origin/HEAD` and
`origin/master` have not been correctly updated:

```
*   f786359 - (HEAD -> master) Merge everything together. (3 hours ago) <Richard Vodden>
|
*   51955ca - Wrote some code. (4 hours ago) <Richard Vodden>
|\
| |
| * 81e4c19 - Update readme. (4 hours ago) <Richard Vodden>
| |
| * a84e10e - wip (15 hours ago) <Richard Vodden>
|/
|
*   2dcce03 - (origin/master, origin/HEAD) Some kind of merge message. (24 hours ago) <Richard Vodden>
|\
| |
| * f1622f9 - This is quite a boring message. (24 hours ago) <Richard Vodden>
| |
| * 2bbc060 - Even more exciting message. (25 hours ago) <Richard Vodden>
| |
| * 19756aa - Exciting commit message (25 hours ago) <Richard Vodden> 
```

Executing `git remote -vv show origin` suggests all is as it should be:

```
* remote origin
  Fetch URL: https://github.com/paulgibbs/behat-wordpress-extension
  Push  URL: https://github.com/paulgibbs/behat-wordpress-extension
  HEAD branch: master
  Local branches configured for 'git pull':
    master merges with remote master
  Local ref configured for 'git push': 
    master pushes to master (up to date) 
```

However `git branch -a -vv` show's something amiss:

`git remote -a -v -v` shows:

```
* master                           ef786359 Merge everything together
  remotes/origin/HEAD              -> origin/master
```

This should show `[origin/master]` after the commit hash - which it
clearly doesn't. So whilst my master branch is set to push and pull to the
right places, its not correctly set to track `origin/master`. However when
I attempt to execute `git branch --set-upstream-to origin master` to fix
that, Git replies with `fatal: Cannot setup tracking information; starting
point 'origin/master' is not a branch.`

A quick google of that error message reveals 
[this stackoverflow
answer](https://stackoverflow.com/questions/22446446/cannot-setup-tracking-information-starting-point-origin-master-is-not-a-branch).
It would seem that `git remote set-branches --add origin master` is the answer here. After
executing it, `git remote -a -v -v` shows things are as they should be:

```
* master                 eef78635 [origin/master] Merge everything together
  remotes/origin/HEAD    -> origin/master
```

Similarly, `git remote -vv show origin` is looking better. A distinct
learning point for me is that it now reports that it's tracking - see
lines 5 and 6.

```
* remote origin
  Fetch URL: https://github.com/paulgibbs/behat-wordpress-extension
  Push  URL: https://github.com/paulgibbs/behat-wordpress-extension
  HEAD branch: master
  Remote branch:
    master tracked
  Local branches configured for 'git pull':
    master merges with remote master
  Local ref configured for 'git push': master pushes to master (up to
  date) 
```

Following a sneaky `git pull` everything in the tree is as it should be.
The pointers are all at the latest commit:

```
*   f786359 - (HEAD -> master, origin/master, origin/HEAD) Merge everything together. (3 hours ago) <Richard Vodden>
|
*   51955ca - Wrote some code. (4 hours ago) <Richard Vodden>
|\
| |
| * 81e4c19 - Update readme. (4 hours ago) <Richard Vodden>
| |
| * a84e10e - wip (15 hours ago) <Richard Vodden>
|/
|
*   2dcce03 - Some kind of merge message. (24 hours ago) <Richard Vodden>
|\
| |
| * f1622f9 - This is quite a boring message. (24 hours ago) <Richard Vodden>
| |
| * 2bbc060 - Even more exciting message. (25 hours ago) <Richard Vodden>
| |
| * 19756aa - Exciting commit message (25 hours ago) <Richard Vodden> 
```

## Recreating it.

I believe that I don't truly understand a problem unless I can re-create
it. My first attempt was to delete my local remote tracking branch with
`git branch -d -r origin/master`. This, however,
showed a much more easily diagnosed output from `git branch -a -vv`:

```
* master                 eef78635 [origin/master: gone] Merge everything together
```

Similarly `git remote -vv show origin` implies that all will fix itself
from here following a simple `git pull`:

```
* remote origin
  Fetch URL: https://github.com/paulgibbs/behat-wordpress-extension
  Push  URL: https://github.com/paulgibbs/behat-wordpress-extension
  HEAD branch: master
  Remote branch:
    master new (next fetch will store in remotes/origin)
  Local branches configured for 'git pull':
    master merges with remote master
  Local ref configured for 'git push':
    master pushes to master (up to date)
```

Next I tried `git remote set-branches origin dev` `dev` being another
brand I picked more or less at random from the remote. This looked a good
deal more promising, with ` git remote -vv show origin` showing:

``` 
* remote origin
  Fetch URL: https://github.com/paulgibbs/behat-wordpress-extension
  Push  URL: https://github.com/paulgibbs/behat-wordpress-extension
  HEAD branch: master
  Remote branch:
    refs/remotes/origin/dev stale (use 'git remote prune' to remove)
  Local branches configured for 'git pull':
    dev    merges with remote dev
    master merges with remote master
  Local ref configured for 'git push':
    master pushes to master (up to date)
```

No luck, however, as when I inspect with `git show-ref` I can see that
`origin/master` no longer exists. So right now I'm stuck. If anyone has
any suggestions as to how to re-create the issue I came across - please do
share in the comments below.


