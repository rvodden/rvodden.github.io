"""pytest file built from content/posts/2021-09-16-pysketcher-geometric-solver-3.md"""
import pytest

from phmdoctest.fixture import managenamespace
from phmdoctest.functions import _phm_compare_exact


def test_code_32(managenamespace):
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


def test_code_234_output_255(capsys, managenamespace):
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


def test_code_299(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_369(managenamespace):
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


def test_code_482_output_502(capsys, managenamespace):
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


def test_code_515():
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


def test_code_539(managenamespace):
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


def test_code_569(managenamespace):
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


def test_code_603(managenamespace):
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


def test_code_646(managenamespace):
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


def test_code_699_output_706(capsys, managenamespace):
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


def test_code_719(managenamespace):
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


def test_code_745_output_757(capsys, managenamespace):
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


def test_code_786(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_853(managenamespace):
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


def test_code_951_output_963(capsys, managenamespace):
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

"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())
