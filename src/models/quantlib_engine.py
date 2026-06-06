import QuantLib as ql
from dataclasses import dataclass
from datetime import date


@dataclass
class MarketParams:
    spot: float
    strike: float
    risk_free_rate: float      # annualized, e.g. 0.045
    dividend_yield: float      # annualized, e.g. 0.015
    volatility: float          # annualized, e.g. 0.25
    maturity: date             # expiration date (calendar date)
    valuation_date: date       # “today” for pricing
    is_call: bool              # True = call, False = put


class QuantLibEngine:
    def __init__(self, calendar: ql.Calendar | None = None, day_counter: ql.DayCounter | None = None):
        self.calendar = calendar or ql.UnitedStates()
        self.day_counter = day_counter or ql.Actual365Fixed()

    def _build_process(self, params: MarketParams) -> ql.BlackScholesMertonProcess:
        valuation = ql.Date(params.valuation_date.day,
                            params.valuation_date.month,
                            params.valuation_date.year)
        maturity = ql.Date(params.maturity.day,
                           params.maturity.month,
                           params.maturity.year)

        ql.Settings.instance().evaluationDate = valuation

        spot_handle = ql.QuoteHandle(ql.SimpleQuote(params.spot))

        rf_curve = ql.YieldTermStructureHandle(
            ql.FlatForward(valuation, params.risk_free_rate, self.day_counter)
        )
        div_curve = ql.YieldTermStructureHandle(
            ql.FlatForward(valuation, params.dividend_yield, self.day_counter)
        )
        vol_curve = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(valuation, self.calendar, params.volatility, self.day_counter)
        )

        return ql.BlackScholesMertonProcess(spot_handle, div_curve, rf_curve, vol_curve), maturity

    def _build_option(self, params: MarketParams) -> ql.VanillaOption:
        payoff = ql.PlainVanillaPayoff(
            ql.Option.Call if params.is_call else ql.Option.Put,
            params.strike
        )
        process, maturity = self._build_process(params)
        exercise = ql.EuropeanExercise(maturity)
        option = ql.VanillaOption(payoff, exercise)

        engine = ql.AnalyticEuropeanEngine(process)
        option.setPricingEngine(engine)
        return option

    def price(self, params: MarketParams) -> float:
        option = self._build_option(params)
        return option.NPV()

    def greeks(self, params: MarketParams) -> dict:
        option = self._build_option(params)
        return {
            "price": option.NPV(),
            "delta": option.delta(),
            "gamma": option.gamma(),
            "theta": option.theta(),
            "vega": option.vega(),
            "rho": option.rho(),
        }

