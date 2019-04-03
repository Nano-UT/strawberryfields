# Copyright 2019 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

r"""
UTests for the various Tensorflow-specific symbolic options of the frontend/backend.
"""

import pytest

import numpy as np
from scipy.special import factorial
import tensorflow as tf

from strawberryfields.ops import Dgate, MeasureX
from strawberryfields.engine import Engine

ALPHA = 0.5


class TestOneModeSymbolic:
    """Tests for symbolic workflows on one mode."""
    num_subsystems = 1

    def setUp(self):
        super().setUp()
        self.vac = np.zeros(cutoff)
        self.vac[0] = 1
        self.vac_dm = np.outer(self.vac, np.conj(self.vac))
        self.coh = np.array([np.exp(- 0.5 * np.abs(ALPHA) ** 2) * ALPHA ** k / np.sqrt(factorial(k)) for k in range(cutoff)])
        self.eng = Engine(self.num_subsystems)
        # attach the backend (NOTE: self.backend is shared between the tests, make sure it is reset before use!)
        self.eng.backend = self.backend
        self.backend.reset()

    #########################################
    # tests basic eval behaviour of eng.run and states class

    def test_eng_run_eval_false_returns_tensor(self):
        """Tests whether the eval=False option to the `eng.run` command
        successfully returns an unevaluated Tensor."""

        q = self.eng.register
        with self.eng:
            Dgate(0.5) | q
        state = self.eng.run(eval=False)
        state_data = state.data
        self.assertTrue(isinstance(state_data, tf.Tensor))

    def test_eng_run_eval_false_measurements_are_tensors(self):
        """Tests whether the eval=False option to the `eng.run` command
        successfully returns a unevaluated Tensors for measurment results."""

        q = self.eng.register
        with self.eng:
            Dgate(0.5) | q
            MeasureX   | q
        self.eng.run(eval=False)
        val = q[0].val
        self.assertTrue(isinstance(val, tf.Tensor))

    def test_eng_run_with_session_and_feed_dict(self):
        """Tests whether passing a tf Session and feed_dict
        through `eng.run` leads to proper numerical simulation."""

        a = tf.Variable(0.5)
        sess = tf.Session()
        sess.run(tf.global_variables_initializer())
        q = self.eng.register
        with self.eng:
            Dgate(a) | q
        state = self.eng.run(session=sess, feed_dict={a: 0.0})

        if state.is_pure:
            k = state.ket()
            if self.batched:
                dm = np.einsum('bi,bj->bij', k, np.conj(k))
            else:
                dm = np.outer(k, np.conj(k))
        else:
            dm = state.dm()
        self.assertAllEqual(dm, self.vac_dm)

    #########################################
    # tests of eval behaviour of ket method

    def test_eng_run_eval_false_state_ket(self):
        """Tests whether the ket of the returned state is an unevaluated
        Tensor object when eval=False is passed to `eng.run`."""

        if self.args.mixed:
            return
        else:
            q = self.eng.register
            with self.eng:
                Dgate(0.5) | q
            state = self.eng.run(eval=False)
            ket = state.ket()
            self.assertTrue(isinstance(ket, tf.Tensor))

    def test_eval_false_state_ket(self):
        """Tests whether the ket of the returned state is an unevaluated
        Tensor object when eval=False is passed to the ket method of a state."""

        if self.args.mixed:
            return
        else:
            q = self.eng.register
            with self.eng:
                Dgate(0.5) | q
            state = self.eng.run()
            ket = state.ket(eval=False)
            self.assertTrue(isinstance(ket, tf.Tensor))

    def test_eval_true_state_ket(self):
        """Tests whether the ket of the returned state is equal to the
        correct value when eval=True is passed to the ket method of a state."""

        if self.args.mixed:
            return
        else:
            q = self.eng.register
            state = self.eng.run()
            ket = state.ket(eval=True)
            self.assertAllAlmostEqual(ket, self.vac, delta=tol)

    #########################################
    # tests of eval behaviour of dm method

    def test_eng_run_eval_false_state_dm(self):
        """Tests whether the density matrix of the returned state is an
        unevaluated Tensor object when eval=False is passed to `eng.run`."""

        if self.args.mixed:
            return
        else:
            q = self.eng.register
            with self.eng:
                Dgate(0.5) | q
            state = self.eng.run(eval=False)
            dm = state.dm()
            self.assertTrue(isinstance(dm, tf.Tensor))

    def test_eval_false_state_dm(self):
        """Tests whether the density matrix of the returned state is an
        unevaluated Tensor object when eval=False is passed to the ket method of a state."""

        if self.args.mixed:
            return
        else:
            q = self.eng.register
            with self.eng:
                Dgate(0.5) | q
            state = self.eng.run()
            dm = state.dm(eval=False)
            self.assertTrue(isinstance(dm, tf.Tensor))

    def test_eval_true_state_dm(self):
        """Tests whether the density matrix of the returned state is equal
        to the correct value when eval=True is passed to the ket method of a state."""

        if self.args.mixed:
            return
        else:
            q = self.eng.register
            state = self.eng.run()
            dm = state.dm(eval=True)
            self.assertAllAlmostEqual(dm, self.vac_dm, delta=tol)

    #########################################
    # tests of eval behaviour of trace method

    def test_eng_run_eval_false_state_trace(self):
        """Tests whether the trace of the returned state is an
      	unevaluated Tensor object when eval=False is passed to `eng.run`."""

        q = self.eng.register
        with self.eng:
            Dgate(0.5) | q
        state = self.eng.run(eval=False)
        tr = state.trace()
        self.assertTrue(isinstance(tr, tf.Tensor))

    def test_eval_false_state_trace(self):
        """Tests whether the trace of the returned state is an
        unevaluated Tensor object when eval=False is passed to the trace method of a state."""

        q = self.eng.register
        with self.eng:
            Dgate(0.5) | q
        state = self.eng.run()
        tr = state.trace(eval=False)
        self.assertTrue(isinstance(tr, tf.Tensor))

    def test_eval_true_state_trace(self):
        """Tests whether the trace of the returned state is equal
        to the correct value when eval=True is passed to the trace method of a state."""

        q = self.eng.register
        with self.eng:
            Dgate(0.5) | q
        state = self.eng.run()
        tr = state.trace(eval=True)
        self.assertAllAlmostEqual(tr, 1, delta=tol)

	#########################################
	# tests of eval behaviour of reduced_dm method

    def test_eng_run_eval_false_state_reduced_dm(self):
        """Tests whether the reduced_density matrix of the returned state
	    is an unevaluated Tensor object when eval=False is passed to `eng.run`."""

        q = self.eng.register
        with self.eng:
            Dgate(0.5) | q
        state = self.eng.run(eval=False)
        rho = state.reduced_dm([0])
        self.assertTrue(isinstance(rho, tf.Tensor))

    def test_eval_false_state_reduced_dm(self):
        """Tests whether the reduced density matrix of the returned state is an
        unevaluated Tensor object when eval=False is passed to the reduced_dm method of a state."""

        q = self.eng.register
        with self.eng:
            Dgate(0.5) | q
        state = self.eng.run()
        rho = state.reduced_dm([0], eval=False)
        self.assertTrue(isinstance(rho, tf.Tensor))

    def test_eval_true_state_reduced_dm(self):
        """Tests whether the reduced density matrix of the returned state is
        equal to the correct value when eval=True is passed to the reduced_dm method of a state."""

        q = self.eng.register
        state = self.eng.run()
        rho = state.reduced_dm([0], eval=True)
        self.assertAllAlmostEqual(rho, self.vac_dm, delta=tol)

    #########################################
    # tests of eval behaviour of fidelity_vacuum method

    def test_eng_run_eval_false_state_fidelity_vacuum(self):
        """Tests whether the fidelity_vacuum method of the state returns an
        unevaluated Tensor object when eval=False is passed to `eng.run`."""

        q = self.eng.register
        with self.eng:
            Dgate(0.5) | q
        state = self.eng.run(eval=False)
        fidel_vac = state.fidelity_vacuum()
        self.assertTrue(isinstance(fidel_vac, tf.Tensor))

    def test_eval_false_state_fidelity_vacuum(self):
        """Tests whether the vacuum fidelity of the returned state is an
        unevaluated Tensor object when eval=False is passed to the fidelity_vacuum method of a state."""

        q = self.eng.register
        with self.eng:
            Dgate(0.5) | q
        state = self.eng.run()
        fidel_vac = state.fidelity_vacuum(eval=False)
        self.assertTrue(isinstance(fidel_vac, tf.Tensor))

    def test_eval_true_state_fidelity_vacuum(self):
        """Tests whether the vacuum fidelity of the returned state is equal
        to the correct value when eval=True is passed to the fidelity_vacuum method of a state."""

        q = self.eng.register
        state = self.eng.run()
        fidel_vac = state.fidelity_vacuum(eval=True)
        self.assertAllAlmostEqual(fidel_vac, 1., delta=tol)

    #########################################
    # tests of eval behaviour of is_vacuum method

    def test_eng_run_eval_false_state_is_vacuum(self):
        """Tests whether the is_vacuum method of the state returns an
        unevaluated Tensor object when eval=False is passed to `eng.run`."""

        q = self.eng.register
        with self.eng:
            Dgate(0.5) | q
        state = self.eng.run(eval=False)
        is_vac = state.is_vacuum()
        self.assertTrue(isinstance(is_vac, tf.Tensor))

    def test_eval_false_state_is_vacuum(self):
        """Tests whether the is_vacuum method of the state returns an
        unevaluated Tensor object when eval=False is passed to the is_vacuum method of a state."""

        q = self.eng.register
        with self.eng:
            Dgate(0.5) | q
        state = self.eng.run()
        is_vac = state.is_vacuum(eval=False)
        self.assertTrue(isinstance(is_vac, tf.Tensor))

    def test_eval_true_state_is_vacuum(self):
        """Tests whether the is_vacuum method of the state returns
        the correct value when eval=True is passed to the is_vacuum method of a state."""

        q = self.eng.register
        state = self.eng.run()
        is_vac = state.is_vacuum(eval=True)
        self.assertAllTrue(is_vac)

    #########################################
    # tests of eval behaviour of fidelity_coherent method

    def test_eng_run_eval_false_state_fidelity_coherent(self):
        """Tests whether the fidelity of the state with respect to coherent states is
        an unevaluated Tensor object when eval=False is passed to `eng.run`."""

        q = self.eng.register
        with self.eng:
            Dgate(ALPHA) | q
        state = self.eng.run(eval=False)
        fidel_coh = state.fidelity_coherent([ALPHA])
        self.assertTrue(isinstance(fidel_coh, tf.Tensor))

    def test_eval_false_state_fidelity_coherent(self):
        """Tests whether the fidelity of the state with respect to coherent states
        is an unevaluated Tensor object when eval=False is passed to the fidelity_coherent method of a state."""

        q = self.eng.register
        with self.eng:
            Dgate(ALPHA) | q
        state = self.eng.run()
        fidel_coh = state.fidelity_coherent([ALPHA], eval=False)
        self.assertTrue(isinstance(fidel_coh, tf.Tensor))

    def test_eval_true_state_fidelity_coherent(self):
        """Tests whether the fidelity of the state with respect to coherent states returns
        the correct value when eval=True is passed to the fidelity_coherent method of a state."""

        q = self.eng.register
        with self.eng:
            Dgate(ALPHA) | q
        state = self.eng.run()
        fidel_coh = state.fidelity_coherent([ALPHA], eval=True)
        self.assertAllAlmostEqual(fidel_coh, 1, delta=tol)

    #########################################
    # tests of eval behaviour of fidelity method

    def test_eng_run_eval_false_state_fidelity(self):
        """Tests whether the fidelity of the state with respect to a local state is an
        unevaluated Tensor object when eval=False is passed to `eng.run`."""

        q = self.eng.register
        with self.eng:
            Dgate(ALPHA) | q
        state = self.eng.run(eval=False)
        fidel = state.fidelity(self.coh, 0)
        self.assertTrue(isinstance(fidel, tf.Tensor))

    def test_eval_false_state_fidelity(self):
        """Tests whether the fidelity of the state with respect to a local state is
        an unevaluated Tensor object when eval=False is passed to the fidelity method of a state."""

        q = self.eng.register
        with self.eng:
            Dgate(ALPHA) | q
        state = self.eng.run()
        fidel = state.fidelity(self.coh, 0, eval=False)
        self.assertTrue(isinstance(fidel, tf.Tensor))

    def test_eval_true_state_fidelity(self):
        """Tests whether the fidelity of the state with respect to a local state
        returns the correct value when eval=True is passed to the fidelity method of a state."""

        q = self.eng.register
        with self.eng:
            Dgate(ALPHA) | q
        state = self.eng.run()
        fidel_coh = state.fidelity(self.coh, 0, eval=True)
        self.assertAllAlmostEqual(fidel_coh, 1, delta=tol)

    #########################################
    # tests of eval behaviour of quad_expectation method

    def test_eng_run_eval_false_state_quad_expectation(self):
        """Tests whether the local quadrature expectation of the state is
        unevaluated Tensor object when eval=False is passed to `eng.run`."""

        q = self.eng.register
        with self.eng:
            Dgate(ALPHA) | q
        state = self.eng.run(eval=False)
        e, v = state.quad_expectation(0, 0)
        self.assertTrue(isinstance(e, tf.Tensor))
        self.assertTrue(isinstance(v, tf.Tensor))

    def test_eval_false_state_quad_expectation(self):
        """Tests whether the local quadrature expectation value of the state is
        an unevaluated Tensor object when eval=False is passed to the quad_expectation method of a state."""

        q = self.eng.register
        with self.eng:
            Dgate(ALPHA) | q
        state = self.eng.run()
        e, v = state.quad_expectation(0, 0, eval=False)
        self.assertTrue(isinstance(e, tf.Tensor))
        self.assertTrue(isinstance(v, tf.Tensor))

    def test_eval_true_state_quad_expectation(self):
        """Tests whether the local quadrature expectation value of the state returns
        the correct value when eval=True is passed to the quad_expectation method of a state."""

        hbar = 2.
        q = self.eng.register
        with self.eng:
            Dgate(ALPHA) | q
        state = self.eng.run()
        e, v = state.quad_expectation(0, 0, eval=True)
        true_exp = np.sqrt(hbar / 2.) * (ALPHA + np.conj(ALPHA))
        true_var = hbar / 2.
        self.assertAllAlmostEqual(e, true_exp, delta=tol)
        self.assertAllAlmostEqual(v, true_var, delta=tol)

    #########################################
    # tests of eval behaviour of mean_photon method

    def test_eng_run_eval_false_state_mean_photon(self):
        """Tests whether the local mean photon number of the state is
        unevaluated Tensor object when eval=False is passed to `eng.run`."""

        q = self.eng.register
        with self.eng:
            Dgate(ALPHA) | q
        state = self.eng.run(eval=False)
        nbar, var = state.mean_photon(0)
        self.assertTrue(isinstance(nbar, tf.Tensor))
        self.assertTrue(isinstance(var, tf.Tensor))

    def test_eval_false_state_mean_photon(self):
        """Tests whether the local mean photon number of the state is
        an unevaluated Tensor object when eval=False is passed to the mean_photon_number method of a state."""

        q = self.eng.register
        with self.eng:
            Dgate(ALPHA) | q
        state = self.eng.run()
        nbar, var = state.mean_photon(0, eval=False)
        self.assertTrue(isinstance(nbar, tf.Tensor))
        self.assertTrue(isinstance(var, tf.Tensor))

    def test_eval_true_state_mean_photon(self):
        """Tests whether the local mean photon number of the state returns
        the correct value when eval=True is passed to the mean_photon method of a state."""

        q = self.eng.register
        with self.eng:
            Dgate(ALPHA) | q
        state = self.eng.run()
        nbar, var = state.mean_photon(0, eval=True)
        ref_nbar = np.abs(ALPHA) ** 2
        ref_var = np.abs(ALPHA) ** 2
        self.assertAllAlmostEqual(nbar, ref_nbar, delta=tol)
        self.assertAllAlmostEqual(var, ref_var, delta=tol)


class TestTwoModeSymbolic:
    """Tests for symbolic workflows on two modes."""

    num_subsystems = 2
    def setUp(self):
        super().setUp()
        self.coh = np.array([np.exp(- 0.5 * np.abs(ALPHA) ** 2) * ALPHA ** k / np.sqrt(factorial(k)) for k in range(cutoff)])
        self.neg_coh = np.array([np.exp(- 0.5 * np.abs(-ALPHA) ** 2) * (-ALPHA) ** k / np.sqrt(factorial(k)) for k in range(cutoff)])
        self.eng = Engine(self.num_subsystems)
        # attach the backend (NOTE: self.backend is shared between the tests, make sure it is reset before use!)
        self.eng.backend = self.backend
        self.backend.reset()


    #########################################
    # tests of eval behaviour of all_fock_probs method

    def test_eng_run_eval_false_state_all_fock_probs(self):
        """Tests whether the Fock-basis probabilities of the state are an
        unevaluated Tensor object when eval=False is passed to `eng.run`."""

        q = self.eng.register
        with self.eng:
            Dgate(ALPHA) | q[0]
            Dgate(-ALPHA) | q[1]
        state = self.eng.run(eval=False)
        probs = state.all_fock_probs()
        self.assertTrue(isinstance(probs, tf.Tensor))

    def test_eval_false_state_all_fock_probs(self):
        """Tests whether the Fock-basis probabilities of the state are an
        unevaluated Tensor object when eval=False is passed to the all_fock_probs method of a state."""

        q = self.eng.register
        with self.eng:
            Dgate(ALPHA) | q[0]
            Dgate(-ALPHA) | q[1]
        state = self.eng.run()
        probs = state.all_fock_probs(eval=False)
        self.assertTrue(isinstance(probs, tf.Tensor))

    def test_eval_true_state_all_fock_probs(self):
        """Tests whether the Fock-basis probabilities of the state return
        the correct value when eval=True is passed to the all_fock_probs method of a state."""

        q = self.eng.register
        with self.eng:
            Dgate(ALPHA) | q[0]
            Dgate(-ALPHA) | q[1]
        state = self.eng.run()
        probs = state.all_fock_probs(eval=True).flatten()
        ref_probs = np.tile(np.abs(np.outer(self.coh, self.neg_coh)).flatten() ** 2, self.bsize)
        self.assertAllAlmostEqual(probs, ref_probs, delta=tol)

    #########################################
    # tests of eval behaviour of fock_prob method

    def test_eng_run_eval_false_state_fock_prob(self, cutoff):
        """Tests whether the probability of a Fock measurement outcome on the state is an
        unevaluated Tensor object when eval=False is passed to `eng.run`."""

        q = self.eng.register
        with self.eng:
            Dgate(ALPHA) | q[0]
            Dgate(-ALPHA) | q[1]
        state = self.eng.run(eval=False)
        prob = state.fock_prob([cutoff // 2, cutoff // 2])
        self.assertTrue(isinstance(prob, tf.Tensor))

    def test_eval_false_state_fock_prob(self):
        """Tests whether the probability of a Fock measurement outcome on the state is an
        unevaluated Tensor object when eval=False is passed to the fock_prob method of a state."""

        q = self.eng.register
        with self.eng:
            Dgate(ALPHA) | q[0]
            Dgate(-ALPHA) | q[1]
        state = self.eng.run()
        prob = state.fock_prob([cutoff // 2, cutoff // 2], eval=False)
        self.assertTrue(isinstance(prob, tf.Tensor))

    def test_eval_false_state_fock_prob(self):
        """Tests whether the probability of a Fock measurement outcome on the state returns
         the correct value when eval=True is passed to the fock_prob method of a state."""

        n1 = cutoff // 2
        n2 = cutoff // 3
        q = self.eng.register
        with self.eng:
            Dgate(ALPHA) | q[0]
            Dgate(-ALPHA) | q[1]
        state = self.eng.run()
        prob = state.fock_prob([n1, n2], eval=True)
        ref_prob = (np.abs(np.outer(self.coh, self.neg_coh)) ** 2)[n1, n2]
        self.assertAllAlmostEqual(prob, ref_prob, delta=tol)
