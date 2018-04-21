"""
All theory models must be subclasses of this Model superclass.


"""
import pathlib
import warnings
from ..theory_results import TheoryResults



model_registry = {}

class BaseTheoryCalculator:
    def __init__(self, config, metadata):
        self.config = config
        self.metadata = metadata
        
        """ We need to load in details of the models"""
        config_file = yaml.load(config.open())
        
        self.source_by_name = config['name']
    
        
    def validate(self):
        """Validating the inputs, This function is missing for now, implement it later"""

class BaseModel:
    theory_calculator_class = None
    theory_results_class = None
    data_class = None
    metadata_class = None


    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        name = cls.name if hasattr(cls, 'name') else cls.__name__
        name = name.lower()
        print(f"Register {name}")
        model_registry[name] = cls


    """
    This is the superclass for all Models, which represent the part of the
    likelihood function that generate mean theory predictions from parameters.

    This is just the skeleton - there are various more complete designs in the sandbox.
    Delete this notice after implementing them!

    """

    def __init__(self, config, data_info, likelihood_class):
        """
        Instantiate the model from a dictionary of options.

        Subclasses usually override this to do their own instantiation.
        They should call this parent method first.
        """
        self.config=config
        self.data = self.data_class.load(data_info)
        self.metadata = self.extract_metadata(data_info)
        self.theory_calculator = self.theory_calculator_class(config, self.metadata)
        self.likelihood = likelihood_class(self.data)

    @staticmethod
    def from_name(name):
        return model_registry[name]

    def extract_metadata(self, data_info):
        pass

    def run(self, parameterSet):
        theory_results = self.theory_calculator.run(parameterSet)
        like = self.likelihood.run(theory_results)
        return like, theory_results

    def likelihood(self, parameterSet):
        return self.run[0]


