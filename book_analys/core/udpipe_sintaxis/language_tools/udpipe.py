import sys

from ufal.udpipe import Model, Pipeline, ProcessingError  # pylint: disable=no-name-in-module


class UDPipe:
    def __init__(self):
        print('Loading model: ')
        model_path = r"D:\py_projects\IWonnaBook\udpipe_syntagrus.model"
        self.model = Model.load(model_path)
        if not self.model:
            print('Модель не загружена :(')
            sys.exit(1)
        self.pipeline = Pipeline(self.model, "tokenize", Pipeline.DEFAULT, Pipeline.DEFAULT, "conllu")
        print('done\n')

    def get_sintax(self, text):
        error = ProcessingError()
        processed = self.pipeline.process(text, error)
        if error.occurred():
            print("An error occurred when running run_udpipe: ")
            print(error.message)
            print("\n")
        return processed
