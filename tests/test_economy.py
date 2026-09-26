from selfbot.capabilities import CapabilityService
from selfbot.db import Database
from selfbot.domain_store import DomainStore
from selfbot.economy import EconomyPolicy, EconomyService
from selfbot.errors import AuthorizationError, ValidationError

def make_service(tmp_path):
    db = Database(f"sqlite:///{tmp_path / 'economy.db'}")
    db.create_schema_for_tests()
    caps = CapabilityService(DomainStore(db))
    caps.set_enabled("owner", "panel_diamond_transfer", True)
    return db, EconomyService(db, caps, owner_id="owner")

def test_transfer_is_atomic_and_charges_fee(tmp_path):
    db, economy = make_service(tmp_path)
    economy.adjust("owner", "alice", 100, reason="seed")
    result = economy.transfer("alice", "bob", 50)
    assert result.fee == 1
    assert economy.balance("alice") == 49
    assert economy.balance("bob") == 50
    history = economy.history("alice")
    assert len(history) == 2
    assert history[0].kind == "transfer"
    assert history[0].fee == 1

def test_transfer_rejects_self_and_insufficient_balance(tmp_path):
    db, economy = make_service(tmp_path)
    economy.adjust("owner", "alice", 100)
    try:
        economy.transfer("alice", "alice", 1)
        assert False
    except ValidationError as exc:
        assert "خود" in str(exc)
    try:
        economy.transfer("alice", "bob", 100)
        assert False
    except ValidationError:
        pass
    assert economy.balance("alice") == 100

def test_limits_and_daily_cap(tmp_path):
    db, economy = make_service(tmp_path)
    economy.adjust("owner", "alice", 5000)
    economy.transfer("alice", "bob", 1000)
    economy.transfer("alice", "bob", 1000)
    economy.transfer("alice", "bob", 1000)
    try:
        economy.transfer("alice", "bob", 1)
        assert False
    except ValidationError as exc:
        assert "سقف" in str(exc)

def test_admin_adjustment_is_owner_only_and_never_negative(tmp_path):
    db, economy = make_service(tmp_path)
    try:
        economy.adjust("not-owner", "alice", 10)
        assert False
    except AuthorizationError:
        pass
    economy.adjust("owner", "alice", 10)
    try:
        economy.adjust("owner", "alice", -11)
        assert False
    except ValidationError:
        pass
    assert economy.balance("alice") == 10

def test_policy_defaults_are_bounded():
    policy = EconomyPolicy()
    assert policy.min_transfer == 1
    assert policy.max_transfer == 1000
    assert policy.daily_transfer_limit == 3000
    assert policy.fee_bps == 100
