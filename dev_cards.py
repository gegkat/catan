import yagmail
import random

players = [
  "gegkat@gmail.com",
  "ellie.wen@gmail.com",
  "evankatz14@gmail.com"
]

class DevCards:
  def __init__(self):
    self.yag = yagmail.SMTP('sheeps.are.best@gmail.com')
    self.pulled_cards = []
    cards = []
    cards += ["Knight"]*14
    cards += ["Victory Point"]*5
    cards += ["Monopoly"]*2
    cards += ["Year of Plenty"]*2
    cards += ["Road Building"]*2
    self.cards = cards
    self.Shuffle()
    self.wisdom = ["Never underestimate the power of sheep!", 
        "Bricks are dumb.",
        "This game is actually just luck.",
      ]

  def Shuffle(self):
    random.shuffle(self.cards)

  def Undo(self):
    if not self.pulled_cards:
      print("Nothing to undo.")
      print()
      return
    self.cards.append(self.pulled_cards.pop())
    print()

  def DrawCard(self, inp):
    if not self.cards:
      print("No cards left to draw!")
      return

    card = self.cards.pop()
    self.pulled_cards.append(card)
    contents = "You drew a " + card + "."
    contents += """


    """
    contents += "Words of wisdom: " + random.choice(self.wisdom)
    print()
    print("e-mail sent to ", player)
    print(contents)
    print()
    self.yag.send(inp, subject = "Your Dev Card Selection.", contents = contents)
    return contents


dc = DevCards()
while True:

  # Print instructions.
  print("Dev cards remaining: ", len(dc.cards))
  for i, p in enumerate(players):
    print(i, ": ", p)
  print("u", ": ", "Undo last pull.")

  # Get input.
  inp = input("Choose a player: ")

  # Undo.
  if inp == "u":
    dc.Undo()
    continue

  # Quit.
  if inp == "quit":
    break

  # Select player.
  try:
    player = players[int(inp)]
  except:
    print("invalid input, try again.")
    print()
    continue

  # Draw card.
  contents = dc.DrawCard(player)


