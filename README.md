# ps-opt
This Python package provides a tool for hyperparameter tuning and feature selection in machine learning models using Particle Swarm Optimization (PSO) techniques. The package includes a vanilla PSO for feature selection, a vanilla PSO for hyperparameter tuning, and two different PSO variants for machine learning hyperparameter tuning.

## Features

Vanilla PSO for Feature Selection: This feature uses the standard PSO algorithm to select the most optimal features for a given machine learning model. The algorithm works by searching the feature space and identifying a subset of features that maximizes the performance of the model.

Vanilla PSO for Hyperparameter Tuning: This feature uses the standard PSO algorithm to tune the hyperparameters of a given machine learning model. The algorithm works by searching the hyperparameter space and identifying a set of parameters that maximize the performance of the model.

PSO Variants for Hyperparameter Tuning: This package includes two different PSO variants for hyperparameter tuning. These variants offer different search strategies and can provide better results depending on the specific characteristics of the problem.

Cross-Validation: The package uses cross-validation in the hyperparameter tuning process to avoid overfitting and to ensure that the tuned parameters generalize well to unseen data.

## Example Usage
The following is a basic example of how to use this package:


Installation
------------

Install it using pip:

    pip install ps-optimize

Hyperparameters Tuning
----------------

    import pandas as pd
    from sklearn.datasets import make_classification
    from ps_opt.hyperparameters_tuning import ParticleSwarmSearchCV
    from ps_opt.search_space_characteristics import Categorical, Real, Integer
    from sklearn.linear_model import LogisticRegression
    
    
    X, y = make_classification()
    X = pd.DataFrame(X)
    y = pd.Series(y)
    
    search_space = {
        "penalty": Categorical("l1", "l2", "elasticnet", None),
        "max_iter": Integer(10, 20, "exponential"),
        "tol": Real(.0001, .1, "uniform"),
        "solver": Categorical('lbfgs', 'liblinear', 'newton-cg', 'sag', 'saga')
    }
    
    psocv = ParticleSwarmSearchCV(
        search_space=search_space,
        n_particles=30,
        estimator=LogisticRegression,
        cv=5,
        scoring="accuracy",
        max_iter=10,
        n_jobs=1,
        verbosity=0
    )
    
    psocv.fit(X, y)
    
    print(f"Best Score: {psocv.best_score_}")
    print(f"Best Parameters: {psocv.best_params_}")
    print(f"Best Probabilities: {psocv.best_proba_}")


Feature Selection
-------------------------

    import pandas as pd
    from sklearn.datasets import make_classification
    from ps_opt.feature_selection import ParticleSwarmFeatureSelectionCV
    from ps_opt.search_space_characteristics import Categorical, Real, Integer
    from sklearn.linear_model import LogisticRegression
    
    
    X, y = make_classification()
    X = pd.DataFrame(X)
    y = pd.Series(y)
    
    psocv = ParticleSwarmFeatureSelectionCV(
        n_particles=30,
        estimator=LogisticRegression,
        cv=5,
        scoring="accuracy",
        max_iter=10,
        n_jobs=-1,
        verbosity=0
    )
    
    psocv.fit(X, y)
    
    print(f"Best Score: {psocv.best_score_}")
    print(f"Best Features: {psocv.best_features_}")
    print(f"Best Probabilities: {psocv.best_proba_}")
