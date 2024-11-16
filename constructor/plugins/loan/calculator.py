from copy import copy
from collections.abc import Mapping
import dataclasses


class NotReadyToCalculate(AssertionError):
    pass


PAYMENT_FIELDS_NAMES = (
    ('loan_amount', 'Кредит, руб'),
    ('payment_percents', 'Ежемесячный платеж начисленные проценты, руб'),
    ('payment_dept', 'Ежемесячный платеж основной долг, руб'),
    ('payment', 'Ежемесячный платёж, руб'),
    ('remaining_payment', 'Остаток общей выплаты с учетом всех стандартных платежей, руб'),
)

def payment_field_name_by(field_id: str) -> str:
    for id_, name in PAYMENT_FIELDS_NAMES:
        if field_id == id_:
            return name
    return '-'


@dataclasses.dataclass
class Payment:
    loan_amount: float
    payment_percents: float
    payment_dept: float
    payment: float
    remaining_payment: float = 0.0

    def __str__(self):
        return " | ".join(["{:12.2f}".format(self[k]) for k, _ in PAYMENT_FIELDS_NAMES])

    def __repr__(self):
        return "Payment({})".format(', '.join(["{}={:.2f}".format(k, self[k]) for k, _ in PAYMENT_FIELDS_NAMES]))

    def __iter__(self):
        return iter((self[k] for k, _ in PAYMENT_FIELDS_NAMES))

    def __copy__(self):
        return dataclasses.replace(self)

    def __getitem__(self, item):
        return self.__dict__[item]


class Loan:
    def __init__(self) -> None:
        self.loan_amount = None
        self.interest_rate_yearly = None
        self.loan_term_years = None
        self.__payments = []

    def __str__(self):
        return (
            f"{self.__class__.__name__}("
            f"loan_amount={self.loan_amount}, "
            f"interest_rate_yearly={self.interest_rate_yearly}, "
            f"loan_term_years={self.loan_term_years}"
            f")"
        )

    def calc(self):
        if not self.is_ready():
            raise NotReadyToCalculate(f"Not ready to calculate: {self}")

        self.__payments.clear()

        loan_amount = self.loan_amount
        interest_rate_yearly = self.interest_rate_yearly
        loan_term_years = self.loan_term_years

        number_of_months_in_year = 12
        number_of_payments = loan_term_years * number_of_months_in_year
        interest_rate_monthly = interest_rate_yearly / number_of_months_in_year

        for payments_left in range(number_of_payments, 0, -1):
            payment_percents = loan_amount * interest_rate_monthly
            payment_dept = loan_amount * (interest_rate_monthly / (1 - ((1 + interest_rate_monthly) ** payments_left)))
            payment = Payment(
                loan_amount=loan_amount,
                payment_percents=payment_percents,
                payment_dept=payment_dept,
                payment=payment_dept - payment_percents
            )
            loan_amount += payment_dept
            self.__payments.append(payment)

        remaining_payment = 0
        for payment in reversed(self.__payments):
            payment.remaining_payment = remaining_payment
            remaining_payment += payment.payment

    def set_loan_amount(self, value: float) -> None:
        self.loan_amount = value

    def set_interest_rate_yearly(self, value: float) -> None:
        self.interest_rate_yearly = value

    def set_loan_term_years(self, value: int) -> None:
        self.loan_term_years = value

    def is_ready(self):
        return all(
            x is not None
            for x in (
                self.loan_amount,
                self.interest_rate_yearly,
                self.loan_term_years,
            )
        )

    def get_payment(self, n: int) -> Payment:
        return copy(self.__payments[n])

    def number_of_payments(self) -> int:
        return len(self.__payments)

    def print(self):
        for payment in self.__payments:
            print(payment)

    def __getitem__(self, item):
        return self.__payments[item]

    def __len__(self):
        return len(self.__payments)


class CustomIterator:
    def __init__(self, iterable: Mapping) -> None:
        self.__iterable = iterable
        self.__iteration_number = 0

    def __iter__(self):
        self.__iteration_number = 0
        return self

    def __next__(self):
        if self.__iteration_number < len(self.__iterable):
            result = self.__iterable[self.__iteration_number]
            self.__iteration_number += 1
            return result
        else:
            raise StopIteration


def test():
    payments = (
        (900000.00,     27525.00,     -5402.16,    -32927.16,   -1942702.39),
        (894597.84,     27359.78,     -5567.38,    -32927.16,   -1909775.23),
        (889030.47,     27189.52,     -5737.64,    -32927.16,   -1876848.07),
        (883292.82,     27014.04,     -5913.12,    -32927.16,   -1843920.92),
        (877379.70,     26833.20,     -6093.96,    -32927.16,   -1810993.76),
        (871285.74,     26646.82,     -6280.34,    -32927.16,   -1778066.60),
        (865005.40,     26454.75,     -6472.41,    -32927.16,   -1745139.44),
        (858532.99,     26256.80,     -6670.36,    -32927.16,   -1712212.28),
        (851862.63,     26052.80,     -6874.36,    -32927.16,   -1679285.12),
        (844988.27,     25842.56,     -7084.60,    -32927.16,   -1646357.96),
        (837903.67,     25625.89,     -7301.27,    -32927.16,   -1613430.80),
        (830602.40,     25402.59,     -7524.57,    -32927.16,   -1580503.64),
        (823077.83,     25172.46,     -7754.70,    -32927.16,   -1547576.48),
        (815323.13,     24935.30,     -7991.86,    -32927.16,   -1514649.32),
        (807331.27,     24690.88,     -8236.28,    -32927.16,   -1481722.16),
        (799094.99,     24438.99,     -8488.17,    -32927.16,   -1448795.01),
        (790606.82,     24179.39,     -8747.77,    -32927.16,   -1415867.85),
        (781859.06,     23911.86,     -9015.30,    -32927.16,   -1382940.69),
        (772843.75,     23636.14,     -9291.02,    -32927.16,   -1350013.53),
        (763552.73,     23351.99,     -9575.17,    -32927.16,   -1317086.37),
        (753977.56,     23059.15,     -9868.01,    -32927.16,   -1284159.21),
        (744109.55,     22757.35,    -10169.81,    -32927.16,   -1251232.05),
        (733939.74,     22446.32,    -10480.84,    -32927.16,   -1218304.89),
        (723458.91,     22125.78,    -10801.37,    -32927.16,   -1185377.73),
        (712657.53,     21795.44,    -11131.72,    -32927.16,   -1152450.57),
        (701525.81,     21455.00,    -11472.16,    -32927.16,   -1119523.41),
        (690053.65,     21104.14,    -11823.02,    -32927.16,   -1086596.25),
        (678230.63,     20742.55,    -12184.61,    -32927.16,   -1053669.09),
        (666046.03,     20369.91,    -12557.25,    -32927.16,   -1020741.94),
        (653488.78,     19985.87,    -12941.29,    -32927.16,    -987814.78),
        (640547.48,     19590.08,    -13337.08,    -32927.16,    -954887.62),
        (627210.40,     19182.18,    -13744.97,    -32927.16,    -921960.46),
        (613465.43,     18761.82,    -14165.34,    -32927.16,    -889033.30),
        (599300.09,     18328.59,    -14598.56,    -32927.16,    -856106.14),
        (584701.52,     17882.12,    -15045.04,    -32927.16,    -823178.98),
        (569656.48,     17421.99,    -15505.17,    -32927.16,    -790251.82),
        (554151.32,     16947.79,    -15979.36,    -32927.16,    -757324.66),
        (538171.95,     16459.09,    -16468.07,    -32927.16,    -724397.50),
        (521703.89,     15955.44,    -16971.72,    -32927.16,    -691470.34),
        (504732.17,     15436.39,    -17490.77,    -32927.16,    -658543.18),
        (487241.40,     14901.47,    -18025.69,    -32927.16,    -625616.02),
        (469215.71,     14350.18,    -18576.98,    -32927.16,    -592688.87),
        (450638.73,     13782.03,    -19145.12,    -32927.16,    -559761.71),
        (431493.61,     13196.51,    -19730.65,    -32927.16,    -526834.55),
        (411762.96,     12593.08,    -20334.08,    -32927.16,    -493907.39),
        (391428.89,     11971.20,    -20955.96,    -32927.16,    -460980.23),
        (370472.93,     11330.30,    -21596.86,    -32927.16,    -428053.07),
        (348876.06,     10669.79,    -22257.37,    -32927.16,    -395125.91),
        (326618.70,      9989.09,    -22938.07,    -32927.16,    -362198.75),
        (303680.63,      9287.57,    -23639.59,    -32927.16,    -329271.59),
        (280041.03,      8564.59,    -24362.57,    -32927.16,    -296344.43),
        (255678.46,      7819.50,    -25107.66,    -32927.16,    -263417.27),
        (230570.80,      7051.62,    -25875.54,    -32927.16,    -230490.11),
        (204695.27,      6260.26,    -26666.90,    -32927.16,    -197562.96),
        (178028.37,      5444.70,    -27482.46,    -32927.16,    -164635.80),
        (150545.91,      4604.20,    -28322.96,    -32927.16,    -131708.64),
        (122222.95,      3737.99,    -29189.17,    -32927.16,     -98781.48),
        ( 93033.78,      2845.28,    -30081.88,    -32927.16,     -65854.32),
        ( 62951.90,      1925.28,    -31001.88,    -32927.16,     -32927.16),
        ( 31950.02,       977.14,    -31950.02,    -32927.16,          0.00),
    )
    test_loan = Loan()
    assert not test_loan.is_ready()
    test_loan.loan_amount=900_000.0
    assert not test_loan.is_ready()
    test_loan.interest_rate_yearly=0.367
    assert not test_loan.is_ready()
    test_loan.loan_term_years=5
    test_loan.calc()

    assert len(payments) == test_loan.number_of_payments(), (
        f"Number of payments do not match test_payments={len(payments)} != loan_payments={test_loan.number_of_payments()}"
    )

    for test_case, loan_payment in zip(payments, CustomIterator(test_loan)):
        a = tuple(round(x, 2) for x in loan_payment)[:len(test_case)]
        assert a == test_case, f'{a} != {test_case}'


def main():
    """
        initial_payment=0.0,
        loan_amount=900_000.0,
        interest_rate_yearly=0.367,
        loan_term_years=5,
        monthly_topup_available=60_000.0,
        monthly_topup_extra=None,
        loan_payment=None,
        refinance_rate_yearly=6.0
    """
    test()

    # loan = Loan()
    # loan.loan_amount=900_000.0
    # loan.interest_rate_yearly=0.367
    # loan.loan_term_years=5
    # loan.calc()
    # loan.print()


if __name__ == '__main__':
    main()
