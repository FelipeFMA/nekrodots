import random

play = "y"
bet = 0
money = input("Enter your deposit amount (minimum $100): ").strip()

while not money.isdigit() or float(money) < 100:
    money = input("Invalid amount. Please enter at least $100: ")

money = float(money)

while play.lower() == "y":
    bet = float(input(f"\nHow much would you like to bet? (Available: ${money:.2f}): "))

    x, y, z = random.choices(["🍒", "🍉", "🍌", "💎", "💰"], k=3)

    print(f"\n {x} {y} {z} | 🎰\n")

    # More winning combinations
    if x == y == z:
        # Jackpot for matching all symbols
        if x == "💎":
            winnings = bet * 10
            print("💎💎💎 JACKPOT! You matched all diamonds!")
        elif x == "💰":
            winnings = bet * 5
            print("💰💰💰 You matched all money bags!")
        else:
            winnings = bet * 3
            print(f"{x}{x}{x} You matched all {x} symbols!")
        money += winnings
        print(f"🎉 Congratulations! You won ${winnings:.2f} (", end="")
        if x == "💎":
            print("10x your bet!")
        elif x == "💰":
            print("5x your bet!")
        else:
            print("3x your bet!")
        print(f"Your new balance: ${money:.2f}")
    elif (x == y) or (y == z) or (x == z):
        # Win for any two matching symbols
        winnings = bet * 1.5
        money += winnings
        print(f"✨ Nice! You matched two symbols and won ${winnings:.2f} (1.5x your bet)")
        print(f"Your new balance: ${money:.2f}")
    else:
        money -= bet
        print(f"😢 You lost ${bet:.2f}. Your remaining balance: ${money:.2f}")

    if money < 1:
        print("💸 You're out of money! Game over.")
        break

    play = input("Do you want to play again? (Y/n): ").strip().lower()
    play = "y" if play in ["y", "yes"] else "n" if play in ["n", "no"] else "y"
