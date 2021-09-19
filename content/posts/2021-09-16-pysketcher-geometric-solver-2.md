---
title: "Writing a Geometric Solver in Python - Part 2: More Modelling"
series:
  - PySketcher Geometric Solver
categories:
  - python
  - pysketcher
  - geometry
  - solver
draft: false
description: >
    I describe, over the series, how to implement a geometric solver in
    Python. In this article we take the model from part one and extend it
    to allow constraints between higher order objects such as `Line` and
    `Circle`.
---
This is the second article in a short series about adding a geometric solver for my [PySketcher](https://github.com/rvodden/pysketcher) side project. The basic premise is that instead of having to tell PySketcher exactly where you'd like your shapes to be, you'll be able to specify the relationships the shapes have to each other, and PySketcher will be able to work our where they need to go. Have a read of [Part 1]() for more details, and for an explanation of how we've built up the model so far.

## Recapitulation

We've built a model, which consists of a `ConstrainedValue` class. This class is a `Descriptor` and is assigned to classes. When `ConstrainedValue` is used in a class, that class will store `ConstraintSet` objects instead of raw values. This means that we can use the `constrain_with` method of `ConstraintSet` to indicate that the value of that `ConstraintSet` is in some way constrained. We built a trivial constraint `FixedValueConstraint` which indicates that the value ofa `ConstraintSet` is constrained to, unsurprisingly, a fixed value. We also built a`LinkedValueConstraint` which indicates that a `ConstraintSet` is constrained to the value of another `ConstraintSet`. We implemented a throwaway `resolve` method on `ConstraintSet` so that we can test how our model hangs together. Finally we spent some time ensuring that the experience was intuitive for people using the model, and that it was possible to interrogate the model to see how things are stitched together. Whilst we were considering the concepts above we implemented a small`Point` object and used that, with our throwaway `revolve` method, to illustrate that our modelling code is effective. The full code is available in [this gist](https://gist.github.com/rvodden/c5d7d6ecea734006469d8dc758f9d1ae), and this is an example of it in use:
<!--phmdoctest-share-names-->
```python
#... {{% skip %}}
from abc import ABC

class Constraint(ABC):
    """Used to restrict that value of a ```ConstrainedValue```."""
    pass

class FixedValueConstraint(Constraint):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.value}>"

class LinkedValueConstraint(Constraint):
    def __init__(self, constraint_set):
        self._constraint_set = constraint_set

    @property
    def constraint_set(self):
        return self._constraint_set

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.constraint_set}>"

class ConstraintSet:
    def __init__(self, name=""):
        self._constraints = []
        self._name = name

    def constrain_with(self, constraint):
        """Add a constraint to this objects list of constraints."""
        self._constraints.append(constraint)

    def reset_constraints(self):
        """Removes the existing constraints from the constraint set"""
        self._constraints = []

    def resolve(self):
        """Naive implementation to aid testing"""
        for constraint in self._constraints:
            if isinstance(constraint, FixedValueConstraint):
                return constraint.value
            if isinstance(constraint, LinkedValueConstraint):
                return constraint.constraint_set.resolve()

        raise UnderconstrainedError("Fixed Value has not been provided.")

    def __repr__(self):
        retval = "ConstraintSet("
        if len(self._constraints) == 0:
            retval += ")"
            return retval

        for constraint in self._constraints:
            retval += f"\n    {constraint}"
        retval += "\n)"
        return retval

    def __str__(self):
        return self._name

class UnderConstrainedError(RuntimeError):
    pass

class ConstrainedValue:
    """An object which can be passed around to represent a value."""

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, instance, typ=None):
        # grab the ConstraintSet from the instance
        constraint_set = getattr(instance, self.private_name, None)

        # If the instance didn't have an initialized ConstraintSet then
        # give it one
        if constraint_set is None:
            constraint_set = ConstraintSet(f"{instance.name}.{self.public_name}")
            setattr(instance, self.private_name, constraint_set)
        return constraint_set

    def __set__(self, instance, value):
        # Grab the ConstraintSet from the instance
        constraint_set = self.__get__(instance, None)

        constraint_set.reset_constraints()
        # if the value we've been asked to assign is a ConstraintSet
        # then add a LinkedValueConstraint:
        if isinstance(value, ConstraintSet):
            constraint_set.constrain_with(LinkedValueConstraint(value))
            return

        # otherwise use a FixedValueConstraint to constrain to the provided
        # value
        constraint_set.constrain_with(FixedValueConstraint(value))
#... {{% /skip %}}
class Point:
    x = ConstrainedValue()
    y = ConstrainedValue()

    def __init__(self, name="", x=None, y=None):
        self._name = name
        if x is not None:
            self.x = x
        if y is not None :
            self.y = y

    @property
    def name(self):
        return self._name

p = Point('p', 1,2)
q = Point('q')
print(f"p.x is {p.x}")
print(f"p.x resolves to {p.x.resolve()}")
q.x = p.x
print(f"q.x is {repr(q.x)}")
print(f"q.x resolves to {q.x.resolve()}")
p.x = 2
print(f"Now p.x has changed, q.x resolves to {q.x.resolve()}")
```
```
p.x is p.x
p.x resolves to 1
q.x is ConstraintSet(
    LinkedValueConstraint<p.x>
)
q.x resolves to 1
Now p.x has changed, q.x resolves to 2
```

Top line stuff. We can define an object with some parameters and constrain those parameters using neat little constraints which are tiny standalone objects in themselves.
## Drawing a line under it

Next, we'd like to be able to represent more complex relationships. We may, for example, wish to constrain our point to being on a line, or perhaps on the circumference of a circle. In both of these examples the value of `x`is only known if the value of `y` is known and visa versa; yet neither can take arbitrary values.Before we consider how we might do that, let's build a simple line object. For the moment we won't worry about using `ConstrainedValue` in this line, as we wish to constrain the point to the line. We can revisit the `Line` object later on when we've established some patterns.
<!--phmdoctest-share-names-->
```python
class Line:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __repr__(self):
        return f"Line<({self.x1},{self.y1}),({self.x2},{self.y2})>"

l = Line(0,1,2,3)
print(l)
```
```
Line<(0,1),(2,3)>
```

As you can see, we've kept this super simple, and haven't even defined properties for `x1`, `x2`etc. It should serve our needs for the moment. Now how might we indicate that our `Point` is constrained to this line? The answer is surprisingly simple. The `Point` needs to be able to accept a constraint, and the easiest way to do that is to have it inherit from `ConstraintSet`:
<!--phmdoctest-share-names-->
```python
class Point(ConstraintSet):
    x = ConstrainedValue()
    y = ConstrainedValue()

    def __init__(self, name="", x=None, y=None):
        super().__init__(self)
        self._name = name
        if x is not None:
            self.x = x
        if y is not None :
            self.y = y

    @property
    def name(self):
        return self._name
```

Here the only changes are the first line of the class, which specifies `ConstraintSet` as a superclass, and the first line of `__init__` which adds the call to the superclass initializer. As we've now inherited from `ConstraintSet`, our `Point` class has a `constrain_with` method which can use to supply a `Constraint` which indicates that our point should be constrained to a `Line`. The fancy pants maths people say that if a point is on a line, then it "coincident", so let's use their fancy pants language and define a `CoincidentConstraint`:
<!--phmdoctest-share-names-->
```python
class CoincidentConstraint(Constraint):
    def __init__(self, line):
        self._line = line

    @property
    def line(self):
        return self._line

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.line}>"

l = Line(1,2,3,4)
p = Point('p')
p.constrain_with(CoincidentConstraint(l))
print(repr(p))
```
```
ConstraintSet(
    CoincidentConstraint<Line<(1,2),(3,4)>>
)
```

## Crisis of identity

Well our point is now telling us that it's constrained, and is listing out the constraints correctly, but it seems to be having a bit of an identity crisis. It's telling us that it's a`ConstraintSet`, and whilst that is true to a certain extent, it should really tell us that it is a`Point`. The issue is because when we originally wrote the `__repr__` method in `ConstraintSet` we hardcoded the class name (tsk). Let's address that:

<!--phmdoctest-share-names-->
```python
class ConstraintSet:
#... {{% skip %}}
    def __init__(self, name=""):
        self._constraints = []
        self._name = name

    def constrain_with(self, constraint):
        """Add a constraint to this objects list of constraints."""
        self._constraints.append(constraint)

    def reset_constraints(self):
        """Removes the existing constraints from the constraint set"""
        self._constraints = []

    def resolve(self):
        """Naive implementation to aid testing"""
        for constraint in self._constraints:
            if isinstance(constraint, FixedValueConstraint):
                return constraint.value
            if isinstance(constraint, LinkedValueConstraint):
                return constraint.constraint_set.resolve()

        raise UnderconstrainedError("Fixed Value has not been provided.")
#... {{% /skip %}}

    def __repr__(self):
        retval = f"{self.__class__.__name__}("
        if len(self._constraints) == 0:
            retval += ")"
            return retval

        for constraint in self._constraints:
            retval += f"\n    {constraint}"
        retval += "\n)"
        return retval

#... {{% skip %}}
    def __str__(self):
        return self._name

class Point(ConstraintSet):
    x = ConstrainedValue()
    y = ConstrainedValue()

    def __init__(self, name="", x=None, y=None):
        super().__init__(self)
        self._name = name
        if x is not None:
            self.x = x
        if y is not None :
            self.y = y

    @property
    def name(self):
        return self._name
#... {{% /skip %}}

l = Line(1,2,3,4)
p = Point('p')
p.constrain_with(CoincidentConstraint(l))
print(repr(p))
```
```
Point(
    CoincidentConstraint<Line<(1,2),(3,4)>>
)
```

Excellent! Our `Point` is a `Point` again, and its correctly reporting its constraints.

## Cascading Constraints

What happens if we look at the co-ordinates of the `Point`?

```python
l = Line(1,2,3,4)
p = Point('p')
p.constrain_with(CoincidentConstraint(l))
print(repr(p.x))
```
```
ConstraintSet()
```

That's not so good. Whilst it is true that we have not directly constrained the `x` coordinate, it is not true that the `x` coordinate is not constrained. It would be much better if the `x`coordinate could tell us that it was being constrained by the `CoincidentConstraint` at the `Point` level.We could just have the `constrain_with` method apply the `CoincidentConstraint` to the `x` and `y`coordinates, and this is certainly a valid approach.

However, let's think more broadly than our current scenario for a moment. We may, for example, be constraining a line to be horizontal. A line (or at least our line) is defined by two points, which in turn are each defined by two values, their `x` and `y` co-ordinates. Constraining a line to being horizontal is only constraining the `y` co-ordinates of those two point (constraining them to being equal) and there is no way that our `constrain_with` method can know this. If we were to just apply the `HorizontalConstraint` to all the properties then we'd end up with the `x` co-ordinates showing the that they were constrained, which is misleading.

So we need an alternative approach. It is only really our `Constraint` implementations which will understand which properties need to be constrained. So we need a mechanism for the `constrain_with`method to give the constraint the means to, in turn, constrain the properties of the object it is constraining. To achieve this we'll use a design pattern called a "callback". We'll define a `constrain_callback` method on the `Constraint` which accepts a `ConstraintSet` object.Then we will update our `constrain_with` method to call that `constrain_callback` method. The`constrain_callback` method can then be overridden by the various implementations of `Constraint` to apply the necessary downstream constraints.

So step 1, we need to modify our `Constraint` definition to include a `constraint_callback` method.We face a design decision at this point. We can either declare this method to be an`@abstractmethod` which will force implementations of `Constraint` to implement it, or we can provide a default implementation, which will do nothing, meaning that our implementations can just pretend the `constraint_callback` doesn't exist if they don't wish to constrain properties. It's not particularly clear which direction we should go here. If we provide a default implementation then we risk our users forgetting that it needs to be implemented, and therefore some nasty bugs. If we don't then implementations will have to explicitly state that they want the `constraint_callback` to do nothing. This is simply a question of style, neither option is particularly better than the other. For pythonic questions of style we should always refer to [PEP20 - the zen of python](https://www.python.org/dev/peps/pep-0020/) and yet again, in this case, it does not let us down. Rule 2 is "Explicit is better than implicit." so rather than providing a default implementation which implicitly does nothing, we will require our implementations to provide an explicit implementation of the method which does nothing (if that's what they require). In practice this means that we will decorate our method with `@abstractmethod`:

<!--phmdoctest-share-names-->
```python
from abc import ABC, abstractmethod

class Constraint(ABC):
    """Used to restrict that value of a `ConstrainedValue`."""

    @abstractmethod
    def constraint_callback(self, instance):
        raise NotImplementedError("`constraint_callback` must be implemented explicitly.")
```

And as a direct result of our design decision we need to update our constraints to include a definition of that method. In the case of `FixedValueConstraint` and `LinkedValueConstraint` it can simply do nothing. `CoincidentConstraint` is a touch more complicated so we'll look at that a little later.

<!--phmdoctest-share-names-->
```python
class FixedValueConstraint(Constraint):
#... {{% skip %}}
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.value}>"
#... {{% /skip %}}
    def constraint_callback(self, instance):
        pass

class LinkedValueConstraint(Constraint):
#... {{% skip %}}
    def __init__(self, constraint_set):
        self._constraint_set = constraint_set

    @property
    def constraint_set(self):
        return self._constraint_set

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.constraint_set}>"
#... {{% /skip %}}
    def constraint_callback(self, instance):
        pass
```

Step two is to update our `constrain_with` method to call the callback:

<!--phmdoctest-share-names-->
```python
class ConstraintSet:
#... {{% skip %}}
    def __init__(self, name=""):
        self._constraints = []
        self._name = name
#... {{% /skip %}}

    def constrain_with(self, constraint):
        constraint.constraint_callback(self)
        """Add a constraint to this objects list of constraints."""
        self._constraints.append(constraint)

#... {{% skip %}}
    def reset_constraints(self):
        """Removes the existing constraints from the constraint set"""
        self._constraints = []

    def resolve(self):
        """Naive implementation to aid testing"""
        for constraint in self._constraints:
            if isinstance(constraint, FixedValueConstraint):
                return constraint.value
            if isinstance(constraint, LinkedValueConstraint):
                return constraint.constraint_set.resolve()

        raise UnderconstrainedError("Fixed Value has not been provided.")

    def __repr__(self):
        retval = f"{self.__class__.__name__}("
        if len(self._constraints) == 0:
            retval += ")"
            return retval

        for constraint in self._constraints:
            retval += f"\n    {constraint}"
        retval += "\n)"
        return retval

    def __str__(self):
        return self._name

class ConstrainedValue:
    """An object which can be passed around to represent a value."""

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, instance, typ=None):
        # grab the ConstraintSet from the instance
        constraint_set = getattr(instance, self.private_name, None)

        # If the instance didn't have an initialized ConstraintSet then
        # give it one
        if constraint_set is None:
            constraint_set = ConstraintSet(f"{instance.name}.{self.public_name}")
            setattr(instance, self.private_name, constraint_set)
        return constraint_set

    def __set__(self, instance, value):
        # Grab the ConstraintSet from the instance
        constraint_set = self.__get__(instance, None)

        constraint_set.reset_constraints()
        # if the value we've been asked to assign is a ConstraintSet
        # then add a LinkedValueConstraint:
        if isinstance(value, ConstraintSet):
            constraint_set.constrain_with(LinkedValueConstraint(value))
            return

        # otherwise use a FixedValueConstraint to constrain to the provided
        # value
        constraint_set.constrain_with(FixedValueConstraint(value))

class Point(ConstraintSet):
    x = ConstrainedValue()
    y = ConstrainedValue()

    def __init__(self, name="", x=None, y=None):
        super().__init__(self)
        self._name = name
        if x is not None:
            self.x = x
        if y is not None :
            self.y = y

    @property
    def name(self):
        return self._name
#... {{% /skip %}}
```

Now we need to decide how we're going to actually constrain the parameters. One approach could be to apply the `CoincidentConstraint` to the `x` and `y`. I've thought about this, and I can't see a reason why it technically wouldn't work, however it does create an ambiguity. It would not be clear if the `CoincidentConstraint` had been applied directly to the `x` or if it had inherited it from its parent shape. So to avoid this we're going to create an `InfluencedConstraint`. This new constraint will indicate that the parameter is constrained by something higher up the food chain.
<!--phmdoctest-share-names-->
```python
class InfluencedConstraint(Constraint):
    def __init__(self, constraint):
        self._constraint = constraint

    def constraint_callback(self, instance):
        pass

    @property
    def constraint(self):
        return self._constraint

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.constraint}>"
```

Now we're ready to implement the `callback_constraint` method on the `CoincidentConstraint` to have it indicate that it is influencing the two co-ordinates.
<!--phmdoctest-share-names-->
```python
class CoincidentConstraint(Constraint):
#... {{% skip %}}
    def __init__(self, line):
        self._line = line

    @property
    def line(self):
        return self._line

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.line}>"
#... {{% /skip %}}

    def constraint_callback(self, point):
        point.x.constrain_with(InfluencedConstraint(self))
        point.y.constrain_with(InfluencedConstraint(self))
```

Let's take this for a spin and see how it goes!

<!--phmdoctest-share-names-->
```python
l = Line(1,2,3,4)
p = Point('p')
p.constrain_with(CoincidentConstraint(l))
print(f"p is {repr(p)}")
print(f"p.x is {repr(p.x)}")
```
```
p is Point(
    CoincidentConstraint<Line<(1,2),(3,4)>>
)
p.x is ConstraintSet(
    InfluencedConstraint<CoincidentConstraint<Line<(1,2),(3,4)>>>
)
```

That looks ideal. The `Point` object is expressing that it is constrained by the`CoincidentConstraint` and if we look at the `x` coordinate we can see that it is influenced by the`CoincidentConstraint` and even see exactly which line the `CoincidentConstraint` is constraining to. This might get a bit verbose in complex diagrams, but right now its perfect for our needs, so let's leave it like that and worry about verbosity if and when it becomes an issue.

## What type of fool do you take me for?

Let's try something a little off the wall. Let's try constraining `p.x` with a`CoincidentConstraint`. As `CoincidentConstraint` is only designed to apply to `Point` objects, it's likely to do something a little strange when applied to a `ConstraintSet`:

<!--phmdoctest-share-names-->
<!--phmdoctest-skip-->
```python
l = Line(1,2,3,4)
p = Point('p')
p.x.constrain_with(CoincidentConstraint(l))
print(repr(p.x))
```
```
AttributeError: 'ConstraintSet' object has no attribute 'x'
```

Oh dear! This isn't a very helpful error message is it? Whilst in our simple example its probably easy enough to work out what has gone on, more complex scenarios could lead to some real head scratching. To resolve this, let's have the `constraint_callback` check that the constraint is being applied to a sensible object. In this case it only really makes sense for`CoincidentConstraint` to be applied to a `Point`, so let's enforce that. And let's create a custom`RuntimeError` object with a nice error message to tell our users what is going on.

<!--phmdoctest-share-names-->
```python

class InvalidConstraintException(RuntimeError):
    """Indicates that a constraint has been applied to an object which doesn't make sense."""

class CoincidentConstraint(Constraint):
#... {{% skip %}}
    def __init__(self, line):
        self._line = line

    @property
    def line(self):
        return self._line

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.line}>"
#... {{% /skip %}}

    def constraint_callback(self, point):
        if not isinstance(point, Point):
            raise InvalidConstraintException(f"{self.__class__.__name__} can only"
            f" be applied to `Point`, it cannot be applied to `{point.__class__.__name__}`")
        point.x.constrain_with(InfluencedConstraint(self))
        point.y.constrain_with(InfluencedConstraint(self))
```

Let's see how that's improved things:
<!--phmdoctest-share-names-->
<!--phmdoctest-skip-->
```python
l = Line(1,2,3,4)
p = Point('p')
p.x.constrain_with(CoincidentConstraint(l))
print(repr(p.x))
```
```
InvalidConstraintException: CoincidentConstraint can only be applied to `Point`, it cannot be applied to `ConstraintSet`.
```

This is much better, and likely to save our developers a chunk of time as compared with the old"missing attribute" error message. Spoiler alert though, this specific implementation will come back to bite us in the next section. Comment if you can see why, and no cheating by reading the next section first!
## One way or another.

Let's take stock of where we have got to. We have a nice strong framework for expressing geometric constraints as `Constraint` objects, and we have a clean way of applying these to our geometric objects. We have clear output when we ask the various objects to `repr` themselves, and we have clear error messages when things don't quite go to plan. There are just a couple of corners we need to clear up before we can call ourselves done. Look at the following example:
<!--phmdoctest-share-names-->
```python
p = Point('p')
q = Point('q')

q.x = p.x
print(f"p.x is {repr(p.x)}")
print(f"q.x is {repr(q.x)}")
```
```
p.x is ConstraintSet()
q.x is ConstraintSet(
    LinkedValueConstraint<p.x>
)
```
This is a tremendously powerful thing to be able to do. We can create a point and say nothing about it, then refer to it in constraints. What would happen, though, if we were solving our constraint system (the subject of a later article) and `q` was given a value first? Equality is a reciprocal condition, and when we assert that `q.x = p.x` we are equally saying that `p.x = q.x`.We could force this on our users. We could decide that for the purposes of our geometric solver,such operations are not reciprocal, and that users must specify both sides of the relationship:
<!--phmdoctest-share-names-->
```python
p = Point('p')
q = Point('q')

q.x = p.x
p.x = q.x
print(f"p.x is {repr(p.x)}")
print(f"q.x is {repr(q.x)}")
```
```
p.x is ConstraintSet(
    LinkedValueConstraint<q.x>
)
q.x is ConstraintSet(
    LinkedValueConstraint<p.x>
)
```

Whilst this does tick the PEP20 "explicit is better than implicit" rule, rule three of the same says"Simple is better than complex". I'm reasonably sure that every geometric relationship is in someway reciprocal. If `l` is parallel to `m` then `m` is parallel to `l`. Even with our`CoincidentConstraint` if our point is on the line, then our line must go through the point. Let's update our `LinkedValueConstraint` to apply the reciprocal constraint.

<!--phmdoctest-share-names-->
```python
class LinkedValueConstraint(Constraint):
#... {{% skip %}}
    def __init__(self, constraint_set):
        self._constraint_set = constraint_set

    @property
    def constraint_set(self):
        return self._constraint_set

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.constraint_set}>"
#... {{% /skip %}}
    def constraint_callback(self, instance):
        if not isinstance(instance, ConstraintSet):
            raise InvalidConstraintException(f"{self.__class__.__name__} can only"
            f" be applied to `ConstraintSet`, it cannot be applied to `{point.__class__.__name__}`")
        self.constraint_set.constrain_with(LinkedValueConstraint(instance))
        pass
```

And let's try again:


<!--phmdoctest-share-names-->
<!--phmdoctest-skip-->
```python
p = Point('p')
q = Point('q')

q.x = p.x
print(f"p.x is {repr(p.x)}")
print(f"q.x is {repr(q.x)}")
```
```
RecursionError: maximum recursion depth exceeded while calling a Python object
```

Oops! What's going on here? Well the problem is that the `LinkedValueConstraint` applies a reciprocal constraint by enforcing a `LinkedValueConstraint` on the original `ConstraintSet` which in turn tries to apply a reciprocal constraint etc. And the whole world explodes in a glorious stack overflow (first one of the project though, I'm proud!). We could fix this by adding some kind of flag to `constrain_with` and `constraint_callback` to indicate that this is a reciprocal call and that they should not apply the reciprocal constraint as its already done. This is crying out to be forgotten and to lead to some nasty stack overflow type bugs. I think a neater solution is to have`constrain_with` check to see if an identical constraint has already been applied and just exit cleanly if it has. To do this we need to establish what it means for two `LinkedValueConstraints` to be equal:

<!--phmdoctest-share-names-->
```python
class LinkedValueConstraint(Constraint):
#... {{% skip %}}
    def __init__(self, constraint_set):
        self._constraint_set = constraint_set

    @property
    def constraint_set(self):
        return self._constraint_set

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.constraint_set}>"

    def constraint_callback(self, instance):
        if not isinstance(instance, ConstraintSet):
            raise InvalidConstraintException(f"{self.__class__.__name__} can only"
            f" be applied to `ConstraintSet`, it cannot be applied to `{point.__class__.__name__}`")
        self.constraint_set.constrain_with(LinkedValueConstraint(instance))
        pass
#... {{% /skip %}}
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.constraint_set == other.constraint_set
```

Here we've said that a `LinkedValueConstraint` is only equal to another object, if and only if that other object is also a `LinkedValueConstraint` and they are both linked to the same `ConstraintSet`.
<!--phmdoctest-share-names-->
```python
p = Point()
l = LinkedValueConstraint(p.x)
m = LinkedValueConstraint(p.x)
n = LinkedValueConstraint(q.x)
print(f"l == m: {l == m}")
print(f"l == n: {l == n}")
```
```
l == m: True
l == n: False
```

And let's stitch this into our `constrain_with` method:


<!--phmdoctest-share-names-->
```python
class ConstraintSet:
#... {{% skip %}}
    def __init__(self, name=""):
        self._constraints = []
        self._name = name
#... {{% /skip %}}

    def constrain_with(self, constraint):
        if constraint in self._constraints:
            return
        constraint.constraint_callback(self)
        """Add a constraint to this objects list of constraints."""
        self._constraints.append(constraint)

#... {{% skip %}}
    def reset_constraints(self):
        """Removes the existing constraints from the constraint set"""
        self._constraints = []

    def resolve(self):
        """Naive implementation to aid testing"""
        for constraint in self._constraints:
            if isinstance(constraint, FixedValueConstraint):
                return constraint.value
            if isinstance(constraint, LinkedValueConstraint):
                return constraint.constraint_set.resolve()

        raise UnderconstrainedError("Fixed Value has not been provided.")

    def __repr__(self):
        retval = f"{self.__class__.__name__}("
        if len(self._constraints) == 0:
            retval += ")"
            return retval

        for constraint in self._constraints:
            retval += f"\n    {constraint}"
        retval += "\n)"
        return retval

    def __str__(self):
        return self._name

class ConstrainedValue:
    """An object which can be passed around to represent a value."""

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, instance, typ=None):
        # grab the ConstraintSet from the instance
        constraint_set = getattr(instance, self.private_name, None)

        # If the instance didn't have an initialized ConstraintSet then
        # give it one
        if constraint_set is None:
            constraint_set = ConstraintSet(f"{instance.name}.{self.public_name}")
            setattr(instance, self.private_name, constraint_set)
        return constraint_set

    def __set__(self, instance, value):
        # Grab the ConstraintSet from the instance
        constraint_set = self.__get__(instance, None)

        constraint_set.reset_constraints()
        # if the value we've been asked to assign is a ConstraintSet
        # then add a LinkedValueConstraint:
        if isinstance(value, ConstraintSet):
            constraint_set.constrain_with(LinkedValueConstraint(value))
            return

        # otherwise use a FixedValueConstraint to constrain to the provided
        # value
        constraint_set.constrain_with(FixedValueConstraint(value))

class Point(ConstraintSet):
    x = ConstrainedValue()
    y = ConstrainedValue()

    def __init__(self, name="", x=None, y=None):
        super().__init__(self)
        self._name = name
        if x is not None:
            self.x = x
        if y is not None :
            self.y = y

    @property
    def name(self):
        return self._name
#... {{% /skip %}}
```

Let's see if that solved our stack overflow:
<!--phmdoctest-share-names-->
<!--phmdoctest-skip-->
```python
p = Point('p')
q = Point('q')

q.x = p.x
print(f"p.x is {repr(p.x)}")
print(f"q.x is {repr(q.x)}")
```
```
RecursionError: maximum recursion depth exceeded
```

It didn't! Nightmare! The issue here is that we are using the `constraint_callback` to apply the reciprocal constraint, but that is being called before the constraint is added to`self._constraints` in the `Constraint` class. We need it to be that way around because the`constraint_callback` is also validating that the object is of a suitable type. Aha! This is our issue. Every time we have to use the work "also" to describe what an object or method is doing, then we likely have ourselves a separation of concerns issue. This was the mistake which I gave you the spoiler alert for earlier! Let's split our `constraint_callback` into three: a `validate_object` method, an `apply_reciprocal_constraint` method, and finally the`cascade_constraints`.

<!--phmdoctest-share-names-->
```python
from abc import ABC, abstractmethod

class Constraint(ABC):
    """Used to restrict that value of a ```ConstrainedValue```."""

    @abstractmethod
    def validate_object(self, instance):
        """Validates that `instance` is suitable. Raises `InvalidConstraintException` if not"""
        raise NotImplementedError("`validate_object` must be implemented explicitly.")

    @abstractmethod
    def apply_reciprocal_constraint(self, instance):
        """Applies a matching constraint to the provided instance."""
        raise NotImplementedError("`apply_reciprocal_callback` must be implemented explicitly.")

    @abstractmethod
    def cascade_constraints(self, instance):
        """Applies appropriate constraints to the properties of `instance`."""
        raise NotImplementedError("`cascade_constraints` must be implemented explicitly.")
```
And let's update our `LinkedValueConstraint`:


<!--phmdoctest-share-names-->
```python
class LinkedValueConstraint(Constraint):
#... {{% skip %}}
    def __init__(self, constraint_set):
        self._constraint_set = constraint_set

    @property
    def constraint_set(self):
        return self._constraint_set

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.constraint_set}>"
#... {{% /skip %}}
    def validate_object(self, instance):
        if not isinstance(instance, ConstraintSet):
            raise InvalidConstraintException(f"{self.__class__.__name__} can only"
            f" be applied to `ConstraintSet`, it cannot be applied to `{point.__class__.__name__}`")

    def apply_reciprocal_constraint(self, instance):
        self.constraint_set.constrain_with(LinkedValueConstraint(instance))

    def cascade_constraints(self, instance):
        pass
#... {{% skip %}}
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.constraint_set == other.constraint_set
#... {{% /skip %}}

```
And finally sort out `ConstraintSet`:
<!--phmdoctest-share-names-->
```python
class ConstraintSet:
#... {{% skip %}}
    def __init__(self, name=""):
        self._constraints = []
        self._name = name
#... {{% /skip %}}

    def constrain_with(self, constraint):
        constraint.validate_object(self)
        if constraint in self._constraints:
            return
        """Add a constraint to this objects list of constraints."""
        self._constraints.append(constraint)
        constraint.cascade_constraints(self)
        constraint.apply_reciprocal_constraint(self)

#... {{% skip %}}
    def reset_constraints(self):
        """Removes the existing constraints from the constraint set"""
        self._constraints = []

    def resolve(self):
        """Naive implementation to aid testing"""
        for constraint in self._constraints:
            if isinstance(constraint, FixedValueConstraint):
                return constraint.value
            if isinstance(constraint, LinkedValueConstraint):
                return constraint.constraint_set.resolve()

        raise UnderconstrainedError("Fixed Value has not been provided.")

    def __repr__(self):
        retval = f"{self.__class__.__name__}("
        if len(self._constraints) == 0:
            retval += ")"
            return retval

        for constraint in self._constraints:
            retval += f"\n    {constraint}"
        retval += "\n)"
        return retval

    def __str__(self):
        return self._name

class ConstrainedValue:
    """An object which can be passed around to represent a value."""

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, instance, typ=None):
        # grab the ConstraintSet from the instance
        constraint_set = getattr(instance, self.private_name, None)

        # If the instance didn't have an initialized ConstraintSet then
        # give it one
        if constraint_set is None:
            constraint_set = ConstraintSet(f"{instance.name}.{self.public_name}")
            setattr(instance, self.private_name, constraint_set)
        return constraint_set

    def __set__(self, instance, value):
        # Grab the ConstraintSet from the instance
        constraint_set = self.__get__(instance, None)

        constraint_set.reset_constraints()
        # if the value we've been asked to assign is a ConstraintSet
        # then add a LinkedValueConstraint:
        if isinstance(value, ConstraintSet):
            constraint_set.constrain_with(LinkedValueConstraint(value))
            return

        # otherwise use a FixedValueConstraint to constrain to the provided
        # value
        constraint_set.constrain_with(FixedValueConstraint(value))

class Point(ConstraintSet):
    x = ConstrainedValue()
    y = ConstrainedValue()

    def __init__(self, name="", x=None, y=None):
        super().__init__(self)
        self._name = name
        if x is not None:
            self.x = x
        if y is not None :
            self.y = y

    @property
    def name(self):
        return self._name
#... {{% /skip %}}
```

This has had the happy effect of making the `constrain_with` method much more readable. Let's see if its finally resolved our stack overflow.
<!--phmdoctest-share-names-->
```python
p = Point('p')
q = Point('q')

q.x = p.x
print(f"p.x is {repr(p.x)}")
print(f"q.x is {repr(q.x)}")
```
```
p.x is ConstraintSet(
    LinkedValueConstraint<q.x>
)
q.x is ConstraintSet(
    LinkedValueConstraint<p.x>
)
```
Hooray! That was a surprising amount of work for the apparently simple task of implementing reciprocal relationships!

## Wrapping it all up

As a final flourish we need to update our existing constraints to have these new methods. Our`FixedValueConstraint` is trivial, we shall just implement each as a no-op:

<!--phmdoctest-share-names-->
```python
class FixedValueConstraint(Constraint):
#... {{% skip %}}
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.value}>"
#... {{% /skip %}}
    def validate_object(self, instance):
        pass

    def apply_reciprocal_constraint(self, instance):
        pass

    def cascade_constraints(self, instance):
        pass
```

`InfluencedConstraint` at first feels like it might be a little more complex. Validation is straightforward, it can only apply to another `ConstraintSet` object, or child object. But what about the reciprocal constraint? In fact, we don't need to do anything here, as the reciprocal object is the "higher up one". If, for example, `InfluencedConstraint` is being applied to `p.x`, that's because`CoincidentConstraint` has been applied to `p` so we already know that the reciprocal constraint isin place, as such we don't need to do anything. Similarly we can make no assumptions as to what constraints will need to be cascaded and we'll leave that to the "higher up" object should that be necessary:
<!--phmdoctest-share-names-->
```python
class InfluencedConstraint(Constraint):
    #... {{% skip %}}
    def __init__(self, constraint):
        self._constraint = constraint

    @property
    def constraint(self):
        return self._constraint

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.constraint}>"
    #... {{% /skip %}}

    def validate_object(self, instance):
        if not isinstance(instance, ConstraintSet):
            raise InvalidConstraintException(f"{self.__class__.__name__} can only"
            f" be applied to `ConstraintSet`, it cannot be applied to `{point.__class__.__name__}`")

    def apply_reciprocal_constraint(self, instance):
        pass

    def cascade_constraints(self, instance):
        pass
```

We've already done `LinkedValueConstraint` so that only leaves `CoincidentConstraint`. In order todo that we'll need to upgrade our `Line` object to be able to take constraints, and as this article is already about twice as long as I intended, let's leave that for next time! In the next article we'll look at upgrading our `Line` to be able to accept `Constraint` objects, and in so doing we'll walk a path towards some pretty powerful generics.
