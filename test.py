import re 

def reformat_award_id(award_id):
    if not isinstance(award_id, str):
        return None
    match = re.search(r'\d+', award_id)
    if match:
        return match.group(0) 
    else:
        return None  
    

print(reformat_award_id("IDIFEDER/2018/048"))  # Should print '1234567'