class account:
    def __init__(self, balance, account):
        self.balance = balance
        self.account_no = account
        print(f"Your balance is Rs: {self.balance}")
        print(f"Your account number is: {self.account_no}")

    def debit(self, amount):
        self.balance -= amount
        print(f"Rs: {amount} was debited.")
        print(f"Total Balance is: {self.balance}")

    def credit(self, amount):
        self.balance += amount
        print(f"Rs: {amount} is Creadited to your account.")
        print(f"Total Balance is: {self.balance}")

    def get_balance(self):
        return self.balance

acc1 = account(100000, 11905080295505)
acc1.balance
acc1.account_no

print()
acc1.debit(10000)

print()
acc1.credit(60000)