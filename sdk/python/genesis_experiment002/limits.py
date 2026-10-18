"""Cooperative monotonic run boundary; no hard OS/network liveness claim."""

import math
import time
from web3.middleware.base import Web3Middleware
from genesis_experiment.protocol import Inconclusive


def check_deadline(end):
    if (
        type(end) not in (int, float)
        or not math.isfinite(end)
        or time.monotonic() >= end
    ):
        raise Inconclusive("local run deadline reached")


def bound_rpc(w3, end):
    class DeadlineRPC(Web3Middleware):
        def wrap_make_request(self, make_request):
            def checked(method, params):
                check_deadline(end)
                response = make_request(method, params)
                check_deadline(end)
                return response

            return checked

    w3.middleware_onion.inject(DeadlineRPC, layer=0)
