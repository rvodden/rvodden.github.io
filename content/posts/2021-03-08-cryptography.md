---
title: Cryptography
draft: true
---

Crytography is the study of the solution to a set of particular problems. These problems are traditionally describe in terms of some people - Alice, Bob and Charlie. Alice and Bob want to send verious pieces of information to and from each other, and Charlie wants to stop that happening in some way. The assumption is that Charlie can read or hear every thing which Alice and Bob send to each other. Examples of some of the problems which cryptography tries to solve are:

1. Alice wants to send Bob a message, doesn't mind that Charlie can read it, but wants Bob to know that only she can have written it.
1. Alice sends Bob a message, doesn't mind that Bob isn't sure its from her, but wants to ensure that only Bob can read it.
1. Alice and Bob want to send messages back and forth, and know that that Charlie cannot read any of the messages.

You might ask why we don't just solve the 3<sup>rd</sup> problem, as this meets the requirments of the 1<sup>st</sup> two. That will become clear in a later article and has to do with establishing the communication channel between the two of them. 

In this series of articles I'd like to explore some of the mathematics and computation which surrounds cryptography and the solutions to these problemes. It's an area I find fascinating and I've been meaning to put some concerted effort into consolodating my knowledge on the subject, and I'm putting it online in case other people find it a helpful place to look.

## The art of the impossible

At the heart of cryptography is the idea of a _one way function_. We want some functions which are very easy for Alice or Bob to calculate the value of, but if Charlie hears the answer, it's practically impossible for him to work out the original value. In order for us to ascertain if a function we're thinking about has these properties, we need to define _very easy_ and _practically impossible_ a litte better.

We'll firstly assume that we're dealing with a relatively normal function. Perhaps a function, `$f : \mathbb{Z} \rightarrow \mathbb{Z}$`.