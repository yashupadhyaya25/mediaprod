import os
import pandas as pd

def prepare_dataset():
    # preparing dataset
    dataset_folder = r'ML/Train_txt/'
    csv_path = r'ML/Dataset/'
    dataset_df = pd.DataFrame()
    for sub_folder in os.listdir(dataset_folder):
        for file in os.listdir(dataset_folder+sub_folder):
            category = sub_folder.split('_')[0]
            with open(dataset_folder+sub_folder+'/'+file) as f :
                # file_text = str(f.readlines())
                file_text = f.readlines()
            f.close()
            # print(file_text)
            text_data = []
            for word in file_text :
                text_data.append(word.strip())
            # print(text_data)
            data_dict = {}
            data_dict['text'] = str(text_data)[1:-1].replace("'","").replace('"',"").replace("None","").replace("#","").replace('\n','').strip()
            data_dict['category'] = category
            dataset_df = dataset_df.append(data_dict,ignore_index = True)

    dataset_df.to_csv(csv_path+'ML_dataset.csv',index=False)
    ml_dataset =  pd.read_csv(csv_path+'ML_dataset.csv')

    # splitting data in training and testing set
    training_data = ml_dataset.sample(frac=0.8, random_state=25)
    testing_data = ml_dataset.drop(training_data.index)

    # Train and Test csv export
    ml_dataset.to_csv(csv_path+'train.csv',index=False)
    testing_data.to_csv(csv_path+'test.csv',index=False)


if '__main__' == __name__ :
    prepare_dataset()
