from gbe.duration import Duration
import nose.tools as nt
from django.test import TestCase


# unit tests for Duration
def test_minutes():
    duration = Duration(seconds=125)
    nt.assert_equal(2, duration.minutes())


def test_total_minutes():
    duration = Duration(hours=3, minutes=24)
    nt.assert_equal(204, duration.total_minutes())


def test_hours():
    duration = Duration(seconds=7215)
    nt.assert_equal(2, duration.hours())


def test_div_by_int():
    duration = Duration(seconds=7200)
    quotient = duration/2
    nt.assert_equal(1, quotient.hours())


def test_div_by_duration():
    duration = Duration(minutes=7200)
    dividend = Duration(minutes=3600)
    quotient = duration/dividend
    nt.assert_equal(2, quotient)


def test_div_by_bad_dividend():
    duration = Duration(seconds=25)
    foo = set([1, 2, 3])
    nt.assert_raises(TypeError, duration.__div__, duration, foo)


def test_floordiv_by_int():
    duration = Duration(seconds=7200)
    quotient = duration//2
    nt.assert_equal(1, quotient.hours())


def test_floordiv_by_duration():
    duration = Duration(minutes=7200)
    dividend = Duration(minutes=3600)
    quotient = duration//dividend
    nt.assert_equal(2, quotient)


def test_floordiv_by_bad_dividend():
    duration = Duration(seconds=25)
    foo = set([1, 2, 3])
    nt.assert_raises(TypeError, duration.__floordiv__, duration, foo)


def test_mod_by_duration():
    duration1 = Duration(minutes=5)
    duration2 = Duration(minutes=2)
    result = duration1 % duration2
    nt.assert_equal(1, result.minutes())


def test_mod_by_int():
    duration1 = Duration(minutes=5)
    result = duration1 % 120
    nt.assert_equal(1, result.minutes())


def test_mod_by_bad_dividend():
    duration = Duration(seconds=25)
    foo = set([1, 2, 3])
    nt.assert_raises(TypeError, duration.__mod__, duration, foo)


def test_divmod_by_int():
    duration = Duration(500)
    nt.assert_equal((duration / 50, duration % 50),
                    duration.__divmod__(50))


def test_divmod_by_duration():
    duration1 = Duration(500)
    duration2 = Duration(10)
    nt.assert_equal((duration1 / duration2, duration1 % duration2),
                    duration1.__divmod__(duration2))


def test_default_string_representation():
    duration = Duration(hours=12,
                        minutes=47,
                        seconds=56)
    nt.assert_equal("12:47:56", duration.__str__())


def test_set_format():
    duration = Duration(days=7,
                        hours=12,
                        minutes=47,
                        seconds=56)
    duration.set_format("{0:0>2}:{1:0>2}:{2:0>2}:{3:0>2}")
    nt.assert_equal("07:12:47:56", duration.__str__())
