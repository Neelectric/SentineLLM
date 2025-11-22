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



def olmo_trace(frontier_model_id, prompt_text, frontier_text):
    """
    Returns documents in pre-training corpus of frontier model that are likely to have led to the completion.
    """
    
    
    
    return