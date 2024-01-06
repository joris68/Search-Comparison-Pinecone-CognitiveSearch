import pinecone
from langchain.embeddings import OpenAIEmbeddings
import openai
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from Handler import Handler
from itertools import tee

openai.api_key = "62bc134381b045a9a8d5961b2c25a984"
openai.api_base= "https://oai-podcastexplorer.openai.azure.com"
openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"


# this functions "calculates" one row of data writes it into the data file
def write_dataline(file, pine_index, search_client, question, embedding_client):


    # first write the question to the file
    file.write(question + ",")

    # embed the question und get the answers
    #vector = embedding_object.embed_query(question)
    vector = embedding_client.embed_query(question)

  
    pinecone_res, cog_search_result = Handler.get_responses(pine_index, search_client, vector, question)

    search_result , search_result_backup = tee(cog_search_result)


    pine_tuple_list, cog_tuple_list = Handler.extract_values(pinecone_res, search_result)

    # calculate intersection and write to the file
    dis_pine, dis_Search, inter, intersec2 = Handler.calc_intersections(pine_tuple_list, cog_tuple_list)

    file.write(str(dis_pine) + "," + str(dis_Search) + "," + str(inter) + "," + str(intersec2) + ",")

    # write the sequence KPI to file

    seq_kpi = Handler.calcKPI(pine_tuple_list, cog_tuple_list)

    file.write(str(seq_kpi) + ",")

    # write which ones is better to file
    pine_json, search_json = Handler.answer_to_json(pinecone_res, search_result_backup)

    #better = Handler.ask_which_ones_better(pine_json, search_json, question)
    ## little check
    #check_names = ["Pinecone", "Search"]
    #if better in check_names:
     #   file.write(str(better) + ",")
    #else:
      #  file.write("N/A,")

    # write the skala values to the file

    number_list = Handler.ask_for_relevance(pine_json, search_json, question)

    try:
        file.write(number_list[0] + ",")
        #file.write(number_list[1])
    except:
        file.write("N/A, N/A")
        
    try:
        file.write(number_list[1])
    except:
        file.write("N/A")
    
    
    file.write("\n")



if __name__ == "__main__":

    pinecone.init(      
	    api_key='41fe2d0f-afb6-42e7-adbc-e8b60baf9aed',      
	    environment='asia-southeast1-gcp-free'      
        )      
    pine_index = pinecone.Index('mypodcastindex')

    AZURE_OPENAI_CHATGPT_DEPLOYMENT = "gpt-35-turbo"

    AZURE_OPENAI_CHATGPT_MODEL = "gpt-35-turbo"

    SEARCH_KEY = "IcV02jWtdKUJTIdR2srIgW7a4ERd4k0W1GR3CS6EkLAzSeBzDLlt"

    SEARCH_ENDPOINT ="https://gptkb-p0dc4573xp10r3r.search.windows.net"

    INDEX_NAME ="angebissen-der-angelpodcast"
    search_client = SearchClient(SEARCH_ENDPOINT, INDEX_NAME, credential=AzureKeyCredential(SEARCH_KEY))

    question_list = ["Gibt es Tipps zur Auswahl der besten Angelrouten?",
             "Kannst du mir einige bewährte Angeltechniken verraten die im Podcast besprochen wurden?",
             "Gibt es Empfehlungen für Angelgewässer oder Angelreisen?",
             "Ist Angeln Kinderfreundlich?",
             "Wie kann ich am besten mit dem Hobby Angeln beginnnen. Werden Anfängertipps genannt?",
             "Ich bin ein bisschen Wasserscheu muss ich Angst haben oft Nass zu werden beim Angeln",
             "Welche Jahreszeit ist die Beste zum Angeln?",
             "Ist Angeln Teuer mit wieviel Ausgaben muss ich rechnen?",
             "Wie kann Ich Angeln und Haustiere unter einen Hut bringen?",
             "Welche Papiere Bescheingungen und Lizenzen benötige ich zum Angeln?",
             "Gibt es spezielle Angeltechniken für verschiedene Fischarten?",
            "Welche Rolle spielt die Wetterlage beim Angeln?",
            "Kannst du Tipps zur richtigen Köderauswahl geben?",
            "Wie finde ich gute Angelplätze in meiner Region?",
            "Gibt es besondere Ausrüstungsempfehlungen für das Nachtangeln?",
            "Welche Rolle spielt die Mondphase beim Angeln?",
            "Wie gehe ich mit schwierigen Wetterbedingungen beim Angeln um?",
            "Kannst du etwas über die Bedeutung von Tarnung und Geruchskontrolle beim Angeln erzählen?",
            "Welche Vorteile bietet die Verwendung von Kunstködern gegenüber Naturködern?",
            "Welche Fischarten sind besonders herausfordernd zu angeln?",
            "Ist es besser vom Ufer aus zu angeln oder eine Bootstour zu unternehmen?",
            "Welche Sicherheitsvorkehrungen sollte man beim Angeln auf offenen Gewässern treffen?",
            "Gibt es besondere Angeltechniken für Anfänger?",
            "Wie wählt man die richtige Angelschnur aus?",
            "Was sind die besten Gewässertypen für Anfänger?",
            "Kannst du Empfehlungen für umweltfreundliches Angeln geben?",
            "Wie erkenne ich gute Angelreviere in unbekannten Gebieten?",
            "Gibt es bewährte Methoden zur Fischpopulationserhaltung?",
            "Wie kann ich die richtige Rute für mein Angelabenteuer auswählen?",
            "Welche Apps oder Online-Tools sind hilfreich für Angler?",
            "Kannst du etwas über die Rolle der Gezeiten beim Küstenangeln erzählen?",
            "Wie wichtig ist die Wahl des richtigen Angelhakens?",
            "Was sind die besten Strategien für das Fangen von Trophäenfischen?",
            "Gibt es Unterschiede in der Ausrüstung für Süß- und Salzwasserangeln?",
            "Welche Rolle spielen Köderfarben beim Angeln?",
            "Kannst du einige ungewöhnliche Angelgewässer oder -methoden vorstellen?",
            "Wie gehe ich mit Unterwasserhindernissen beim Angeln um?",
            "Was sind die besten Techniken für das Angeln in Flüssen?",
            "Wie wichtig ist die Wahl der richtigen Angelbekleidung?",
            "Gibt es besondere Überlegungen für das Eisangeln?",
    "Wie finde ich heraus welche Fischarten in meiner Region vorkommen?",
    "Kannst du etwas über die Bedeutung der Angelrutenaktion erklären?",
    "Welche Rolle spielt die Wasserqualität beim Angeln?",
    "Was sind die besten Methoden zur Fischbestandserhaltung?",
    "Wie gehe ich mit Fischschonzeiten und Fangbegrenzungen um?",
    "Welche Rolle spielt die Jahreszeit beim Fliegenfischen?",
    "Kannst du einige Angeltechniken für Raubfische vorstellen?",
    "Wie kann ich meine Angeltechniken an verschiedene Gewässertypen anpassen?",
    "Gibt es besondere Tipps für das Angeln in städtischen Gebieten?",
    "Was sind die besten Methoden zur Fischvermessung und -freilassung?",
    "Kannst du Empfehlungen für umweltfreundliche Angelköder geben?",
    "Wie wichtig ist die richtige Technik zum Hakenlösen?",
    "Was sind die besten Strategien für das Nachtangeln?",
    "Gibt es besondere Herausforderungen beim Hochseeangeln?",
    "Wie gehe ich mit Wetterumschwüngen beim Angeln um?",
    "Kannst du etwas über die Bedeutung der richtigen Angelrolle erklären?",
    "Welche Rolle spielt die Windrichtung beim Angeln?",
    "Was sind die besten Techniken für das Angeln mit lebenden Ködern?",
    "Wie kann ich meine Angelmethoden an verschiedene Jahreszeiten anpassen?",
    "Gibt es spezielle Tipps für das Angeln in Bergseen?",
    "Kannst du einige Methoden zur Vorhersage von Fischaktivitäten teilen?",
    "Wie wichtig ist die Wahl der richtigen Angelschnur für verschiedene Fischarten?",
    "Was sind die besten Methoden zur Vermeidung von Überfischung?",
    "Wie erkenne ich Anzeichen von Fischaktivität auf der Wasseroberfläche?",
    "Gibt es spezielle Angeltechniken für Kinder?",
    "Welche Rolle spielt die Tarnung beim Fischen in klarem Wasser?",
    "Was sind die besten Methoden zur Fischzählung in einem Gewässer?",
    "Kannst du Empfehlungen für umweltfreundliche Angelruten geben?",
    "Wie kann ich die richtige Taktik für das Fliegenfischen auswählen?",
    "Gibt es besondere Techniken für das Angeln in großen Seen?",
    "Welche Rolle spielt die Wasserströmung beim Angeln in Flüssen?",
    "Was sind die besten Methoden zur Fischpflege in einem Aquarium?",
    "Wie gehe ich mit Fischkrankheiten um?",
    "Kannst du einige Techniken für das Angeln an stark befischten Gewässern teilen?",
    "Wie wichtig ist die Wahl des richtigen Angelköders für verschiedene Fischarten?",
    "Was sind die besten Strategien für das Angeln auf Forellen?",
    "Gibt es besondere Überlegungen für das Angeln in Küstengebieten?",
    "Wie erkenne ich geeignete Angelgewässer in meinem Urlaubsziel?",
    "Kannst du etwas über die Bedeutung der Angelrutenlänge erklären?",
    "Welche Rolle spielt die Struktur des Gewässers beim Angeln?",
    "Was sind die besten Methoden zur Fischzählung in einem Teich?",
    "Wie kann ich meine Angeltechniken für verschiedene Tageszeiten optimieren?",
    "Gibt es spezielle Tipps für das Angeln während der Laichzeit?",
    "Kannst du einige bewährte Methoden für das Eisfischen teilen?",
    "Wie wichtig ist die richtige Montage von Angelhaken?",
    "Was sind die besten Strategien für das Angeln auf Hechte?",
    "Gibt es besondere Überlegungen für das Angeln in tropischen Gewässern?",
    "Wie gehe ich mit schwierigen Lichtverhältnissen beim Angeln um?",
    "Kannst du etwas über die Bedeutung der Angelrolle erklären?",
    "Welche Rolle spielt die Vegetation beim Angeln?",
    "Was sind die besten Methoden zur Fischzählung in einem Fluss?",
    "Wie kann ich meine Angeltechniken für verschiedene Wassertiefen optimieren?",
    "Gibt es spezielle Tipps für das Angeln von der Küste aus?",
    "Kannst du einige Methoden zur Fischidentifizierung teilen?",
    "Wie wichtig ist die Wahl des richtigen Angelgewichts?",
    "Was sind die besten Strategien für das Angeln auf Zander?",
    "Gibt es besondere Überlegungen für das Angeln in Bergbächen?",
    "Wie erkenne ich Anzeichen von kranken Fischen?",
    "Kannst du etwas über die Bedeutung der richtigen Angelrutenaktion erklären?",
    "Welche Rolle spielt die Sichttiefe beim Angeln?",
    "Was sind die besten Methoden zur Fischzählung in einem See?",
    "Wie kann ich meine Angeltechniken für verschiedene Wassertemperaturen optimieren?",
    "Gibt es spezielle Tipps für das Angeln in Gewässern mit starkem Strömung?",
    "Kannst du einige bewährte Methoden für das Nachtangeln teilen?",
    "Wie wichtig ist die richtige Pflege von Angelgerät?",
    "Was sind die besten Strategien für das Angeln auf Karpfen?",
    "Gibt es besondere Überlegungen für das Angeln in stehenden Gewässern?",
    "Wie erkenne ich Anzeichen von überfischten Gewässern?",
    "Kannst du etwas über die Bedeutung der richtigen Angelrolle erklären?"]

    # open the file
    file = open('data.csv', 'w')

    #openai.api_key = "62bc134381b045a9a8d5961b2c25a984"
    #openai.api_base= "https://oai-podcastexplorer.openai.azure.com"
    #openai.api_type = "azure"
    #openai.api_version = "2023-03-15-preview"

    # initialize embedding object
    embedding_object = OpenAIEmbeddings(deployment="text-embedding-ada-002", openai_api_key="62bc134381b045a9a8d5961b2c25a984", openai_api_type="azure", model="text-embedding-ada-002")
    #embedding_object = openai.Embedding.create(model=text)
    #embedding_client = OpenAI()

    # for all questions in list do write_line
    for x in range(0, len(question_list)):
        if x == 0:
            file.write("Question,disEpiPine,disEpiSearch,interEpi,interChunkEpi,seq,relPine,relSearch\n")
        print(f"starting with the {x} question")
        write_dataline(file, pine_index, search_client, question_list[x], embedding_object)
        print(f"finished with the {x} question")
        print("--------------------------")

    # close file
    file.close()