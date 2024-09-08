import llm,re

def getRelevancy(review_text):
    # seeds:
    # 2145  :   Long details, generally slightly lower relevancy
    # 102   :   Consice, around 2 sentences, higher relevancy
    # Chosen: 2145
    response=llm.complete("phi3.5",f"How relevant is this review to a french fry review website: `{review_text}`. Respond in under 3 sentences and a percentage: 100% being this is the most relevant thing ever to exist, and 0% meaning it is talking about something totally off topic. Relevancy should be calculated based off if it talks about french fries, what is was like ordering there, and service.",{"seed":2145})['response']
    relevance=None
    for word in re.sub(r"[^0192456789% ]","",response).split():
        word=word.replace("%","").strip()
        try:
            relevance=int(word)
            break
        except:0
    return {
        "relevance":relevance,
        "reason":response
    }
if __name__=='__main__':
    print(getRelevancy("I came to McDonalds with low hopes, but the fries were good, a bit soggy though. Service was quick and the atmostphere was a 3/5."))