import unittest
from pydit.types.dependency_proxy import DependencyProxy

class Number:
    def __init__(self, value):
        self.value = value

    def __add__(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value)
        return Number(self.value + other)
    
    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value)
        return Number(self.value - other)
    
    def __mul__(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value)
        return Number(self.value * other)
    
    def __eq__(self, other):
        if isinstance(other, Number):
            return self.value == other.value
        return self.value == other

    def __len__(self):
        return self.value

    def __getitem__(self, key):
        return self.value + key

    def __repr__(self):
        return f"Number({self.value})"
        
    def __bool__(self):
        return bool(self.value)

class ProxyArithmeticTest(unittest.TestCase):
    def test_add(self):
        num = Number(10)
        proxy = DependencyProxy(num)
        
        result = proxy + 5
        self.assertEqual(result.value, 15)
        
        result2 = proxy + Number(5)
        self.assertEqual(result2.value, 15)

        proxy2 = DependencyProxy(12)
        self.assertEqual(proxy2 + 10, 22)
        
    def test_radd(self):
        num = Number(10)
        proxy = DependencyProxy(num)
        
        result = 5 + proxy
        self.assertEqual(result.value, 15)

        proxy2 = DependencyProxy(12)
        self.assertEqual(10 + proxy2, 22)

    def test_sub(self):
        num = Number(10)
        proxy = DependencyProxy(num)
        
        result = proxy - 5
        self.assertEqual(result.value, 5)

        proxy2 = DependencyProxy(12)
        self.assertEqual(proxy2 - 10, 2)

    def test_mul(self):
        num = Number(10)
        proxy = DependencyProxy(num)
        
        result = proxy * 5
        self.assertEqual(result.value, 50)

        proxy2 = DependencyProxy(12)
        self.assertEqual(proxy2 * 10, 120)
        
    def test_eq_with_primitive(self):
        num = Number(10)
        proxy = DependencyProxy(num)
        
        self.assertTrue(proxy == 10)
        self.assertFalse(proxy == 5)
        
    def test_eq_with_object(self):
        num = Number(10)
        proxy = DependencyProxy(num)
        
        self.assertTrue(proxy == Number(10))
        self.assertFalse(proxy == Number(5))
        
    def test_len(self):
        num = Number(10)
        proxy = DependencyProxy(num)
        
        self.assertEqual(len(proxy), 10)
        
    def test_getitem(self):
        num = Number(10)
        proxy = DependencyProxy(num)
        
        self.assertEqual(proxy[5], 15)
        
    def test_bool(self):
        num = Number(10)
        proxy = DependencyProxy(num)
        self.assertTrue(bool(proxy))
        
        num_zero = Number(0)
        proxy_zero = DependencyProxy(num_zero)
        self.assertFalse(bool(proxy_zero))
