""" Module implementing agent in the system. """

from multiprocessing import Lock

from sklearn import svm
from sklearn.utils.validation import NotFittedError

from sample_storage import SampleStorage
from lexicon import Lexicon


class Agent(object):
    """
    Class representing agent in the system.

    Agent remember old samples from environment and can classify new ones. It can name categories.

    Agent has some mechanisms that will help it forget the samples if needed.

    There is an option of monitoring agent fitness.
    """

    # AID is set that it will match networks nodes.
    AID = 0
    AID_lock = Lock()

    def __init__(self, aid=None, classifier=None, sample_storage=None, lexicon=None):
        """
        Parameters explanation:
        aid - an agent id
        classifier - machine learning algorithm
            which implements functions fit and predict as defined in sklearn library.
        sample_storage - storage all samples used to teach classifier
        lexicon - storage associations between sample storage categories and words.
        """
        self.id = aid or Agent.get_next_id()
        self.classifier = classifier or svm.SVC()
        self.sample_storage = sample_storage or SampleStorage()
        self.lexicon = lexicon or Lexicon

        # fitness is dictionary of agent's fitness measures
        self.fitness = {}

    @classmethod
    def get_next_id(cls):
        """
        Generates new unique id for agent.

        It asserts that user doesn't specify id value for any agent.
        """
        cls.AID_lock.acquire()
        aid = cls.AID
        cls.AID += 1
        cls.AID_lock.release()
        return aid

    def add_sample(self, sample_index, environment, category=None):
        """
        Adds sample_index form environment to storage.
        """
        self.sample_storage.add_sample(sample_index, environment, category)

    def bad_word_for_category(self, word, category):
        """
        Weakens association between word and category in lexicon.
        """
        self.lexicon.weaken_association(word, category)

    def category_for_word(self, word):
        return self.lexicon.category_for_word(word)

    def classify(self, sample):
        """
        Classify given specific sample.

        If agent known only one class, it return the class.
        If agent hasn't taught any classification yet, it  return None.
        """
        if self.sample_storage.get_categories_size() == 1:
            return self.sample_storage.get_categories()[0]
        else:
            try:
                # Classifier predicts categories for array of samples and returns array of predicted categories.
                return self.classifier.predict([sample])[0]
            except NotFittedError:
                return None

    def forget(self):
        """
        Weakens agent's memory of all known samples and removes categories that become scarcely known.
        """
        self.sample_storage.decrease_weights()
        removed_categories = self.sample_storage.remove_weak_samples()

        for category in removed_categories:
            self.lexicon.remove_category(category)

    def good_category_for_sample(self, category, sample_index, environment):
        """
        Strengthen memory of sample storage samples in category that are similar to sample form environment.
        """
        self.sample_storage.increase_weights_in_category(sample_index, environment, category)

    def good_word_for_category(self, word, category):
        """
        Strengthen association between word and category.
        """
        self.lexicon.strengthen_association(word, category)

    def learn(self):
        """
        Teaches classifier using samples and class from sample storage.
        """
        data, decisions = self.sample_storage.export()
        if len(decisions) > 0 and self.sample_storage.get_categories_size() > 1:
            self.classifier.fit(data, decisions)

    def update_fitness(self, name, information):
        """
        Gives information to fitness measure with a specific name.
        """
        self.fitness[name].update(information)

    def the_best_category_for_word(self, word, category):
        """
        Weakens associations between other categories and word.
        """
        self.lexicon.weaken_other_associations_for_categories(word, category)

    def the_best_word_for_category(self, word, category):
        """
        Weakens associations between other words and category.
        """
        self.lexicon.weaken_other_associations_for_words(word, category)

    def word_for_category(self, category):
        return self.lexicon.word_for_category(category)

    def get_category_class(self, category):
        """"
        Returns class of given category.
        """
        return self.sample_storage.get_class(category)

    def get_id(self):
        """
        Returns agent's id.
        """
        return self.id

    def get_fitness_measure(self, name):
        """
        Returns value of fitness measure with a specific name.
        """
        return self.fitness[name].get_measure()

    def get_words(self):
        """
        Returns all words known by agents.
        """
        return self.lexicon.get_words()

    def set_fitness(self, name, fitness_measure):
        """
        Adds given fitness measure with a specific name.
        """
        self.fitness[name] = fitness_measure
