---
title: "Writing a Geometric Solver in Python - Part 3: Fixing our line"
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
    Python. In this article we take the existing model and upgrade our `Line` object to use
    `ConstrainedValue`. In so doing, we remove a chunk of duplicated code, and implementing a
    generic `__repr__` method and a generic `__init__` method at the `ConstraintSet` level.
---

So far we have a nice strong framework for expressing geometric constraints as `Constraint` objects, and we have a clean way of applying these to our geometric objects. We have clear output when we ask the various objects to `repr` themselves, and we have clear error messages when things don't quite go to plan. Our constraints now support being reciprocal, and if we constraint one object to another that will magically constraint the other object back to the original if we so wish. Where we left it last time is that we needed to update our `ConincidentConstraint` object so that it implemented this reciprocal feature, and to do that we needed to upgrade our `Line` object so that it could take constraints. The code from the previous article can be found in [this gist](https://gist.github.com/rvodden/2b1467693448a6159d7d625ba9ad905c).
## Upgrading our line.

To get us started in the last article we created a very simple line object:

<!--phmdoctest-share-names-->
```python
#... {{% skip %}}
from abc import ABC, abstractmethod

class Constraint(ABC):
    """Used to restrict that value of a `ConstrainedValue`."""

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

class FixedValueConstraint(Constraint):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.value}>"

    def validate_object(self, instance):
        pass

    def apply_reciprocal_constraint(self, instance):
        pass

    def cascade_constraints(self, instance):
        pass

class LinkedValueConstraint(Constraint):
    def __init__(self, constraint_set):
        self._constraint_set = constraint_set

    @property
    def constraint_set(self):
        return self._constraint_set

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.constraint_set}>"

    def validate_object(self, instance):
        if not isinstance(instance, ConstraintSet):
            raise InvalidConstraintException(f"{self.__class__.__name__} can only"
            f" be applied to `ConstraintSet`, it cannot be applied to `{instance.__class__.__name__}`")

    def apply_reciprocal_constraint(self, instance):
        self.constraint_set.constrain_with(LinkedValueConstraint(instance))

    def cascade_constraints(self, instance):
        pass

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.constraint_set == other.constraint_set

class InvalidConstraintException(RuntimeError):
    """Indicates that a constraint has been applied to an object which doesn't make sense."""

class InfluencedConstraint(Constraint):
    def __init__(self, constraint):
        self._constraint = constraint

    @property
    def constraint(self):
        return self._constraint

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.constraint}>"

    def validate_object(self, instance):
        if not isinstance(instance, ConstraintSet):
            raise InvalidConstraintException(f"{self.__class__.__name__} can only"
            f" be applied to `ConstraintSet`, it cannot be applied to `{instance.__class__.__name__}`")

    def apply_reciprocal_constraint(self, instance):
        pass

    def cascade_constraints(self, instance):
        pass

class ConstraintSet:
    def __init__(self, name=""):
        self._constraints = []
        self._name = name

    def constrain_with(self, constraint):
        constraint.validate_object(self)
        if constraint in self._constraints:
            return
        """Add a constraint to this objects list of constraints."""
        self._constraints.append(constraint)
        constraint.cascade_constraints(self)
        constraint.apply_reciprocal_constraint(self)

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

class Line:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __repr__(self):
        return f"Line<({self.x1},{self.y1}),({self.x2},{self.y2})>"

```

Let's look at how we might upgrade that `Line` to use `ConstraintSet` so that we can apply constraints to it. How's this for starters:
<!--phmdoctest-share-names-->
```python
class Line(ConstraintSet):
    def __init__(self, name="", start=None, end=None):
        super().__init__(name=name)
        self._start = start if start is not None else Point(name + ".start")
        self._end = end if end is not None else Point(name + ".end")

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    def __repr__(self):
        return f"Line({self._name})<{repr(self.start)},{repr(self.end)}>"

l = Line("l")
print(repr(l))
```
```
Line(l)<Point(),Point()>
```

This is great stuff, we have a line which starts at a point and ends at a point. Let's try and play around with it a bit.
<!--phmdoctest-share-names-->
<!--phmdoctest-skip-->
```python
l = Line("l")
p = Point(1,2)
l.start = p
print(repr(l))
```
```
AttributeError: can't set attribute
```

Disaster! The issue here is that we didn't define setters for our `start` and `end` parameters. But we didn't have to do that when we defined out `Point` object, so what is going on? Let's revisit that definition of `Point`:

<!--phmdoctest-skip-->
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

So we used `ConstrainedValue()` at the class level when we defined our `Point` and that looks very neat. Can we do something similar with `Line` to specify our `Point` parameters? We could define a `ConstrainedPoint` object, but this would get very tiresome once we have a large collection of objects. Let's instead modify `ConstrainedValue` so that it accepts a subclass of `ConstraintSet` and then use that to specify the parameters of `Line`:


<!--phmdoctest-share-names-->
```python
class ConstrainedValue:
    """An object which can be passed around to represent a value."""

    def __init__(self, constraint_set_class):
        self._constraint_set_class = constraint_set_class
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
            constraint_set = self._constraint_set_class(name=f"{instance.name}.{self.public_name}")
            setattr(instance, self.private_name, constraint_set)
        return constraint_set
    #... {{% skip %}}
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

class Line(ConstraintSet):
    start = ConstrainedValue(Point)
    end = ConstrainedValue(Point)

    def __init__(self, name="", start=None, end=None):
        super().__init__(name=name)
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end

    def __repr__(self):
        return f"Line({self._name})<{repr(self.start)},{repr(self.end)}>"
```
And see how it flies:

<!--phmdoctest-share-names-->
<!--phmdoctest-skip-->
```python
l = Line("l")
p = Point('p',1,2)
l.start = p
print(repr(l))
```
```
AttributeError: 'Line' object has no attribute 'name'
```

Whoops! Strangely we chose to define the `name` property on the `Point` class even though `_name` is implemented in `ConstraintSet`. Let's extract that up to `ConstraintSet`, which will simplify `Point` a little.

<!--phmdoctest-share-names-->
```python
class ConstraintSet:
    #... {{% skip %}}
    def __init__(self, name=""):
        self._constraints = []
        self._name = name

    def constrain_with(self, constraint):
        constraint.validate_object(self)
        if constraint in self._constraints:
            return
        """Add a constraint to this objects list of constraints."""
        self._constraints.append(constraint)
        constraint.cascade_constraints(self)
        constraint.apply_reciprocal_constraint(self)

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

        raise UnderConstrainedError("Fixed Value has not been provided.")

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

    #... {{% /skip %}}
    @property
    def name(self):
        return self._name
    #... {{% skip %}}

class LinkedValueConstraint(Constraint):
    def __init__(self, constraint_set):
        self._constraint_set = constraint_set

    @property
    def constraint_set(self):
        return self._constraint_set

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.constraint_set}>"

    def validate_object(self, instance):
        if not isinstance(instance, ConstraintSet):
            raise InvalidConstraintException(f"{self.__class__.__name__} can only"
            f" be applied to `ConstraintSet`, it cannot be applied to `{instance.__class__.__name__}`")

    def apply_reciprocal_constraint(self, instance):
        self.constraint_set.constrain_with(LinkedValueConstraint(instance))

    def cascade_constraints(self, instance):
        pass

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.constraint_set == other.constraint_set

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
            f" be applied to `ConstraintSet`, it cannot be applied to `{instance.__class__.__name__}`")

    def apply_reciprocal_constraint(self, instance):
        pass

    def cascade_constraints(self, instance):
        pass
    #... {{% /skip %}}
class Point(ConstraintSet):
    x = ConstrainedValue(ConstraintSet)
    y = ConstrainedValue(ConstraintSet)

    def __init__(self, name="", x=None, y=None):
        super().__init__(self)
        self._name = name
        if x is not None:
            self.x = x
        if y is not None :
            self.y = y
```
And have another go at defining `Line`:
<!--phmdoctest-share-names-->
```python
class Line(ConstraintSet):
    start = ConstrainedValue(Point)
    end = ConstrainedValue(Point)

    def __init__(self, name="", start=None, end=None):
        super().__init__(name=name)
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})<{repr(self.start)},{repr(self.end)}>"

l = Line('l')
p = Point('p', 1,2)
l.start = p
print(repr(l))
```
```
Line(l)<Point(
    LinkedValueConstraint<p>
),Point()>
```

Woohoo! This is exactly what we were after.
## Returning to the Constraint

So now we must upgrade our `CoincidentConstraint` so that it provides a reciprocal constraint and implements the three methods with introduced to the `Constraint` class in the last article. A question we must first answer is what should we call our reciprocal constraint. It seems to me to be equally acceptable to say that a line is coincident with a point as it is to say that a point is coincident with a line. So our natural language tells us that we should use the same constraint object for both the constraint and its reciprocal, which means we need to make our `CoincidentConstraint` object apply to a `Line` as well as a `Point`.

There are other circumstances where this kind of relationship is appropriate. For example if a line is tangent to a circle, then it is equally acceptable to say that the circle is tangent to a line, so it feels like this is a pattern which we may well use again.

Let's remind ourselves what our existing `CoincidentConstraint` class looks like:

```python
class CoincidentConstraint(Constraint):
    def __init__(self, line):
        self._line = line

    @property
    def line(self):
        return self._line

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.line}>"

    def constraint_callback(self, point):
        if not isinstance(point, Point):
            raise InvalidConstraintException(f"{self.__class__.__name__} can only"
            f" be applied to `Point`, it cannot be applied to `{point.__class__.__name__}`")
        point.x.constrain_with(InfluencedConstraint(self))
        point.y.constrain_with(InfluencedConstraint(self))
```

Let's first of all add the new methods, without considering the addition of the `Line` functionality, and we'll leave the `apply_reciprocal_constraint` method empty for the moment.


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

    def validate_object(self, instance):
        if not isinstance(point, Point):
            raise InvalidConstraintException(f"{self.__class__.__name__} can only"
            f" be applied to `Point`, it cannot be applied to `{instance.__class__.__name__}`")

    def apply_reciprocal_constraint(self, instance):
        pass

    def cascade_constraints(self, instance):
        point.x.constrain_with(InfluencedConstraint(self))
        point.y.constrain_with(InfluencedConstraint(self))
```

We also need to define an `__eq__` method to avoid repeating our stack overflow woes from last time, so let's go ahead and do that now.
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

    def validate_object(self, instance):
        if not isinstance(point, Point):
            raise InvalidConstraintException(f"{self.__class__.__name__} can only"
            f" be applied to `Point`, it cannot be applied to `{instance.__class__.__name__}`")

    def apply_reciprocal_constraint(self, instance):
        pass

    def cascade_constraints(self, instance):
        point.x.constrain_with(InfluencedConstraint(self))
        point.y.constrain_with(InfluencedConstraint(self))
    #... {{% /skip %}}
    def __eq__(self, other):
        return type(other) == type(self) and self.line == other.line
```

In order for our `CoincidentConstraint` to apply to a `Line` we must allow it to accept a `Point`. That's a little more messy that it might at first appear, as we'll need to adapt our shiny new `__eq__` method to consider this possibility, and the same for our `__repr__` method:
<!--phmdoctest-share-names-->
```python
class CoincidentConstraint(Constraint):
    def __init__(self, object):
        self._line = object if type(object) == Line else None
        self._point = object if type(object) == Point else None
    #... {{% skip %}}

    @property
    def line(self):
        return self._line

    #... {{% /skip %}}
    @property
    def point(self):
        return self._point

    def __repr__(self):
        if self.line is not None:
            return f"{self.__class__.__name__}<{self.line}>"
        return f"{self.__class__.__name__}<{self.point}>"

    #... {{% skip %}}
    def validate_object(self, instance):
        if not isinstance(point, Point):
            raise InvalidConstraintException(f"{self.__class__.__name__} can only"
            f" be applied to `Point`, it cannot be applied to `{instance.__class__.__name__}`")

    def apply_reciprocal_constraint(self, instance):
        pass

    def cascade_constraints(self, instance):
        point.x.constrain_with(InfluencedConstraint(self))
        point.y.constrain_with(InfluencedConstraint(self))
    #... {{% /skip %}}
    def __eq__(self, other):
        return type(other) == type(self) and self.line == other.line and self.point == other.point
```

And now let's modify the `validate_object` method so that it checks for the correct object type, and tweak `cascade_constraints` so that it cascades as well to a `Line` as it does to a `Point`:

<!--phmdoctest-share-names-->
```python
class CoincidentConstraint(Constraint):
    #... {{% skip %}}
    def __init__(self, object):
        self._line = object if type(object) == Line else None
        self._point = object if type(object) == Point else None

    @property
    def line(self):
        return self._line

    @property
    def point(self):
        return self._point

    def __repr__(self):
        if self.line is not None:
            return f"{self.__class__.__name__}<{self.line}>"
        return f"{self.__class__.__name__}<{self.point}>"
    #... {{% /skip %}}

    def validate_object(self, instance):
        if self._line is not None:
            if not isinstance(instance, Point):
                raise InvalidConstraintException(f"{self.__class__.__name__} which has been"
                " assigned a Line can only be applied to Point, it cannot be applied to"
                f" `{instance.__class__.__name__}`")
        else:
            if not isinstance(instance, Line):
                raise InvalidConstraintException(f"{self.__class__.__name__} which has been"
                " assigned a Point can only be applied to Line, it cannot be applied to"
                f" `{instance.__class__.__name__}`")

    #... {{% skip %}}
    def apply_reciprocal_constraint(self, instance):
        pass

    def cascade_constraints(self, instance):
        if self.line is not None:
            # if we've been assigned a line, we should be applied to a point
            instance.x.constrain_with(InfluencedConstraint(self))
            instance.y.constrain_with(InfluencedConstraint(self))
            return
        # and vice versa
        instance.start.constrain_with(InfluencedConstraint(self))
        instance.end.constrain_with(InfluencedConstraint(self))

    def __eq__(self, other):
        return type(other) == type(self) and self.line == other.line and self.point == other.point
    #... {{% /skip %}}
```

<!--phmdoctest-share-names-->
```python
p = Point('p')
c = CoincidentConstraint(p)
l = Line('l')
l.constrain_with(c)
print(repr(l))
```
```
Line(l)<Point(
    InfluencedConstraint<CoincidentConstraint<p>>
),Point(
    InfluencedConstraint<CoincidentConstraint<p>>
)>
```

Aha! Let's alter our `Line` `__repr__` method so that it includes the constraints at the `Line` level:

<!--phmdoctest-share-names-->
```python
class Line(ConstraintSet):
    #... {{% skip %}}
    start = ConstrainedValue(Point)
    end = ConstrainedValue(Point)

    def __init__(self, name="", start=None, end=None):
        super().__init__(name=name)
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end

    #... {{% /skip %}}
    def __repr__(self):
        repr_string = f"{self.__class__.__name__}({self.name})<{repr(self.start)},{repr(self.end)}>"
        if len(self._constraints) == 0:
            return repr_string + "()"
        repr_string += "(\n"
        for constraint in self._constraints:
            repr_string += f"    {constraint}\n"
        repr_string += ")"
        return repr_string
```

<!--phmdoctest-share-names-->
```python
p = Point('p')
c = CoincidentConstraint(p)
l = Line('l')
l.constrain_with(c)
print(repr(l))
m = Line('m')
d = CoincidentConstraint(m)
q = Point('q')
q.constrain_with(d)
print(repr(q))
```
```
Line(l)<Point(
    InfluencedConstraint<CoincidentConstraint<p>>
),Point(
    InfluencedConstraint<CoincidentConstraint<p>>
)>(
    CoincidentConstraint<p>
)
Point(
    CoincidentConstraint<m>
)
```

Now we can see the constraints to which the parameters are bound, as well as those to which the object is bound, or we can for the `Line` object at least. The `Point` object is a lot less forthcoming, and on reflection its kind of annoying having to implement `__repr__` on every object we define. Is there a way we can do this at the `ConstraintSet` level and just forget about `__repr__` for the rest of time. We can if we make an assumption. I'm pretty sure that the assumption is safe, but I'm also pretty sure that I've been bitten by every other assumption I've ever made. Let's live dangerously and implement a generic `__repr__` method. If it bites us we can re-implement it later.

## A More Generic Representation

To write something generic, we need a list of the `ConstrainedValue` attributes in our class. Let's tweak our `ConstrainedValue` class so that it keeps track:

<!--phmdoctest-share-names-->
```python {hl_lines=[4-5,14]}
class ConstrainedValue:
    """An object which can be passed around to represent a value."""
    #... {{% skip %}}
    def __init__(self, constraint_set_class):
        self._constraint_set_class = constraint_set_class
    #... {{% /skip %}}
    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"
        # append the name to the list of ConstrainedSets on the class
        # creating that list if it doesn't exist
        try:
            constraint_sets = owner._constraint_sets
        except AttributeError:
            constraint_sets = []
            owner._constraint_sets = constraint_sets
        finally:
            owner._constraint_sets.append(self.public_name)
    #... {{% skip %}}
    def __get__(self, instance, typ=None):
        # grab the ConstraintSet from the instance
        constraint_set = getattr(instance, self.private_name, None)

        # If the instance didn't have an initialized ConstraintSet then
        # give it one
        if constraint_set is None:
            constraint_set = self._constraint_set_class(name=f"{instance.name}.{self.public_name}")
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
```

Now we can iterate through that list in our `__repr__` method. For the avoidance of doubt, the assumption here being that the only attributes we're printing out are the ones that are participating in our model, and all of those will be of type `ConstraintSet`. Let's see how that goes:

<!--phmdoctest-share-names-->
```python class ConstraintSet: #... {{% skip %}}
def __init__(self, name=""): self._constraints = [] self._name = name

    def constrain_with(self, constraint):
        constraint.validate_object(self)
        if constraint in self._constraints:
            return
        """Add a constraint to this objects list of constraints."""
        self._constraints.append(constraint)
        constraint.cascade_constraints(self)
        constraint.apply_reciprocal_constraint(self)

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

        raise UnderConstrainedError("Fixed Value has not been provided.")

    #... {{% /skip %}}
    def __repr__(self):
        retval = f"{self.name}: {self.__class__.__name__}"
        try:
            num_constraint_sets = len(self._constraint_sets)
        except AttributeError:
            num_constraint_sets = 0
        if num_constraint_sets == 0:
            retval += "()"
        else:
            constraint_set_string = ""
            for constraint_set_name in self._constraint_sets:
                constraint_set_string += repr(getattr(self,constraint_set_name))
            retval += "(\n"
            retval += "    " + "    ".join([l for l in constraint_set_string.splitlines(True)])
            retval += ")\n"

        if len(self._constraints) == 0:
            retval += "<>\n"
        else:
            retval += "<\n"
            for constraint in self._constraints:
                retval += "    " + "    ".join([l for l in repr(constraint).splitlines(True)])
            retval += "\n>\n"
        return retval
    #... {{% skip %}}

    def __str__(self):
        return self._name

    @property
    def name(self):
        return self._name
    #... {{% /skip %}}
```
And redefine `Point` and `Line` without the `__repr__` method:

<!--phmdoctest-share-names-->
```python
class Point(ConstraintSet):
    x = ConstrainedValue(ConstraintSet)
    y = ConstrainedValue(ConstraintSet)

    def __init__(self, name="", x=None, y=None):
        super().__init__(self)
        self._name = name
        if x is not None:
            self.x = x
        if y is not None :
            self.y = y

class Line(ConstraintSet):
    start = ConstrainedValue(Point)
    end = ConstrainedValue(Point)

    def __init__(self, name="", start=None, end=None):
        super().__init__(name=name)
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end

#... {{% skip %}}
class InfluencedConstraint(Constraint):
    def __init__(self, constraint):
        self._constraint = constraint

    @property
    def constraint(self):
        return self._constraint

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.constraint}>"

    def validate_object(self, instance):
        if not isinstance(instance, ConstraintSet):
            raise InvalidConstraintException(f"{self.__class__.__name__} can only"
            f" be applied to `ConstraintSet`, it cannot be applied to `{instance.__class__.__name__}`")

    def apply_reciprocal_constraint(self, instance):
        pass

    def cascade_constraints(self, instance):
        pass

class CoincidentConstraint(Constraint):
    def __init__(self, object):
        self._line = object if type(object) == Line else None
        self._point = object if type(object) == Point else None

    @property
    def line(self):
        return self._line

    @property
    def point(self):
        return self._point

    def __repr__(self):
        if self.line is not None:
            return f"{self.__class__.__name__}<{self.line}>"
        return f"{self.__class__.__name__}<{self.point}>"

    def validate_object(self, instance):
        if self._line is not None:
            if not isinstance(instance, Point):
                raise InvalidConstraintException(f"{self.__class__.__name__} which has been"
                " assigned a Line can only be applied to Point, it cannot be applied to"
                f" `{instance.__class__.__name__}`")
        else:
            if not isinstance(instance, Line):
                raise InvalidConstraintException(f"{self.__class__.__name__} which has been"
                " assigned a Point can only be applied to Line, it cannot be applied to"
                f" `{instance.__class__.__name__}`")

    def apply_reciprocal_constraint(self, instance):
        pass

    def cascade_constraints(self, instance):
        if self.line is not None:
            # if we've been assigned a line, we should be applied to a point
            instance.x.constrain_with(InfluencedConstraint(self))
            instance.y.constrain_with(InfluencedConstraint(self))
            return
        # and vice versa
        instance.start.constrain_with(InfluencedConstraint(self))
        instance.end.constrain_with(InfluencedConstraint(self))

    def __eq__(self, other):
        return type(other) == type(self) and self.line == other.line and self.point == other.point
#... {{% /skip %}}
```

These are starting to look super clean! That apparently duplicated code in the `__init__` methods hasn't escaped my attention, but I don't want to get distracted. Let's check that that last change worked:
<!--phmdoctest-share-names-->
```python
p = Point('p')
c = CoincidentConstraint(p)
l = Line('l')
l.constrain_with(c)
print(repr(l))
m = Line('m')
d = CoincidentConstraint(m)
q = Point('q')
q.constrain_with(d)
print(repr(q))
```
```
l: Line(
    l.start: Point(
        l.start.x: ConstraintSet()<>
        l.start.y: ConstraintSet()<>
    )
    <
        InfluencedConstraint<CoincidentConstraint<p>>
    >
    l.end: Point(
        l.end.x: ConstraintSet()<>
        l.end.y: ConstraintSet()<>
    )
    <
        InfluencedConstraint<CoincidentConstraint<p>>
    >
)
<
    CoincidentConstraint<p>
>

q: Point(
    q.x: ConstraintSet()<
        InfluencedConstraint<CoincidentConstraint<m>>
    >
    q.y: ConstraintSet()<
        InfluencedConstraint<CoincidentConstraint<m>>
    >
)
<
    CoincidentConstraint<m>
>

```

This is a really great output. We can really see how the hierarchy of our constraints is building up. So what about that initializer? Well it turns out we can play a pretty similar trick.

## Generic Initialization

Firstly let's describe the behavior we're after, using our `Point` object as an example:

<!--phmdoctest-skip-names-->
```python
# Firstly we should be able to define a point specifying nothing at all:
p = Point()

# The it would be great to have a simple constructor which can accept some values:
p = Point(1,2)

# Finally we should be able to specify parameters by nae:
p = Point(x=1, y=2, name='p')
```

In order to achieve this, in particular the 2nd example, we need to be able to provide a default name. Something like `Point1`, when no name is specified, but obviously unique for each point created. Let's add a `generate_name` method to `ConstraintSet` which can do this for us:

<!--phmdoctest-share-names-->
```python
class ConstraintSet:
    #... {{% skip %}}
    def __init__(self, name=""):
        self._constraints = []
        self._name = name

    def constrain_with(self, constraint):
        constraint.validate_object(self)
        if constraint in self._constraints:
            return
        """Add a constraint to this objects list of constraints."""
        self._constraints.append(constraint)
        constraint.cascade_constraints(self)
        constraint.apply_reciprocal_constraint(self)

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

        raise UnderConstrainedError("Fixed Value has not been provided.")

    def __repr__(self):
        retval = f"{self.name}: {self.__class__.__name__}"
        try:
            num_constraint_sets = len(self._constraint_sets)
        except AttributeError:
            num_constraint_sets = 0
        if num_constraint_sets == 0:
            retval += "()"
        else:
            constraint_set_string = ""
            for constraint_set_name in self._constraint_sets:
                constraint_set_string += repr(getattr(self,constraint_set_name))
            retval += "(\n"
            retval += "    " + "    ".join([l for l in constraint_set_string.splitlines(True)])
            retval += ")\n"

        if len(self._constraints) == 0:
            retval += "<>\n"
        else:
            retval += "<\n"
            for constraint in self._constraints:
                retval += "    " + "    ".join([l for l in repr(constraint).splitlines(True)])
            retval += "\n>\n"
        return retval

    def __str__(self):
        return self._name

    @property
    def name(self):
        return self._name
    #... {{% /skip %}}
    @classmethod
    def _generate_name(cls):
        try:
            index = cls._counter
        except AttributeError:
            index = 0
        cls._counter = index + 1
        return f"{cls.__name__}{index}"
    #... {{% skip %}}
class Point(ConstraintSet):
    x = ConstrainedValue(ConstraintSet)
    y = ConstrainedValue(ConstraintSet)

    def __init__(self, name="", x=None, y=None):
        super().__init__(name=name)
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y

class Line(ConstraintSet):
    start = ConstrainedValue(Point)
    end = ConstrainedValue(Point)

    def __init__(self, name="", start=None, end=None):
        super().__init__(name=name)
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end
    #... {{% /skip %}}
```

It's worth reflecting on how this method works, as its a little subtle. Firstly this method is decorated with `@classmethod` This means that the class is passed in as the first parameter instead of the instance. By convention this is called `cls` to distinguish from `self` in a normal method where the instance is passed in. By using a class method, and the value of `cls` we can  have a different counter for `Point` and `Line`. Next try and assign the the value of `_counter` to `index`, if we've not yet initialized it this will throw an `AttributeError`, we catch that and set `index` to zero. This is an example of "EAFP" or ["Easier to ask forgiveness than permission"](https://docs.python.org/3.5/glossary.html#term-eafp) coding. This rule is not part of PEP20, but it is well established python coding style. Now we set the value of `_counter` to one more than `index`, which will initialize counter if its not already, and finally construct our default name out of `type(self).__name__` and our `index`. Let's give it a quick test. The `_` prefix by convention means that this is a private method which shouldn't be called from outside of the class, but python does nothing to enforce that, so our test is nice and easy to write:

<!--phmdoctest-share-names-->
```python

l = Line()
print(l._generate_name())
print(l._generate_name())
p = Point()
print(p._generate_name())
print(p._generate_name())
```
```
Line0
Line1
Point0
Point1
```

Perfect. Now let's write a generic initializer on `ConstraintSet` which means we don't have to write initializers on all our objects. Let's remind ourselves of our target behavior:

<!--phmdoctest-skip-->
```python
# Firstly we should be able to define a point specifying nothing at all:
p = Point()

# The it would be great to have a simple constructor which can accept some values:
p = Point(1,2)

# Finally we should be able to specify parameters by nae:
p = Point(x=1, y=2, name='p')
```

The final behavior is the easiest to implement. We will iterate through the `_constraint_sets` we built for our `__repr__` method and assign values if matching `kwargs` have been passed. We `pop` them off `kwargs` and then pass the remaining `kwargs` to `super().__init__ `. This last part is important as it preserves our ability to subclass. To pluck an example out of thing air, we might want to create a "DoubleLine" class which draw two lines right next to each other, and takes the distance between the two lines as a parameter:

<!--phmdoctest-skip-->
```python
class DoubleLine(Line):
    distance = ConstrainedValue(ConstraintSet)

dl = DoubleLine(start=Point(1,2), end=Point(2,3), distance=0.1)
```

If we miss out the "pop and pass" part of our initializer, then `Line` will never be sent the correct values, and `start` and `end` would never be set. A first stab at this generic initializer looks like this:
```python
class ConstraintSet:
    def __init__(self, *args, **kwargs):
        self._constraints = []
        try:
            constraint_sets = self._constraint_sets
        except AttributeError:
            # _constraint_sets is not set if `self` is a top level ConstraintSet
            # so this is not an error, there's just nothing to do.
            pass
        else:
            for constraint_set_name in self._constraint_sets:
                try:
                    setattr(self, constraint_set_name, kwargs.pop(constraint_set_name))
                except KeyError:
                    # Not a problem if a value for _constraint_set_name has not been provided.
                    pass
        super().__init__(*args, **kwargs)
```

`name` is not a `ConstraintSet` so won't appear in our list, so we must explicitly handle that. It's tempting to write something like this:
```python
class ConstraintSet:
    def __init__(self, *args, **kwargs):
        self._constraints = []
        name = kwargs.pop('name') if 'name' in kwargs else self._generate_name
        self._name = name
        # ... ConstraintSet code
    # ...
```

However if we did write this, then the call to `super().__init__()` would not have a `name` parameter, so that call would immediately overwrite our `name` with a `_generate_name` value. To prevent this we must check to see if `_name` is already defined, and only provide a default value if it is not.
```python
class ConstraintSet:
    def __init__(self, *args, **kwargs):
        self._constraints = []
        try:
            if not hasattr(self._name):
                self._name = kwargs.pop('name')
        except IndexError: # 'name' has not been provided as a kwargs, so provide a default value
            self._name = self._generate_name()
        super().__init__(*args, **kwargs)
    #... ConstraintSet code {{% skip %}}
        try:
            constraint_sets = self._constraint_sets
        except AttributeError:
            # _constraint_sets is not set if `self` is a top level ConstraintSet
            # so this is not an error, there's just nothing to do.
            pass
        else:
            for constraint_set_name in self._constraint_sets:
                try:
                    setattr(self, constraint_set_name, kwargs.pop(constraint_set_name))
                except IndexError:
                    # Not a problem if a value for _constraint_set_name has not been provided.
                    pass
    #... {{% /skip %}}
```

Lastly we need to consider `args`. To maximize code reuse, the best thing to do is to work out which `ConstraintSet` each `arg` belongs to, and add it explicitly to `**kwargs`. The initializers are called from the most specific subclass up to the most general. Our `DoubleLine` for example would have its initializer called first, and then the initializer for `Line` and finally the initializer for `ConstraintSet`. We therefore want to start at the end of our list and work towards the start, so that more specific `args` go at the end of the call. In order to make this work we'll need to split out `arg` processing into a separate method so that we can call it further up the initializer. Also, by default, `args` is passed to us a `tuple` which is immutable, so we'll need to change it to something we can remove values from. A `List` will do:

```python
    def __init__(self, *args, **kwargs):
        self._constraints = []
        # converts args to a list, so that we can mutate it
        args = list(args)
    #... name code
        kwargs |= self._process_args(args)
    #... ConstraintSet code {{% skip %}}
        try:
            constraint_sets = self._constraint_sets
        except AttributeError:
            # _constraint_sets is not set if `self` is a top level ConstraintSet
            # so this is not an error, there's just nothing to do.
            pass
        else:
            for constraint_set_name in self._constraint_sets:
                try:
                    setattr(self, constraint_set_name, kwargs.pop(constraint_set_name))
                except IndexError:
                    # Not a problem if a value for _constraint_set_name has not been provided.
                    pass
        try:
            if not hasattr(self, '_name'):
                self._name = kwargs.pop('name')
        except KeyError: # 'name' has not been provided as a kwargs, so provide a default value
            self._name = self._generate_name()
        super().__init__(*args, **kwargs)
    #... {{% /skip %}}

    def _process_args(self, args):
        # give our parent a chance to nab the arguments before us:
        try:
            super().__process_args(args)
        except AttributeError:
            # not a problem if `super() doesn't have `__process_args`
            # just means we're near the top of the tree
            pass

        retval = dict()
        # iterate backwards through our constraints, and add a
        # dictionary entry for each arg whilst one exists
        try:
            for constraint_set_name in self._constraint_sets[::-1]:
                retval[constraint_name] = args.pop()
        except IndexError:
            # just means we got to the end of the list
            pass
        return retval

```

Putting these together gives us a mammoth initializer, so I've broken out the `kwargs` processing into a separate method too, to give anyone reading this code half a chance of following it:

<!--phmdoctest-share-names-->
```python
class ConstraintSet:

    def __init__(self, *args, **kwargs):
        self._constraints = []
        # convert args to a list, so that we can mutate it
        args = list(args)
        """give ourselves a sensible name unless one is provided."""
        try:
            if not hasattr(self, '_name'):
                self._name = kwargs.pop('name')
        except KeyError: # 'name' has not been provided as a kwargs, so provide a default value
            self._name = self._generate_name()
        """copy args into the appropriate place in kwargs"""
        kwargs |= self._process_args(args)
        """assign each kwarg to its matching ConstraintSet"""
        self._process_kwargs(kwargs)
        super().__init__(*args, **kwargs)

    def _process_args(self, args):
        # give our parent a chance to nab the arguments before us:
        try:
            super().__process_args(args)
        except AttributeError:
            # not a problem if `super() doesn't have `__process_args`
            # just means we're near the top of the tree
            pass

        retval = dict()
        # iterate backwards through our constraints, and add a
        # dictionary entry for each arg whilst one exists
        try:
            for constraint_set_name in self._constraint_sets[::-1]:
                retval[constraint_set_name] = args.pop()
        except (IndexError, AttributeError):
            # just means we got to the end of the list
            pass

        return retval

    def _process_kwargs(self, kwargs):
        try:
            constraint_sets = self._constraint_sets
        except AttributeError:
            # _constraint_sets is not set if `self` is a top level ConstraintSet
            # so this is not an error, there's just nothing to do.
            pass
        else:
            for constraint_set_name in self._constraint_sets:
                try:
                    setattr(self, constraint_set_name, kwargs.pop(constraint_set_name))
                except KeyError:
                    # Not a problem if a value for _constraint_set_name has not been provided.
                    pass

    #... {{% skip %}}
    def constrain_with(self, constraint):
        constraint.validate_object(self)
        if constraint in self._constraints:
            return
        """Add a constraint to this objects list of constraints."""
        self._constraints.append(constraint)
        constraint.cascade_constraints(self)
        constraint.apply_reciprocal_constraint(self)

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

        raise UnderConstrainedError("Fixed Value has not been provided.")

    def __repr__(self):
        retval = f"{self.name}: {self.__class__.__name__}"
        try:
            num_constraint_sets = len(self._constraint_sets)
        except AttributeError:
            num_constraint_sets = 0
        if num_constraint_sets == 0:
            retval += "()"
        else:
            constraint_set_string = ""
            for constraint_set_name in self._constraint_sets:
                constraint_set_string += repr(getattr(self,constraint_set_name))
            retval += "(\n"
            retval += "    " + "    ".join([l for l in constraint_set_string.splitlines(True)])
            retval += ")\n"

        if len(self._constraints) == 0:
            retval += "<>\n"
        else:
            retval += "<\n"
            for constraint in self._constraints:
                retval += "    " + "    ".join([l for l in repr(constraint).splitlines(True)]) + "\n"
            retval += ">\n"
        return retval

    def __str__(self):
        return self._name

    @property
    def name(self):
        return self._name

    @classmethod
    def _generate_name(cls):
        try:
            index = cls._counter
        except AttributeError:
            index = 0
        cls._counter = index + 1
        return f"{cls.__name__}{index}"

class LinkedValueConstraint(Constraint):
    def __init__(self, constraint_set):
        self._constraint_set = constraint_set

    @property
    def constraint_set(self):
        return self._constraint_set

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.constraint_set}>"

    def validate_object(self, instance):
        if not isinstance(instance, ConstraintSet):
            raise InvalidConstraintException(f"{self.__class__.__name__} can only"
            f" be applied to `ConstraintSet`, it cannot be applied to `{instance.__class__.__name__}`")

    def apply_reciprocal_constraint(self, instance):
        self.constraint_set.constrain_with(LinkedValueConstraint(instance))

    def cascade_constraints(self, instance):
        pass

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.constraint_set == other.constraint_set

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
            f" be applied to `ConstraintSet`, it cannot be applied to `{instance.__class__.__name__}`")

    def apply_reciprocal_constraint(self, instance):
        pass

    def cascade_constraints(self, instance):
        pass

class ConstrainedValue:
    """An object which can be passed around to represent a value."""

    def __init__(self, constraint_set_class):
        self._constraint_set_class = constraint_set_class

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"
        # append the name to the list of ConstrainedSets on the class
        # creating that list if it doesn't exist
        try:
            constraint_sets = owner._constraint_sets
        except AttributeError:
            constraint_sets = []
            owner._constraint_sets = constraint_sets
        finally:
            owner._constraint_sets.append(self.public_name)

    def __get__(self, instance, typ=None):
        # grab the ConstraintSet from the instance
        constraint_set = getattr(instance, self.private_name, None)

        # If the instance didn't have an initialized ConstraintSet then
        # give it one
        if constraint_set is None:
            constraint_set = self._constraint_set_class(name=f"{instance.name}.{self.public_name}")
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
```

Redefine `Point` and `Line` without their initializers...
<!--phmdoctest-share-names-->
```python
class Point(ConstraintSet):
    x = ConstrainedValue(ConstraintSet)
    y = ConstrainedValue(ConstraintSet)

class Line(ConstraintSet):
    start = ConstrainedValue(Point)
    end = ConstrainedValue(Point)

#... {{% skip %}}
class CoincidentConstraint(Constraint):
    def __init__(self, object):
        self._line = object if type(object) == Line else None
        self._point = object if type(object) == Point else None

    @property
    def line(self):
        return self._line

    @property
    def point(self):
        return self._point

    def __repr__(self):
        if self.line is not None:
            return f"{self.__class__.__name__}<{self.line}>"
        return f"{self.__class__.__name__}<{self.point}>"

    def validate_object(self, instance):
        if self._line is not None:
            if not isinstance(instance, Point):
                raise InvalidConstraintException(f"{self.__class__.__name__} which has been"
                " assigned a Line can only be applied to Point, it cannot be applied to"
                f" `{instance.__class__.__name__}`")
        else:
            if not isinstance(instance, Line):
                raise InvalidConstraintException(f"{self.__class__.__name__} which has been"
                " assigned a Point can only be applied to Line, it cannot be applied to"
                f" `{instance.__class__.__name__}`")

    def apply_reciprocal_constraint(self, instance):
        pass

    def cascade_constraints(self, instance):
        if self.line is not None:
            # if we've been assigned a line, we should be applied to a point
            instance.x.constrain_with(InfluencedConstraint(self))
            instance.y.constrain_with(InfluencedConstraint(self))
            return
        # and vice versa
        instance.start.constrain_with(InfluencedConstraint(self))
        instance.end.constrain_with(InfluencedConstraint(self))

    def __eq__(self, other):
        return type(other) == type(self) and self.line == other.line and self.point == other.point
#... {{% /skip %}}
```
Let's test this by revisiting our behaviors:
<!--phmdoctest-share-names-->
```python
# Firstly we should be able to define a point specifying nothing at all:
p = Point()
print(repr(p))

# The it would be great to have a simple constructor which can accept some values:
p = Point(1,2)
print(repr(p))

# Finally we should be able to specify parameters by nae:
p = Point(x=1, y=2, name='p')
print(repr(p))
```
```
Point0: Point(
    Point0.x: ConstraintSet()<>
    Point0.y: ConstraintSet()<>
)
<>

Point1: Point(
    Point1.x: ConstraintSet()<
        FixedValueConstraint<1>
    >
    Point1.y: ConstraintSet()<
        FixedValueConstraint<2>
    >
)
<>

p: Point(
    p.x: ConstraintSet()<
        FixedValueConstraint<1>
    >
    p.y: ConstraintSet()<
        FixedValueConstraint<2>
    >
)
<>

```

This is pretty incredible stuff. We've managed to abstract all our functionality into our `ConstrainedValue` and `ConstraintSet` classes so that we have this super clean and easy to use developer interface. The only thing which bugs me slightly. Have another look at this listing:

<!--phmdoctest-skip-->
```python
class Point(ConstraintSet):
    x = ConstrainedValue(ConstraintSet)
    y = ConstrainedValue(ConstraintSet)

class Line(ConstraintSet):
    start = ConstrainedValue(Point)
    end = ConstrainedValue(Point)
```

To my mind, `ConstrainedValue(Point)` is intuitive. It clearly says that we'd like a constrained value and that it should be of type `Point`. `ConstrainedValue(ConstraintSet)` doesn't have the same feel however, it really isn't clear what type the value is. Let's fix that by adding an alias clas to `ConstrainedSet` which has a more appropriate name for the end user:

<!--phmdoctest-share-names-->
```python
class Scalar(ConstraintSet):
    """Alias for ConstraintSet to provide more intuitive name"""
    pass

class Point(ConstraintSet):
    x = ConstrainedValue(Scalar)
    y = ConstrainedValue(Scalar)

#... {{% skip %}}
class Line(ConstraintSet):
    start = ConstrainedValue(Point)
    end = ConstrainedValue(Point)

class CoincidentConstraint(Constraint):
    def __init__(self, object):
        self._line = object if type(object) == Line else None
        self._point = object if type(object) == Point else None

    @property
    def line(self):
        return self._line

    @property
    def point(self):
        return self._point

    def __repr__(self):
        if self.line is not None:
            return f"{self.__class__.__name__}<{self.line}>"
        return f"{self.__class__.__name__}<{self.point}>"

    def validate_object(self, instance):
        if self._line is not None:
            if not isinstance(instance, Point):
                raise InvalidConstraintException(f"{self.__class__.__name__} which has been"
                " assigned a Line can only be applied to Point, it cannot be applied to"
                f" `{instance.__class__.__name__}`")
        else:
            if not isinstance(instance, Line):
                raise InvalidConstraintException(f"{self.__class__.__name__} which has been"
                " assigned a Point can only be applied to Line, it cannot be applied to"
                f" `{instance.__class__.__name__}`")

    def apply_reciprocal_constraint(self, instance):
        pass

    def cascade_constraints(self, instance):
        if self.line is not None:
            # if we've been assigned a line, we should be applied to a point
            instance.x.constrain_with(InfluencedConstraint(self))
            instance.y.constrain_with(InfluencedConstraint(self))
            return
        # and vice versa
        instance.start.constrain_with(InfluencedConstraint(self))
        instance.end.constrain_with(InfluencedConstraint(self))

    def __eq__(self, other):
        return type(other) == type(self) and self.line == other.line and self.point == other.point

#... {{% /skip %}}
p = Point(1,2)
print(repr(p))
```
```
Point0: Point(
    Point0.x: Scalar()<
        FixedValueConstraint<1>
    >
    Point0.y: Scalar()<
        FixedValueConstraint<2>
    >
)
<>

```
Let's just quickly check that we've not broken anything:

<!--phmdoctest-share-names-->
```python
#... {{% skip %}}
Line._counter = 0
Point._counter = 0
Scalar._counter = 0
#... {{% /skip %}}
p = Point()
c = CoincidentConstraint(p)
l = Line()
l.constrain_with(c)
q = Point()
l.start = q
print(repr(l))
```
```
Line0: Line(
    Line0.start: Point(
        Line0.start.x: Scalar()<>
        Line0.start.y: Scalar()<>
    )
    <
        LinkedValueConstraint<Point1>
    >
    Line0.end: Point(
        Line0.end.x: Scalar()<>
        Line0.end.y: Scalar()<>
    )
    <
        InfluencedConstraint<CoincidentConstraint<Point0>>
    >
)
<
    CoincidentConstraint<Point0>
>

```

Small bug, looks like the `LinkedValueConstraint` has nuked the `InfluencedConstraint` from `Line0.end`.  This is because our `__set__` method in `ConstrainedValue` calls `reset_constraints` which probably seemed like a good idea at the time, but now looks more like a bug. Let's remove that call:

<!--phmdoctest-share-names-->
```python
class ConstrainedValue:
    """An object which can be passed around to represent a value."""
    #... {{% skip %}}
    def __init__(self, constraint_set_class):
        self._constraint_set_class = constraint_set_class

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"
        # append the name to the list of ConstrainedSets on the class
        # creating that list if it doesn't exist
        try:
            constraint_sets = owner._constraint_sets
        except AttributeError:
            constraint_sets = []
            owner._constraint_sets = constraint_sets
        finally:
            owner._constraint_sets.append(self.public_name)

    def __get__(self, instance, typ=None):
        # grab the ConstraintSet from the instance
        constraint_set = getattr(instance, self.private_name, None)

        # If the instance didn't have an initialized ConstraintSet then
        # give it one
        if constraint_set is None:
            constraint_set = self._constraint_set_class(name=f"{instance.name}.{self.public_name}")
            setattr(instance, self.private_name, constraint_set)
        return constraint_set
    #... {{% /skip %}}
    def __set__(self, instance, value):
        # Grab the ConstraintSet from the instance
        constraint_set = self.__get__(instance, None)

        # if the value we've been asked to assign is a ConstraintSet
        # then add a LinkedValueConstraint:
        if isinstance(value, ConstraintSet):
            constraint_set.constrain_with(LinkedValueConstraint(value))
            return

        # otherwise use a FixedValueConstraint to constrain to the provided
        # value
        constraint_set.constrain_with(FixedValueConstraint(value))

#... {{% skip %}}
class Scalar(ConstraintSet):
    """Alias for ConstraintSet to provide more intuitive name"""
    pass

class Point(ConstraintSet):
    x = ConstrainedValue(Scalar)
    y = ConstrainedValue(Scalar)

class Line(ConstraintSet):
    start = ConstrainedValue(Point)
    end = ConstrainedValue(Point)

class CoincidentConstraint(Constraint):
    def __init__(self, object):
        self._line = object if type(object) == Line else None
        self._point = object if type(object) == Point else None

    @property
    def line(self):
        return self._line

    @property
    def point(self):
        return self._point

    def __repr__(self):
        if self.line is not None:
            return f"{self.__class__.__name__}<{self.line}>"
        return f"{self.__class__.__name__}<{self.point}>"

    def validate_object(self, instance):
        if self._line is not None:
            if not isinstance(instance, Point):
                raise InvalidConstraintException(f"{self.__class__.__name__} which has been"
                " assigned a Line can only be applied to Point, it cannot be applied to"
                f" `{instance.__class__.__name__}`")
        else:
            if not isinstance(instance, Line):
                raise InvalidConstraintException(f"{self.__class__.__name__} which has been"
                " assigned a Point can only be applied to Line, it cannot be applied to"
                f" `{instance.__class__.__name__}`")

    def apply_reciprocal_constraint(self, instance):
        pass

    def cascade_constraints(self, instance):
        if self.line is not None:
            # if we've been assigned a line, we should be applied to a point
            instance.x.constrain_with(InfluencedConstraint(self))
            instance.y.constrain_with(InfluencedConstraint(self))
            return
        # and vice versa
        instance.start.constrain_with(InfluencedConstraint(self))
        instance.end.constrain_with(InfluencedConstraint(self))

    def __eq__(self, other):
        return type(other) == type(self) and self.line == other.line and self.point == other.point
#... {{% /skip %}}
```
<!--phmdoctest-share-names-->
```python
#... {{% skip %}}
Line._counter = 0
Point._counter = 0
Scalar._counter = 0
#... {{% /skip %}}
p = Point()
c = CoincidentConstraint(p)
l = Line()
l.constrain_with(c)
q = Point()
l.start = q
print(repr(l))
```
```
Line0: Line(
    Line0.start: Point(
        Line0.start.x: Scalar()<>
        Line0.start.y: Scalar()<>
    )
    <
        InfluencedConstraint<CoincidentConstraint<Point0>>
        LinkedValueConstraint<Point1>
    >
    Line0.end: Point(
        Line0.end.x: Scalar()<>
        Line0.end.y: Scalar()<>
    )
    <
        InfluencedConstraint<CoincidentConstraint<Point0>>
    >
)
<
    CoincidentConstraint<Point0>
>

```

Phew! We made it! We now have a super powerful little framework with which we can model constraints. It's really worth reflecting on what we've achieved here. Not only have we implemented all that power, but if we compare the implementation of our `Point` with the naive implementation we started with at the beginning of part 1, you'll see its actually simpler to implement using our framework than without.

In the next article we'll look at adding some more constraints into the mix. In particular we'll look at how we can do some simple arithmetic operations with out `ConstraintSet`.
