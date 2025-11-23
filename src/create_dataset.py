from datasets import load_dataset
import random



def create_dataset():
    """Loads wildjailbreak and wilguardmix, shuffles them and combines into a list"""
    
    wgm_ds = load_dataset("allenai/wildguardmix", "wildguardtrain")["train"].shuffle(seed=42)
    wgm_prompts = [elt["prompt"] for elt in wgm_ds if elt["prompt"]][::8]
    
    
    
    wjb_ds = load_dataset("allenai/wildjailbreak", "eval")["train"]
    wjb_ds = wjb_ds.shuffle(seed=42)
    wjb_prompts = [elt["adversarial"] for elt in wjb_ds if elt["adversarial"]]
    ds = wgm_prompts + wjb_prompts
    random.shuffle(ds)
    print(f"Adding {len(wgm_prompts)} prompts from WildGuardMix and {len(wjb_prompts)} from WildJailBreak")
    return ds[0:200]