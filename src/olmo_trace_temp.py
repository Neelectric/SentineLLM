### here we implement the tracing functionality from OLMoTrace. Full credit goes to the AllenAI team, https://allenai.org/blog/olmotrace, https://infini-gram.readthedocs.io/en/latest/api.html, and the authors of OlmoTrace:
# @misc{liu2025olmotracetracinglanguagemodel,
#       title={OLMoTrace: Tracing Language Model Outputs Back to Trillions of Training Tokens}, 
#       author={Jiacheng Liu and Taylor Blanton and Yanai Elazar and Sewon Min and YenSung Chen and Arnavi Chheda-Kothary and Huy Tran and Byron Bischoff and Eric Marsh and Michael Schmitz and Cassidy Trier and Aaron Sarnat and Jenna James and Jon Borchardt and Bailey Kuehl and Evie Cheng and Karen Farley and Sruthi Sreeram and Taira Anderson and David Albright and Carissa Schoenick and Luca Soldaini and Dirk Groeneveld and Rock Yuren Pang and Pang Wei Koh and Noah A. Smith and Sophie Lebrecht and Yejin Choi and Hannaneh Hajishirzi and Ali Farhadi and Jesse Dodge},
#       year={2025},
#       eprint={2504.07096},
#       archivePrefix={arXiv},
#       primaryClass={cs.CL},
#       url={https://arxiv.org/abs/2504.07096}, 
# }

##### we love you allenai <3 pls take me as an intern

import requests



def olmo_trace(frontier_model_id, prompt_text, frontier_text, frontier_tokenizer):
    """
    Returns documents in pre-training corpus of frontier model that are likely to have led to the completion.
    """
    if len(frontier_text) > 1000:
        query = frontier_text[0:1000]
    else:
        query = frontier_text

    # Step 1: Find all segments
    payload = {
        'index': 'v4_olmo-2-1124-13b-instruct_llama',
        'query_type': 'find',
        'query': query,
    }
    result = requests.post('https://api.infini-gram.io/', json=payload).json()
    print(f"Total occurrences: {result['cnt']}")

    segment_by_shard = result['segment_by_shard']

    # Step 2: Iterate through all shards and ranks
    # Step 2: Iterate through ALL shards and ranks
    all_documents = []

    for shard_idx, (start_rank, end_rank) in enumerate(segment_by_shard):
        print(f"Processing shard {shard_idx}: ranks {start_rank} to {end_rank} ({end_rank - start_rank + 1} documents)")
        
        for rank in range(start_rank, end_rank + 1):
            payload = {
                'index': 'v4_olmo-2-1124-13b-instruct_llama',
                'query_type': 'get_doc_by_rank',
                'query': query,
                's': shard_idx,
                'rank': rank
            }
            
            doc_result = requests.post('https://api.infini-gram.io/', json=payload).json()
            
            doc_span = doc_result["spans"][0][0]
            doc_span_tokenized = frontier_tokenizer(doc_span)[0]
            frontier_text_tokenized = frontier_tokenizer(frontier_text)[0]
            assert frontier_text_tokenized == doc_result['token_ids']
            
            sub_string_matching(doc_result['token_ids'], doc_span)
            
            all_documents.append(doc_result)
            
    print(f"\nTotal documents retrieved: {len(all_documents)}")
    
    
    
    return all_documents

def sub_string_matching(frontier_text, span):
    """Finds the maximum matching substring betwen LLM response and pre-train docs, returns indices"""
    "taken from https://www.geeksforgeeks.org/dsa/longest-common-substring-dp-29/"
    s1 = frontier_text
    s2 = span
    m = len(s1)
    n = len(s2)

    # Create a table to store lengths of longest
    # common suffixes of substrings.
    LCSuf = [[0] * (n + 1) for _ in range(m + 1)]
    res = 0
    end_pos = 0

    # Build LCSuf[m+1][n+1] in bottom-up fashion.
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                LCSuf[i][j] = LCSuf[i - 1][j - 1] + 1
                res = max(res, LCSuf[i][j])
                end_pos = i
            else:
                LCSuf[i][j] = 0
    lcs = s1[end_pos - res:end_pos] if res > 0 else ""

    return lcs