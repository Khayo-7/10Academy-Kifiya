import zipfile

def extract_datasets(input_data_path, output_data_path):

    with zipfile.ZipFile(input_data_path, 'r') as zip:    
        zip.extractall(output_data_path)
        print(f"Extracted {input_data_path} to {output_data_path}")
