import random
import string
import time
import numpy as np
from Mindrove import MindroveDevice
#######################################################
def start_balance():
    while True:
        try:
            balance = int(input("Enter your starting balance: $"))
            if balance <= 0:
                print("Balance must be a positive number.")
            else:
                print("\nWelcome to the Slot Machine Game!")
                print(f"You start with a balance of ${balance}")
                return balance
        except ValueError:
            print("Please enter a valid number.")
#######################################################
def bet_amount(balance):
    while True:
        try:
            bet_amount = int(input("Enter your bet amount: $"))
            if bet_amount <= 0 or bet_amount > balance:
                print(f"Invalid bet amount. You can bet between $1 and ${balance}")
            else:
                print(f"You bet ${bet_amount}")
                return bet_amount
        except ValueError:
            print("Please enter a valid number.")

#######################################################
def lottery():
    elements = list([1, 2, 3, 4, 5, 6])
    random_selection = random.choices(elements, k=3)
    return random_selection
#######################################################
def count(random_list):
    max_count = 0
    for i in range(len(random_list)):
        counter = 0
        temp = random_list[i]
        for j in range(len(random_list)):
            if temp == random_list[j]:
                counter += 1
        if counter > max_count:
            max_count = counter
    return max_count
#######################################################
def game(count_number, balance, bet_money):
    if count_number == 1:
        print("You lost")
        balance = balance - bet_money
        return balance
    elif count_number == 2:
        print("You won $", bet_money*2)
        balance = (bet_money*2) + (balance - bet_money)
        return balance
    else:
        print("You won $", bet_money*10)
        balance = (bet_money * 10) + (balance - bet_money)
        return balance

#######################################################
def question(mindrove_device):
    print("Contract within 5 seconds to play again, or stay relaxed to stop.")
    start_time = time.time()
    while time.time() - start_time < 5:
        emg_chunk = mindrove_device.get_data_chunk()
        if emg_chunk.size > 0:
            strength = np.max(emg_chunk)
            if strength > 30:
                return True
        time.sleep(5)
    print("Thanks and Bye")
    return False
#######################################################
def special_winner(list):
    count = 0
    for i in range(len(list)):
        if list[i] == 6:
            count += 1
    if count == len(list):
        return True
    else:
        return False
#######################################################

mindrove_device = MindroveDevice()
mindrove_device.start_stream()

balance = start_balance()
print(f"\ncurrent balance: {balance}")

try:
    while True:
        bet_money = bet_amount(balance)
        print(bet_money)
        print("****************")
        print("Game result:")

        random_list = lottery()
        print(random_list)

        if special_winner(random_list):
            print("YOU WON JACKPOT, $ 1000000")
            balance = 1000000
            print(f"Current balance: {balance}")
            break

        count_number = count(random_list)
        rest_balance = game(count_number, balance, bet_money)
        print(f"Current Balance: ${rest_balance}")

        if rest_balance > 0:
            if question(mindrove_device):
                balance = rest_balance
                continue
            else:
                balance = rest_balance
                print(f"Current balance: {balance}")
                break
        else:
            balance = rest_balance
            print(f"Current balance: {balance}")
            print("Lost all credits!")
            break
finally:
    mindrove_device.stop()
