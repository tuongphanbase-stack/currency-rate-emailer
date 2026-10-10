"""Run: python -m unittest discover tests

The market, fawazahmed0 and fxratesapi.com sources used to ask for VND-base
rates and invert them. open.er-api.com rounds those to 6 decimal places (USD
came back as 0.000039), so the market USD rate was stuck at 1 / 0.000039 =
25,641 VND for every run. These tests serve fake API payloads that round the
same way and check every source now keeps full precision.
"""
import unittest
from unittest import mock
from urllib.parse import urlparse

from test_settings import load

# Units of each currency per 1 USD, i.e. what a USD-base API returns.
USD_TO_X = {
    "USD": 1.0,
    "VND": 26283.5,
    "EUR": 0.857143,
    "JPY": 151.234,
    "SGD": 1.2876,
    "KRW": 1378.91,
}
WATCHLIST = ["USD", "EUR", "JPY", "SGD", "KRW"]


def expected_vnd_per_unit(code):
    return USD_TO_X["VND"] / USD_TO_X[code]


def rates_for_base(base, lower=False):
    """What the APIs return for `base`. VND-base rates are rounded to 6
    decimal places, like open.er-api.com does."""
    rates = {}
    for code, per_usd in USD_TO_X.items():
        rate = per_usd / USD_TO_X[base]
        if base == "VND":
            rate = round(rate, 6)
        rates[code.lower() if lower else code] = rate
    return rates


def response(payload):
    resp = mock.Mock(status_code=200)
    resp.json.return_value = payload
    resp.raise_for_status.return_value = None
    return resp


def fake_get(url, headers=None, params=None, timeout=None):
    """Serves open.er-api.com, fawazahmed0/currency-api and fxratesapi.com."""
    parsed = urlparse(url)
    if parsed.hostname == "open.er-api.com":
        base = parsed.path.rsplit("/", 1)[-1]
        return response({"result": "success", "base_code": base, "rates": rates_for_base(base)})
    if parsed.path.endswith(".json"):  # fawazahmed0 (either mirror)
        base = parsed.path.rsplit("/", 1)[-1][:-len(".json")]
        return response({"date": "2026-10-10", base: rates_for_base(base.upper(), lower=True)})
    if parsed.hostname == "api.fxratesapi.com":
        wanted = params["currencies"].split(",")
        rates = {c: r for c, r in rates_for_base(params["base"]).items() if c in wanted}
        return response({"success": True, "base": params["base"], "rates": rates})
    raise AssertionError(f"unexpected URL {url}")


class FullPrecision(unittest.TestCase):
    def setUp(self):
        self.m = load({"WATCHLIST": ",".join(WATCHLIST)})
        patcher = mock.patch.object(self.m.requests, "get", side_effect=fake_get)
        self.get = patcher.start()
        self.addCleanup(patcher.stop)

    def assert_full_precision(self, rates):
        self.assertEqual(set(rates), set(WATCHLIST))
        for code in WATCHLIST:
            # Within a thousandth of a VND; the rounded VND-base rates were off
            # by up to several hundred VND (USD: 25,641 instead of 26,283.5).
            self.assertAlmostEqual(rates[code], expected_vnd_per_unit(code), delta=0.001, msg=code)

    def test_market_rates(self):
        rates = self.m.fetch_market_rates()
        self.assert_full_precision(rates)
        self.assertEqual(rates["USD"], 26283.5)

    def test_fawaz_rates(self):
        self.assert_full_precision(self.m.fetch_fawaz_rates())

    def test_fawaz_fallback_mirror(self):
        primary = self.m.FAWAZ_PRIMARY_URL

        def primary_down(url, **kwargs):
            if url == primary:
                raise self.m.requests.ConnectionError("down")
            return fake_get(url, **kwargs)

        self.get.side_effect = primary_down
        with mock.patch.object(self.m.time, "sleep"):
            self.assert_full_precision(self.m.fetch_fawaz_rates())

    def test_fxrates_rates(self):
        self.assert_full_precision(self.m.fetch_fxrates_rates())

    def test_small_moves_are_not_lost(self):
        # A 0.1% move in USD/VND must show up; on the VND base it rounded away.
        first = self.m.fetch_market_rates()["USD"]
        with mock.patch.dict(USD_TO_X, {"VND": USD_TO_X["VND"] * 1.001}):
            second = self.m.fetch_market_rates()["USD"]
        self.assertAlmostEqual(second / first, 1.001, places=9)


class VndPerUnit(unittest.TestCase):
    def setUp(self):
        self.m = load({"WATCHLIST": "USD,EUR,THB"})

    def test_usd_is_one_when_the_base_is_left_out(self):
        rates = self.m.vnd_per_unit({"VND": 26283.5, "EUR": 0.857143})
        self.assertEqual(rates, {"USD": 26283.5, "EUR": 26283.5 / 0.857143})

    def test_lowercase_keys(self):
        rates = self.m.vnd_per_unit({"usd": 1, "vnd": 26283.5, "thb": 32.5}, key=str.lower)
        self.assertEqual(rates, {"USD": 26283.5, "THB": 26283.5 / 32.5})

    def test_missing_vnd_is_an_error(self):
        # The caller turns this into "source failed" instead of wrong numbers.
        with self.assertRaises(RuntimeError):
            self.m.vnd_per_unit({"USD": 1, "EUR": 0.857143})


if __name__ == "__main__":
    unittest.main()
