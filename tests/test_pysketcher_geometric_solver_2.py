"""pytest file built from content/posts/2021-09-16-pysketcher-geometric-solver-2.md"""
import pytest

from phmdoctest.fixture import managenamespace
from phmdoctest.functions import _phm_compare_exact


def test_code_44_output_172(capsys, managenamespace):
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

    _phm_expected_str = """\
p.x is p.x
p.x resolves to 1
q.x is ConstraintSet(
    LinkedValueConstraint<p.x>
)
q.x resolves to 1
Now p.x has changed, q.x resolves to 2
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_196_output_210(capsys, managenamespace):
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

    _phm_expected_str = """\
Line<(0,1),(2,3)>
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_220(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_246_output_263(capsys, managenamespace):
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

    _phm_expected_str = """\
ConstraintSet(
    CoincidentConstraint<Line<(1,2),(3,4)>>
)
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_278_output_341(capsys, managenamespace):
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

    _phm_expected_str = """\
Point(
    CoincidentConstraint<Line<(1,2),(3,4)>>
)
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_353_output_359(capsys):
    l = Line(1,2,3,4)
    p = Point('p')
    p.constrain_with(CoincidentConstraint(l))
    print(repr(p.x))

    _phm_expected_str = """\
ConstraintSet()
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)


def test_code_403(managenamespace):
    from abc import ABC, abstractmethod

    class Constraint(ABC):
        """Used to restrict that value of a ```ConstrainedValue```."""

        @abstractmethod
        def constraint_callback(self, instance):
            raise NotImplementedError("`constraint_callback` must be implemented explicitly.")

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_421(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_456(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_557(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_577(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_599_output_606(capsys, managenamespace):
    l = Line(1,2,3,4)
    p = Point('p')
    p.constrain_with(CoincidentConstraint(l))
    print(f"p is {repr(p)}")
    print(f"p.x is {repr(p.x)}")

    _phm_expected_str = """\
p is Point(
    CoincidentConstraint<Line<(1,2),(3,4)>>
)
p.x is ConstraintSet(
    InfluencedConstraint<CoincidentConstraint<Line<(1,2),(3,4)>>>
)
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_647(managenamespace):

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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_698_output_706(capsys, managenamespace):
    p = Point('p')
    q = Point('q')

    q.x = p.x
    print(f"p.x is {repr(p.x)}")
    print(f"q.x is {repr(q.x)}")

    _phm_expected_str = """\
p.x is ConstraintSet()
q.x is ConstraintSet(
    LinkedValueConstraint<p.x>
)
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_720_output_729(capsys, managenamespace):
    p = Point('p')
    q = Point('q')

    q.x = p.x
    p.x = q.x
    print(f"p.x is {repr(p.x)}")
    print(f"q.x is {repr(q.x)}")

    _phm_expected_str = """\
p.x is ConstraintSet(
    LinkedValueConstraint<q.x>
)
q.x is ConstraintSet(
    LinkedValueConstraint<p.x>
)
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_746(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_797(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_825_output_833(capsys, managenamespace):
    p = Point()
    l = LinkedValueConstraint(p.x)
    m = LinkedValueConstraint(p.x)
    n = LinkedValueConstraint(q.x)
    print(f"l == m: {l == m}")
    print(f"l == n: {l == n}")

    _phm_expected_str = """\
l == m: True
l == n: False
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_842(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_963(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_988(managenamespace):
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


    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_1019(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_1120_output_1128(capsys, managenamespace):
    p = Point('p')
    q = Point('q')

    q.x = p.x
    print(f"p.x is {repr(p.x)}")
    print(f"q.x is {repr(q.x)}")

    _phm_expected_str = """\
p.x is ConstraintSet(
    LinkedValueConstraint<q.x>
)
q.x is ConstraintSet(
    LinkedValueConstraint<p.x>
)
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_1145(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_1177(managenamespace):
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
                f" be applied to `ConstraintSet`, it cannot be applied to `{point.__class__.__name__}`")

        def apply_reciprocal_constraint(self, instance):
            pass
    
        def cascade_constraints(self, instance):
            pass

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())
