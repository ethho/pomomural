import csv
from google_images_search import GoogleImagesSearch #pip install Google-Images-Search I'm not sure how to use poetry lol
import openai #pip install openai
from configparser import ConfigParser

def read_conf_file(keys_filename = "keys.ini"):
	try:
		config_object = ConfigParser()
		config_object.read(keys_filename)
		GOOGLE_IMAGES_SEARCH_API_KEY = config_object["keys"]["GOOGLE_IMAGES_SEARCH_API_KEY"]
		GOOGLE_IMAGES_SEARCH_PROJECT_CX = config_object["keys"]["GOOGLE_IMAGES_SEARCH_PROJECT_CX"]
		openai_api_key = config_object["keys"]["openai_api_key"]
		return GOOGLE_IMAGES_SEARCH_API_KEY,GOOGLE_IMAGES_SEARCH_PROJECT_CX, openai_api_key
	except Exception as e:
		print(e)
		print("Cheater :), don't try to steal my API Keys")
		return None

temp = read_conf_file
start = False
if temp != None:
	GOOGLE_IMAGES_SEARCH_API_KEY, GOOGLE_IMAGES_SEARCH_PROJECT_CX, openai_api_key = read_conf_file("keys.ini")
	openai.api_key = openai_api_key
	start = True
else:
	print("API keys not provided")

def process_dataset_csv(dataset_path="Mural_Registry.csv"):
    """
        Reads a csv file and returns a dictionary containing the dataframe entries
        The keys are the column names and each value is a list containing the corresponding column
        Parameters: Path to dataset
        Returns: Dictionary
    """
    dataset_dict = {}
    line_count = 0
    with open(dataset_path,"r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if line_count == 0:
                for key,value in row.items():
                    dataset_dict[key] = []
                    dataset_dict[key].append(value)
            else:
                for key,value in row.items():
                    dataset_dict[key].append(value)
            line_count += 1
    return dataset_dict

def create_prompt_from_row(df_dict,row):
    """
      Creates the prompt that will be used for both the google search as well as the Dall-E 2 image generation
      Parameters: df_dictionary as well as row -> integer which is the index to that row
    """
    prompt = df_dict["Artwork Title"][row] + " by " + df_dict["Artist Credit"][row] + " located in " + df_dict["Street Address"][row] + " of " + df_dict["Affiliated (or Commissioning) Organization"][row]
    return prompt

def create_image_url(df_dict,latitude_colname,longitude_colname,img_url_keyname = "image_url"):
    """
        Takes dictionary dataset as an input along with the column names of latitude and longitude as well as a key name
        and adds an extra key, value pair to the dict: the key will be the input to the function and the values will be the 
        image urls using the google image search API
        Parameters: df_dictionary, column names for latitude and longitude, image url key name
        Returns: Edited dictionary
    """
    gis = GoogleImagesSearch(GOOGLE_IMAGES_SEARCH_API_KEY,GOOGLE_IMAGES_SEARCH_PROJECT_CX)
    num_rows = len(df_dict[latitude_colname])
    df_dict[img_url_keyname] = []
    for row in range(num_rows):
      _search_params = {
      'q': create_prompt_from_row(df_dict,row),
      'num': 1,
      'fileType': 'png',
      }
      gis.search(search_params=_search_params)
      image = list(gis.results())[0]
      df_dict[img_url_keyname].append(image.url)
    return df_dict

def create_dall_e_image_url(df_dict,latitude_colname,longitude_colname,dall_e_img_url_keyname = "image_url"):
    """
        Takes dictionary dataset as an input along with the column names of latitude and longitude as well as a key name
        and adds an extra key, value pair to the dict: the key will be the input to the function and the values will be the 
        image urls using the the Dall-E 2 API
        Parameters: df_dictionary, column names for latitude and longitude, image url key name
        Returns: Edited dictionary
    """
    num_rows = len(df_dict[latitude_colname])
    df_dict[dall_e_img_url_keyname] = []
    for row in range(num_rows):
      response = openai.Image.create(
        prompt=create_prompt_from_row(df_dict,row),
        n=1,
        size="1024x1024"
      )
      df_dict[dall_e_img_url_keyname].append(response['data'][0]['url'])
    return df_dict
    
if __name__ == "__main__":
	if start == False:
		print("Didn't work")
	else:
		df_dict = process_dataset_csv("../../data/Mural_Registry.csv")
