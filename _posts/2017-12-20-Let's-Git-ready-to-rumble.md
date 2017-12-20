# Let's Git ready to rumble

If found myself with a rather strange git problem. As far as I was aware,
I was tracking a remote, however when ever I git a git pull, my bash
prompt would show me as having commits outstanding.

``` 
[voddenr:~/repository] master(4)+i ± 
```

Looking at the commit tree, it would seem that `origin/HEAD` and
`origin/master` have not been correctly updated:

```
*   f786359 - (HEAD -> master) Merge everything together. (3 hours ago) <Paul Gibbs>
|
*   51955ca - Wrote some code. (4 hours ago) <Paul Gibbs>
|\
| |
| * 81e4c19 - Update readme. (4 hours ago) <Richard Vodden>
| |
| * a84e10e - wip (15 hours ago) <Richard Vodden>
|/
|
*   2dcce03 - (rvodden/master, origin/master, origin/HEAD) Some kind of merge message. (24 hours ago) <Richard Vodden>
|\
| |
| * f1622f9 - This is quite a boring message. (24 hours ago) <Richard Vodden>
| |
| * 2bbc060 - Even more exciting message. (25 hours ago) <Richard Vodden>
| |
| * 19756aa - Exciting commit message (25 hours ago) <Richard Vodden> 
```


