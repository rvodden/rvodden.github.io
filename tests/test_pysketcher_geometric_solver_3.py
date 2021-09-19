"""pytest file built from content/posts/2021-09-16-pysketcher-geometric-solver-3.md"""
import pytest

from phmdoctest.fixture import managenamespace
from phmdoctest.functions import _phm_compare_exact


def test_code_34(managenamespace):
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


    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_236_output_257(capsys, managenamespace):
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

    _phm_expected_str = """\
Line(l)<Point(),Point()>
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_301(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_371(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_484_output_504(capsys, managenamespace):
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

    _phm_expected_str = """\
Line(l)<Point(
    LinkedValueConstraint<p>
),Point()>
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_519():
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

    # Caution- no assertions.


def test_code_543(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_573(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_607(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_650(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_703_output_710(capsys, managenamespace):
    p = Point('p')
    c = CoincidentConstraint(p)
    l = Line('l')
    l.constrain_with(c)
    print(repr(l))

    _phm_expected_str = """\
Line(l)<Point(
    InfluencedConstraint<CoincidentConstraint<p>>
),Point(
    InfluencedConstraint<CoincidentConstraint<p>>
)>
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_723(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_749_output_761(capsys, managenamespace):
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

    _phm_expected_str = """\
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
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_790(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_844(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_912(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_1010_output_1022(capsys, managenamespace):
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

    _phm_expected_str = """\
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

"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_1064():
    # Firstly we should be able to define a point specifying nothing at all:
    p = Point()

    # The it would be great to have a simple constructor which can accept some values:
    p = Point(1,2)

    # Finally we should be able to specify parameters by nae:
    p = Point(x=1, y=2, name='p')

    # Caution- no assertions.


def test_code_1080(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_1191_output_1201(capsys, managenamespace):

    l = Line()
    print(l._generate_name())
    print(l._generate_name())
    p = Point()
    print(p._generate_name())
    print(p._generate_name())


    _phm_expected_str = """\
Line0
Line1
Point0
Point1
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_1241():
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

    # Caution- no assertions.


def test_code_1264():
    class ConstraintSet:
        def __init__(self, *args, **kwargs):
            self._constraints = []
            name = kwargs.pop('name') if 'name' in kwargs else self._generate_name
            self._name = name
            # ... ConstraintSet code
        # ...

    # Caution- no assertions.


def test_code_1278():
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

    # Caution- no assertions.


def test_code_1314():
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
            

    # Caution- no assertions.


def test_code_1368(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_1586(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_1645_output_1658(capsys, managenamespace):
    # Firstly we should be able to define a point specifying nothing at all:
    p = Point()
    print(repr(p))

    # The it would be great to have a simple constructor which can accept some values:
    p = Point(1,2)
    print(repr(p))

    # Finally we should be able to specify parameters by nae:
    p = Point(x=1, y=2, name='p')
    print(repr(p))

    _phm_expected_str = """\
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

"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_1708_output_1772(capsys, managenamespace):
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

    _phm_expected_str = """\
Point0: Point(
    Point0.x: Scalar()<
        FixedValueConstraint<1>
    >
    Point0.y: Scalar()<
        FixedValueConstraint<2>
    >
)
<>

"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_1787_output_1801(capsys, managenamespace):
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

    _phm_expected_str = """\
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

"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_1829(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_1935_output_1949(capsys, managenamespace):
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

    _phm_expected_str = """\
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

"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())
