#import pinecone
#from langchain.embeddings import OpenAIEmbeddings
import openai
import ast
import json
import openai
from azure.search.documents.models import Vector
from azure.search.documents import SearchClient
import re
#from azure.core.credentials import AzureKeyCredential

openai.api_key = "62bc134381b045a9a8d5961b2c25a984"
openai.api_base= "https://oai-podcastexplorer.openai.azure.com"
openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"


class Handler:

    
    def get_responses(pine_index, search_client, vector, question):
        
        # get the response from the pinecone 
        pinecone_res = pine_index.query(
            top_k=4,
            include_values=False,
            include_metadata=True,
            vector=vector,
            namespace='angebissen')
        
        vector_search = Vector(value=vector, k=3, fields="contentVector")

        cog_search_result = search_client.search(  
        search_text=question,  
        vectors=[vector_search],
        select=["blob_name", "content","chunknumber"],
        query_type="semantic",
        query_language="de-de",
        semantic_configuration_name="my-semantic-config",
        query_caption="extractive", 
        query_answer="extractive",
        top=4
        )

        print("successfully gotten the responses for pinecone and search")

        return pinecone_res, cog_search_result
    
    
    def extract_values(pinecone_response, cogSearch_response):

        pine_list = pinecone_response['matches']
        pine_tuple_list = []

        for x in pine_list:
            a = x['metadata']
            pine_tuple_list.append((int(a['chunk_counter']), a['blob_name']))

        
        cog_tuple_list = []

        for a in cogSearch_response:
            cog_tuple_list.append((a["chunknumber"], a["blob_name"]))

        print("Successfully extracted the values for pinecone and search")
        
        return pine_tuple_list, cog_tuple_list
    
    
    def calc_intersections(pinecone_tuples, cogSearch_tuples):

        pinecone_episodes = []
        cogSearch_episodes = []
        for y in range(0, len(pinecone_tuples)):

            pinecone_episodes.append(pinecone_tuples[y][1])
            cogSearch_episodes.append(cogSearch_tuples[y][1])
        
        # calculate intersection
        A = set(pinecone_episodes)
        B  = set(cogSearch_episodes)
        intersec = A & B

        # this calculates just the intersection of episodes
        dis_pine = len(A)
        dis_Search = len(B)
        inter = len(intersec)

        #-----------------------------------------------
        # this calculates the intersection of episodes and chunks

        A2 = set(pinecone_tuples)
        B2 = set(cogSearch_tuples)

        intersec2 = len(A2 & B2)

        print("calculated the intersections")

        return dis_pine, dis_Search, inter, intersec2
    
    
    def calcKPI(pinecone_tuples , cogSearch_tuples):

        # basic test
        if (len(pinecone_tuples) != len(cogSearch_tuples)) or (len(pinecone_tuples[0]) != len(cogSearch_tuples[0])):
            raise Exception("Hier läuft etwas extrem schief")
    
       # here we will evaluate how the sequence equal - if the the same chunks got scored on the same rank
        for y in range(0, len(pinecone_tuples)):
              
            counter = 0
            # eine Übereinstimmung zählt nur, wenn die chunknumber und der Blobname gleich ist! Achtung, das wertet nur ob die Reihenfolge gleich ist.
            # werte nicht die eigentliche schnittmenge
            if pinecone_tuples[y][0] == cogSearch_tuples[y][0] and pinecone_tuples[y][1] == cogSearch_tuples[y][1]:
                counter += 1
        
        print("calculated the KPI")
            
        return counter/len(pinecone_tuples)
    
    def answer_to_json(res_pinecone, res_search):
    
        pine_list = res_pinecone['matches']

        a = {
            "Textteil 1": pine_list[0]['metadata']['clear_text'],
            "Textteil 2" : pine_list[1]['metadata']['clear_text'],
            "Textteil 3" : pine_list[2]['metadata']['clear_text'],
            "Tectteil 4" : pine_list[3]['metadata']['clear_text']
        }

        pine = json.dumps(a)

        counter = 1
        b = dict()

        for r in res_search:
            b[f"Textteil {str(counter)}"] =  r['content']
            counter += 1
            


        search = json.dumps(b)

        return pine, search



    
    def ask_for_relevance(pine_json, CogSearch_json, question):


        with open('metaVergleich/propt_scala.txt') as f:
            prompt = f.read()

        prompt = prompt.replace("<<Pinecone>>", pine_json)
        prompt = prompt.replace("<<Frage>>", question)
        prompt = prompt.replace("<<Search>>", CogSearch_json)

        completion = openai.Completion.create(model="gpt-3.5-turbo", deployment_id= "gpt-35-turbo", prompt=prompt, temperature=0, max_tokens=10)



        print("asked for the relevance")
        a = completion.choices[0].text.strip()

        numbers = re.findall(r'\d+', a)

        return numbers

        
   
    def ask_which_ones_better(pine_json, CogSearch_json, question):
        
        with open('metaVergleich/prompt.txt') as f:
            prompt = f.read()

        
    
        prompt = prompt.replace("<<Pinecone>>", pine_json)
        prompt = prompt.replace("<<Frage>>", question)
        prompt = prompt.replace("<<Search>>", CogSearch_json)

        completion = openai.Completion.create(model="gpt-3.5-turbo", deployment_id= "gpt-35-turbo", prompt=prompt, temperature=0, max_tokens=10)

        a = completion.choices[0].text.strip()
        
        matches = re.findall(r'\b(Pinecone|Search)\b', a)
        return matches[0]









     






        
