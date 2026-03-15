
import sys
import copy
from django.template import context

def apply_patches():
    """
    Apply patches for compatibility with Python 3.14.
    Django 4.2's Context class uses copy(super()), which fails in Python 3.14
    with 'AttributeError: super object has no attribute dicts'.
    """
    if sys.version_info >= (3, 14):
        print("Applying Python 3.14 compatibility patch for Django Context...")
        
        def patched_copy(self):
            # Create a new instance of the same class without calling __init__
            cls = self.__class__
            duplicate = cls.__new__(cls)
            # Copy all instance variables except 'dicts'
            for key, value in self.__dict__.items():
                if key != 'dicts':
                    setattr(duplicate, key, copy.copy(value))
            # Handle 'dicts' specifically as Django does
            duplicate.dicts = self.dicts[:]
            return duplicate

        context.BaseContext.__copy__ = patched_copy
