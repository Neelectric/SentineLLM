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
import json



async def olmo_trace(frontier_model_id, prompt_text, frontier_text, frontier_tokenizer):
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
    for i in range(5):
        try:
            result = requests.post('https://api.infini-gram.io/', json=payload).json()
            occurences = result['cnt']
            break
        except:
            continue
    print(f"Total occurrences: {occurences} after {i} retries")

    segment_by_shard = result['segment_by_shard']

    # Step 2: Iterate through all shards and ranks
    # Step 2: Iterate through ALL shards and ranks
    all_documents = []

    for shard_idx, (start_rank, end_rank) in enumerate(segment_by_shard):
        # print(f"Processing shard {shard_idx}: ranks {start_rank} to {end_rank} ({end_rank - start_rank + 1} documents)")
        
        for rank in range(start_rank, end_rank + 1):
            payload = {
                'index': 'v4_olmo-2-1124-13b-instruct_llama',
                'query_type': 'get_doc_by_rank',
                'query': query,
                's': shard_idx,
                'rank': rank
            }
            
            doc_result = requests.post('https://api.infini-gram.io/', json=payload).json()
            # print(doc_result)
            doc_span = doc_result["spans"][0][0]
            # print(f"doc_result['spans'] is {doc_result['spans']}")
            # print("\n"*4)
            
            # given the doc and the response from the LLM, find the longest common substring (in tokens)
            
            doc_span_tokenized = frontier_tokenizer(doc_span)[0].ids[1:]
            frontier_text_tokenized = frontier_tokenizer(frontier_text)[0].ids[1:]
            doc_result_tokenized = doc_result['token_ids']
            # assert frontier_text_tokenized == doc_result_tokenized
            
            # Find LCS token positions
            _, lcs_toks, lcs_len = sub_string_matching(doc_result_tokenized, doc_span_tokenized)
            lcs = frontier_tokenizer.decode(lcs_toks)  # Now from the span!

            doc_result["longest_common_substring"] = lcs
            
            metadata = json.loads(doc_result["metadata"])
            return_object = {
                "span": doc_result["spans"][0][0],
                "longest_common_substring": lcs,
                "doc_ix": doc_result["doc_ix"],
                "source": metadata["path"],
            }

            if len(lcs_toks) == 0:
                print("LCS HAS LENGTH 0")
                continue
            all_documents.append(return_object)
    
    print(f"\nTotal documents retrieved: {len(all_documents)}")
    
    
    return_string = ""
    for doc in all_documents:
        span = doc["span"].replace('```', '`\u200b`\u200b`')
        lcs = doc["longest_common_substring"]
        doc_id = doc["doc_ix"]
        source = doc["source"]

        
        # Tokenize the span to find LCS position
        doc_span_tokenized = frontier_tokenizer(span)[0].ids[1:]
        lcs_tokenized = frontier_tokenizer(lcs)[0].ids[1:]
        
        # Find where LCS appears in the span tokens
        lcs_start = -1
        for i in range(len(doc_span_tokenized) - len(lcs_tokenized) + 1):
            if doc_span_tokenized[i:i+len(lcs_tokenized)] == lcs_tokenized:
                lcs_start = i
                break
        
        # Truncate to 50 tokens before and after
        if lcs_start != -1:
            lcs_end = lcs_start + len(lcs_tokenized)
            start_idx = max(0, lcs_start - 50)
            end_idx = min(len(doc_span_tokenized), lcs_end + 50)
            
            # Decode in three parts to preserve exact LCS
            before_tokens = doc_span_tokenized[start_idx:lcs_start]
            lcs_tokens = doc_span_tokenized[lcs_start:lcs_end]
            after_tokens = doc_span_tokenized[lcs_end:end_idx]
            
            before_text = frontier_tokenizer.decode(before_tokens)
            lcs_text = frontier_tokenizer.decode(lcs_tokens)
            after_text = frontier_tokenizer.decode(after_tokens)
            
            marked_span = f"{before_text}<marked>{lcs_text}</marked>{after_text}"
            # print("Truncation successful")
        else:
            marked_span = span
            # print("Truncation failed, falling back")
        
        metadata_header = f'<div style="color: #666; margin-bottom: 8px;"><b>Doc ID:</b> {doc_id} | <b>Source:</b> {source}</div>'
        return_string += metadata_header + marked_span + "<hr />"

    return return_string


            

def sub_string_matching(s1, s2):
    """Returns (lcs_from_s1, lcs_from_s2, length)"""
    m = len(s1)
    n = len(s2)
    LCSuf = [[0] * (n + 1) for _ in range(m + 1)]
    res = 0
    end_pos_s1 = 0
    end_pos_s2 = 0

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                LCSuf[i][j] = LCSuf[i - 1][j - 1] + 1
                if LCSuf[i][j] > res:
                    res = LCSuf[i][j]
                    end_pos_s1 = i
                    end_pos_s2 = j
            else:
                LCSuf[i][j] = 0
    
    lcs_s1 = s1[end_pos_s1 - res:end_pos_s1] if res > 0 else []
    lcs_s2 = s2[end_pos_s2 - res:end_pos_s2] if res > 0 else []
    
    return lcs_s1, lcs_s2, res