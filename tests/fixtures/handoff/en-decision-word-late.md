The order screen is delivered and its tests pass. The checkout flow now refuses a payment whose card has expired, shows the total after the discount, and keeps the cart when the session times out. The customer form validates the tax number and the postal code before it saves, and the search by name returns results in alphabetical order, accents included. The monthly report separates returns from cancellations and exports to a spreadsheet without cutting long descriptions.

One thing is left before it ships: an empty order. I recommend refusing it at checkout, because the checkout rule already says an order needs at least one item; that would change if a product owner says an empty order is a valid draft.

- `a` — refuse it
- `b` — accept it, and change the rule first

Which one?
