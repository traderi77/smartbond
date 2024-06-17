from functools import wraps


class Participant: 
    def __init__(self, role: str): 
        if role in ["buyer", "seller"]:
            self.role = role
        else:
            raise ValueError('Invalid Role')
        
        self.orders = []
        self.balance = 0.0
    
    
class Order: 
    def __init__(self, amount: int, limit: float, investor: Participant): 
        self.amount = amount
        self.limit = limit
        self.investor = investor


def assert_orderbook_is_open(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.orderbook_open:
            raise PermissionError("Orderbook is closed.")
        return method(self, *args, **kwargs)
    return wrapper


class OrderBook:
    def __init__(self):
        self.orderbook_open = False
        self._orders = []

    @assert_orderbook_is_open
    def add_order(self, order: Order):
        self._orders.append(order)

    @assert_orderbook_is_open
    def remove_order(self, order: Order):
        self._orders.remove(order)

    @assert_orderbook_is_open
    def modify_order(self, order: Order):
        try:
            self._orders[self._orders.index(order)] = order
        except ValueError:
            raise ValueError("Order does not exist.")

    def open_orderbook(self, open: bool, requestor: Participant):
        if requestor.role in ['ISSUER', 'ADMIN']:
            self.orderbook_open = open
        else:
            raise PermissionError(f"You do not have permission to {'open' if open else 'close'} the orderbook.")

    @property
    def orders(self): raise AttributeError("Direct access to orders is not allowed. Use get_orders method.")

    @property
    def orderbook_open(self): return self._orderbook_open

    def get_orders(self, requestor: Participant):
        if requestor.role in ['ADMIN', 'BOOKRUNNER', 'ISSUER']:
            return self._orders
        elif requestor.role == 'INVESTOR': 
            return [order for order in self._orders if order.investor == requestor]
        else:
            raise PermissionError("You do not have permission to access the orders.")

                           
class Contract: 
    states = ['terms', 'orderbook_open', 'settlement']

    def __init__(self): 
        self.orderbook = OrderBook() 

    def update_state(self, requestor: Participant, new_state: str): 
        if Participant.role == 'ADMIN' and new_state in Contract.states: 
            self.state = new_state
