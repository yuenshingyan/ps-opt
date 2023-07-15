"""Feature selection for machine learning models, using Particle Swarm
Optimization and cross-validation.

Particle swarm optimization (PSO) is a computational method that
optimizes a problem by iteratively improving a candidate solution
based on a given measure of quality. The algorithm works by having
a population of candidate particles called particles, which move
around in the search space according to simple mathematical formulas
over their position and velocity. Each particle's movement is
influenced by its local best-known position and the best-known
positions in the search-space, which are updated as better positions
are found by other particles.

The basic PSO algorithm starts by initializing the position and
velocity of each particle, and setting the initial best-known
position for both the particle and the entire swarm. During each
iteration, the algorithm updates each particle's velocity based
on its own best-known position and the swarm's best-known position,
and then updates the particle's position accordingly. If a particle
finds a better position, it updates its best-known position and
potentially the swarm's best-known position. This process is
repeated until a termination criterion is met.
"""

# Author: Yuen Shing Yan Hindy <yuenshingyan@gmail.com>
# License: BSD 3 clause

__all__ = ['ParticleSwarmFeatureSelectionCV']
__version__ = '2.0.0'
__author__ = 'Yuen Shing Yan Hindy'

from datetime import datetime
import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.model_selection import cross_val_score


class _Base:
    """
    Class '_Base' consist of a single method '_system_datetime',
    and takes no arguments to instantiate.
    """
    def __init__(self):
        pass

    @property
    def _system_datetime(self):
        """
        return current datetime in '[%Y-%m-%d | %H:%M:%S]' format.
        This method is primarily used for constructing message to
        inform users which stage is the feature selection currently
        at.
        """
        return datetime.now().strftime("[%Y-%m-%d | %H:%M:%S]")


class _Initialization(_Base):
    """
    Class '_Initialization' consist of a single method '_initialize',
    and inherent class '_Base' as the sole parent class to inherent class
    method '_system_datetime'. 2 arguments are required to instantiate
    class '_Initialization'.
    """
    def __init__(self, n_particles, verbosity):
        """
        Parameters
        ----------
        n_particles : int
                      'n_particles' controls how many sets of probabilities
                      are generated during the initialization process.

        verbosity : int
                    'verbosity' controls if any messages are being print
                    out during feature selection processes.
        """
        if not isinstance(n_particles, int):
            raise ValueError("Argument 'n_particles' only accept integer as "
                             "input.")

        if not isinstance(verbosity, int):
            raise ValueError("Argument 'verbosity' only accept integer as "
                             "input.")

        _Base.__init__(self)
        self.n_particles = n_particles
        self.verbosity = verbosity

    def _initialize(self, X):
        """
        Generate multiple sets of probabilities that determines if corresponding
        features are being selected during the evaluation phase.


        Parameters
        ----------
        X : pandas.core.frame.DataFrame or numpy.ndarray of shape (n_samples,
        n_features)
            The data to fit.

        Returns
        -------
        ``particles``
            The probability array of shape (n_particles, n_features), which contains
            sets of different probabilities which determines if corresponding
            features are being selected during the evaluation phase.
        ``velocities``
            The velocity array of shape (n_particles, n_features), which is being
            used to update the velocities of the particles. 'velocities'
            will be calculated during the with the '_calculate_velocities' function
            from class 'Communication'.
        ``global_best``
            A variable that determines the velocities being calculated. The value of
            'global_best' is None when its first defined during initiation.
        ``global_best_particle``
            A variable that store the row and columns numbers of the best particle
            found during the evaluation phase.
        """
        if not isinstance(X, pd.core.frame.DataFrame) and not isinstance(X, np.ndarray):
            raise ValueError("Argument 'X' only accept 'pandas.core.frame.DataFrame' or 'numpy.ndarray' as input.")

        if self.verbosity:
            print(f"{self._system_datetime} Particle Swarm Feature Selection CV started.")
            print(f"{self._system_datetime} Initiate 'global_best', 'global_best_particle', 'particles' and 'velocities'.")

        particles = np.random.random(size=(self.n_particles, X.shape[1]))
        particles = pd.DataFrame(particles)
        velocities = np.zeros(particles.shape)
        global_best = None
        global_best_particle = None

        return particles, velocities, global_best, global_best_particle


class _Evaluation(_Base):
    """
    Class '_Evaluation' consist of a single method '_evaluate_performance', and
    inherent class '_Base' as the sole parent class to inherent class
    method '_system_datetime'. 5 arguments are required to instantiate
    class '_Evaluation'.
    """
    def __init__(self, estimator, cv, scoring, n_jobs, verbosity):
        """
        Parameters
        ----------
        estimator : estimator object.
            An object of that type is instantiated for each search point.
            This object is assumed to implement the scikit-learn estimator api.
            Either estimator needs to provide a ``score`` function,
            or ``scoring`` must be passed.

        cv : int, cross-validation generator or an iterable, optional
            Determines the cross-validation splitting strategy.
            Possible inputs for cv are:
              - None, to use the default 3-fold cross validation,
              - integer, to specify the number of folds in a `(Stratified)KFold`,
              - An object to be used as a cross-validation generator.
              - An iterable yielding train, test splits.
            For integer/None inputs, if the estimator is a classifier and ``y`` is
            either binary or multiclass, :class:`StratifiedKFold` is used. In all
            other cases, :class:`KFold` is used.

        scoring : string, callable or None, default=None
            A string (see model evaluation documentation) or
            a scorer callable object / function with signature
            ``scorer(estimator, X, y)``.
            If ``None``, the ``score`` method of the estimator is used.

        n_jobs : int, default=-1
            Number of jobs to run in parallel. At maximum there are
            ``n_points`` times ``cv`` jobs available during each iteration.

        verbosity : int
                    'verbosity' controls if any messages are being print
                    out during feature selection processes.
        """

        if not isinstance(cv, int):
            raise ValueError("Argument 'cv' only accept integer as input.")

        if not isinstance(scoring, str):
            raise ValueError("Argument 'cv' only accept string as input.")

        if not isinstance(n_jobs, int):
            raise ValueError("Argument 'n_jobs' only accept integer as input.")

        if not isinstance(verbosity, int):
            raise ValueError("Argument 'verbosity' only accept integer as input.")

        _Base.__init__(self)
        self.estimator = estimator
        self.cv = cv
        self.scoring = scoring
        self.candidates_score = {}
        self.n_jobs = n_jobs
        self.verbosity = verbosity

    def _evaluate_performance(self, X, y, particles):
        """
        Parameters
        ----------
        X : pandas.core.frame.DataFrame or numpy.ndarray of shape (n_samples, n_features)
            The data to fit.

        y : array-like of shape (n_samples,) or (n_samples, n_outputs),
            The target variable to try to predict in the case of
            supervised learning.

        particles : pandas.core.frame.DataFrame
                    The probability array of shape (n_particles, n_features), which contains
                    sets of different probabilities which determines if corresponding
                    features are being selected during the evaluation phase.

        Returns
        -------
        ``particles``
            As described in 'Parameters' section.
        ``velocities``
            The velocity array of shape (n_particles, n_features), which is being
            used to update the velocities of the particles. 'velocities'
            will be calculated during the with the '_calculate_velocities' function
            from class 'Communication'.
        ``global_best``
            A variable that determines the velocities being calculated. The value of
            'global_best' is None when its first defined during initiation.
        ``global_best_particle``
            A variable that store the row and columns numbers of the best particle
            found during the evaluation phase.
        """
        if self.verbosity:
            print(f"{self._system_datetime} Evaluating particles:")

        if isinstance(X, pd.core.frame.DataFrame):
            X = X.to_numpy()

        for i, vals in tqdm(particles.iterrows(), total=particles.shape[0]):
            # selecting particles base on randomly generated probabilities from parent class 'Initialization'.
            is_selected = vals >= np.random.random()
            particle = vals[is_selected].index
            particle = tuple(particle)

            # if selected particle contains any features and the selected particle has not been evaluated before,
            # evaluate the particle.
            is_any_particle = any(particle)
            is_not_scored = particle not in self.candidates_score
            if is_any_particle and is_not_scored:
                cv_score = cross_val_score(
                    estimator=self.estimator,
                    cv=self.cv,
                    X=X[:, particle],
                    y=y,
                    scoring=self.scoring,
                    n_jobs=self.n_jobs
                )

                self.candidates_score[(i, particle)] = cv_score.mean()

        results = pd.DataFrame([self.candidates_score], index=['score']).T

        return results


class _Communication(_Base):
    """
    Class '_Communication' consist of 2 methods '_update_global_best',
    and '_calculate_velocities'. Class '_Communication' inherent class
    '_Base' as the sole parent class to inherent class method
    '_system_datetime'. 1 argument are required to instantiate class
    '_Communication'.
    """
    def __init__(self, verbosity):
        """
        Parameters
        ----------
        verbosity : int
                    'verbosity' controls if any messages are being print
                    out during feature selection processes.
        """
        if not isinstance(verbosity, int):
            raise ValueError("Argument 'verbosity' only accept integer as input.")

        _Base.__init__(self)
        self.verbosity = verbosity

    def _update_global_best(self, evaluation_results, global_best, global_best_particle):
        """
        Update the global best variable found during evaluation phase.

        Parameters
        ----------
        evaluation_results : pd.core.frame.DataFrame
                      The scores array that uses a tuple of selected
                      features as index and stores the corresponding
                      scores evaluated.

        global_best : float
                      A variable that determines the velocities being calculated.
                      The value of 'global_best' is None when its first defined
                      during initiation and will be updated during communication
                      phase.

        global_best_particle : tuple
                            A variable that store the row and columns numbers of
                            the best particle found during the evaluation phase.
                            'global_best_particle' will be updated during the
                            communication phase.

        Returns
        -------
        ``global_best``
            As described in 'Parameters' section.
        ``global_best_particle``
            As described in 'Parameters' section.
        """
        if self.verbosity:
            print(f"\n{self._system_datetime} Update global best score and best particle.")

        # get the current best particle and the current best score from evaluation results.
        current_best_particle = evaluation_results.idxmax().iloc[0]
        current_best = evaluation_results.max().iloc[0]

        # if the global best score is not defined or a better particle is found,
        # update the current best score and particle.
        is_global_best_not_defined = global_best is None and global_best_particle is None
        is_current_particle_better = global_best is None or global_best < current_best
        if is_global_best_not_defined or is_current_particle_better:
            global_best = current_best
            global_best_particle = current_best_particle

        return global_best, global_best_particle

    def _calculate_velocities(self, particles, global_best_particle, max_iter):
        """
        Update the global best variable found during evaluation phase.

        Parameters
        ----------
        particles : pandas.core.frame.DataFrame
                    The probability array of shape (n_particles, n_features), which contains
                    sets of different probabilities which determines if corresponding
                    features are being selected during the evaluation phase.

        global_best_particle : tuple
                    A variable that store the row and columns numbers of
                    the best particle found during the evaluation phase.
                    'global_best_particle' will be updated during the
                    communication phase.

        max_iter : int
                    Determines the maximum number of iterations or step size
                    that particles or probabilities will be updated.

        Returns
        -------
        `velocities``
            The velocity array of shape (n_particles, n_features), which is being
            used to update the velocities of the particles. 'velocities'
            will be calculated during the with the '_calculate_velocities' function
            from class 'Communication'.
        """
        if self.verbosity:
            print(f"{self._system_datetime} Calculate new velocities for particles.")

        global_best_particle = particles.loc[global_best_particle[0]]
        velocities = (global_best_particle - particles) / max_iter

        return velocities


class ParticleSwarmFeatureSelectionCV(_Initialization, _Evaluation, _Communication):
    """
    Class 'ParticleSwarmFeatureSelectionCV' consist of 1 method 'fit'.
    Class 'ParticleSwarmFeatureSelectionCV' inherent classes
    '_Initialization', '_Evaluation' and '_Communication' as the parent
    classes to inherent class methods from them. 5 arguments and 2 optional
    arguments are required to instantiate class 'ParticleSwarmFeatureSelectionCV'.
    """
    def __init__(self, n_particles, estimator, cv, scoring, max_iter, n_jobs=-1, verbosity=0):
        """
        Parameters
        ----------
        n_particles : int
              'n_particles' controls how many sets of probabilities
              are generated during the initialization process.

        estimator : estimator object.
            An object of that type is instantiated for each search point.
            This object is assumed to implement the scikit-learn estimator api.
            Either estimator needs to provide a ``score`` function,
            or ``scoring`` must be passed.

        cv : int, cross-validation generator or an iterable, optional
            Determines the cross-validation splitting strategy.
            Possible inputs for cv are:
              - None, to use the default 3-fold cross validation,
              - integer, to specify the number of folds in a `(Stratified)KFold`,
              - An object to be used as a cross-validation generator.
              - An iterable yielding train, test splits.
            For integer/None inputs, if the estimator is a classifier and ``y`` is
            either binary or multiclass, :class:`StratifiedKFold` is used. In all
            other cases, :class:`KFold` is used.

        scoring : string, callable or None, default=None
            A string (see model evaluation documentation) or
            a scorer callable object / function with signature
            ``scorer(estimator, X, y)``.
            If ``None``, the ``score`` method of the estimator is used.

        max_iter : int
            Determines the maximum number of iterations or how many steps
            that particles or probabilities will be updated.

        n_jobs : int, default=-1
            Number of jobs to run in parallel. At maximum there are
            ``n_points`` times ``cv`` jobs available during each iteration.

        verbosity : int, default=0
            'verbosity' controls if any messages are being print
            out during feature selection processes.
        """
        if not isinstance(max_iter, int):
            raise ValueError("Argument 'max_iter' only accept integer as input.")

        _Initialization.__init__(self, n_particles, verbosity)
        _Evaluation.__init__(self, estimator, cv, scoring, n_jobs, verbosity)
        _Communication.__init__(self, verbosity)

        self.best_score_ = None
        self.best_features_ = None
        self.best_proba_ = None
        self.n_particles = n_particles
        self.estimator = estimator
        self.cv = cv
        self.scoring = scoring
        self.n_iter = max_iter
        self.first_iter = max_iter
        self.n_jobs = n_jobs
        self.verbosity = verbosity

    def fit(self, X, y):
        particles, velocities, global_best, global_best_particle = self._initialize(X)
        while self.n_iter > 0:
            if self.n_iter != self.first_iter and self.verbosity:
                print(f"{self._system_datetime} Update particles' velocities.")

            particles += velocities
            results = self._evaluate_performance(X, y, particles)
            global_best, global_best_particle = self._update_global_best(results, global_best, global_best_particle)
            velocities = self._calculate_velocities(particles, global_best_particle, self.n_iter)

            if self.verbosity:
                print(f"{self._system_datetime} Iteration {self.first_iter - self.n_iter} is done.")

            self.n_iter -= 1

        self.best_proba_ = particles.loc[global_best_particle[0], list(global_best_particle[1])]
        self.best_features_ = global_best_particle[1]
        self.best_score_ = global_best
