---
title: "Writing a Geometric Solver in Python - Part 3: Fixing our line and adding arithmetic"
series:
  - PySketcher Geometric Solver
categories:
  - python
  - pysketcher
  - geometry
  - solver
draft: true
description: >
    I describe, over the series, how to implement a geometric solver in
    Python. In this article we take the existing model and upgrade our `Line` object to use `ConstrainedValue`. We also look at adding arithmetic capability.
---

So far have a nice strong framework for expressing geometric constraints as `Constraint` objects,
and we have a clean way of applying these to our geometric objects. We have clear output when we ask
the various objects to `repr` themselves, and we have clear error messages when things don't quite
go to plan. Our constraints now support being reciprocal, and if we constraint one object to another
that will magically constraint the other object back to the original if we so wish. Where we left it
last time is that we needed to update our `ConincidentConstraint` object so that it implemented this
reciprocal feature, and to do that we needed to upgrade our `Line` object so that it could take
constraints. The code from the previous article can be found in [this
gist](https://gist.github.com/rvodden/2b1467693448a6159d7d625ba9ad905c).

## Upgrading our line.

To get us started in the last article we created a very simple line object:

<!--phmdoctest-share-names-->
```python
#... {{% skip %}}
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

Let's look at how we might upgrade that `Line` to use `ConstraintSet` so that we can apply
constraints to it. How's this for starters:

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

This is great stuff, we have a line which starts at a point and ends at a point. Let's try and play
around with it a bit.

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
```python {hl_lines=[4-5,14]}
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
            constraint_set = self._constraint_set_class(f"{instance.name}.{self.public_name}")
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
We also need to define an `__eq__` method to avoid repeating our stack overflow woes from last time,
so let's go ahead and do that now.

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

In order for our `CoincidentConstraint` to apply to a `Line` we must allow it to accept a `Point`.
That's a little more messy that it might at first appear, as we'll need to adapt our shiny new
`__eq__` method to consider this possibility, and the same for our `__repr__` method:

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

And now let's modify the `validate_object` method so that it checks for the correct object type, and
tweak `cascade_constraints` so that it cascades as well to a `Line` as it does to a `Point`:


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

Aha! Let's alter our `Line` `__repr__` method so that it includes the constraints at the `Line`
level:


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

Now we can see the constraints to which the parameters are bound, as well as those to which the
object is bound, or we can for the `Line` object at least. The `Point` object is a lot less
forthcoming, and on reflection its kind of annoying having to implement `__repr__` on every object
we define. Is there a way we can do this at the `ConstraintSet` level and just forget about
`__repr__` for the rest of time. We can if we make an assumption. I'm pretty sure that the
assumption is safe, but I'm also pretty sure that I've been bitten by every other assumption I've
ever made. Let's live dangerously and implement a generic `__repr__` method. If it bites us we can
reimplement it later.

I'm going to use the python built in `dir` function which accepts an object and returns a list of
its attributes. I'm then going to filter that list for those attributes which are of type
`ConstraintSet`. The assumption here being that the only attributes we're printing out are the ones
that are participating in our model, and all of those will be of type `ConstraintSet`. Let's see how
that goes:

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
    
    #... {{% /skip %}}
    def __repr__(self):
        parameters = [getattr(self, d) for d in dir(self) if isinstance(getattr(self, d), ConstraintSet)]
        parameters = list(set(parameters))
        parameters.sort(key=lambda x: x.name)
        retval = f"{self.name}: {self.__class__.__name__}"
        if len(parameters) == 0:
            retval += "()"
        else:
            paramstring = ""
            for parameter in parameters:
                paramstring += repr(parameter)
            retval += "(\n"
            retval += "    " + "    ".join([l for l in paramstring.splitlines(True)])
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
These are starting to look super clean! That apparently duplicated code in the `__init__` methods
hasn't escaped my attention, but I don't want to get distracted. Let's check that that last change worked:

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
    l.end: Point(
        l.end.x: ConstraintSet()<>
        l.end.y: ConstraintSet()<>
    )
    <
        InfluencedConstraint<CoincidentConstraint<p>>
    >
    l.start: Point(
        l.start.x: ConstraintSet()<>
        l.start.y: ConstraintSet()<>
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
