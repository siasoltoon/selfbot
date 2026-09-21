"""Isolated game/economy primitives; integrations remain plugins."""
from __future__ import annotations
from dataclasses import dataclass,field
from .errors import ConflictError,ValidationError
@dataclass(slots=True)
class Wallet:
    owner_id:str
    balance:int=0
    def credit(self,amount:int)->None:
        if amount<0: raise ValidationError("credit must be non-negative")
        self.balance+=amount
    def debit(self,amount:int)->None:
        if amount<0: raise ValidationError("debit must be non-negative")
        if amount>self.balance: raise ConflictError("insufficient balance")
        self.balance-=amount
@dataclass(slots=True)
class GameEngine:
    wallets:dict[str,Wallet]=field(default_factory=dict)
    def wallet(self,owner_id:str)->Wallet: return self.wallets.setdefault(owner_id,Wallet(owner_id))
    def award(self,owner_id:str,amount:int)->int:
        w=self.wallet(owner_id); w.credit(amount); return w.balance
    def buy(self,owner_id:str,price:int)->int:
        w=self.wallet(owner_id); w.debit(price); return w.balance
