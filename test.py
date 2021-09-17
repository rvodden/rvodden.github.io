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

class UnderConstrainedError(RuntimeError):
    pass

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
        if not isinstance(self, ConstraintSet):
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
    
    @property
    def name(self):
        return self._name

class ConstrainedValue:
    """An object which can be passed around to represent a value."""

    def __init__(self, constraint_set_class):
        self._constraint_set_class = constraint_set_class
    
    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, instance, typ=None):
        # grab the ConstraintSet from the instance
        constraint_set = getattr(instance, self.private_name, None)
        
        # If the instance didn't have an initialized ConstraintSet then
        # give it one
        if constraint_set is None:
            constraint_set = self._constraint_set_class(f"{instance.name}.{self.public_name}")
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
    
    def __repr__(self):
        return f"Line({self._name})<{repr(self.start)},{repr(self.end)}>"

l = Line("l")
print(l.name)
p = Point('p',1,2)
print(p)
print(p.x)
print(p.y)
l.start = p
print(repr(l))