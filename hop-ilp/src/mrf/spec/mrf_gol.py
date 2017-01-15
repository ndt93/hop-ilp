from logger import logger
from mrf.spec.mrf_base import BaseMRF


class GolMRF(BaseMRF):
    var_to_idx = {}  # Var is a tuple (name, future, horizon)
    idx_to_var = []
    constr_cats = ['init_states', 'init_actions', 'concurrency', 'transition', 'reward']
    constrs = {}

    def __init__(self, *args, **kwargs):
        BaseMRF.__init__(self, *args, **kwargs)

