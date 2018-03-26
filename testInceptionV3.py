import numpy as np
from utils import GetLabelAndCategory
import time


def get_model_api():
    from keras.preprocessing.image import img_to_array
    from keras.models import model_from_json
    from keras.preprocessing import image
    from keras.applications.inception_v3 import preprocess_input

    json_file=open('model.json','r')
    load_model_json=json_file.read()
    json_file.close()
    load_model =model_from_json(load_model_json)
    load_model.load_weights('model.h5')

    def model_api(input_data,array_type):
        if(array_type):
            label=arraytype(input_data)
            return label


        """
        Args:
            input_data: submitted to the API, raw string

        Returns:
            output_data: after some transformation, to be
                returned to the API

        """
        # 2. process input
        start=time.time()
        img = image.load_img(input_data, target_size=(299, 299))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        read_dictionary = np.load('CategoryMapping.npy').item()
        Mapping = GetLabelAndCategory(read_dictionary)

        preds = load_model.predict(x)
        end = time.time()
        response_time = end - start
        print(response_time)
        it = np.nditer(preds, flags=['f_index'])
        result = []
        while not it.finished:
          result.append(it[0])
          it.iternext()
        max_probality_Catgory = max(result)
        index = result.index(max_probality_Catgory)
        Predicted_Category = Mapping[index]
        label = "{}: {:.2f}%".format(Predicted_Category, max_probality_Catgory * 100)

        # 5. return the output for the api
        return label
    def arraytype(x):
        start=time.time()
        #img = image.load_img(input_data, target_size=(299, 299))
        x = image.img_to_array(x)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        read_dictionary = np.load('CategoryMapping.npy').item()
        Mapping = GetLabelAndCategory(read_dictionary)

        preds = load_model.predict(x)
        end = time.time()
        response_time = end - start
        print(response_time)
        it = np.nditer(preds, flags=['f_index'])
        result = []
        while not it.finished:
          result.append(it[0])
          it.iternext()
        max_probality_Catgory = max(result)
        index = result.index(max_probality_Catgory)
        Predicted_Category = Mapping[index]
        label = "{}: {:.2f}%".format(Predicted_Category, max_probality_Catgory * 100)

        return label
    return model_api



