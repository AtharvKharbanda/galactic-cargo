# 🚀 Galactic Cargo

**Galactic Cargo** is a real-time, 2-player multiplayer card game built with a Python/Django WebSocket backend and a React/Tailwind CSS frontend. 

**🎮 [PLAY THE GAME LIVE HERE](https://galactic-cargo.vercel.app/)**

Take on the role of a space freighter captain. Your mission? Be the first to empty your cargo hold by successfully docking and matching shipments across the galaxy. But beware—rival captains, solar flares, and pirate raids stand in your way.

---

## 🛠️ Tech Stack
* **Frontend:** React.js, Tailwind CSS (Hosted on Vercel)
* **Backend:** Python, Django, Django Channels / WebSockets (Hosted on Render)

---

## 📖 How to Play

### The Objective
The first player to empty their Cargo Hold (reach 0 cards) wins the game. 

### The Setup
1. Two players connect to the terminal using the link above (open in two different browser windows/devices). 
2. Player 1 initiates the launch sequence.
3. Both players are dealt a starting hand of **7 cards**.
4. One card is flipped face-up in the center to become the **Current Target Destination**.

### Your Turn
When the terminal indicates it is your turn, you must play a card from your hold that matches the center card in **at least one** of two ways:
* **Match the Planet:** (e.g., You can play *Desert Tech* on top of *Desert Fuel*).
* **Match the Cargo:** (e.g., You can play *Volcanic Fuel* on top of *Desert Fuel*).

If you successfully play a card, it becomes the new Target Destination, your hand size decreases by one, and your turn ends.

### Getting Stuck (Drawing Cargo)
If you do not have a card that matches the Planet or the Cargo, you cannot play. You must click the **Draw Cargo** button. This will pull one random card from the deck into your hold and immediately pass your turn to the opponent.

---

## ⚡ Action Cards (Special Abilities)
Hidden within the deck are three types of special Action Cards. Playing these at the right time can turn the tide of the game.

* 🏴‍☠️ **Pirate Raid:** * *Effect:* Forces your opponent to immediately draw 2 penalty cards from the deck. The turn then passes to them as normal.
* ☀️ **Solar Flare:** * *Effect:* Jams your opponent's systems. You skip their turn and get to go again immediately!
* 🌀 **Wormhole (Wildcard):**
  * *Effect:* A Wormhole can be played on **any** card, regardless of the current Planet or Cargo. When played, the Wormhole randomly recalibrates the terminal to a brand new Target Planet, and your turn ends.

---
*Note: Because the backend is hosted on a free Render tier, the server goes to "sleep" after 15 minutes of inactivity. If the game doesn't load immediately, give it about 30-50 seconds to wake the server up!*