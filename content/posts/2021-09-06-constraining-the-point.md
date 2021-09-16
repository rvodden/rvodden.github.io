---
title: "Writing a Geometric Solver in Python - Part 1: Modelling Constraints"
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
    Python. In this article we look at how we might represent a set of geometric
    relationships in a class hierarchy. We partially implement this for a
    `Point`object, and consider the developer experience.
---

[PySketcher](https://github.com/rvodden/pysketcher) is little library which I maintain which makes it simple (hopefully) to draw geometric images. It was originally written by Hans Petter Langtangen, who sadly passed away in 2016, and since 2019 I've been keeping it up to date and adding features.

Right now, PySketcher only supports absolute positioning of shapes. This means that you have to know exactly where you'd like the center of your circle to be and exactly what radius it should have. 

I'd like to add a facility for a user to describe the various geometric features and relationships which the shapes have, as well as potentially being able to specify the properties absolutely. So instead of saying "I'd like to have a circle of radius $3$ and centered at the point $(0,0)$, a user could say "Please create me a circle which is centered where these two lines cross and is tangent to this other line."

This presents some interesting challenges:

1. How will the relationships between the shapes be represented.
2. Once the relationships are understood, how will we work out where the shapes should go? Can we do this without creating performance issues?
3. What should the experience be for the developer coding a diagram when they want to represent relationships in code?

At first glance it may look like the first and last items are the same. In fact, the representation and the developer experience are separate concerns. For example if I wish to specify that two lines are parallel, I am constraining the gradient of the 2<sup>nd</sup> line to be the same as the first. I don't think there is any argument that the concept of "parallel" is more intuitive, however a gradient equality constraint may make more sense from an implementation perspective.

So over a series of articles, I shall explore each of these challenges. This will hopefully be interesting to some readers, and will also help document my thought processes. That way when in two years I look at my code and think "Why on earth did you to that?" I may have some way of understanding my original justification.

## The Problem

In this article let's focus on the problem of how to represent the relationships between shapes internally to PySketcher. This is probably a little backwards, as we'd usually like to consider how the users (or developers in this instance) interact with the library before we look at the internals, but in this instance looking at the internals gives us a quite valuable insight into the art of the possible. And we won't completely ignore the developers - we'll look at the internals whilst considering what potential options that opens up for our API in part 3.

So we'd like for PySketcher to enable us to specify a number of shapes, and for us to then specify how those shapes interact, and for this to be represented somehow internally. We'll leave the problem of working out what the shapes end up looking like to part 2. I think it's useful to think about what we're actually saying when we specify a relationship, and I return to the example of parallelization which I briefly mentioned earlier. If we say that a line is parallel to another line, then we are restricting the values which its gradient can take. This means that we may not know what the gradient of the line is when we create it, but instead we'll need to allow it to be worked out later. Perhaps more subtle is to realise that we may not know what the gradient is when we assign that constraint. If we assert that one line is parallel to another, but don't yet know the gradient of that other line (as we've not yet asserted all the constraints in the diagram), then we will be unable to assign the value of the gradient at assignment time. So we need a means to:

1. Represent that a shape has some property or value without knowing what that value might be (yet).
1. Be able to assign constraints to that property or value.
1. Trigger the calculation of the value on the basis of the constraints.

## Constrained Thinking

Let's have a look at how we might implement this. As with all my python articles, where you see a line which says `#...` that means I've omitted some code for clarity, and usually that code is code from a previous example. Let's start by defining a class which holds a list of constraints, and has a `resolve` method to work out a final value from those constraints. As I mentioned earlier, in this article we won't concern ourselves with how we calculate that value, right now we're just interested in how we might represent objects which might be constrained:

<!--phmdoctest-share-names-->
```python
class ConstrainedValue():
    """An object which can be passed around to represent a value."""

    def __init__(self):
        self._constraints: List[Constraint] = []

    def constrain_with(self, constraint):
        """Add a constraint to this objects list of constraints."""
        self._constraints.append(constraint)

    def resolve(self):
        """Leave to specific implementations to calculate the value on the basis
        of constraints."""
        raise NotImplementedError("`resolve` has not yet been implemented.")
```


Let's also think about what a constraint might look like. I'll define an abstract constraint and the implement the simplest example of a constraint - a constraint which ties the object to a fixed value.

<!--phmdoctest-share-names-->
```python
from abc import ABC

class Constraint(ABC):
    """Used to restrict that value of a ```ConstrainedValue```."""
    pass

class FixedValueConstraint(Constraint):
    def __init__(self, value):
        self._value = value

    def check(self, t):
        return t == self._value

    @property
    def value(self):
        return self._value
```

This really looks like we're getting somewhere. We have a class which represents a constrainable value, and we can apply constraints to it. 

So how might we integrate this with a shape? Let's take the simplest of shapes, a point, and see what we might do. A naive implementation of a `Point` with no `ConstrainedValue` integration might be:

<!--phmdoctest-share-names-->
```python
class Point:
    def __init__(x=None, y=None):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
```

To stitch our `ConstrainedValue` into this, we need to modify the initializer so that it creates `ConstrainedValue` objects; alter the properties so that they add a `FixedValueConstraint` to the `ConstrainedValue`; and then use those properties to set the values in the initializer if they are provided:

<!--phmdoctest-share-names-->
```python
class Point:
    def __init__(self, x=None, y=None):
        self._x = ConstrainedValue()
        self._y = ConstrainedValue()
        if x is not None: 
            self.x = x
        if y is not None : 
            self.y = y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x.constrain_with(FixedValueConstraint(value))    

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y.constrain_with(FixedValueConstraint(value))
```

So now we can create a `Point`, assign it some co-ordinates, and have it return a `ConstrainedValue` for each of those properties:

<!--phmdoctest-share-names-->
```python
p = Point(1,2)
print(type(p.x).__name__)
print(type(p.y).__name__)
```
```
ConstrainedValue
ConstrainedValue
```

## Getting Value Back

Right now this constrained value isn't a lot of use as there's no way of finding out what the value is. The details of how we do this in general are for a later article, but let's implement a trivial resolve method in `ConstrainedValue` which simply checks if its constrained with a `FixedValueConstraint` and if so returns that value, otherwise throws an `UnderConstrainedError`. This will allow us to play a little more and really check that what we've built so far will work for us:

<!--phmdoctest-share-names-->
```python
class UnderConstrainedError(RuntimeError):
    pass

class ConstrainedValue():
    """An object which can be passed around to represent a value."""

    def __init__(self):
        self._constraints: List[Constraint] = []

    def constrain_with(self, constraint):
        """Add a constraint to this objects list of constraints."""
        self._constraints.append(constraint)

    def resolve(self):
        """Naive implementation to aid testing"""
        for constraint in self._constraints:
            if isinstance(constraint, FixedValueConstraint):
                return constraint.value

            raise UnderconstrainedError("Fixed Value has not been provided.")
```

So now we should be able to ask our `Point` what the values are of its properties:

<!--phmdoctest-share-names-->
```python
p = Point(1,2)
print(f"p.x is {p.x.resolve()}")
print(f"p.y is {p.y.resolve()}")
```
Which gives us the output we'd expect:
```
p.x is 1
p.y is 2
```

This is all well and good. We can create a point and give it values, but as it stands we cannot constrain one point to "point to" another. If create a `Point` `p` with some initial values, and then another point `q` and then set the `x` value of `q` to the `x` value of `p`, then ask `q.x` what its value is:

<!--phmdoctest-share-names-->
<!--phmdoctest-skip-->
```python
p = Point(1,2)
q = Point()
q.x = p.x
print(f"q.x is {q.x.resolve()}")
```

then we get a reference to the `ConstrainedValue` which is `p.x` instead of `1` as we'd probably expect.

```
q.x is <test_pysketcher_memoization.test_code_150.<locals>.ConstrainedValue object at 0x106375460>
```

We can call `resolve` twice to get the value we want:

<!--phmdoctest-share-names-->
```python
p = Point(1,2)
q = Point()
q.x = p.x
print(f"q.x is {q.x.resolve().resolve()}")
```

```
q.x is 1
```

but that is very messy and in complex diagrams we may have to call resolve many times. We could
alter our resolve method to detect if it is about to return a `ConstrainedValue` and if it is, call `resolve()` again until such time as it gets to a defined value. I feel its neater, however, to detect if we're _assigning_ a `ConstrainedValue`. If we are, then instead of adding a `FixedValueConstraint` we simply set the property to the provided `ConstrainedValue`.

<!--phmdoctest-share-names-->
```python
class Point:
#... {{% skip %}}
    def __init__(self, x=None, y=None):
        self._x = ConstrainedValue()
        self._y = ConstrainedValue()
        if x is not None: 
            self.x = x
        if y is not None : 
            self.y = y

    @property
    def x(self):
        return self._x
# {{% /skip %}}
    @x.setter
    def x(self, value):
        if isinstance(value, ConstrainedValue):
            self._x = value
        self._x.constrain_with(FixedValueConstraint(value))    

#... {{% skip %}}
    @property
    def y(self):
        return self._y

# {{% /skip %}}
    @y.setter
    def y(self, value):
        if isinstance(value, ConstrainedValue):
            self._y = value
        self._y.constrain_with(FixedValueConstraint(value))
```

This now gives us more intuitive behavior:

<!--phmdoctest-share-names-->
```python
p = Point(1,2)
q = Point()
q.x = p.x
print(f"q.x is {q.x.resolve()}")
```
```
q.x is 1
```

Great!

## Let's get the descriptors in

All is not well and good, however. If we look at our `Point` class we have a code which is repeated for the `x` and `y` properties. Moreover this code will need to be repeated for all the properties on all of our shapes, which is far from ideal. It would be much better if we could somehow encapsulate the assignment logic into the `ConstrainedValue` itself and have that behavior shared across all such objects in PySketcher. 

It so happens that there is a way to do this. Python provides a mechanism called a `Descriptor` which calls a method when a field is set or read. It is a `protocol` which means that we don't have to explicitly declare that we are creating a `Descriptor`, we just have to comply with its requirements. In this case defining a `__set__`, `__get__`, or `__delete__` method is sufficient.

```python
class ExampleDescriptor:
    def __init(self):
        self._value = None

    def __get__(self, instance, type=None):
        print("I am a get method")
        return self._value

    def __set__(self, instance, value):
        print("I am a set method")
        self._value = value

class ExampleObject:
    prop = ExampleDescriptor()


test = ExampleObject()
print("##")
test.prop = 1
print("##")
print(test.prop)
print("##")

```
```
##
I am a set method
##
I am a get method
1
##
```

So by augmenting out `ConstrainedValue` class with a `__get__` and `__set__` method, we can move the assignment logic out of the properties in the `Point` class, and in fact do away with the properties all together.

<!--phmdoctest-share-names-->
```python
class ConstrainedValue():
    """An object which can be passed around to represent a value."""
#... {{% skip %}}
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

            raise UnderconstrainedError("Fixed Value has not been provided.")
#{{% /skip %}}
    def __init__(self):
        self._value = None
        self._constraints: List[Constraint] = []

    def __get__(self, instance, type=None):
        return self

    def __set__(self, instance, value):
        if isinstance(value, type(self)):
            self._value = value
            return
        
        self.reset_constraints()
        self.constrain_with(FixedValueConstraint(value))


class Point:
    x = ConstrainedValue()
    y = ConstrainedValue()

    def __init__(self, x=None, y=None):
        if x is not None: 
            self.x = x
        if y is not None : 
            self.y = y

p = Point(1,2)
print(f"p.x is {p.x.resolve()}")
q = Point()
q.x = p.x
print(f"q.x is {q.x.resolve()}")
```
```
p.x is 1
q.x is 1
```

Now this is starting to look great! The `Point` class has a really clean definition and the interface for PySketcher users is intuitive. As is so often the way, all is not as rosy as things might at first appear. Let us investigate using `p` and `q` as independent points.

<!--phmdoctest-share-names-->
```python
p = Point(1,2)
q = Point(2,3)
print(f"p.x is {p.x.resolve()}")
print(f"q.x is {q.x.resolve()}")
```
```
p.x is 2
q.x is 2
```

Disaster! Both `p` and `q` have the same value for `x` even though we want them to have separate values. 

## Perhaps a little too constrained

This is because the `ConstrainedValue` belongs to the class `Point` not to the instances of class `Point`, and as such is shared by all the instances of `Point`. Alas it has to be this way because that's how decorators work. If you would like to read more about decorators [there is an excellent article here!](https://realpython.com/python-descriptors/), and that very article discusses our exact problem. To fix it we use the  `__set_name__` magic method which is called on instance creation, and use that to define a field on the instance in which to store our values. This also means we have to separate the data away from assignment logic so that we can store it in the instance, which we shall do in a `ConstraintSet` object. This is a little neater as the code which assigns the values and deals with the method calls is contained in `ConstrainedValue` and the code which holds the value and the resolution logic is held in `ConstraintSet`; so we have better separation of concerns.

<!--phmdoctest-share-names-->
```python
class ConstraintSet:
    def __init__(self):
        self._constraints = []
    
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

        raise UnderconstrainedError("Fixed Value has not been provided.")

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
            constraint_set = ConstraintSet()
            setattr(instance, self.private_name, constraint_set)
        return constraint_set

    def __set__(self, instance, value):
        if isinstance(value, ConstraintSet):
            setattr(instance, self.private_name, value)
            return

        constraint_set = self.__get__(instance)
        constraint_set.reset_constraints()
        constraint_set.constrain_with(FixedValueConstraint(value))

class Point:
    x = ConstrainedValue()
    y = ConstrainedValue()

    def __init__(self, x=None, y=None):
        if x is not None: 
            self.x = x
        if y is not None : 
            self.y = y

```

And this now works:
<!--phmdoctest-share-names-->
```python
p = Point(1,2)
q = Point(2,3)
print(f"p.x is {p.x.resolve()}")
print(f"q.x is {q.x.resolve()}")
```
```
p.x is 1
q.x is 2
```

As does our original logic:

<!--phmdoctest-share-names-->
```python
p = Point(1,2)
print(f"p.x is {p.x.resolve()}")
q = Point()
q.x = p.x
print(f"q.x is {q.x.resolve()}")
```
```
p.x is 1
q.x is 1
```

And for the icing on the cake, let's validate that when we change the value of `p.x`, the value of `q.x` changes with it:


<!--phmdoctest-share-names-->
```python
p = Point(1,2)
print(f"p.x is {p.x.resolve()}")
q = Point()
q.x = p.x
print(f"q.x is {q.x.resolve()}")
p.x = 2
print(f"p.x is {p.x.resolve()}")
print(f"q.x is {q.x.resolve()}")
```
```
p.x is 1
q.x is 1
p.x is 2
q.x is 2
```

## Making things more explicit

As a little recap, let's review what we've achieved so far. We can create an object which has fields which can have constraints applied to them by creating them as `ConstrainedValues` at the class level. This results in a set of constraints being stored in a `ConstraintSet` object at the instance level, and constraints can be added using the `constrain_with` method. Our fields can either be assigned a value or another `ConstraintSet`. Value assignment is implemented by, behind the scenes, applying a `FixedValueConstraint` to the field in question having cleared any previously applied constraints. We have validated this by implementing a `Point` object with two fields `x` and `y`. instantiating this twice, linking the `x` field of one instance to the other, and validating that when the first is changed, the second changes with it.

Certainly great progress! What might happen if we wanted to reverse engineer this process, however? If we wanted to ask say, `q.x`, what it is constrained by? At the moment, if we executed `print(q.x)` it would show the same object as `p.x`, namely a `FixedValueConstraint`. Moreover seeing that `q.x` has been constrained by a `FixedValueConstraint` may lead a developer to think that a value had been directly assigned to `q.x` which is not the case. This may be confusing if we're trying to debug a complex diagram. As such let's create an additional constraint, a `LinkedValueConstraint`, which means we can explicitly model that `q.x` has been assigned `p.x`.

Before we do that let's sort out how `ConstraintSets` are displayed. Right now, if we print one directly, we are given a type and a memory location. Let's override the `__repr__` method to give us something a little more meaningful. We'll need to do something similar to `FixedValueConstraint` as well:

<!--phmdoctest-share-names-->
```python
class ConstraintSet:
#... {{% skip %}}
    def __init__(self):
        self._constraints = []
    
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

        raise UnderconstrainedError("Fixed Value has not been provided.")
# {{% /skip %}}
    def __repr__(self):
        retval = "ConstraintSet("
        if len(self._constraints) == 0:
            retval += ")"
            return retval

        for constraint in self._constraints:
            retval += f"\n    {constraint}"
        retval += "\n)"
        return retval 

class FixedValueConstraint(Constraint):
#... {{% skip %}}
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value
# {{% /skip %}}
    def __repr__(self):
        return f"{self.__class__.__name__}<{self.value}>"

#... {{% skip %}}
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
            constraint_set = ConstraintSet()
            setattr(instance, self.private_name, constraint_set)
        return constraint_set

    def __set__(self, instance, value):
        # if value is itself a ConstraintSet then use that
        if isinstance(value, ConstraintSet):
            setattr(instance, self.private_name, value)
            return

        # otherwise, grab the ConstraintSet from the instance
        constraint_set = self.__get__(instance) 
        constraint_set.reset_constraints()
        constraint_set.constrain_with(FixedValueConstraint(value))

class Point:
    x = ConstrainedValue()
    y = ConstrainedValue()

    def __init__(self, x=None, y=None):
        if x is not None: 
            self.x = x
        if y is not None : 
            self.y = y
# {{% /skip %}}
p = Point(1,2)
print(p.x) 
```
```
ConstraintSet(
    FixedValueConstraint<1>
)
```

Okay, so on to our new constraint. This `LinkedValueConstraint` will store a link to a `ConstraintSet`:

<!--phmdoctest-share-names-->
```python
class LinkedValueConstraint(Constraint):
    def __init__(self, constraint_set):
        self._constraint_set = constraint_set

    @property
    def constraint_set(self):
        return self._constraint_set
    
    def __repr__(self):
        return f"{self.__class__.__name__}<{self.constraint_set}>"
```

A quick test:

<!--phmdoctest-share-names-->
```python
p = Point(1,2)
c = LinkedValueConstraint(p.x)
print(c)
```
```
LinkedValueConstraint<ConstraintSet(
    FixedValueConstraint<1>
)>
```
So we can see now that our `LinkedValueConstraint` is linked to a `ConstraintSet` which contains a single constraint which is a `FixedValueConstraint` fixed at 1. This is helpful, but it would be even more helpful if we could link back to `p.x` itself. The output I would like to see is:

```
LinkedValueConstraint<p.x>
```

So let's have a look at what we can do with our `ConstraintSet` to give it a useful name. The list of all the constraints may well be useful so we'll leave that in `__repr__` but we can override `__str__` to use the name as an alternative. 

 We create the `ConstraintSet` in the `ConstrainedValue` class, and that is aware of the instance to which the `ConstraintSet` belongs, so at that point we can pass a name in. Let's update the constructor of `ConstraintSet` to take a name, and add the `__str__` method:


<!--phmdoctest-share-names-->
```python
class ConstraintSet:
    def __init__(self, name=""):
        self._constraints = []
        self._name = name
#... {{% skip %}}
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
# {{% /skip %}}
    def __str__(self):
        return self._name
```

And update `ConstrainedValue` to provide that name:
<!--phmdoctest-share-names-->
```python
class ConstrainedValue:
    """An object which can be passed around to represent a value."""

#... {{% skip %}}
    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"

#... {{% /skip %}}
    def __get__(self, instance, typ=None):
        # grab the ConstraintSet from the instance
        constraint_set = getattr(instance, self.private_name, None)
        
        # If the instance didn't have an initialized ConstraintSet then
        # give it one
        if constraint_set is None:
            constraint_set = ConstraintSet(f"{instance.name}.{self.public_name}")
            setattr(instance, self.private_name, constraint_set)
        return constraint_set

#... {{% skip %}}
    def __set__(self, instance, value):
        # if value is itself a ConstraintSet then use that
        if isinstance(value, ConstraintSet):
            setattr(instance, self.private_name, value)
            return

        constraint_set = self.__get__(instance)
        constraint_set.reset_constraints()
        constraint_set.constrain_with(FixedValueConstraint(value))
#... {{% /skip %}}
```
And finally, [as there is no easy way to work out the name of the variable to which an instance has been defined](https://stackoverflow.com/questions/1690400/getting-an-instance-name-inside-class-init), we'll update the `Point` class to optionally take a name at creation time. This is less than ideal, and I may well fix it later, but I don't want us to get distracted away from constraint modelling!

<!--phmdoctest-share-names-->
```python
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
```

Check that worked:

<!--phmdoctest-share-names-->
```python
p = Point('p',1,2)
print(p.x)
c = LinkedValueConstraint(p.x)
print(c)
```
```
p.x
LinkedValueConstraint<p.x>
```

Now let's stitch this into our `__set__` method in the `ConstrainedValue` class:
<!--phmdoctest-share-names-->
```python
class ConstrainedValue:
    """An object which can be passed around to represent a value."""
#... {{% skip %}}
    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, instance, typ=None):
        constraint_set = getattr(instance, self.private_name, None)
        if constraint_set is None:
            constraint_set = ConstraintSet(f"{instance.name}.{self.public_name}")
            setattr(instance, self.private_name, constraint_set)
        return constraint_set

#... {{% /skip %}}
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

#... {{% skip %}}
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
# {{% /skip %}}
```

Finally let's tweak our `resolve` method on the `ConstraintSet` so that it understands what a `LinkedValueConstraint` is. Remember this method is only a place holder and the real logic of calculating values we'll deal with in a later article.

<!--phmdoctest-share-names-->
```python
class ConstraintSet:
    def __init__(self, name=""):
        self._constraints = []
        self._name = name
#... {{% skip %}}
    def constrain_with(self, constraint):
        """Add a constraint to this objects list of constraints."""
        self._constraints.append(constraint)

    def reset_constraints(self):
        """Removes the existing constraints from the constraint set"""
        self._constraints = []

# {{% /skip %}}
    def resolve(self):
        """Naive implementation to aid testing"""
        for constraint in self._constraints:
            if isinstance(constraint, FixedValueConstraint):
                return constraint.value
            if isinstance(constraint, LinkedValueConstraint):
                return constraint.constraint_set.resolve()

        raise UnderconstrainedError("Fixed Value has not been provided.")
    
#... {{% skip %}}
    def __repr__(self):
        retval = "ConstraintSet("
        if len(self._constraints) == 0:
            retval += ")"
            return retval

        for constraint in self._constraints:
            retval += f"\n    {constraint}"
        retval += "\n)"
        return retval 
# {{% /skip %}}
    def __str__(self):
        return self._name
```
And now everything should work end to end:
<!--phmdoctest-share-names-->
```python
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

Are we done? Not just yet. We can constrain a property to another property, which is helpful, but there are scenarios where we'll need to do more than that. We may, for example, wish to constrain a `Point` to being on a line, or on the circumference of a circle. To do this, constraining the properties independently isn't sufficient. We need to be able to constrain the `Point` (or indeed any shape) and have that constraint, in turn, constrain the properties of that `Point` (or shape). This article, is however, long enough. We shall deal with that in part two!