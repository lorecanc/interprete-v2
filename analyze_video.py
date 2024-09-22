import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig

def analyze_video_with_vertex(video_uri: str, prompt_type: str):
    project_id = "prj-c-dev-shared-resource"
    vertexai.init(project=project_id, location="europe-west1")
    model = GenerativeModel("gemini-1.5-pro-001")

    if prompt_type == "default":
        prompt = """
        Voglio che tu agisca come un esperto di media e marketing:
        Fornisci una descrizione dettagliata della pubblicità, includendo tutte le informazioni rilevanti e le dichiarazioni importanti delle persone presenti nello spot.
        Dopo aver descritto dettagliatamente la pubblicità, fanne un'analisi dal punto di vista delle scelte comunicative (narrative, visive...).
        Dopo aver completato le prime due sezioni, scrivi una trascrizione PAROLA PER PAROLA dell'audio del video.

        * NON scrivere i titoli delle sezioni, scrivi solo i contenuti dell'analisi
        """
    elif prompt_type == "gara_desa":
        prompt = """
        Sei un esperto di marketing/advertising e lavori in un centro media. Voglio tu faccia un’analisi approfondita sulla pubblicità rappresentata nel video allegato. Sappi che il mercato di riferimento è quello dei detergenti per la casa/detergenti per bucato/prodotti per cura della persona. Inizia fornendomi una descrizione dettagliata dello spot, includendo nome del prodotto (se presente). Sviluppa la tua analisi in modo da evidenziare le seguenti aree:

        Target Audience: qual è il target di questo spot?
        Tone of Voice/Lunghezza Spot: qual è il tono con cui lo spot si rivolge al suo pubblico? Quanto dura lo spot?
        Informativo vs Emotivo: lo spot si focalizza di più sul descrivere il prodotto evidenziandone caratteristiche distintive rispetto alla concorrenza o creando una connessione emotiva del consumatore con il prodotto stesso?
        Prodotto singolo o linea: lo spot parla di un prodotto solo o di una gamma?
        Innovazione: lo spot esplicita caratteristiche innovative del prodotto (nuova formula, nuova concentrazione…)
        Sostenibilità: si esplicita l’aspetto ecologico/sostenibile del prodotto?
        Slogan/Jingle/Claim: è presente uno slogan/jingle/claim facilmente associabile/riconducibile al prodotto? Se sì, analizzane il messaggio

        L’obiettivo è fornire insights utili a costruire un'analisi della concorrenza, evidenziando gli aspetti positivi e negativi della comunicazione.

        * NON scrivere i titoli delle sezioni, scrivi solo i contenuti dell'analisi
        """
    elif prompt_type == "affinity":
            prompt = """
        Sei un esperto di marketing/advertising e lavori in un centro media. Voglio tu faccia un’analisi approfondita sulla pubblicità rappresentata nel video allegato. Sappi che il mercato di riferimento è quello del pet food, in particolare per cani e gatti. Inizia fornendomi una descrizione dettagliata dello spot, includendo nome del prodotto (se presente). Sviluppa la tua analisi in modo da evidenziare le seguenti aree:

        Target Audience: qual è il target di questo spot?
        Tone of Voice/Lunghezza Spot: qual è il tono con cui lo spot si rivolge al suo pubblico? Quanto dura lo spot?
        Informativo vs Emotivo: lo spot si focalizza di più sul descrivere il prodotto evidenziandone caratteristiche distintive rispetto alla concorrenza o creando una connessione emotiva del consumatore con il prodotto stesso?
        Prodotto singolo o linea: lo spot parla di un prodotto solo o di una gamma? In particolare, la linea si riferisce a gatti, cani o entrambi?
        Innovazione: lo spot esplicita caratteristiche innovative del prodotto (nuova formula, nuova concentrazione…)
        Sostenibilità: si esplicita l’aspetto ecologico/sostenibile del prodotto?
        Slogan/Jingle/Claim: è presente uno slogan/jingle/claim facilmente associabile/riconducibile al prodotto? Se sì, analizzane il messaggio

        L’obiettivo è fornire insights utili a costruire un'analisi della concorrenza

        * NON scrivere i titoli delle sezioni, scrivi solo i contenuti dell'analisi
        """    
    else:
        raise ValueError("Prompt type not recognized")

    video_file = Part.from_uri(video_uri, mime_type="video/mp4")
    contents = [video_file, prompt]
    response = model.generate_content(contents)
    return response.text.replace("*","")
