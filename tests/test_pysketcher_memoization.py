"""pytest file built from content/posts/2021-09-06-pysketcher-memoization.md"""
import pytest

from phmdoctest.fixture import managenamespace
from phmdoctest.functions import _phm_compare_exact


def test_code_43(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_64(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_88(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_114(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_144_output_149(capsys, managenamespace):
    p = Point(1,2)
    print(type(p.x).__name__)
    print(type(p.y).__name__)

    _phm_expected_str = """\
ConstrainedValue
ConstrainedValue
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_159(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_185_output_191(capsys, managenamespace):
    p = Point(1,2)
    print(f"p.x is {p.x.resolve()}")
    print(f"p.y is {p.y.resolve()}")

    _phm_expected_str = """\
p.x is 1
p.y is 2
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_216_output_223(capsys, managenamespace):
    p = Point(1,2)
    q = Point()
    q.x = p.x
    print(f"q.x is {q.x.resolve().resolve()}")

    _phm_expected_str = """\
q.x is 1
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_231(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_268_output_274(capsys, managenamespace):
    p = Point(1,2)
    q = Point()
    q.x = p.x
    print(f"q.x is {q.x.resolve()}")

    _phm_expected_str = """\
q.x is 1
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_286_output_311(capsys):
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


    _phm_expected_str = """\
##
I am a set method
##
I am a get method
1
##
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)


def test_code_323_output_376(capsys, managenamespace):
    class ConstrainedValue():
        """An object which can be passed around to represent a value."""
    #... {{% skip %}}
        def constrain_with(self, constraint):
            """Add a constraint to this objects list of constraints."""
            self._constraints.append(constraint)
    
        def reset_constraints(self):
            """Removes the exsting constraints from the constraint set"""
            self._constraints = []
    

        def resolve(self):
            """Nieve implementation to aid testing"""
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

    _phm_expected_str = """\
p.x is 1
q.x is 1
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_384_output_390(capsys, managenamespace):
    p = Point(1,2)
    q = Point(2,3)
    print(f"p.x is {p.x.resolve()}")
    print(f"q.x is {q.x.resolve()}")

    _phm_expected_str = """\
p.x is 2
q.x is 2
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_402(managenamespace):
    class ConstraintSet:
        def __init__(self):
            self._constraints = []
    
        def constrain_with(self, constraint):
            """Add a constraint to this objects list of constraints."""
            self._constraints.append(constraint)

        def reset_constraints(self):
            """Removes the exsting constraints from the constraint set"""
            self._constraints = []

        def resolve(self):
            """Nieve implementation to aid testing"""
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
        
            # If the instance didn't have an initialised ConstraintSet then
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


    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_464_output_470(capsys, managenamespace):
    p = Point(1,2)
    q = Point(2,3)
    print(f"p.x is {p.x.resolve()}")
    print(f"q.x is {q.x.resolve()}")

    _phm_expected_str = """\
p.x is 1
q.x is 2
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_478_output_485(capsys, managenamespace):
    p = Point(1,2)
    print(f"p.x is {p.x.resolve()}")
    q = Point()
    q.x = p.x
    print(f"q.x is {q.x.resolve()}")

    _phm_expected_str = """\
p.x is 1
q.x is 1
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_494_output_504(capsys, managenamespace):
    p = Point(1,2)
    print(f"p.x is {p.x.resolve()}")
    q = Point()
    q.x = p.x
    print(f"q.x is {q.x.resolve()}")
    p.x = 2
    print(f"p.x is {p.x.resolve()}")
    print(f"q.x is {q.x.resolve()}")

    _phm_expected_str = """\
p.x is 1
q.x is 1
p.x is 2
q.x is 2
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_520_output_608(capsys, managenamespace):
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

    _phm_expected_str = """\
ConstraintSet(
    FixedValueConstraint<1>
)
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_617(managenamespace):
    class LinkedValueConstraint(Constraint):
        def __init__(self, constraint_set):
            self._constraint_set = constraint_set

        @property
        def constraint_set(self):
            return self._constraint_set
    
        def __repr__(self):
            return f"{self.__class__.__name__}<{self.constraint_set}>"

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_633_output_638(capsys, managenamespace):
    p = Point(1,2)
    c = LinkedValueConstraint(p.x)
    print(c)

    _phm_expected_str = """\
LinkedValueConstraint<ConstraintSet(
    FixedValueConstraint<1>
)>
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_655(managenamespace):
    class ConstraintSet:
        def __init__(self, name=""):
            self._constraints = []
            self._name = name
    #... {{% skip %}}
        def constrain_with(self, constraint):
            """Add a constraint to this objects list of constraints."""
            self._constraints.append(constraint)

        def reset_constraints(self):
            """Removes the exsting constraints from the constraint set"""
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_694(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_729(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_750_output_756(capsys, managenamespace):
    p = Point('p',1,2)
    print(p.x)
    c = LinkedValueConstraint(p.x)
    print(c)

    _phm_expected_str = """\
p.x
LinkedValueConstraint<p.x>
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
    managenamespace(operation="update", additions=locals())


def test_code_763(managenamespace):
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

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_815(managenamespace):
    class ConstraintSet:
        def __init__(self, name=""):
            self._constraints = []
            self._name = name
    #... {{% skip %}}
        def constrain_with(self, constraint):
            """Add a constraint to this objects list of constraints."""
            self._constraints.append(constraint)

        def reset_constraints(self):
            """Removes the exsting constraints from the constraint set"""
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
    # {{% /skip %}}
        def __str__(self):
            return self._name

    # Caution- no assertions.
    managenamespace(operation="update", additions=locals())


def test_code_855_output_866(capsys, managenamespace):
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
